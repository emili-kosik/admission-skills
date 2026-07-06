# Authoring guide — skills and agents in the admit plugin

This is the style contract every skill and agent in this repo follows. CI
enforces the mechanical parts (`tests/test_frontmatter.py`).

## Voice and audience

- Written to the **operator**: a parent, or a student who is 18+. Calm,
  concrete, anti-panic. No hype, no fear, no condescension.
- Supports **domestic and international** applicants; international-specific
  guidance is labeled, not assumed.
- Facts come from **bundled datasets or named primary sources**, never from
  memory. Every deadline shown to a user carries a "verify on the college's
  official page" caveat.
- Chancing honesty: reach/match/safety bands, never fake-precise percentages.
  Admit rate under 15% is a reach for everyone.

## Skill files (`skills/<name>/SKILL.md`)

Frontmatter (only these fields are allowed):

```yaml
---
name: <must equal the folder name>
description: >
  <What it does + "Use when the user says ..." trigger phrases. Max 1536 chars.>
argument-hint: "[...]"            # optional
disable-model-invocation: true    # only for side-effectful user-only skills
user-invocable: false             # only for shared knowledge skills
---
```

Body conventions:

- ≤ 200 lines. Depth goes to `references/*.md`, loaded on demand and
  referenced explicitly ("Read `references/x.md` when ...").
  Every referenced file must exist (CI checks).
- Steps in imperative voice addressed to Claude ("Read colleges.json, then...").
- End with two sections: **Cross-skill delegation** (name other skills by
  their kebab-case names) and **Persistence contract** (exactly which
  workspace files the skill may read/write; read-modify-write whole JSON
  files; never write `essays/drafts/**`).
- **Output style (quiet writes):** update workspace files quietly — a single
  whole-file write, and **never paste JSON, code, raw file contents, or diffs
  into replies**. Confirm changes in one short, plain-language sentence.
  Rendering a human-readable table/summary for the user is fine; the editor's
  change card is the app's own UI — don't narrate it. Any skill that writes to
  the workspace states this near the top as an `## Output style` section.

## Agent files (`agents/<name>.md`)

Frontmatter fields: `name` (= filename stem), `description`, `tools`
(comma-separated whitelist — smallest set that works), `model` (default
`sonnet`; `haiku` for cheap high-volume work), `maxTurns` (5-60).
`essay-reviewer` must never have Write, Edit, or Bash.

Body: persona sentence → ordered steps → tables where useful → **Output
format** (structured, machine-mergeable — the calling skill writes workspace
files, agents return data) → cross-references.

## The plugin API surface (what skills can rely on)

### Scripts — always invoked through the shim

```
node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs <script> [args]
```

| Script | Purpose | Key args |
|---|---|---|
| `init_workspace` | scaffold a workspace | `--dir`, `--grad-year`, `--force` |
| `scorecard_search` | live College Scorecard data | `--name`, `--state MA,CT`, `--admit-rate 0.3..0.6`, `--size`, `--sat-math-75`, `--sort admission_rate[:desc]`, `--id`, `--per-page` |
| `urban_lookup` | IPEDS applicants/admits/requirements (no key) | `--unitid`, `--endpoint admissions-enrollment\|admissions-requirements\|directory` |
| `timeline_build` | recompute `.admissions/milestones.json` | `--workspace` |
| `ics_generate` | timeline → `output/admit-calendar.ics` | `--workspace`, `--out` |
| `scholarship_search` | CareerOneStop scholarships | `--keyword`, `--state`, `--level`, `--max` |
| `refresh_data` | refresh bundled datasets from GitHub | `--branch` |

All scripts print a single JSON document; errors are
`{"error": {"code": ..., "message": ...}}` with exit ≠ 0. `needs_key` and
DEMO_KEY-429 errors include actionable signup guidance — relay it.

### Bundled datasets (`data/*.json`, each with `_meta.last_verified`)

| File | Contents |
|---|---|
| `deadlines.json` | ~1,150 colleges: ED/ED2/EA/EA2/REA/RD dates, fees, essay/writing flags, test-policy code, rec counts; UC/CSU/MIT/Georgetown/ApplyTexas overrides with `annual_rules` (MM-DD anchors) |
| `test_policy.json` | required/optional/flexible/free per college (+ verified overrides) |
| `test_dates.json` | current-cycle SAT/ACT dates + registration deadlines; PSAT/AP windows; lead-time rules |
| `milestones.json` | the timeline rule table (do not read directly — use `timeline_build`) |
| `essay_prompts.json` | 7 Common App prompts + 8 UC PIQs, verbatim, with word limits |
| `ai_policies.json` | per-college AI-use policies: tier, verbatim quote, citation URL |
| `systems.json` | application-system metadata (portals, rounds, essay/rec models) |
| `college_index.json` | name/state/unitid index of 2,796 four-year institutions |
| `sources.json` | primary-source URL registry — cite these, don't paste from memory |

Staleness rule: if `_meta.cycle` is behind the workspace cycle or
`last_verified` is >12 months old (6 for test policies), say so, phrase facts
as "as of <date>", and suggest `/admit:refresh-data`.

### Workspace files

`profile.json` (student, academics, testing, interests, finances, narrative —
PII-minimized), `colleges.json` (the tracker; statuses researching→…→enrolled),
`essays/index.json`, `essays/drafts|brainstorm|feedback/`, `aid/`,
`.admissions/config.json` (cycle, systems, engagement state),
`.admissions/milestones.json` (computed timeline), `output/`.

A PostToolUse hook checks every write to the structured files and, if a value
looks off, **quietly nudges you** (via additionalContext) to fix it on the next
turn — it never blocks the write or shows the user an error. A PreToolUse hook
**blocks all writes to `essays/drafts/**`** — that is by design; never try to
work around it.

### Existing skills (for cross-skill delegation)

start, guide, tracker, roadmap, college-list, college-research, essay-coach,
testing-plan, financial-aid, scholarships, international, interview-prep,
activities, visits, decision-day, parent-guide, checkin, sync,
data-sources, refresh-data.

### Ethics floor (applies to every skill that touches essays)

Per the Common App fraud policy (`data/ai_policies.json`), submitting AI-
generated essay content is application fraud. The plugin brainstorms from the
student's real experiences, critiques the student's own drafts, and flags
mechanical errors — it never generates, outlines, rewrites, or "humanizes"
essay text, for any school, at any parent's request. `essay-coach` owns the
full ruleset; other skills route essay work there.
