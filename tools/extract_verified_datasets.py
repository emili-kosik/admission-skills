"""Maintainer tool: unpack the verify-verbatim workflow result into data/*.json.

The verification workflow (4 agents fetching primary sources) returns JSON code
blocks per topic. This script parses them and writes:
  data/essay_prompts.json
  data/ai_policies.json
  data/test_dates.json
  tools/overrides/test_policy_overrides.json

Usage:
    python tools/extract_verified_datasets.py --result <workflow-output-file> [--cycle 2026-27]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def parse_json_block(text: str) -> dict:
    m = re.search(r"```json\s*(.*?)```", text, re.S)
    raw = m.group(1) if m else text
    return json.loads(raw)


def write(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {path}")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--result", required=True)
    ap.add_argument("--cycle", default="2026-27")
    args = ap.parse_args(argv)

    payload = json.loads(Path(args.result).read_text(encoding="utf-8"))
    result = payload["result"] if "result" in payload else payload
    today = dt.date.today().isoformat()
    meta = {"cycle": args.cycle, "built_at": today, "last_verified": today}

    prompts = parse_json_block(result["essay_prompts"])
    write(REPO_ROOT / "data" / "essay_prompts.json", {
        "_meta": {**meta, "source": "commonapp.org/apply/essay-prompts + admission.universityofcalifornia.edu (fetched and quoted verbatim; see per-section notes)"},
        **prompts,
    })

    policies = parse_json_block(result["ai_policies"])
    write(REPO_ROOT / "data" / "ai_policies.json", {
        "_meta": {**meta, "source": "Institution admissions pages, quoted verbatim with per-entry citations",
                  "default_tier": "prohibitive",
                  "notes": "When a college has no entry here, apply the strictest-common-denominator rules (tier: prohibitive). The Common App fraud-policy baseline applies to all its members."},
        **policies,
    })

    dates = parse_json_block(result["test_dates"])
    write(REPO_ROOT / "data" / "test_dates.json", {
        "_meta": {**meta, "source": "satsuite.collegeboard.org, act.org, apstudents.collegeboard.org"},
        **dates,
    })

    seed = parse_json_block(result["test_policy_seed"])
    write(REPO_ROOT / "tools" / "overrides" / "test_policy_overrides.json", {
        "_meta": {**meta, "source": "Per-institution admissions pages / compassprep.com / fairtest.org (verified individually)"},
        **seed,
    })
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
