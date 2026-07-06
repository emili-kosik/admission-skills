"""Workspace location and atomic JSON I/O (stdlib only).

A workspace is any directory containing .admissions/config.json. Writes are
atomic (tmp file + os.replace) and the previous version of a mutated file is
kept in .admissions/backups/ (rotating, last 3 per file).
"""

from __future__ import annotations

import json
import os
import shutil
import time
import uuid
from pathlib import Path

MARKER = Path(".admissions") / "config.json"
BACKUPS_PER_FILE = 3


def find_workspace(start: Path | None = None) -> Path | None:
    """Walk up from `start` (default cwd) looking for a workspace marker."""
    cur = (start or Path.cwd()).resolve()
    for candidate in [cur, *cur.parents]:
        if (candidate / MARKER).is_file():
            return candidate
    return None


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _backup(workspace: Path, path: Path) -> None:
    if not path.is_file():
        return
    backups = workspace / ".admissions" / "backups"
    try:
        backups.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        shutil.copy2(path, backups / f"{path.name}.{stamp}")
        siblings = sorted(backups.glob(f"{path.name}.*"))
        for old in siblings[:-BACKUPS_PER_FILE]:
            old.unlink(missing_ok=True)
    except OSError:
        pass  # backups are best-effort


def write_json(workspace: Path, path: Path, data: dict | list) -> None:
    """Atomically write JSON, backing up the previous version first.

    The temp name is unique per writer — a shared fixed name would let two
    concurrent writers interleave on one tmp file and publish garbage.
    """
    _backup(workspace, path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(f"{path.suffix}.{os.getpid()}.{uuid.uuid4().hex[:8]}.tmp")
    try:
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)
