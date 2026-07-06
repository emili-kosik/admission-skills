"""Search the CareerOneStop Scholarship Finder (US Dept. of Labor, 9,500+ awards).

Usage:
    node scripts/run.mjs scholarship_search --keyword robotics --state NJ --max 25

Requires free credentials (careeronestop_user_id + careeronestop_token) from
https://www.careeronestop.org/Developers/WebAPI/registration.aspx — there is
no demo tier. Without keys the script exits with a structured `needs_key`
error so the calling skill can fall back to guided web search.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from lib import config
from lib.http_cache import HttpError, get_json
from lib.workspace import find_workspace

BASE = "https://api.careeronestop.org/v1/scholarship"
STUDY_LEVELS = {"high_school": "High School", "bachelors": "Bachelor's",
                "graduate": "Graduate", "vocational": "Vocational"}
CACHE_TTL = 3 * 24 * 3600  # deadlines churn — keep the cache short


def normalize(item: dict) -> dict:
    return {
        "name": item.get("Title") or item.get("ScholarshipName"),
        "organization": item.get("Organization") or item.get("OrganizationName"),
        "purpose": (item.get("Purpose") or item.get("Description") or "")[:400] or None,
        "award_type": item.get("AwardType"),
        "amount": item.get("Awards") or item.get("AwardAmount"),
        "deadline": item.get("DeadlineDate") or item.get("Deadline"),
        "level_of_study": item.get("LevelOfStudy"),
        "url": item.get("Website") or item.get("ScholarshipURL"),
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keyword", default="")
    ap.add_argument("--state", default="", help="two-letter state code; empty = national")
    ap.add_argument("--level", choices=sorted(STUDY_LEVELS), default="high_school")
    ap.add_argument("--max", type=int, default=25)
    ap.add_argument("--workspace", default=None)
    ap.add_argument("--no-cache", action="store_true")
    args = ap.parse_args(argv)

    ws = Path(args.workspace) if args.workspace else find_workspace()
    user_id = config.get_key("careeronestop_user_id", ws)
    token = config.get_key("careeronestop_token", ws)
    if not user_id or not token:
        print(json.dumps({"error": {
            "code": "needs_key",
            "message": "CareerOneStop credentials not configured. Free signup: "
                       "https://www.careeronestop.org/Developers/WebAPI/registration.aspx — "
                       "then set careeronestop_user_id and careeronestop_token in the plugin settings. "
                       "Until then, fall back to guided web search for scholarships.",
        }}))
        return 1

    params = {
        "keyword": args.keyword or None,
        "location": args.state.upper() or None,
        "StudyLevelFilter": STUDY_LEVELS[args.level],
        "numberOfResults": str(args.max),
        "sortColumns": "Deadline",
        "sortDirections": "ASC",
    }
    try:
        doc = get_json(f"{BASE}/{user_id}", params, source="careeronestop", workspace=ws,
                       ttl_seconds=CACHE_TTL, use_cache=not args.no_cache,
                       headers={"Authorization": f"Bearer {token}"})
    except HttpError as e:
        code = "auth_failed" if e.status in (401, 403) else f"http_{e.status}"
        print(json.dumps({"error": {"code": code, "message": str(e)}}))
        return 1

    items = doc.get("Scholarships") or doc.get("ScholarshipList") or []
    out = {
        "total": doc.get("ScholarshipCount") or len(items),
        "query": {"keyword": args.keyword, "state": args.state, "level": STUDY_LEVELS[args.level]},
        "results": [normalize(i) for i in items],
    }
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
