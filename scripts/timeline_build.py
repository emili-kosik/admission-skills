"""Build the personalized milestone timeline from the rule table.

Usage:
    node scripts/run.mjs timeline_build [--workspace DIR] [--today YYYY-MM-DD]

Reads profile.json, .admissions/config.json, colleges.json and the bundled
data/milestones.json + data/test_dates.json; writes .admissions/milestones.json
(preserving `done` flags across regenerations) and prints a summary.

Year math (documented in data/milestones.json): a milestone at grade g,
month m falls in calendar year grad_year-13+g when m >= 8, else grad_year-12+g.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from lib.config import load_dataset
from lib.workspace import find_workspace, read_json, write_json

LOOKBACK_DAYS = 30


def compute_grade(grad_year: int, today: dt.date) -> int:
    school_year_end = today.year + 1 if today.month >= 8 else today.year
    return 12 - (grad_year - school_year_end)


def milestone_year(grad_year: int, grade: int, month: int) -> int:
    return grad_year - 13 + grade if month >= 8 else grad_year - 12 + grade


def resolve_tracks(profile: dict, cfg: dict, colleges: list[dict]) -> set[str]:
    tracks = {"all"}
    tracks.update(cfg.get("systems", ["common_app"]))
    tracks.update(c["system"] for c in colleges if c.get("system"))
    if profile.get("student", {}).get("residency") == "international":
        tracks.add("international")

    policies = [c.get("test_policy") for c in colleges if c.get("test_policy")]
    all_test_free = bool(policies) and all(p == "free" for p in policies)
    if not all_test_free:
        tracks.add("test_taker")

    academics = profile.get("academics", {})
    if academics.get("ap_taken") or any(str(c).startswith("AP") for c in academics.get("current_courses", [])):
        tracks.add("ap_student")
    if profile.get("finances", {}).get("need_based_aid") is not False:
        tracks.add("aid_seeker")
    return tracks


def test_dates_in(dataset: dict, kind: str, grad_year: int, grade: int, months: list[int]) -> list[dict]:
    """Test dates whose month is in `months`, each resolved to its own year."""
    prefixes = {f"{milestone_year(grad_year, grade, m):04d}-{m:02d}-" for m in months}
    return [d for d in dataset.get(kind, {}).get("dates", [])
            if any(d["test_date"].startswith(p) for p in prefixes)]


def build_items(profile, cfg, colleges, rules, test_dates, today):
    grad_year = profile["student"]["grad_year"]
    current_grade = compute_grade(grad_year, today)
    tracks = resolve_tracks(profile, cfg, colleges)
    horizon_start = today - dt.timedelta(days=LOOKBACK_DAYS)
    items = []

    def include(date: dt.date | None, grade: int, month: int) -> bool:
        if date is not None:
            return date >= horizon_start
        # Undated advisory: include if its month anchor isn't clearly past.
        anchor = dt.date(milestone_year(grad_year, grade, month), month, 28)
        return anchor >= horizon_start

    for rule in rules["milestones"]:
        # Coarse guard only — the immediately previous grade still flows
        # through the date logic, so windows that stay open across the Aug 1
        # grade rollover (e.g. the grade-11 summer essay, open until Aug 15)
        # and items inside the lookback survive. Older grades age out anyway.
        if rule["grade"] < current_grade - 1:
            continue
        if not set(rule["tracks"]) & tracks:
            continue
        grade, month = rule["grade"], rule["month"]
        base = {
            "id": rule["id"],
            "title": rule["title"],
            "action": rule["action"],
            "priority": rule["priority"],
            "tracks": rule["tracks"],
            "source_url": rule.get("source_url"),
            "verification": rule.get("verification"),
            "done": False,
        }
        dtype = rule["date_type"]
        drule = rule["date_rule"]

        if dtype == "fixed_annual":
            date = dt.date(milestone_year(grad_year, grade, drule["month"]), drule["month"], drule["day"])
            if include(date, grade, month):
                items.append({**base, "date": date.isoformat()})
        elif dtype == "window":
            s, e = drule["start"], drule["end"]
            start = dt.date(milestone_year(grad_year, grade, s["month"]), s["month"], s["day"])
            # The end is anchored to the start: same calendar year when the
            # end month/day isn't earlier (Jun->Aug), next year when the
            # window wraps (Dec->Feb). Resolving it independently through
            # milestone_year would flip Jul->Aug windows a year backwards.
            end_year = start.year + (1 if (e["month"], e["day"]) < (s["month"], s["day"]) else 0)
            end = dt.date(end_year, e["month"], e["day"])
            if end >= horizon_start:
                items.append({**base, "date": start.isoformat(), "window_end": end.isoformat()})
        elif dtype == "pattern":
            year = milestone_year(grad_year, grade, month)
            expanded = False
            if drule.get("dataset") == "test_dates.json":
                months = drule.get("months", [month])
                for kind in ("sat", "act"):
                    for d in test_dates_in(test_dates, kind, grad_year, grade, months):
                        expanded = True
                        items.append({**base,
                                      "id": f"{rule['id']}/{kind}-{d['test_date']}",
                                      "title": f"{kind.upper()} test date — {rule['title']}",
                                      "date": d["test_date"]})
                        reg = d.get("registration_deadline")
                        if reg and dt.date.fromisoformat(reg) >= horizon_start:
                            items.append({**base,
                                          "id": f"{rule['id']}/{kind}-{d['test_date']}/reg",
                                          "title": f"{kind.upper()} registration closes (test {d['test_date']})",
                                          "priority": "critical",
                                          "date": reg})
            if not expanded and include(None, grade, month):
                items.append({**base, "date": None, "approx": drule.get("description", "date varies"),
                              "approx_month": f"{year:04d}-{month:02d}"})
        elif dtype == "relative":
            year = milestone_year(grad_year, grade, month)
            if include(None, grade, month):
                items.append({**base, "date": None, "approx": drule.get("description", ""),
                              "approx_month": f"{year:04d}-{month:02d}"})
        elif dtype == "college_specific":
            pass  # generated from colleges.json below

    open_statuses = {"researching", "applying", "essays_in_progress", "ready_to_submit"}
    for c in colleges:
        if c.get("status") not in open_statuses:
            continue
        deadline = c.get("deadline")
        rec = c.get("recommended_submit_by")
        # The family should aim for the strategic date when set (rolling / wave /
        # priority review), not the backstop deadline.
        target = rec or deadline
        if not target:
            continue
        try:
            tdate = dt.date.fromisoformat(target)
        except ValueError:
            continue
        system = c.get("system", "common_app")
        strategic = bool(rec and rec != deadline)

        if tdate >= horizon_start:
            if strategic:
                why = c.get("timing_note") or (
                    "This college reviews on a rolling/priority basis — submitting early means better "
                    "odds and earlier scholarship/housing consideration; competitive majors fill along the way."
                )
                back = f" The final deadline ({deadline}) is the backstop, not the goal." if deadline else ""
                items.append({
                    "id": f"college/{c['name']}/recommended-submit",
                    "title": f"{c['name']} — submit by (strategic, earlier than the deadline)",
                    "action": f"{why}{back} Verify the timing on the college's admissions page.",
                    "priority": "critical",
                    "tracks": [system],
                    "source_url": c.get("portal_url"),
                    "date": rec,
                    "done": False,
                })
            else:
                verified = "" if c.get("deadline_verified") else " (unverified — check the college's page)"
                items.append({
                    "id": f"college/{c['name']}/{c.get('plan') or 'deadline'}",
                    "title": f"{c['name']} {c.get('plan') or ''} application deadline{verified}".strip(),
                    "action": "Submit the complete application, then confirm receipt in the college portal.",
                    "priority": "critical",
                    "tracks": [system],
                    "source_url": c.get("portal_url"),
                    "date": deadline,
                    "done": False,
                })

        # When a strategic date is set, still keep the hard deadline on the
        # calendar as a lower-priority backstop.
        if strategic and deadline:
            try:
                ddate = dt.date.fromisoformat(deadline)
            except ValueError:
                ddate = None
            if ddate and ddate >= horizon_start:
                items.append({
                    "id": f"college/{c['name']}/deadline-backstop",
                    "title": f"{c['name']} final application deadline (backstop)",
                    "action": "Last possible submission — but aim for the earlier recommended date above.",
                    "priority": "normal",
                    "tracks": [system],
                    "source_url": c.get("portal_url"),
                    "date": deadline,
                    "done": False,
                })

        # Priority scholarship/honors/housing date, if it's a separate earlier date.
        pdate = c.get("priority_date")
        if pdate and pdate not in (deadline, rec):
            try:
                pd = dt.date.fromisoformat(pdate)
            except ValueError:
                pd = None
            if pd and pd >= horizon_start:
                items.append({
                    "id": f"college/{c['name']}/priority",
                    "title": f"{c['name']} priority date (scholarship / honors / housing)",
                    "action": "Submit by this earlier date to be considered for merit aid, honors, or housing priority. Verify on the college's page.",
                    "priority": "high",
                    "tracks": [system],
                    "source_url": c.get("portal_url"),
                    "date": pdate,
                    "done": False,
                })

    items.sort(key=lambda i: (i.get("date") or i.get("approx_month", "9999") + "-28", i["id"]))
    return items, current_grade, tracks


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", default=None)
    ap.add_argument("--today", default=None, help="override for tests, YYYY-MM-DD")
    args = ap.parse_args(argv)

    ws = Path(args.workspace) if args.workspace else find_workspace()
    if ws is None or not (ws / ".admissions" / "config.json").is_file():
        print(json.dumps({"error": {"code": "no_workspace",
                                    "message": f"{ws or 'cwd'} is not an admit workspace — run /admit:start first"}}))
        return 1
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()

    try:
        profile = read_json(ws / "profile.json")
        cfg = read_json(ws / ".admissions" / "config.json")
        colleges_doc = read_json(ws / "colleges.json") if (ws / "colleges.json").is_file() else {"colleges": []}
    except FileNotFoundError as e:
        print(json.dumps({"error": {"code": "missing_file", "message": str(e)}}))
        return 1
    except json.JSONDecodeError as e:
        print(json.dumps({"error": {"code": "corrupt_file",
                                    "message": f"a workspace file is not valid JSON ({e}); "
                                               f"restore it from .admissions/backups/"}}))
        return 1
    if not profile.get("student", {}).get("grad_year"):
        print(json.dumps({"error": {"code": "no_grad_year", "message": "set student.grad_year in profile.json first"}}))
        return 1
    rules = load_dataset("milestones.json")
    test_dates = load_dataset("test_dates.json")

    items, grade, tracks = build_items(profile, cfg, colleges_doc["colleges"], rules, test_dates, today)

    out_path = ws / ".admissions" / "milestones.json"
    previous_done = set()
    if out_path.is_file():
        try:
            previous_done = {m["id"] for m in read_json(out_path).get("milestones", []) if m.get("done")}
        except (json.JSONDecodeError, KeyError):
            pass
    for item in items:
        if item["id"] in previous_done:
            item["done"] = True

    doc = {
        "generated_at": today.isoformat(),
        "grade": grade,
        "cycle": cfg.get("cycle"),
        "tracks": sorted(tracks),
        "milestones": items,
    }
    write_json(ws, out_path, doc)

    print(json.dumps({
        "ok": True, "grade": grade, "tracks": sorted(tracks),
        "milestones": len(items),
        "dated": sum(1 for i in items if i.get("date")),
        "next_5": [{"date": i.get("date") or i.get("approx_month"), "title": i["title"]}
                   for i in items if not i["done"]][:5],
        "out": str(out_path),
    }, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
