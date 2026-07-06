"""Maintainer tool: parse the Common App Requirements Grid PDF into data/deadlines.json.

Usage (from repo root, dev venv with pdfplumber):
    python tools/build_reqgrid.py --pdf tools/_downloads/ReqGrid.pdf --out data/deadlines.json

The grid is a landscape ruled table, ~20 rows/page, headers repeated per page.
Columns (2025-26 layout):
  0 name | 1 school type | 2 ED | 3 EDII | 4 EA | 5 EAII | 6 REA | 7 RD/Rolling
  8 US fee | 9 INTL fee | 10 personal essay | 11 C&G | 12 portfolio | 13 writing
  14 test policy | 15 SAT/ACT used | 16 INTL english tests
  17 TE | 18 OE | 19 MR | 20 CR | 21 saves forms

Test-policy legend (PDF footnotes): A=Always required, F=Flexible,
I=Ignored, N=Never required, S=Sometimes required.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

import pdfplumber

REPO_ROOT = Path(__file__).resolve().parent.parent

TEST_POLICY_MAP = {
    "A": "required",
    "F": "flexible",
    "S": "flexible",
    "N": "optional",
    "I": "free",
}

DATE_RE = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")
FEE_RE = re.compile(r"^\$(\d+)$")


def clean(cell) -> str:
    if cell is None:
        return ""
    return re.sub(r"\s+", " ", str(cell)).strip()


def parse_date(cell: str) -> str | None:
    m = DATE_RE.match(cell)
    if not m:
        return None
    mm, dd, yyyy = (int(g) for g in m.groups())
    try:
        return dt.date(yyyy, mm, dd).isoformat()
    except ValueError:
        return None


def parse_fee(cell: str) -> int | None:
    m = FEE_RE.match(cell.replace(",", ""))
    return int(m.group(1)) if m else None


def parse_int(cell: str) -> int | None:
    return int(cell) if cell.isdigit() else None


def parse_row(row: list) -> dict | None:
    cells = [clean(c) for c in row]
    if len(cells) < 22:
        cells += [""] * (22 - len(cells))
    name = cells[0]
    if not name or name.startswith(("2025-", "2026-", "First Year", "Common App Member", "See bottom")):
        return None
    # Footnote fragments on the notes pages land in the table grid; every real
    # college row carries a school type. Overrides (UC, MIT, ...) merge later.
    if not cells[1].startswith(("Coed", "Women", "Men", "Coord")):
        return None

    deadlines = {}
    stats = {"date_cells": 0, "parsed_dates": 0}
    for key, idx in (("ED", 2), ("ED2", 3), ("EA", 4), ("EA2", 5), ("REA", 6)):
        val = cells[idx]
        if val:
            stats["date_cells"] += 1
            iso = parse_date(val)
            if iso:
                stats["parsed_dates"] += 1
                deadlines[key] = iso
            else:
                deadlines[key] = {"note": val}
    rd = cells[7]
    if rd:
        if rd.lower() == "rolling":
            deadlines["RD"] = "rolling"
        else:
            stats["date_cells"] += 1
            iso = parse_date(rd)
            if iso:
                stats["parsed_dates"] += 1
                deadlines["RD"] = iso
            else:
                deadlines["RD"] = {"note": rd}

    tp_code = cells[14][:1].upper() if cells[14] else ""
    record = {
        "name": name,
        "system": "common_app",
        "school_type": cells[1] or None,
        "deadlines": deadlines,
        "fees": {"us": parse_fee(cells[8]), "intl": parse_fee(cells[9])},
        "personal_essay": cells[10].lower().startswith("y"),
        "courses_and_grades": cells[11] or None,
        "portfolio": cells[12] or None,
        "writing_supplement": cells[13] or None,
        "test_policy_code": cells[14] or None,
        "test_policy": TEST_POLICY_MAP.get(tp_code),
        "tests_used": cells[15] or None,
        "english_tests": cells[16] or None,
        "recs": {
            "teacher_evals": parse_int(cells[17]),
            "other_evals": parse_int(cells[18]),
            "midyear_report": cells[19].upper().startswith("Y"),
            "counselor_rec": cells[20].upper().startswith("Y"),
        },
    }
    # Rolling review rewards early submission — flag it so skills can set a
    # strategic recommended_submit_by rather than pointing at the deadline.
    if deadlines.get("RD") == "rolling":
        record["admission_type"] = "rolling"
    record["_stats"] = stats
    return record


def extract_meta(first_page_text: str) -> dict:
    cycle_m = re.search(r"(20\d{2})-(\d{2})", first_page_text)
    updated_m = re.search(r"Updated:\s*(\d{2})-(\d{2})-(\d{4})", first_page_text)
    meta = {}
    if cycle_m:
        meta["cycle"] = f"{cycle_m.group(1)}-{cycle_m.group(2)}"
    if updated_m:
        mm, dd, yyyy = updated_m.groups()
        meta["source_updated"] = f"{yyyy}-{mm}-{dd}"
    return meta


def merge_overrides(colleges: list[dict], overrides_path: Path) -> list[dict]:
    if not overrides_path.is_file():
        return colleges
    overrides = json.loads(overrides_path.read_text(encoding="utf-8"))
    by_name = {c["name"].lower(): c for c in colleges}
    for entry in overrides.get("colleges", []):
        key = entry["name"].lower()
        if key in by_name:
            by_name[key].update(entry)
        else:
            colleges.append(entry)
    return colleges


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", default=str(REPO_ROOT / "data" / "deadlines.json"))
    ap.add_argument("--overrides", default=str(REPO_ROOT / "tools" / "overrides" / "deadlines_overrides.json"))
    args = ap.parse_args(argv)

    colleges: list[dict] = []
    date_cells = parsed_dates = 0

    # The grid draws horizontal rules per college row, but vertical rules only
    # in the header band — so defaults collapse each data row into one cell.
    # Fix: feed the header's vertical line positions in as explicit full-height
    # lines. Canonical 2025-26 layout has 23 lines / 22 columns.
    canonical_vlines = [18, 76, 114, 145, 176, 207, 237, 268, 299, 346, 385,
                        419, 453, 486, 520, 553, 601, 630, 659, 688, 716, 745, 774]

    with pdfplumber.open(args.pdf) as pdf:
        meta = extract_meta(pdf.pages[0].extract_text() or "")
        for page in pdf.pages:
            vlines = sorted({round(ln["x0"]) for ln in page.lines if abs(ln["x0"] - ln["x1"]) < 0.5})
            if len(vlines) < 20:
                vlines = canonical_vlines
            settings = {
                "vertical_strategy": "explicit",
                "explicit_vertical_lines": vlines,
                "horizontal_strategy": "lines",
            }
            for table in page.extract_tables(settings):
                for row in table:
                    rec = parse_row(row)
                    if rec is None:
                        continue
                    stats = rec.pop("_stats")
                    date_cells += stats["date_cells"]
                    parsed_dates += stats["parsed_dates"]
                    colleges.append(rec)

    # De-duplicate rows that wrap across page breaks (same name twice → keep the
    # one with more populated deadline cells).
    dedup: dict[str, dict] = {}
    for c in colleges:
        key = c["name"].lower()
        if key not in dedup or len(c["deadlines"]) > len(dedup[key]["deadlines"]):
            dedup[key] = c
    colleges = sorted(dedup.values(), key=lambda c: c["name"].lower())

    colleges = merge_overrides(colleges, Path(args.overrides))

    parse_rate = parsed_dates / date_cells if date_cells else 0
    doc = {
        "_meta": {
            **meta,
            "source": "https://content.commonapp.org/Files/ReqGrid.pdf",
            "built_at": dt.date.today().isoformat(),
            "last_verified": dt.date.today().isoformat(),
            "college_count": len(colleges),
            "date_parse_rate": round(parse_rate, 4),
            "notes": "Common App members from the Requirements Grid plus hand-maintained overrides for non-member systems (UC, CSU, MIT, Georgetown, ApplyTexas). Deadlines are cycle-specific — always verify on the college's official page.",
        },
        "colleges": colleges,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({
        "ok": True, "colleges": len(colleges),
        "date_parse_rate": round(parse_rate, 4), "out": str(out), **meta,
    }, indent=2))

    if not (1000 <= len(colleges) <= 1400):
        print(f"WARNING: college count {len(colleges)} outside expected 1000-1400", file=sys.stderr)
        return 1
    if parse_rate < 0.98:
        print(f"WARNING: date parse rate {parse_rate:.2%} below 98%", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
