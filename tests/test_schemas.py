"""Workspace-schema documentation checks (dev-only jsonschema).

The runtime validator is the hand-rolled non-blocking hook; these tests keep
the documented JSON Schemas honest against the sample fixtures.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def test_all_schemas_are_valid_json(repo_root: Path):
    for f in sorted((repo_root / "data" / "schemas").glob("*.json")):
        schema = load(f)
        assert "$schema" in schema, f.name


def test_hs_timeline_schema_accepts_sample(repo_root: Path):
    schema = load(repo_root / "data" / "schemas" / "hs-timeline.schema.json")
    sample = load(repo_root / "tests" / "fixtures" / "workspace" / "hs_timeline.json")
    jsonschema.validate(sample, schema)


def test_hs_timeline_schema_rejects_bad_milestone_type(repo_root: Path):
    schema = load(repo_root / "data" / "schemas" / "hs-timeline.schema.json")
    sample = load(repo_root / "tests" / "fixtures" / "workspace" / "hs_timeline.json")
    sample["phases"][1]["milestones"][0]["type"] = "bogus"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(sample, schema)


def test_hs_timeline_schema_tolerates_extra_fields(repo_root: Path):
    """additionalProperties is permissive so the overview endpoint can grow."""
    schema = load(repo_root / "data" / "schemas" / "hs-timeline.schema.json")
    sample = load(repo_root / "tests" / "fixtures" / "workspace" / "hs_timeline.json")
    sample["future_field"] = {"anything": 1}
    sample["phases"][0]["milestones"][0]["new_key"] = "ok"
    jsonschema.validate(sample, schema)  # must not raise
