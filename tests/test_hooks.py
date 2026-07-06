"""Hook behavior tests: run the real Node scripts as subprocesses."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


def run_hook(repo_root: Path, script: str, stdin: dict, env_extra: dict | None = None) -> subprocess.CompletedProcess:
    import os

    env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(repo_root), **(env_extra or {})}
    return subprocess.run(
        ["node", str(repo_root / "scripts" / "hooks" / script)],
        input=json.dumps(stdin),
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )


# --- session_start ---------------------------------------------------------

def test_session_start_silent_outside_workspace(repo_root: Path, tmp_path: Path):
    r = run_hook(repo_root, "session_start.mjs", {"cwd": str(tmp_path)})
    assert r.returncode == 0
    assert r.stdout.strip() == ""


def test_session_start_briefing_in_workspace(repo_root: Path, workspace: Path):
    import datetime as dt

    soon = (dt.date.today() + dt.timedelta(days=5)).isoformat()
    colleges = {
        "schema_version": 1,
        "last_list_review": None,
        "colleges": [{
            "name": "Test University", "system": "common_app", "status": "applying",
            "plan": "EA", "deadline": soon, "deadline_verified": True,
        }],
    }
    (workspace / "colleges.json").write_text(json.dumps(colleges), encoding="utf-8")
    r = run_hook(repo_root, "session_start.mjs", {"cwd": str(workspace)})
    assert r.returncode == 0
    out = json.loads(r.stdout)
    ctx = out["hookSpecificOutput"]["additionalContext"]
    assert out["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "Test University" in ctx and "in 5 days" in ctx


def test_session_start_survives_corrupt_json(repo_root: Path, workspace: Path):
    (workspace / "colleges.json").write_text("{not json", encoding="utf-8")
    r = run_hook(repo_root, "session_start.mjs", {"cwd": str(workspace)})
    assert r.returncode == 0  # a broken workspace must never break the session


# --- essay_guard -----------------------------------------------------------

def test_essay_guard_blocks_drafts(repo_root: Path, workspace: Path):
    target = workspace / "essays" / "drafts" / "common-app-v1.md"
    r = run_hook(repo_root, "essay_guard.mjs", {"tool_name": "Write", "tool_input": {"file_path": str(target)}})
    assert r.returncode == 0
    out = json.loads(r.stdout)
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "fraud" in out["hookSpecificOutput"]["permissionDecisionReason"]


def test_essay_guard_allows_feedback(repo_root: Path, workspace: Path):
    target = workspace / "essays" / "feedback" / "memo.md"
    r = run_hook(repo_root, "essay_guard.mjs", {"tool_name": "Write", "tool_input": {"file_path": str(target)}})
    assert r.returncode == 0
    assert r.stdout.strip() == ""


def test_essay_guard_ignores_paths_outside_workspaces(repo_root: Path, tmp_path: Path):
    target = tmp_path / "essays" / "drafts" / "x.md"
    r = run_hook(repo_root, "essay_guard.mjs", {"tool_name": "Write", "tool_input": {"file_path": str(target)}})
    assert r.returncode == 0
    assert r.stdout.strip() == ""


def test_essay_guard_blocks_casing_variant_on_folding_platforms(repo_root: Path, workspace: Path):
    """NTFS/APFS are case-insensitive: Essays/Drafts/ writes to the real
    drafts dir, so the guard must fold case there."""
    import sys

    if sys.platform not in ("win32", "darwin"):
        return
    target = workspace / "Essays" / "Drafts" / "common-app-v1.md"
    r = run_hook(repo_root, "essay_guard.mjs", {"tool_name": "Write", "tool_input": {"file_path": str(target)}})
    assert r.returncode == 0
    assert json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_essay_guard_blocks_writeish_bash(repo_root: Path, workspace: Path):
    cmd = f"echo 'my essay' > \"{workspace / 'essays' / 'drafts' / 'x.md'}\""
    r = run_hook(repo_root, "essay_guard.mjs", {"tool_name": "Bash", "tool_input": {"command": cmd}})
    assert json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_essay_guard_allows_readonly_bash(repo_root: Path, workspace: Path):
    cmd = f"cat \"{workspace / 'essays' / 'drafts' / 'x.md'}\""
    r = run_hook(repo_root, "essay_guard.mjs", {"tool_name": "Bash", "tool_input": {"command": cmd}})
    assert r.stdout.strip() == ""


def test_essay_guard_covers_notebook_edit(repo_root: Path, workspace: Path):
    target = workspace / "essays" / "drafts" / "essay.ipynb"
    r = run_hook(repo_root, "essay_guard.mjs",
                 {"tool_name": "NotebookEdit", "tool_input": {"notebook_path": str(target)}})
    assert json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"


# --- validate_workspace (non-blocking: exit 0 + additionalContext note) -----

def _added_context(r) -> str:
    """The quiet note a non-blocking PostToolUse hook feeds back to Claude."""
    if not r.stdout.strip():
        return ""
    return json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]


def test_validator_flags_bad_status_without_blocking(repo_root: Path, workspace: Path):
    bad = {"schema_version": 1, "colleges": [{"name": "MIT", "system": "institutional", "status": "aplied"}]}
    path = workspace / "colleges.json"
    path.write_text(json.dumps(bad), encoding="utf-8")
    r = run_hook(repo_root, "validate_workspace.mjs", {"tool_input": {"file_path": str(path)}})
    assert r.returncode == 0, "validation must never block the tool call"
    assert "aplied" in _added_context(r)


def test_validator_silent_on_valid_colleges(repo_root: Path, workspace: Path):
    good = {
        "schema_version": 1,
        "colleges": [{"name": "MIT", "unitid": 166683, "system": "institutional",
                      "status": "researching", "plan": "EA", "deadline": "2026-11-01"}],
    }
    path = workspace / "colleges.json"
    path.write_text(json.dumps(good), encoding="utf-8")
    r = run_hook(repo_root, "validate_workspace.mjs", {"tool_input": {"file_path": str(path)}})
    assert r.returncode == 0
    assert r.stdout.strip() == ""  # silent when everything is fine


def test_validator_tolerates_incomplete_onboarding_profile(repo_root: Path, workspace: Path):
    """A half-filled profile mid-onboarding (operator unset, free-text income)
    must not trigger any note — this was the false 'hook error'."""
    profile = json.loads((workspace / "profile.json").read_text(encoding="utf-8"))
    profile["operator"] = None
    profile["finances"]["income_bracket"] = "<$100K, family of 5"
    profile["testing"]["sat"] = [{"total": 1370, "note": "retake planned August 2026"}]
    path = workspace / "profile.json"
    path.write_text(json.dumps(profile), encoding="utf-8")
    r = run_hook(repo_root, "validate_workspace.mjs", {"tool_input": {"file_path": str(path)}})
    assert r.returncode == 0
    assert r.stdout.strip() == ""


def test_validator_flags_bad_admission_type_without_blocking(repo_root: Path, workspace: Path):
    bad = {"schema_version": 1, "colleges": [{"name": "X", "system": "common_app",
           "status": "researching", "admission_type": "instant", "recommended_submit_by": "Augustish"}]}
    path = workspace / "colleges.json"
    path.write_text(json.dumps(bad), encoding="utf-8")
    r = run_hook(repo_root, "validate_workspace.mjs", {"tool_input": {"file_path": str(path)}})
    assert r.returncode == 0
    ctx = _added_context(r)
    assert "admission_type" in ctx and "recommended_submit_by" in ctx


def test_validator_flags_pii_keys_without_blocking(repo_root: Path, workspace: Path):
    profile = json.loads((workspace / "profile.json").read_text(encoding="utf-8"))
    profile["student"]["birthdate"] = "2009-01-01"
    path = workspace / "profile.json"
    path.write_text(json.dumps(profile), encoding="utf-8")
    r = run_hook(repo_root, "validate_workspace.mjs", {"tool_input": {"file_path": str(path)}})
    assert r.returncode == 0
    assert "birthdate" in _added_context(r)


def test_validator_ignores_unrelated_files(repo_root: Path, workspace: Path):
    path = workspace / "notes.json"
    path.write_text("{definitely: not valid json", encoding="utf-8")
    r = run_hook(repo_root, "validate_workspace.mjs", {"tool_input": {"file_path": str(path)}})
    assert r.returncode == 0


def test_validator_catches_casing_variant_on_folding_platforms(repo_root: Path, workspace: Path):
    import sys

    if sys.platform not in ("win32", "darwin"):
        return
    profile = json.loads((workspace / "profile.json").read_text(encoding="utf-8"))
    profile["student"]["ssn"] = "123-45-6789"
    (workspace / "profile.json").write_text(json.dumps(profile), encoding="utf-8")
    variant = workspace / "Profile.json"  # same file on NTFS/APFS
    r = run_hook(repo_root, "validate_workspace.mjs", {"tool_input": {"file_path": str(variant)}})
    assert r.returncode == 0
    assert "ssn" in _added_context(r)


# --- snapshot_essay --------------------------------------------------------

def test_snapshot_essay_saves_history_and_counts_words(repo_root: Path, workspace: Path):
    draft = workspace / "essays" / "drafts" / "piq-1.md"
    draft.parent.mkdir(parents=True, exist_ok=True)
    draft.write_text("word " * 400, encoding="utf-8")
    index = {"schema_version": 1, "essays": [{"file": "drafts/piq-1.md", "target": "uc_piq", "word_limit": 350}]}
    (workspace / "essays" / "index.json").write_text(json.dumps(index), encoding="utf-8")

    r = run_hook(repo_root, "snapshot_essay.mjs", {"tool_input": {"file_path": str(draft)}})
    assert r.returncode == 0
    out = json.loads(r.stdout)
    note = out["hookSpecificOutput"]["additionalContext"]
    assert "400 words" in note and "50 OVER" in note
    assert list((workspace / "essays" / ".history").glob("drafts__piq-1.*.md"))


def test_snapshot_namespaces_by_subdir(repo_root: Path, workspace: Path):
    """drafts/x.md and feedback/x.md must not share one history namespace."""
    for sub in ("drafts", "feedback"):
        f = workspace / "essays" / sub / "x.md"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(f"{sub} content", encoding="utf-8")
        run_hook(repo_root, "snapshot_essay.mjs", {"tool_input": {"file_path": str(f)}})
    history = [p.name for p in (workspace / "essays" / ".history").glob("*.md")]
    assert any(n.startswith("drafts__x.") for n in history)
    assert any(n.startswith("feedback__x.") for n in history)


def test_session_start_nudges_on_malformed_checkin_date(repo_root: Path, workspace: Path):
    cfg_path = workspace / ".admissions" / "config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    cfg["state"]["last_checkin"] = "2026-07-01T10:00:00Z"  # not YYYY-MM-DD
    cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
    r = run_hook(repo_root, "session_start.mjs", {"cwd": str(workspace)})
    assert r.returncode == 0
    ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "check-in due" in ctx
