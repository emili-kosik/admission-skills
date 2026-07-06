"""Bundled dataset integrity: structure + anchor facts from primary sources."""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

import pytest

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load(repo_root: Path, name: str) -> dict:
    return json.loads((repo_root / "data" / name).read_text(encoding="utf-8"))


def test_every_dataset_has_meta(repo_root: Path):
    for f in sorted((repo_root / "data").glob("*.json")):
        doc = json.loads(f.read_text(encoding="utf-8"))
        assert "_meta" in doc, f"{f.name} missing _meta"
        meta = doc["_meta"]
        assert meta.get("last_verified") or meta.get("built_at"), f"{f.name} _meta lacks last_verified"


# --- deadlines.json ---------------------------------------------------------

def test_deadlines_shape_and_volume(repo_root: Path):
    d = load(repo_root, "deadlines.json")
    assert 1000 <= len(d["colleges"]) <= 1400
    assert d["_meta"]["date_parse_rate"] >= 0.98
    assert re.fullmatch(r"\d{4}-\d{2}", d["_meta"]["cycle"])


def test_deadlines_anchor_schools(repo_root: Path):
    d = load(repo_root, "deadlines.json")
    by = {c["name"]: c for c in d["colleges"]}
    stanford = by["Stanford University"]
    assert stanford["test_policy"] == "required"
    rea = stanford["deadlines"]["REA"]
    assert DATE.match(rea) and rea.endswith("-11-01"), "Stanford REA should be Nov 1"
    uc = by["University of California (all campuses)"]
    assert uc["system"] == "uc"
    assert uc["annual_rules"] == {"filing_open": "10-01", "filing_close": "11-30"}
    assert uc["test_policy"] == "free"
    mit = by["Massachusetts Institute of Technology"]
    assert mit["system"] == "institutional" and mit["test_policy"] == "required"


def test_deadlines_rolling_autodetected(repo_root: Path):
    """Rolling review is auto-flagged from the ReqGrid, not hand-listed per
    school. Every flagged entry must actually show rolling in its data."""
    d = load(repo_root, "deadlines.json")
    rolling = [c for c in d["colleges"] if c.get("admission_type") == "rolling"]
    assert len(rolling) > 100
    for c in rolling:
        assert c.get("deadlines", {}).get("RD") == "rolling", c["name"]
    for c in d["colleges"]:
        assert c.get("admission_type") in (None, "rolling", "priority", "rounds", "wave", "unknown")


def test_deadlines_dates_parse(repo_root: Path):
    d = load(repo_root, "deadlines.json")
    for c in d["colleges"]:
        for round_name, v in c.get("deadlines", {}).items():
            if isinstance(v, str) and v != "rolling":
                assert DATE.match(v), f"{c['name']} {round_name}: bad date {v!r}"


# --- milestones.json --------------------------------------------------------

VALID_DATE_TYPES = {"fixed_annual", "pattern", "window", "college_specific", "relative"}
VALID_TRACKS = {"all", "common_app", "uc", "csu", "international", "test_taker", "ap_student", "aid_seeker"}


def test_milestones_rows_valid(repo_root: Path):
    m = load(repo_root, "milestones.json")
    ids = set()
    for row in m["milestones"]:
        assert row["id"] not in ids, f"duplicate id {row['id']}"
        ids.add(row["id"])
        assert row["date_type"] in VALID_DATE_TYPES, row["id"]
        assert row["grade"] in (9, 10, 11, 12), row["id"]
        assert set(row["tracks"]) <= VALID_TRACKS, row["id"]
        assert row["tracks"], row["id"]
        assert row.get("action"), row["id"]
        assert row.get("priority") in ("normal", "high", "critical"), row["id"]


def test_milestones_anchor_facts(repo_root: Path):
    m = load(repo_root, "milestones.json")
    by = {r["id"]: r for r in m["milestones"]}
    assert by["fafsa-open"]["date_rule"] == {"month": 10, "day": 1}
    assert by["fafsa-open"]["date_type"] == "fixed_annual"
    assert by["uc-filing-deadline"]["date_rule"] == {"month": 11, "day": 30}
    assert by["decision-day"]["date_rule"] == {"month": 5, "day": 1}
    assert by["ca-open"]["date_rule"] == {"month": 8, "day": 1}
    assert "international" in by["int-i20-chain"]["tracks"]


# --- test_policy.json -------------------------------------------------------

