"""scorecard_search: query building, key resolution, response normalization."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest
import scorecard_search
from lib import config

FIXTURE = Path(__file__).parent / "fixtures" / "http" / "scorecard_stanford.json"


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for var in ("CLAUDE_PLUGIN_OPTION_SCORECARD_API_KEY", "SCORECARD_API_KEY"):
        monkeypatch.delenv(var, raising=False)


def parse_args(argv: list[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name")
    ap.add_argument("--id", type=int)
    ap.add_argument("--state")
    ap.add_argument("--admit-rate")
    ap.add_argument("--size")
    ap.add_argument("--sat-math-75")
    ap.add_argument("--sort")
    ap.add_argument("--per-page", type=int, default=50)
    ap.add_argument("--page", type=int, default=0)
    ap.add_argument("--fields", default="core")
    return ap.parse_args(argv)


def test_demo_key_fallback():
    assert config.get_scorecard_key(None) == "DEMO_KEY"


def test_key_resolution_order(monkeypatch):
    monkeypatch.setenv("SCORECARD_API_KEY", "env-key")
    assert config.get_scorecard_key(None) == "env-key"
    monkeypatch.setenv("CLAUDE_PLUGIN_OPTION_SCORECARD_API_KEY", "userconfig-key")
    assert config.get_scorecard_key(None) == "userconfig-key"


def test_build_params_ranges_and_sort():
    args = parse_args(["--state", "ma,ct", "--admit-rate", "0.3..0.6",
                       "--size", "2000..15000", "--sort", "admission_rate"])
    p = scorecard_search.build_params(args, "KEY")
    assert p["school.state"] == "MA,CT"
    assert p["latest.admissions.admission_rate.overall__range"] == "0.3..0.6"
    assert p["latest.student.size__range"] == "2000..15000"
    assert p["sort"] == "latest.admissions.admission_rate.overall"
    assert p["school.degrees_awarded.predominant"] == "3"  # 4-year default for list queries


def test_build_params_name_lookup_skips_degree_filter():
    args = parse_args(["--name", "Stanford"])
    p = scorecard_search.build_params(args, "KEY")
    assert p["school.name"] == "Stanford"
    assert "school.degrees_awarded.predominant" not in p


def test_normalize_fixture():
    doc = json.loads(FIXTURE.read_text(encoding="utf-8"))
    row = scorecard_search.normalize(doc["results"][0])
    assert row["unitid"] == 243744
    assert row["name"] == "Stanford University"
    assert row["ownership"] == "private_nonprofit"
    assert 0 < row["admit_rate"] < 0.1
    assert row["sat"]["math_75"] == 800
    assert row["net_price_calculator"]
    assert row["median_earnings_10yr"] > 50000
