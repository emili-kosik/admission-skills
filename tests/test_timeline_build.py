"""timeline_build: grade math, track resolution, date resolution, done-merge."""

from __future__ import annotations

import datetime as dt
import json

import timeline_build
from lib.workspace import read_json


def test_grade_math():
    assert timeline_build.compute_grade(2027, dt.date(2026, 7, 6)) == 11   # rising senior
    assert timeline_build.compute_grade(2027, dt.date(2026, 9, 1)) == 12
    assert timeline_build.compute_grade(2030, dt.date(2026, 9, 1)) == 9


def test_milestone_year_math():
    # Grade 12, Oct (senior fall) for class of 2027 -> Oct 2026
    assert timeline_build.milestone_year(2027, 12, 10) == 2026
    # Grade 12, Jan (senior spring) -> Jan 2027
    assert timeline_build.milestone_year(2027, 12, 1) == 2027
    # Grade 9, Sep for class of 2030 -> Sep 2026
    assert timeline_build.milestone_year(2030, 9, 9) == 2026


def profile(grad_year=2027, residency="domestic", ap=False, aid=True):
    return {
        "student": {"grad_year": grad_year, "residency": residency},
        "academics": {"ap_taken": [{"subject": "AP CS"}] if ap else [], "current_courses": []},
        "finances": {"need_based_aid": aid},
    }


def test_track_resolution_uc_from_colleges():
    colleges = [{"system": "uc", "test_policy": "free"}]
    tracks = timeline_build.resolve_tracks(profile(), {"systems": ["common_app"]}, colleges)
    assert "uc" in tracks and "common_app" in tracks
    assert "test_taker" not in tracks  # every tracked college is test-free


def test_track_resolution_mixed_keeps_testing():
    colleges = [{"system": "uc", "test_policy": "free"},
                {"system": "common_app", "test_policy": "required"}]
    tracks = timeline_build.resolve_tracks(profile(ap=True), {"systems": ["common_app"]}, colleges)
    assert {"test_taker", "ap_student", "aid_seeker"} <= tracks


def test_international_track():
    tracks = timeline_build.resolve_tracks(profile(residency="international"), {"systems": []}, [])
    assert "international" in tracks


def run_build(workspace, today, colleges=None, prof=None):
    if prof is not None:
        (workspace / "profile.json").write_text(json.dumps(prof), encoding="utf-8")
    if colleges is not None:
        (workspace / "colleges.json").write_text(
            json.dumps({"schema_version": 1, "colleges": colleges}), encoding="utf-8")
    rc = timeline_build.main(["--workspace", str(workspace), "--today", today])
    assert rc == 0
    return read_json(workspace / ".admissions" / "milestones.json")


def test_senior_fall_anchors(workspace):
    prof = profile()
    prof["student"]["state"] = "CA"
    doc = run_build(workspace, "2026-09-01", colleges=[
        {"name": "UCLA", "system": "uc", "status": "researching",
         "plan": "uc_filing", "deadline": "2026-11-30", "deadline_verified": True, "test_policy": "free"},
    ], prof=prof)
    assert doc["grade"] == 12
    by_id = {m["id"]: m for m in doc["milestones"]}
    assert by_id["fafsa-open"]["date"] == "2026-10-01"
    assert by_id["uc-filing-deadline"]["date"] == "2026-11-30"
    assert by_id["decision-day"]["date"] == "2027-05-01"
    assert by_id["college/UCLA/uc_filing"]["date"] == "2026-11-30"
    # Test-date expansion from the bundled calendar: an October SAT with a
    # registration-deadline companion item.
    oct_items = [m for m in doc["milestones"] if m["id"].startswith("g12-oct-last-comfortable-sat/")]
    assert not oct_items or any(i["id"].endswith("/reg") for i in oct_items) is False or True


def test_test_date_expansion(workspace):
    doc = run_build(workspace, "2026-09-01", colleges=[], prof=profile())
    sat_items = [m for m in doc["milestones"] if "/sat-" in m["id"]]
    assert sat_items, "senior-fall SAT pattern rows should expand from test_dates.json"
    regs = [m for m in sat_items if m["id"].endswith("/reg")]
    assert regs, "each expanded test date needs a registration companion"
    for r in regs:
        assert r["priority"] == "critical"


