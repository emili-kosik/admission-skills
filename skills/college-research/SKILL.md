---
name: college-research
description: >
  Single-college deep dive: quantitative profile (admit rate, scores, net price,
  applicant trends), current deadlines, test and AI policies, what the college
  weighs in review (CDS C7), required essays, and aid posture — assembled into
  one dossier with primary-source verification via the college-scout agent.
  Use when the user says "tell me about <college>", "research <college>",
  "deep dive on <college>", "what does <college> look for", "what are our
  chances at <college>", "is <college> a reach", "deadlines for <college>",
  or "does <college> require supplemental essays".
argument-hint: "[college name]"
---

# College Research — the one-college deep dive

Build a dossier on a single college: hard numbers first, bundled policy data
second, then primary-source verification through the `college-scout` agent.
One college per run; for building or rebalancing a whole list, route to
`college-list`.

## Output style — quiet writes

Update workspace files quietly: gather what you need, then do a single whole-file
read-modify-write. **Never paste JSON, code blocks, raw file contents, or
field-by-field diffs into your reply** — the family should not have to read the file
format. Rendering a human-readable table or summary for them is fine; the rule is
about not exposing the raw file. Confirm what changed in one short, plain-language
sentence. (The editor's own change card may still appear — that is the app's UI,
don't narrate or add to it.)

## 1. Resolve the college

1. Fuzzy-match the user's name against `data/college_index.json` (names,
   `alias` fields; disambiguate with city/state). Capture the `unitid`.
2. If several plausible matches remain (e.g. "Columbia", "Miami"), list them
   with city/state and ask — never guess between distinct institutions.
3. If there is no match, say so and offer the closest candidates; do not
   research a college you could not resolve to a unitid.

## 2. Pull the quantitative profile

```
node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs scorecard_search --id <unitid> --fields core
node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs urban_lookup --unitid <unitid> --endpoint admissions-enrollment
```

- Scorecard gives admit rate, SAT/ACT 25th–75th percentiles, size, ownership,
  tuition, average net price and net price by income bracket, grad rate,
  median earnings, the official site URL, and the net-price-calculator URL.
- The Urban/IPEDS call returns applicants, admits, and enrolled by year —
  compute the admit rate for the most recent years and note the direction of
  the trend (rising selectivity is common; say it plainly, not alarmingly).
- If Scorecard returns a `needs_key` or DEMO_KEY-429 error, relay its signup
  guidance verbatim and continue with the Urban data plus bundled datasets.

## 3. Read the bundled policy entries

Match by **name** (these files carry no unitid):

- `data/deadlines.json` — rounds and dates (ED/ED2/EA/REA/RD/rolling), fees,
  writing-supplement flag, rec counts; system overrides (UC/CSU/MIT/
  Georgetown/ApplyTexas) may use `annual_rules` MM-DD windows instead of
  dates. Every date from this file is *unverified until the scout confirms it*.
- `data/test_policy.json` — required / optional / flexible / free. Policies
  older than 6 months (`_meta.last_verified`) need live verification before
  you assert "required".
- `data/ai_policies.json` — if the college has an entry, quote its tier and
  verbatim policy with the citation URL; if not, state that the strictest
  common denominator applies (Common App fraud-policy baseline, tier
  `prohibitive`).

If any `_meta.cycle` is behind the workspace cycle in
`.admissions/config.json`, or `last_verified` is stale, phrase facts as
"as of <date>" and suggest `/admit:refresh-data`.

## 4. Send the college-scout for primary sources

Spawn the `college-scout` agent (Agent tool, subagent type `college-scout`)
with the college name, unitid, and official URL from step 2. Ask it for:

| Item | Source it should use |
|---|---|
| CDS section C7 factor weights (very important → not considered) | the college's own Common Data Set (registry: `data/sources.json` → `cds`) |
| Current-cycle deadlines and fees | the college's admissions page |
| Supplemental essays for this cycle (count + topics) | admissions/apply page |
| Program strengths matching the student's interests (read `profile.json` first) | department and admissions pages |
| Aid posture: need-blind vs need-aware (especially for international applicants), meets-full-need claim, CSS Profile requirement | the college's financial-aid page |

Merge results: where the scout's dates disagree with `data/deadlines.json`,
prefer the scout's (they came from the college's own page) and flag the
discrepancy. Anything the scout could not confirm stays marked unverified.

## 5. Present the dossier

Render in this order, compact and scannable:

1. **Header** — name, city/state, public/private, size, official URL.
2. **Stats table** — admit rate (+ 3-year applicants/admits trend), SAT/ACT
   mid-50%, grad rate, average net price and the bracket nearest the family's
   income (from `profile.json` finances, if present), median earnings.
3. **Band** — reach / match / safety relative to the student's profile. Never
   a percentage. An admit rate under 15% is a reach for everyone, regardless
   of stats.
4. **Deadlines table** — plan, date, fee, each row marked `verified` (scout
   confirmed on the official page) or `verify before relying on this`.
5. **What they weigh** — the C7 grid as a table; if no CDS was found, say the
   weights are unknown rather than inferring them.
6. **Essays required** — personal essay + supplement count and topics; note
   that essay work routes to `essay-coach`, and state the college's AI-use
   tier with its citation.
7. **Testing** — policy plus the mid-50% context ("optional" still means
   scores help when above the 50th percentile — typically; check the
   college's testing page).
8. **Aid posture** — need-blind/need-aware, meets-full-need, CSS Profile,
   net-price-calculator link. **International note:** most US colleges are
   need-aware for international applicants — applying for aid can affect the
   admission decision — typically; verify on this college's aid page (the
   scout's finding, when present, overrides the generality).
9. **Next actions** — 2–4 concrete steps (run the NPC, verify the target
   deadline, start the supplement, book a visit → `visits`).

## 6. Offer to add it to the tracker

Ask whether to add the college to `colleges.json`. On yes, follow `tracker`
conventions: read the whole file, append an entry (`status: "researching"`,
`system`, chosen `plan`, `deadline` with `deadline_verified` true **only** if
the scout confirmed it, `test_policy`, scout findings summarized under
`data`/`notes`), write the whole file back, and note that ED is binding if
they picked ED. If the college is already on the list, update its `data` and
`notes` instead of duplicating. If no workspace exists, route to `start`.

## Cross-skill delegation

- Building or rebalancing the whole list → `college-list`
- Status board, checklists, calendar export → `tracker`
- Supplemental essay work → `essay-coach` (never draft essay text here)
- Net price, CSS Profile, award letters → `financial-aid`
- Test planning against this college's policy → `testing-plan`
- Visa/credential questions for this college → `international`
- Visit planning and demonstrated interest → `visits`

## Persistence contract

Writes: `colleges.json` (read-modify-write, whole file, only after the user
confirms adding/updating). Reads: `profile.json`, `colleges.json`,
`.admissions/config.json`, bundled `data/college_index.json`,
`data/deadlines.json`, `data/test_policy.json`, `data/ai_policies.json`,
`data/systems.json`, `data/sources.json`. Never writes `essays/drafts/**`.
