# Contributing

Thanks for helping families navigate US admissions. Ground rules first, then
mechanics.

## Non-negotiables

1. **Primary sources or nothing.** Every date, fee, or policy in a skill or
   dataset traces to a bundled dataset (with `_meta.last_verified`) or a named
   primary-source URL (`data/sources.json`). "I'm pretty sure" is not a source.
2. **The essay-integrity floor is not up for debate.** The plugin never
   generates, outlines, rewrites, or "humanizes" application essay text —
   see `skills/essay-coach/SKILL.md` (rules E1–E10) and the PreToolUse guard.
   PRs that weaken this are closed.
3. **Dataset changes come from build tools**, not hand edits
   (`tools/build_*.py` against primary sources). See SECURITY.md.
4. **Privacy defaults hold**: nothing personal outside the workspace, no new
   telemetry, no default cloud writes.

## Dev setup

```
python -m venv .venv
.venv/Scripts/pip install -e ".[dev]"     # pytest, ruff, jsonschema, pyyaml, pdfplumber
pytest        # offline — network use fails the suite by design
ruff check .
claude --plugin-dir .   # live-test the plugin in Claude Code
```

## Authoring skills and agents

`docs/AUTHORING.md` is the binding contract (frontmatter fields, ≤200-line
SKILL.md bodies, references/ pattern, cross-skill delegation + persistence
contract sections, the verify-every-deadline discipline). CI enforces the
mechanical parts via `tests/test_frontmatter.py`.

## Runtime constraints

- User-facing Python under `scripts/` is **stdlib-only** (dev deps are for
  `tools/` and `tests/` only).
- Hooks under `scripts/hooks/` are **Node stdlib-only**, exec-form, and must
  exit 0 on any internal error (except deliberate validation exit 2s), in
  well under their timeout.
- Everything must work on Windows, macOS, and Linux — CI runs all three.
  Invoke Python only through `scripts/run.mjs`.

## PR checklist

- [ ] `pytest` and `ruff check .` green locally
- [ ] New/changed facts cite a primary source
- [ ] New skill/agent follows `docs/AUTHORING.md` (tests will tell you)
- [ ] CHANGELOG.md entry under an Unreleased heading
- [ ] No personal data in fixtures or examples
