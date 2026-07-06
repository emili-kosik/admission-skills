"""init_workspace scaffolding and lib.workspace atomic I/O."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import init_workspace
from lib import workspace as ws_lib


def test_scaffold_layout(workspace: Path):
    for rel in ["profile.json", "colleges.json", "essays/index.json", ".gitignore",
                "README.md", ".admissions/config.json", "essays/drafts",
                "essays/brainstorm", "essays/feedback", "aid/award-letters", "output"]:
        assert (workspace / rel).exists(), f"missing {rel}"
    config = json.loads((workspace / ".admissions" / "config.json").read_text(encoding="utf-8"))
    assert config["cycle"] == "2026-27"  # grad 2027 → apply fall 2026
    profile = json.loads((workspace / "profile.json").read_text(encoding="utf-8"))
    assert profile["student"]["grad_year"] == 2027


def test_refuses_to_overwrite(workspace: Path, capsys):
    rc = init_workspace.main(["--dir", str(workspace)])
    assert rc == 1
    assert "already_workspace" in capsys.readouterr().out


def test_cycle_math():
    assert init_workspace.compute_cycle(2027) == "2026-27"
    assert init_workspace.compute_cycle(2030) == "2029-30"
    # No grad year: assume the upcoming cycle from June onward — a summer
    # setup is a rising senior, and the prior cycle ended on May 1.
    assert init_workspace.compute_cycle(None, dt.date(2026, 5, 31)) == "2025-26"
    assert init_workspace.compute_cycle(None, dt.date(2026, 6, 1)) == "2026-27"
    assert init_workspace.compute_cycle(None, dt.date(2026, 7, 15)) == "2026-27"


def test_find_workspace_walks_up(workspace: Path):
    deep = workspace / "essays" / "drafts"
    assert ws_lib.find_workspace(deep) == workspace
    assert ws_lib.find_workspace(workspace.parent) is None


def test_atomic_write_and_backup(workspace: Path):
    path = workspace / "colleges.json"
    original = ws_lib.read_json(path)
    for i in range(5):
        data = {**original, "last_list_review": f"2026-0{i + 1}-01"}
        ws_lib.write_json(workspace, path, data)
    final = ws_lib.read_json(path)
    assert final["last_list_review"] == "2026-05-01"
    backups = list((workspace / ".admissions" / "backups").glob("colleges.json.*"))
    assert 1 <= len(backups) <= ws_lib.BACKUPS_PER_FILE
    assert not list(workspace.glob("*.tmp"))
