---
name: college-list
description: >
  Build or rebalance a balanced reach/match/safety college list from the student's
  profile, using live College Scorecard data, bundled test-policy and deadline data,
  and honest banding (sub-15% admit rate is a reach for everyone). Use when the user
  says "build a college list", "reach match safety", "rebalance the list", "is X a
  safety", "where should we apply", "find colleges that fit", "we need more safeties",
  or "is our list balanced".
argument-hint: "[build|rebalance|check <college>]"
---

# College list — reach/match/safety, built on live data

Classification follows `references/methodology.md` — read it before banding any
college. Never give fake-precise chances; speak in bands. If no workspace exists,
route to `start` first.

## Output style — quiet writes

Update workspace files quietly: gather what you need, then do a single whole-file
read-modify-write. **Never paste JSON, code blocks, raw file contents, or
field-by-field diffs into your reply** — the family should not have to read the file
format. Rendering a human-readable table or summary for them is fine; the rule is
about not exposing the raw file. Confirm what changed in one short, plain-language
sentence. (The editor's own change card may still appear — that is the app's UI,
don't narrate or add to it.)

## Step 1 — Read the profile

Read `profile.json` and `colleges.json`. You need, at minimum:

- `testing` (best SAT sections / ACT composite), `academics.gpa_unweighted`,
  `academics.rigor_arc`
- `interests` (majors, size, regions, setting, must_haves)
- `finances.budget_per_year_usd` and `finances.income_bracket`
- `student.residency` (domestic vs international) and `student.state`

If GPA or budget is missing, ask before searching — banding without stats is
guesswork, and a list built without a budget produces fake safeties.

## Step 2 — Search with live Scorecard data

Derive filters from preferences and run one pass per band so each band gets real
candidates (not leftovers):

```
node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs scorecard_search --state MA,CT --size 2000..15000 --admit-rate 0.5..1.0 --sort admission_rate:desc
node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs scorecard_search --state MA,CT --size 2000..15000 --admit-rate 0.3..0.6
node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs scorecard_search --name "<specific college>"
```

Each result carries `admit_rate`, SAT/ACT 25th/75th percentiles, `avg_net_price`,
`net_price_by_income`, `net_price_calculator`, `grad_rate`, and
`median_earnings_10yr`. If the script returns a `needs_key` or DEMO_KEY rate-limit
error, relay its signup guidance verbatim and continue with cached/bundled data.

## Step 3 — Cross-reference bundled data

For every candidate:

- `data/test_policy.json` → `required | optional | flexible | free`. If
  `_meta.last_verified` is over 6 months old, say so and phrase policies as
  "as of <date>" (policies flipped repeatedly 2024–2026).
- `data/deadlines.json` → plan dates (ED/EA/RD…), fees, writing supplement,
  rec counts, and `admission_type` (Common App rolling schools are auto-flagged
  from the ReqGrid). Every date gets the "verify on the college's official page"
  caveat.

## Step 4 — Classify

Apply `references/methodology.md` exactly. The non-negotiables, in brief:

- **STEP 0**: admit rate under 15% is a **reach for everyone — no exceptions ever**.
- **STEP 1**: score position vs 25th/75th percentiles (skipped at test-free
  colleges; at test-optional colleges with a below-midpoint score, advise
  withholding and band on GPA/rigor with a one-notch shift toward reach).
- **STEP 2**: base band from admit rate, then modifier shifts.
- **STEP 3**: `safety` is a certification, not a vibe — four tests, all must pass,
  otherwise cap at `match`.
- **STEP 4**: every school gets a financial-fit annotation
  (affordable / stretch / requires-aid-outcome) plus its own Net Price Calculator
  link from the scorecard `net_price_calculator` field.

## Step 5 — Discuss before writing anything

Present the candidates as a table:

```
| College | Admit rate | Score position | Band | Financial fit | Test policy | Deadline (unverified) |
```

Then check list balance against these rules:

| Rule | Target |
|---|---|
| Total size | 8–12 colleges |
| Certified safeties — **choose these first** | 2–3 |
| Matches | 3–4 |
| Reaches | 2–3 |
| Lottery picks (sub-15% admit, labeled as such) | max 2 |
| Financial safety (certified safety that is also `affordable`) | at least 1 |

Ask the would-attend question **out loud for every school**: "If this were the
only acceptance in April, would <student> enroll happily?" Anything that gets a
"no" comes off the list — safeties especially. Build safeties first; a list is
only as strong as the schools at the bottom of it.

For finalists the family will act on, offer to spawn the `college-scout` agent
(one college per run) to live-verify deadlines and CDS facts on primary sources
before the list is written; prefer its verified dates over bundled ones.

## Step 6 — On confirmation, write the list

Only after the user confirms. Read `colleges.json`, modify, write the whole file
back. New entries look like:

```json
{
  "name": "Example College", "unitid": 123456, "system": "common_app",
  "status": "researching", "category": "match",
  "plan": null, "deadline": "2026-01-05", "deadline_verified": false,
  "admission_type": "rolling", "recommended_submit_by": "2026-09-15",
  "timing_note": "Rolling review — earlier is better.",
  "test_policy": "optional", "financial_fit": "affordable",
  "net_price_calculator": "https://example.edu/npc",
  "notes": "Would-attend: yes. Withhold scores (below midpoint)."
}
```

- `status` is always `researching`; `category` is the certified band
  (`reach | match | safety`).
- `deadline` auto-fills from `data/deadlines.json` for the intended plan (RD if
  undecided), always with `deadline_verified: false`. For rolling schools the
  deadline is the backstop — set `admission_type: "rolling"` and a
  `recommended_submit_by` (see Submission timing above).
- `system`: UC campuses → `uc`, CSU → `csu`, MIT/Georgetown and other
  non-members → `institutional`, otherwise `common_app` (as in `tracker`).
- Rebalancing an existing list updates `category`, `financial_fit`, and notes on
  existing entries — never resets `status` or deletes entries without asking.
- Update `last_list_review` to today, then offer the calendar export via `tracker`.

## Submission timing — the deadline is rarely the best date

The application deadline is the **backstop, not the target**. Many colleges —
rolling/holistic-as-completed reviewers, wave-decision schools, and anywhere
competitive majors fill along the way — reward submitting *early* (better odds,
plus scholarship/honors/housing priority). Read `references/submission-timing.md`
for the full framework. In brief, for each college you record:

- If `data/deadlines.json` gives an `admission_type` of `rolling` (Common App
  rolling schools are auto-flagged, or `deadlines.RD == "rolling"`), set
  `recommended_submit_by` to shortly after the application opens — weeks before
  any deadline.
- Set `priority_date` when a scholarship/honors/housing date is earlier than the
  admission deadline.
- For anything the bundled data can't flag (ApplyTexas, UC, institutional
  portals), **don't guess** — have `college-scout` read the admissions page to
  detect rolling/wave/priority review, or tell the family to confirm it there.
  (A well-known case is Texas A&M — rolling waves, competitive majors fill early,
  so submit in August rather than by the Dec 1 backstop — but confirm it live;
  it is not baked into the data.)

