"""Refresh bundled datasets from the GitHub repo without a plugin update.

Usage:
    node scripts/run.mjs refresh_data [--branch main]

Downloads data/*.json from raw.githubusercontent.com into $CLAUDE_PLUGIN_DATA/data/
(which persists across plugin updates and is preferred by lib.config.data_path).
Each file must parse as JSON and carry _meta before it replaces anything.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from lib.config import PLUGIN_ROOT, data_path
from lib.http_cache import HttpError, get_json

REPO = "emili-kosik/admission-skills"
DATASETS = [
    "deadlines.json", "test_policy.json", "test_dates.json", "milestones.json",
    "essay_prompts.json", "ai_policies.json", "systems.json", "college_index.json", "sources.json",
]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--branch", default="main")
    args = ap.parse_args(argv)

    plugin_data = os.environ.get("CLAUDE_PLUGIN_DATA")
    if not plugin_data:
        print(json.dumps({"error": {
            "code": "no_plugin_data",
            "message": "CLAUDE_PLUGIN_DATA is not set (this command must run inside Claude Code). "
                       "Alternatively update the plugin itself to get fresh data.",
        }}))
        return 1
    target_dir = Path(plugin_data) / "data"
    target_dir.mkdir(parents=True, exist_ok=True)

    report = []
    failures = 0
    for name in DATASETS:
        url = f"https://raw.githubusercontent.com/{REPO}/{args.branch}/data/{name}"
        try:
            doc = get_json(url, source="refresh", use_cache=False, timeout=60)
        except (HttpError, json.JSONDecodeError) as e:
            report.append({"file": name, "status": "failed", "error": str(e)})
            failures += 1
            continue
        if "_meta" not in doc:
            report.append({"file": name, "status": "rejected", "error": "missing _meta"})
            failures += 1
            continue

        old_meta = {}
        try:
            old_meta = json.loads(data_path(name).read_text(encoding="utf-8")).get("_meta", {})
        except (OSError, json.JSONDecodeError):
            pass

        # Atomic replace — an interrupted write must never leave a truncated
        # dataset that data_path() would then prefer over the bundled copy.
        target = target_dir / name
        tmp = target.with_suffix(f".{os.getpid()}.tmp")
        try:
            tmp.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            os.replace(tmp, target)
        except OSError as e:
            report.append({"file": name, "status": "failed", "error": f"write failed: {e}"})
            failures += 1
            continue
        finally:
            tmp.unlink(missing_ok=True)
        report.append({
            "file": name, "status": "updated",
            "old": {k: old_meta.get(k) for k in ("cycle", "last_verified")},
            "new": {k: doc["_meta"].get(k) for k in ("cycle", "last_verified")},
        })

    print(json.dumps({
        "ok": failures == 0,
        "target": str(target_dir),
        "bundled_fallback": str(PLUGIN_ROOT / "data"),
        "report": report,
    }, indent=1, ensure_ascii=False))
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
