"""Maintainer tool: build data/college_index.json from the Urban Institute
Education Data API (IPEDS directory mirror, no key required).

Usage:
    python tools/build_college_index.py [--year 2023] [--out data/college_index.json]

Keeps 4-year degree-granting institutions (sectors 1, 2, 3) — the admissions
use case — with name, state, city, unitid. ~250KB on disk.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE = "https://educationdata.urban.org/api/v1/college-university/ipeds/directory/{year}/"
SECTORS_4YEAR = {1, 2, 3}


def fetch_year(year: int) -> list[dict]:
    rows: list[dict] = []
    url = BASE.format(year=year)
    while url:
        req = urllib.request.Request(url, headers={"User-Agent": "admission-skills/1.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            doc = json.load(resp)
        rows.extend(doc.get("results", []))
        url = doc.get("next")
    return rows


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=None)
    ap.add_argument("--out", default=str(REPO_ROOT / "data" / "college_index.json"))
    args = ap.parse_args(argv)

    years = [args.year] if args.year else [dt.date.today().year - 2, dt.date.today().year - 3]
    rows, used_year = [], None
    for year in years:
        try:
            rows = fetch_year(year)
            if rows:
                used_year = year
                break
        except Exception as e:  # noqa: BLE001 - try the next year
            print(f"year {year} failed: {e}", file=sys.stderr)
    if not rows:
        print("no directory data retrieved", file=sys.stderr)
        return 1

    colleges = []
    for r in rows:
        if r.get("sector") not in SECTORS_4YEAR:
            continue
        name = (r.get("inst_name") or "").strip()
        if not name:
            continue
        entry = {
            "unitid": r.get("unitid"),
            "name": name,
            "state": r.get("state_abbr"),
            "city": (r.get("city") or "").strip() or None,
        }
        alias = (r.get("inst_alias") or "").strip()
        if alias and alias != name:
            entry["alias"] = alias
        colleges.append(entry)

    colleges.sort(key=lambda c: c["name"].lower())
    doc = {
        "_meta": {
            "source": BASE.format(year=used_year),
            "ipeds_year": used_year,
            "built_at": dt.date.today().isoformat(),
            "last_verified": dt.date.today().isoformat(),
            "count": len(colleges),
            "notes": "4-year degree-granting institutions (IPEDS sectors 1-3). unitid joins to College Scorecard 'id'.",
        },
        "colleges": colleges,
    }
    out = Path(args.out)
    out.write_text(json.dumps(doc, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "count": len(colleges), "ipeds_year": used_year, "out": str(out)}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
