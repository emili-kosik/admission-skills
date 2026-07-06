"""Test bootstrap: block all network access so the suite is offline-only."""

from __future__ import annotations

import socket
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))


class _NetworkBlocked(Exception):
    pass


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    def _blocked(*args, **kwargs):
        raise _NetworkBlocked("Network access is forbidden in tests — use recorded fixtures.")

    monkeypatch.setattr(socket.socket, "connect", _blocked)


@pytest.fixture()
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture()
def workspace(tmp_path: Path) -> Path:
    """A freshly scaffolded workspace in a temp dir."""
    import init_workspace

    rc = init_workspace.main(["--dir", str(tmp_path / "ws"), "--grad-year", "2027"])
    assert rc == 0
    return tmp_path / "ws"