The roadmap and calendar then surface `recommended_submit_by`, keeping the hard
`deadline` only as a labeled backstop.

## Demonstrated interest — check before performing

Whether a college tracks "demonstrated interest" is published in its Common Data
Set, item C7 ("Level of applicant's interest"):

- **Considered or Important** → interest is a real input. Log concrete actions in
  the `tracker` checklist for that college: virtual info session, campus visit,
  optional interview, opening admissions emails.
- **Not Considered** → stop performing. Visits and email-opening change nothing
  there; spend the hours on essays instead.

Fetch the CDS live (search "<college> Common Data Set"; index and definitions in
`data/sources.json` → `cds`) at exactly two moments: **list finalization** (confirm
C7 for each school) and **submit-or-withhold decisions** at test-optional colleges
(section C9 shows what share of enrolled students submitted scores). Day-to-day,
the bundled data is enough.

## Cross-skill delegation

- Deep per-college research (programs, vibe, CDS deep-dive) → `college-research`
- Adding a single college or advancing statuses → `tracker`
- Submit-or-withhold strategy and score improvement plans → `testing-plan`
- Net price calculators, aid forms, award comparison → `financial-aid`
- International admit rates, aid for internationals, visa timeline → `international`
- Visit planning once interest is worth demonstrating → `visits`

## Persistence contract

Writes: `colleges.json` (read-modify-write, whole file). Reads: `profile.json`,
`colleges.json`, `data/test_policy.json`, `data/deadlines.json`,
`data/college_index.json`, `data/sources.json`. Never writes `essays/drafts/**`.