def test_test_policy_anchors(repo_root: Path):
    d = load(repo_root, "test_policy.json")
    assert len(d["policies"]) >= 1000
    by = {p["name"]: p for p in d["policies"]}
    assert by["University of California"]["policy"] == "free"
    assert by["California State University"]["policy"] == "free"
    assert by["Harvard University"]["policy"] == "required"
    assert by["Massachusetts Institute of Technology"]["policy"] == "required"
    for p in d["policies"]:
        assert p["policy"] in ("required", "optional", "flexible", "free"), p["name"]


# --- essay_prompts.json -----------------------------------------------------

def test_essay_prompts(repo_root: Path):
    d = load(repo_root, "essay_prompts.json")
    ca = d["common_app"]
    assert len(ca["prompts"]) == 7
    assert ca["word_limit_min"] == 250 and ca["word_limit_max"] == 650
    assert ca["verified"] is True
    piq = d["uc_piq"]
    assert len(piq["prompts"]) == 8
    assert "350" in piq["instructions"]
    assert piq["verified"] is True
    for p in ca["prompts"] + piq["prompts"]:
        assert len(p["text"]) > 40, f"prompt {p['id']} suspiciously short"


# --- ai_policies.json -------------------------------------------------------

def test_ai_policies(repo_root: Path):
    d = load(repo_root, "ai_policies.json")
    assert len(d["policies"]) >= 5
    by = {p["institution"]: p for p in d["policies"]}
    fraud = by["Common App"]
    assert fraud["tier"] == "fraud-baseline"
    assert "artificial intelligence" in fraud["quote"].lower()
    assert by["Brown University"]["tier"] == "prohibitive"
    assert d["_meta"]["default_tier"] == "prohibitive"
    for p in d["policies"]:
        assert p.get("quote") and p.get("source_url"), p["institution"]


# --- test_dates.json --------------------------------------------------------

def test_test_dates(repo_root: Path):
    d = load(repo_root, "test_dates.json")
    assert len(d["sat"]["dates"]) >= 6
    assert len(d["act"]["dates"]) >= 5
    for block in (d["sat"], d["act"]):
        for row in block["dates"]:
            assert DATE.match(row["test_date"]), row
            if row.get("registration_deadline"):
                assert row["registration_deadline"] < row["test_date"], row
    rules = d["lead_time_rules"]
    assert rules["sat_registration_days_before"] >= 10
    assert rules["act_registration_weeks_before"] >= 3


# --- systems.json / college_index.json / sources.json -----------------------

def test_systems(repo_root: Path):
    d = load(repo_root, "systems.json")
    assert set(d["systems"]) == {"common_app", "uc", "csu", "applytexas", "coalition_scoir", "institutional"}


def test_college_index(repo_root: Path):
    d = load(repo_root, "college_index.json")
    assert len(d["colleges"]) >= 2000
    unitids = [c["unitid"] for c in d["colleges"]]
    assert len(set(unitids)) == len(unitids), "unitids must be unique"
    names = {c["name"] for c in d["colleges"]}
    assert "Stanford University" in names and "Harvard University" in names


def test_sources_urls(repo_root: Path):
    d = load(repo_root, "sources.json")

    def walk(node):
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, str) and node.startswith("http"):
            assert node.startswith("https://"), f"non-https source: {node}"

    walk(d["sources"])


# --- cross-dataset consistency ----------------------------------------------

def test_cycles_are_coherent(repo_root: Path):
    """All hand-authored datasets target the same cycle; the ReqGrid-derived
    deadlines file may lag one cycle behind (refreshed each Aug 1)."""
    cycles = {}
    for name in ["milestones.json", "systems.json", "essay_prompts.json", "test_dates.json"]:
        cycles[name] = load(repo_root, name)["_meta"]["cycle"]
    assert len(set(cycles.values())) == 1, f"cycle drift: {cycles}"
    deadlines_cycle = load(repo_root, "deadlines.json")["_meta"]["cycle"]
    hand_cycle = next(iter(cycles.values()))
    years = int(hand_cycle[:4]) - int(deadlines_cycle[:4])
    assert years in (0, 1), f"deadlines cycle {deadlines_cycle} too far behind {hand_cycle}"


@pytest.mark.parametrize("name", [
    "deadlines.json", "test_policy.json", "test_dates.json", "milestones.json",
    "essay_prompts.json", "ai_policies.json", "systems.json", "college_index.json", "sources.json",
])
def test_dataset_freshness_documented(repo_root: Path, name: str):
    meta = load(repo_root, name)["_meta"]
    stamp = meta.get("last_verified") or meta.get("built_at")
    parsed = dt.date.fromisoformat(stamp)
    assert parsed <= dt.date.today()
