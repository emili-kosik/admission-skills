"""scholarship_search: needs_key degradation and normalization."""

from __future__ import annotations

import json

import pytest
import scholarship_search


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for var in ("CLAUDE_PLUGIN_OPTION_CAREERONESTOP_USER_ID", "CAREERONESTOP_USER_ID",
                "CLAUDE_PLUGIN_OPTION_CAREERONESTOP_TOKEN", "CAREERONESTOP_TOKEN"):
        monkeypatch.delenv(var, raising=False)


def test_needs_key_without_credentials(tmp_path, capsys):
    rc = scholarship_search.main(["--keyword", "robotics", "--workspace", str(tmp_path)])
    assert rc == 1
    err = json.loads(capsys.readouterr().out)["error"]
    assert err["code"] == "needs_key"
    assert "careeronestop.org/Developers" in err["message"]


def test_normalize_shapes():
    row = scholarship_search.normalize({
        "Title": "Robotics Scholars Award",
        "Organization": "Example Foundation",
        "Purpose": "Supports high school seniors pursuing robotics.",
        "AwardType": "Scholarship",
        "Awards": "$5,000",
        "DeadlineDate": "2027-02-01",
        "LevelOfStudy": "High School Senior",
        "Website": "https://example.org/apply",
    })
    assert row["name"] == "Robotics Scholars Award"
    assert row["deadline"] == "2027-02-01"
    assert row["url"].startswith("https://")
