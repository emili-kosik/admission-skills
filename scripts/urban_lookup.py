"""Query the Urban Institute Education Data API (IPEDS mirror, no key needed).

Usage:
    node scripts/run.mjs urban_lookup --unitid 166027 --endpoint admissions-enrollment
    node scripts/run.mjs urban_lookup --unitid 243744 --endpoint admissions-requirements --year 2022

unitid here equals the College Scorecard `id`, so results join across both
APIs. `--year latest` (default) probes back from two years ago until a year
with data is found. Output: one JSON document on stdout.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from lib.http_cache import HttpError, get_json
from lib.workspace import find_workspace

BASE = "https://educationdata.urban.org/api/v1/college-university/ipeds"
ENDPOINTS = {"admissions-enrollment", "admissions-requirements", "directory"}


def fetch(endpoint: str, year: int, unitid: int, workspace) -> dict:
    url = f"{BASE}/{endpoint}/{year}/"
    return get_json(url, {"unitid": unitid}, source="urban", workspace=workspace)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--unitid", type=int, required=True)
    ap.add_argument("--endpoint", choices=sorted(ENDPOINTS), default="admissions-enrollment")
    ap.add_argument("--year", default="latest")
    ap.add_argument("--workspace", default=None)
    args = ap.parse_args(argv)

    ws = Path(args.workspace) if args.workspace else find_workspace()

    years: list[int]
    if args.year == "latest":
        newest = dt.date.today().year - 2
        years = list(range(newest, newest - 4, -1))
    else:
        years = [int(args.year)]

    last_err = None
    for year in years:
        try:
            doc = fetch(args.endpoint, year, args.unitid, ws)
        except HttpError as e:
            last_err = e
            continue
        results = doc.get("results", [])
        if results:
            print(json.dumps({"year": year, "endpoint": args.endpoint, "results": results},
                             indent=1, ensure_ascii=False))
            return 0

    msg = str(last_err) if last_err else f"no data for unitid {args.unitid} in years {years}"
    print(json.dumps({"error": {"code": "no_data", "message": msg}}))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
