"""Key and data-path resolution for the admit plugin (stdlib only).

Key resolution chain (first hit wins):
  1. CLAUDE_PLUGIN_OPTION_<NAME>  (plugin userConfig, keychain-backed)
  2. plain environment variable   (power users, CI)
  3. workspace .admissions/config.json  keys.<name>  (plaintext fallback)
  4. built-in default (DEMO_KEY for College Scorecard only)

Dataset resolution: a refreshed copy under $CLAUDE_PLUGIN_DATA/data/<file>
wins over the bundled $CLAUDE_PLUGIN_ROOT/data/<file>.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent

SCORECARD_DEMO_KEY = "DEMO_KEY"


def _workspace_config(workspace: Path | None) -> dict:
    if workspace is None:
        return {}
    cfg = workspace / ".admissions" / "config.json"
    if not cfg.is_file():
        return {}
    try:
        return json.loads(cfg.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def get_key(name: str, workspace: Path | None = None, default: str | None = None) -> str | None:
    """Resolve an API credential by short name, e.g. 'scorecard_api_key'."""
    upper = name.upper()
    for env_name in (f"CLAUDE_PLUGIN_OPTION_{upper}", upper):
        val = os.environ.get(env_name)
        if val:
            return val
    keys = _workspace_config(workspace).get("keys", {})
    if isinstance(keys, dict) and keys.get(name):
        return str(keys[name])
    return default


def get_scorecard_key(workspace: Path | None = None) -> str:
    return get_key("scorecard_api_key", workspace, default=SCORECARD_DEMO_KEY) or SCORECARD_DEMO_KEY


def data_path(filename: str) -> Path:
    """Resolve a bundled dataset, preferring a refreshed copy in CLAUDE_PLUGIN_DATA."""
    plugin_data = os.environ.get("CLAUDE_PLUGIN_DATA")
    if plugin_data:
        refreshed = Path(plugin_data) / "data" / filename
        if refreshed.is_file():
            return refreshed
    return PLUGIN_ROOT / "data" / filename


def load_dataset(filename: str) -> dict:
    """Load a dataset, falling back to the bundled copy if a refreshed one
    under CLAUDE_PLUGIN_DATA turns out truncated or corrupt."""
    path = data_path(filename)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        bundled = PLUGIN_ROOT / "data" / filename
        if path != bundled:
            return json.loads(bundled.read_text(encoding="utf-8"))
        raise
