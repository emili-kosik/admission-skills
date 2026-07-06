"""Frontmatter contracts for every skill and agent."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

KNOWN_SKILL_FIELDS = {
    "name", "description", "argument-hint", "user-invocable",
    "disable-model-invocation", "allowed-tools", "disallowed-tools",
    "context", "agent", "model", "license", "metadata",
}
KNOWN_AGENT_FIELDS = {"name", "description", "tools", "model", "maxTurns"}
MAX_DESCRIPTION_CHARS = 1536


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, f"{path} has no frontmatter"
    return yaml.safe_load(m.group(1))


def skill_files(repo_root: Path) -> list[Path]:
    return sorted((repo_root / "skills").glob("*/SKILL.md"))


def agent_files(repo_root: Path) -> list[Path]:
    agents = repo_root / "agents"
    return sorted(agents.glob("*.md")) if agents.is_dir() else []


def test_skills_exist(repo_root: Path):
    assert len(skill_files(repo_root)) >= 3


def test_skill_frontmatter(repo_root: Path):
    for f in skill_files(repo_root):
        fm = frontmatter(f)
        assert fm.get("name") == f.parent.name, f"{f}: name must match folder"
        desc = fm.get("description", "")
        assert desc and len(desc) <= MAX_DESCRIPTION_CHARS, f"{f}: bad description length"
        assert "Use when" in desc or "use when" in desc, f"{f}: description needs trigger phrases"
        unknown = set(fm) - KNOWN_SKILL_FIELDS
        assert not unknown, f"{f}: unknown frontmatter fields {unknown}"


def test_skill_referenced_files_exist(repo_root: Path):
    """Every references/<file>.md mentioned in a SKILL.md body must exist."""
    missing = []
    for f in skill_files(repo_root):
        body = f.read_text(encoding="utf-8")
        for ref in re.findall(r"references/[\w./-]+\.md", body):
            if not (f.parent / ref).is_file():
                missing.append(f"{f.parent.name}: {ref}")
    assert not missing, f"skills reference missing files: {missing}"


def test_refresh_data_is_user_only(repo_root: Path):
    f = repo_root / "skills" / "refresh-data" / "SKILL.md"
    if not f.is_file():
        return  # authored in a later phase; enforced once present
    fm = frontmatter(f)
    assert fm.get("disable-model-invocation") is True


def test_agent_frontmatter(repo_root: Path):
    for f in agent_files(repo_root):
        fm = frontmatter(f)
        assert fm.get("name") == f.stem
        assert fm.get("description")
        unknown = set(fm) - KNOWN_AGENT_FIELDS
        assert not unknown, f"{f}: unknown frontmatter fields {unknown}"
        if "maxTurns" in fm:
            assert isinstance(fm["maxTurns"], int) and 5 <= fm["maxTurns"] <= 60


def test_essay_reviewer_cannot_write(repo_root: Path):
    f = repo_root / "agents" / "essay-reviewer.md"
    if not f.is_file():
        return  # authored in phase 5; enforced once present
    tools = frontmatter(f).get("tools", "")
    for forbidden in ("Write", "Edit", "Bash"):
        assert forbidden not in tools, "essay-reviewer must be read-only by construction"
