"""ics_generate: RFC 5545 shape, stable UIDs, alarms, golden comparison."""

from __future__ import annotations

import json
from pathlib import Path

import ics_generate

GOLDEN = Path(__file__).parent / "fixtures" / "golden" / "admit-calendar.ics"

SAMPLE = {
    "generated_at": "2026-09-01",
    "grade": 12,
    "cycle": "2026-27",
    "milestones": [
        {"id": "fafsa-open", "title": "FAFSA opens", "date": "2026-10-01",
         "action": "File within the first weeks; state priority deadlines can be early.",
         "priority": "critical", "source_url": "https://studentaid.gov/apply-for-aid/fafsa/fafsa-deadlines",
         "done": False},
        {"id": "college/University of Michigan/EA", "title": "University of Michigan EA application deadline",
         "date": "2026-11-01", "action": "Submit, then confirm receipt in the portal.",
         "priority": "critical", "done": False},
        {"id": "done-item", "title": "Already handled", "date": "2026-10-05", "done": True},
        {"id": "undated", "title": "No date yet", "date": None, "approx": "typically late Feb", "done": False},
    ],
}


def render(workspace) -> bytes:
    (workspace / ".admissions" / "milestones.json").write_text(json.dumps(SAMPLE), encoding="utf-8")
    out = workspace / "output" / "cal.ics"
    rc = ics_generate.main(["--workspace", str(workspace), "--out", str(out)])
    assert rc == 0
    return out.read_bytes()


def test_matches_golden(workspace):
    raw = render(workspace)
    assert raw == GOLDEN.read_bytes(), (
        "ICS output changed — if intentional, regenerate the golden file "
        "(see tests/fixtures/golden/README)"
    )


def test_structure(workspace):
    text = render(workspace).decode("utf-8")
    assert text.startswith("BEGIN:VCALENDAR\r\n")
    assert text.count("BEGIN:VEVENT") == 2  # done + undated items excluded
    assert text.count("BEGIN:VALARM") == 4  # two alarms per event
    assert "UID:fafsa-open-" in text and "@admission-skills" in text
    assert "DTSTART;VALUE=DATE:20261001" in text
    assert "TRIGGER:-P7D" in text and "TRIGGER:-P1D" in text
    for line in text.split("\r\n"):
        assert len(line.encode("utf-8")) <= 75, f"unfolded line: {line!r}"


def test_deterministic(workspace):
    assert render(workspace) == render(workspace)


def test_unicode_ids_get_distinct_uids(workspace):
    """slug() alone collapses non-Latin college names to one UID and calendar
    apps then merge the events — the hash suffix must keep them distinct."""
    doc = {
        "generated_at": "2026-09-01",
        "milestones": [
            {"id": "college/漢陽大學/RD", "title": "Hanyang RD", "date": "2027-01-05", "done": False},
            {"id": "college/성균관대/RD", "title": "SKKU RD", "date": "2027-01-15", "done": False},
        ],
    }
    (workspace / ".admissions" / "milestones.json").write_text(
        json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    out = workspace / "output" / "u.ics"
    assert ics_generate.main(["--workspace", str(workspace), "--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    uids = [line for line in text.splitlines() if line.startswith("UID:")]
    assert len(uids) == 2 and len(set(uids)) == 2, uids
