"""Query the College Scorecard API (US Dept. of Education) for college data.

Usage examples:
    node scripts/run.mjs scorecard_search --name "Stanford"
    node scripts/run.mjs scorecard_search --state MA,CT --admit-rate 0.3..0.6 \
        --size 2000..15000 --sort admission_rate --per-page 50
    node scripts/run.mjs scorecard_search --id 166027 --fields full

Free API. Key resolution: plugin userConfig -> env SCORECARD_API_KEY ->
workspace config -> DEMO_KEY (30 req/hour, 50/day/IP). Responses are cached
in the workspace for 7 days. Output: one JSON document on stdout.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from lib import config
from lib.http_cache import HttpError, get_json
from lib.workspace import find_workspace

BASE_URL = "https://api.data.gov/ed/collegescorecard/v1/schools"

CORE_FIELDS = [
    "id",
    "school.name",
    "school.state",
    "school.city",
    "school.school_url",
    "school.price_calculator_url",
    "school.ownership",
    "latest.student.size",
    "latest.admissions.admission_rate.overall",
    "latest.admissions.sat_scores.25th_percentile.critical_reading",
    "latest.admissions.sat_scores.75th_percentile.critical_reading",
    "latest.admissions.sat_scores.25th_percentile.math",
    "latest.admissions.sat_scores.75th_percentile.math",
    "latest.admissions.act_scores.25th_percentile.cumulative",
    "latest.admissions.act_scores.75th_percentile.cumulative",
    "latest.cost.avg_net_price.public",
    "latest.cost.avg_net_price.private",
    "latest.cost.net_price.public.by_income_level.48001-75000",
    "latest.cost.net_price.private.by_income_level.48001-75000",
    "latest.cost.net_price.public.by_income_level.75001-110000",
    "latest.cost.net_price.private.by_income_level.75001-110000",
    "latest.cost.tuition.in_state",
    "latest.cost.tuition.out_of_state",
    "latest.completion.consumer_rate",
    "latest.earnings.10_yrs_after_entry.median",
]

SORTABLE = {
    "admission_rate": "latest.admissions.admission_rate.overall",
    "size": "latest.student.size",
    "earnings": "latest.earnings.10_yrs_after_entry.median",
    "net_price_public": "latest.cost.avg_net_price.public",
    "net_price_private": "latest.cost.avg_net_price.private",
    "name": "school.name",
}


def normalize(row: dict) -> dict:
    """Flatten a Scorecard row into the record shape skills consume."""
    g = row.get

    def np(kind: str, bracket: str):
        return g(f"latest.cost.net_price.{kind}.by_income_level.{bracket}")

    ownership = {1: "public", 2: "private_nonprofit", 3: "private_forprofit"}.get(g("school.ownership"))
    return {
        "unitid": g("id"),
        "name": g("school.name"),
        "state": g("school.state"),
        "city": g("school.city"),
        "url": g("school.school_url"),
        "net_price_calculator": g("school.price_calculator_url"),
        "ownership": ownership,
        "size": g("latest.student.size"),
        "admit_rate": g("latest.admissions.admission_rate.overall"),
        "sat": {
            "ebrw_25": g("latest.admissions.sat_scores.25th_percentile.critical_reading"),
            "ebrw_75": g("latest.admissions.sat_scores.75th_percentile.critical_reading"),
            "math_25": g("latest.admissions.sat_scores.25th_percentile.math"),
            "math_75": g("latest.admissions.sat_scores.75th_percentile.math"),
        },
        "act": {
            "comp_25": g("latest.admissions.act_scores.25th_percentile.cumulative"),
            "comp_75": g("latest.admissions.act_scores.75th_percentile.cumulative"),
        },
        "avg_net_price": g("latest.cost.avg_net_price.public") or g("latest.cost.avg_net_price.private"),
        "net_price_by_income": {
            "48001-75000": np("public", "48001-75000") or np("private", "48001-75000"),
            "75001-110000": np("public", "75001-110000") or np("private", "75001-110000"),
        },
        "tuition": {"in_state": g("latest.cost.tuition.in_state"), "out_of_state": g("latest.cost.tuition.out_of_state")},
        "grad_rate": g("latest.completion.consumer_rate"),
        "median_earnings_10yr": g("latest.earnings.10_yrs_after_entry.median"),
    }


def build_params(args, api_key: str) -> dict:
    params: dict[str, str] = {"api_key": api_key, "per_page": str(args.per_page), "page": str(args.page)}
    params["fields"] = ",".join(CORE_FIELDS)
    if args.id:
        params["id"] = str(args.id)
    if args.name:
        params["school.name"] = args.name
    if args.state:
        params["school.state"] = args.state.upper()
    if args.admit_rate:
        params["latest.admissions.admission_rate.overall__range"] = args.admit_rate
    if args.size:
        params["latest.student.size__range"] = args.size
    if args.sat_math_75:
        params["latest.admissions.sat_scores.75th_percentile.math__range"] = args.sat_math_75
    # Degree-granting 4-year schools by default (predominant degree: bachelor's).
    if not args.id and not args.name:
        params["school.degrees_awarded.predominant"] = "3"
    if args.sort:
        field = SORTABLE.get(args.sort.removesuffix(":desc"), None)
        if field:
            params["sort"] = field + (":desc" if args.sort.endswith(":desc") else "")
    return params


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name")
    ap.add_argument("--id", type=int)
    ap.add_argument("--state", help="comma-separated, e.g. MA,CT")
    ap.add_argument("--admit-rate", help="range min..max, e.g. 0.3..0.6")
    ap.add_argument("--size", help="range, e.g. 2000..15000")
    ap.add_argument("--sat-math-75", help="range, e.g. 700..")
    ap.add_argument("--sort", help="admission_rate|size|earnings|net_price_public|net_price_private|name[:desc]")
    ap.add_argument("--per-page", type=int, default=50)
    ap.add_argument("--page", type=int, default=0)
    ap.add_argument("--fields", choices=["core", "full"], default="core")
    ap.add_argument("--workspace", default=None)
    ap.add_argument("--no-cache", action="store_true")
    args = ap.parse_args(argv)

    ws = Path(args.workspace) if args.workspace else find_workspace()
    api_key = config.get_scorecard_key(ws)
    params = build_params(args, api_key)
    if args.fields == "full":
        params.pop("fields", None)

    try:
        doc = get_json(BASE_URL, params, source="scorecard", workspace=ws, use_cache=not args.no_cache)
    except HttpError as e:
        err = {"error": {"code": f"http_{e.status}", "url": BASE_URL}}
        if e.status == 429 and api_key == config.SCORECARD_DEMO_KEY:
            err["error"]["message"] = (
                "DEMO_KEY rate limit reached (30 requests/hour, 50/day per IP). "
                "Get a free instant key at https://api.data.gov/signup and set it in the "
                "plugin settings, or wait an hour. Cached results are unaffected."
            )
        elif e.status == 403:
            err["error"]["message"] = "API key rejected — check the scorecard_api_key plugin setting."
        else:
            err["error"]["message"] = str(e)
        print(json.dumps(err))
        return 1

    results = doc.get("results", [])
    out = {
        "total": doc.get("metadata", {}).get("total"),
        "page": doc.get("metadata", {}).get("page"),
        "per_page": doc.get("metadata", {}).get("per_page"),
        "demo_key": api_key == config.SCORECARD_DEMO_KEY,
        "results": [normalize(r) for r in results] if args.fields == "core" else results,
    }
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
