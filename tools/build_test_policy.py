"""Maintainer tool: build data/test_policy.json.

Layers, later wins:
  1. Self-reported testing-policy codes from the Common App Requirements Grid
     (already normalized in data/deadlines.json) — ~1,100 colleges.
  2. Hand-verified overrides for high-volatility institutions and the test-free
     systems (tools/overrides/test_policy_overrides.json, each entry citing the
     admissions page it was verified against).

Usage:
    python tools/build_test_policy.py [--out data/test_policy.json]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VALID = {"required", "optional", "flexible", "free"}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO_ROOT / "data" / "test_policy.json"))
    args = ap.parse_args(argv)

    deadlines = json.loads((REPO_ROOT / "data" / "deadlines.json").read_text(encoding="utf-8"))
    overrides = json.loads(
        (REPO_ROOT / "tools" / "overrides" / "test_policy_overrides.json").read_text(encoding="utf-8")
    )

    policies: dict[str, dict] = {}
    for c in deadlines["colleges"]:
        policy = c.get("test_policy")
        if policy in VALID:
            policies[c["name"].lower()] = {
                "name": c["name"],
                "policy": policy,
                "source": "commonapp_reqgrid",
                "source_detail": c.get("test_policy_code"),
            }

    for entry in overrides.get("policies", []) + overrides.get("systems", []):
        if entry.get("policy") not in VALID:
            continue
        key = entry["name"].lower()
        existing = policies.get(key, {})
        conflict = existing and existing.get("policy") != entry["policy"]
        policies[key] = {
            "name": entry["name"],
            "policy": entry["policy"],
            "source": "verified_override",
            "source_url": entry.get("source_url"),
            "verified": entry.get("verified", False),
            "notes": entry.get("notes") or None,
        }
        if conflict:
            policies[key]["superseded_reqgrid_value"] = existing["policy"]

    doc = {
        "_meta": {
            "cycle": deadlines["_meta"].get("cycle"),
            "built_at": dt.date.today().isoformat(),
            "last_verified": overrides.get("_meta", {}).get("last_verified", dt.date.today().isoformat()),
            "count": len(policies),
            "sources": [
                "Common App Requirements Grid testing-policy column (self-reported per college)",
                "Hand-verified per-institution overrides with citations",
            ],
            "staleness_rule": "Test policies flipped repeatedly 2024-2026. Treat any 'required' claim older than 6 months as needing live verification before it is asserted.",
            "legend": {"required": "SAT/ACT required", "optional": "test-optional", "flexible": "test-flexible (alternatives accepted or sometimes required)", "free": "test-free — scores never considered"},
        },
        "policies": sorted(policies.values(), key=lambda p: p["name"].lower()),
    }
    out = Path(args.out)
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "count": len(policies), "out": str(out)}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