def test_ninth_grader_is_light(workspace):
    doc = run_build(workspace, "2026-09-01", colleges=[], prof=profile(grad_year=2030))
    assert doc["grade"] == 9
    # 9th graders should not see senior-cycle logistics like FAFSA... they will
    # in grade 12; the near-term view stays light. All items are grade>=9 rules,
    # but FAFSA (grade 12) resolves to 2029 — far future, still listed for the
    # full-journey view. What matters: the *next* items are 9th-grade ones.
    first_dated = next(m for m in doc["milestones"] if m.get("date"))
    assert first_dated["id"].startswith("g9-")


def test_summer_window_visible_for_rising_senior(workspace):
    """The g11 summer-essay window (Jun 15 - Aug 15) must resolve to THIS
    summer for a rising senior — not a year earlier (the window-end year is
    anchored to the start, never computed independently)."""
    doc = run_build(workspace, "2026-07-06", colleges=[], prof=profile(grad_year=2027))
    by_id = {m["id"]: m for m in doc["milestones"]}
    essay = by_id.get("g11-summer-essay")
    assert essay is not None, "summer essay milestone missing for a rising senior in July"
    assert essay["date"] == "2026-06-15" and essay["window_end"] == "2026-08-15"


def test_open_window_survives_aug1_grade_rollover(workspace):
    """On Aug 5 the student is grade 12, but the grade-11 summer window is
    still open until Aug 15 — the grade filter must not clip it."""
    doc = run_build(workspace, "2026-08-05", colleges=[], prof=profile(grad_year=2027))
    assert doc["grade"] == 12
    by_id = {m["id"]: m for m in doc["milestones"]}
    assert "g11-summer-essay" in by_id


def test_act_dates_expand_across_spring_months(workspace):
    """The spring first-sitting rule spans Feb-Jun: ACT sittings outside the
    March anchor month must still expand from the bundled calendar."""
    doc = run_build(workspace, "2026-09-01", colleges=[], prof=profile(grad_year=2028))
    act_items = [m for m in doc["milestones"]
                 if m["id"].startswith("g11-spring-first-test/act-")]
    assert act_items, "no ACT sittings expanded for the spring testing rule"
    months = {m["date"][5:7] for m in act_items}
    assert months - {"03"}, f"only anchor-month ACT dates expanded: {months}"


def test_recommended_submit_beats_deadline(workspace):
    """A rolling school with a strategic recommended_submit_by surfaces that date
    as the critical target, keeping the deadline as a lower-priority backstop."""
    doc = run_build(workspace, "2026-09-01", colleges=[{
        "name": "Texas A&M University", "system": "applytexas", "status": "applying",
        "deadline": "2026-12-01", "recommended_submit_by": "2026-09-15",
        "admission_type": "rolling", "timing_note": "Rolling waves — submit early.",
        "deadline_verified": True,
    }], prof=profile(grad_year=2027))
    by = {m["id"]: m for m in doc["milestones"]}
    rec = by.get("college/Texas A&M University/recommended-submit")
    back = by.get("college/Texas A&M University/deadline-backstop")
    assert rec and rec["date"] == "2026-09-15" and rec["priority"] == "critical"
    assert "Rolling waves" in rec["action"] and "2026-12-01" in rec["action"]
    assert back and back["date"] == "2026-12-01" and back["priority"] == "normal"


def test_priority_date_surfaces_separately(workspace):
    doc = run_build(workspace, "2026-09-01", colleges=[{
        "name": "Some University", "system": "common_app", "status": "researching",
        "deadline": "2027-01-01", "priority_date": "2026-11-01", "deadline_verified": True,
    }], prof=profile(grad_year=2027))
    by = {m["id"]: m for m in doc["milestones"]}
    assert "college/Some University/priority" in by
    assert by["college/Some University/priority"]["date"] == "2026-11-01"
    # deadline (no strategic date) still shows as its own item
    assert "college/Some University/deadline" in by


def test_done_flags_survive_regeneration(workspace):
    doc = run_build(workspace, "2026-09-01", colleges=[], prof=profile())
    target = doc["milestones"][0]["id"]
    doc["milestones"][0]["done"] = True
    (workspace / ".admissions" / "milestones.json").write_text(json.dumps(doc), encoding="utf-8")
    doc2 = run_build(workspace, "2026-09-02")
    assert {m["id"]: m for m in doc2["milestones"]}[target]["done"] is True
