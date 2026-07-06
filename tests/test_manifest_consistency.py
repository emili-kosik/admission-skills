"""Manifest integrity: plugin.json is the single source of truth."""

from __future__ import annotations

import json
import re
from pathlib import Path


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def test_plugin_manifest(repo_root: Path):
    manifest = load(repo_root / ".claude-plugin" / "plugin.json")
    assert manifest["name"] == "admit"
    assert re.fullmatch(r"[a-z][a-z0-9-]*", manifest["name"])
    assert re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"])
    assert manifest["license"] == "MIT"
    # every path the manifest references must exist
    hooks_rel = manifest["hooks"]
    assert hooks_rel.startswith("./")
    assert (repo_root / hooks_rel[2:]).is_file()


def test_marketplace_manifest(repo_root: Path):
    mp = load(repo_root / ".claude-plugin" / "marketplace.json")
    assert mp["name"] == "admission-skills"
    entries = mp["plugins"]
    assert len(entries) == 1
    assert entries[0]["name"] == "admit"
    assert entries[0]["source"] == "./"
    # marketplace must not pin its own version — plugin.json is authoritative
    assert "version" not in entries[0]


def test_no_stray_files_in_claude_plugin_dir(repo_root: Path):
    allowed = {"plugin.json", "marketplace.json"}
    actual = {p.name for p in (repo_root / ".claude-plugin").iterdir()}
    assert actual <= allowed, f"unexpected files: {actual - allowed}"


def test_hooks_json_paths_exist(repo_root: Path):
    hooks = load(repo_root / "hooks" / "hooks.json")["hooks"]
    for event, groups in hooks.items():
        for group in groups:
            for h in group["hooks"]:
                assert h["type"] == "command"
                # Claude Code executes `command` as a single shell string (an
                # `args` array is ignored — node would then eval stdin).
                assert "args" not in h, f"{event}: use a single command string, not args"
                m = re.fullmatch(r'node "\$\{CLAUDE_PLUGIN_ROOT\}/([^"]+)"', h["command"])
                assert m, f"{event}: command must be node \"${{CLAUDE_PLUGIN_ROOT}}/<script>\": {h['command']}"
                assert (repo_root / m.group(1)).is_file(), f"missing hook script: {m.group(1)}"


def test_changelog_top_entry_matches_version(repo_root: Path):
    changelog = repo_root / "CHANGELOG.md"
    if not changelog.is_file():
        return  # written in the docs phase; enforced once present
    manifest = load(repo_root / ".claude-plugin" / "plugin.json")
    top = re.search(r"^## \[?(\d+\.\d+\.\d+)", changelog.read_text(encoding="utf-8"), re.M)
    assert top, "CHANGELOG.md has no version heading"
    assert top.group(1) == manifest["version"]
