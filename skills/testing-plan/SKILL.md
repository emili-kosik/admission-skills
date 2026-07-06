---
name: testing-plan
description: >
  Standardized-testing strategy branched on each college's test policy: who
  actually needs to test, SAT-vs-ACT choice, which sittings feed which
  deadlines, registration lead times, submit-or-withhold calls at
  test-optional schools, PSAT/AP context, and English-proficiency tests for
  international applicants. Use when the user says "testing plan", "SAT or
  ACT", "should we submit scores", "test optional", "test blind", "when is
  the SAT", "register for the ACT", "retake", "superscore", "Score Choice",
  "PSAT", "AP exams", "TOEFL", "IELTS", or "Duolingo".
argument-hint: "[plan|dates|submit|english]"
---

# Testing plan — test for the list the family actually has

Testing effort should follow the college list, not the other way around.
Read these before advising:

1. `profile.json` — `testing` (`psat`, `sat[]`, `act[]`,
   `english_proficiency`), `student.grad_year`, `student.residency`,
   `academics.ap_taken`.
2. `colleges.json` — each entry's `test_policy`, `plan`, and `deadline`.
3. `data/test_policy.json` — fill any missing `test_policy` by name match
   (`required|optional|flexible|free`); offer to write backfilled values
   into `colleges.json`.
4. `data/test_dates.json` — current-cycle SAT/ACT dates with registration
   deadlines, PSAT/AP windows, and `lead_time_rules`.

Staleness discipline: `data/test_policy.json` treats any `required` claim
older than 6 months as needing live verification — check `_meta`, phrase
stale facts "as of <date>", and suggest `/admit:refresh-data`. Policies
flipped repeatedly 2024–2026; before the family books a sitting around one
college's policy, verify it on that college's admissions page (maintained
indexes: the FairTest list and the Compass tracker — URLs in
`data/sources.json` → `testing_policy`).

## Step 1 — sort the list into the three regimes

| Regime | Meaning | Consequence |
|---|---|---|
| `required` | scores mandatory | the student is testing; plan sittings with retake margin |
| `optional` / `flexible` | file read either way | sit anyway if feasible; submit per-college by the numbers |
| `free` | scores never seen (UC/CSU) | testing buys nothing at these schools |

`flexible` means alternatives are accepted or scores are required only for
some applicants (by major, program, or residency) — check what that college
actually accepts before treating it as plain optional.

State the split plainly: "3 of your 8 schools require scores, so you're
testing — here's the sitting plan," or "your list is all UC/CSU — scores are
never seen; skip the SAT unless the list changes."

## Step 2 — regime-specific advice

**Any `required` school on the list → the student tests.** Plan the first
real sitting by spring of 11th grade and hold a senior-fall retake slot;
most students improve on a second sitting, and a first attempt in senior
October leaves no margin before November deadlines.

**`optional` / `flexible` schools:** sitting for the test keeps options
open — a good score is an asset the family controls. The submit/withhold
call is per-college and by the numbers: pull each school's mid-50% range via

```
node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs scorecard_search --name "<name>" --fields core
```

(returns SAT EBRW/math and ACT composite 25th/75th percentiles). The
college's Common Data Set section C9 adds useful context — it shows what
share of enrolled students actually submitted scores. Read
`references/score-send-strategy.md` before making any submit/withhold
recommendation; it has the full decision tree plus superscore and Score
Choice explained as concepts.

**`free` schools (UC, CSU):** scores are never seen for admission. If the
list is entirely test-free, say so and stop — every prep hour is better
spent on grades and PIQs. Even on mixed lists, do not let test prep displace
PIQ drafting time in the fall: the PIQs are what UC actually reads (essay
work routes to `essay-coach`).

## Step 3 — calendar mechanics

Use `data/test_dates.json` for exact dates; never recite dates from memory.
The `lead_time_rules` there are the trap to flag:

- **SAT registration closes ~15 days before** the test date (a late window
  runs a few days longer, for an extra fee).
- **ACT registration closes ~5 weeks before** — far earlier than families
  expect, and the most common way students get locked out of a sitting.

Which sitting feeds which deadline (confirm exact dates in the dataset):

| Application deadline | Last comfortable SAT | Last comfortable ACT |
|---|---|---|
| Nov 1 ED/EA | October | October (September is safer) |
| Jan 1–15 RD / ED2 | December | December |

Later sittings sometimes arrive in time — some colleges accept scores that
land after the deadline — but that is a per-college policy to confirm on the
college's page, never a plan. Put **registration deadlines**, not just test
dates, on the family calendar. After writing any `test_policy` changes to
`colleges.json`, rerun

```
node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs timeline_build --workspace <ws>
```

so `.admissions/milestones.json` picks up (or drops) the testing track, then
offer the calendar export via `tracker`.

## SAT vs ACT — decide by percentile, once

Have the student take one full-length **official** practice test of each,
free: Bluebook practice plus Khan Academy's Official SAT Prep (linked from
satsuite.collegeboard.org/sat/practice-preparation) and ACT's free practice
materials on act.org. Compare **percentiles, not raw scores**; prep for
whichever is clearly higher, and on a tie pick either and stop switching.
Colleges have no preference between the two tests.

## PSAT and AP

- **PSAT/NMSQT:** October, administered through the high school — the school
  picks the date, not the student (window in `data/test_dates.json`). The
  11th-grade sitting is the National Merit qualifier; earlier sittings are
  practice with no prep pressure.
- **AP exams:** the first two full weeks of May (window in
  `data/test_dates.json`; respect its `verified` flag — next-year dates are
  often unpublished until fall). Rigor beats exam count: admissions readers
  weigh the transcript's course rigor first, and a longer AP list adds
  little beyond a coherent, rising arc. AP scores are **self-reported** on
  applications and sent officially once — to the college the student
  enrolls at. Do not pay to send AP scores to every school on the list.

## English proficiency (international)

If `student.residency` is international or the student's schooling is not
English-medium, read `references/english-proficiency.md` — TOEFL/IELTS/
Duolingo comparison, delivery times, waiver patterns, and the
test-by-September–October rule for November deadlines. Broader international
logistics (visas, credential evaluation) → `international`.

## Record the plan

Write agreed facts back to `profile.json` → `testing` (read-modify-write the
whole file): sittings and scores in `sat`/`act`, PSAT result in `psat`,
proficiency test and score in `english_proficiency`. Keep entries factual
(dates, scores, planned sittings); the narrative rationale lives in the
conversation and the timeline.

## Cross-skill delegation

- Adding colleges, verifying deadlines, calendar export → `tracker`
- Building or rebalancing the list this plan depends on → `college-list`
- One college's exact policy, in depth → `college-research`
- PIQ and essay time-budgeting → `essay-coach`
- Visas, credentials, the rest of the international file → `international`
- Grade-by-grade sequencing of prep → `roadmap`
- Background reading for the family → `guide` (its testing chapter)

## Persistence contract

Writes: `profile.json` (testing section; read-modify-write whole file),
`colleges.json` (backfilling `test_policy` values only; read-modify-write
whole file), `.admissions/milestones.json` (via `timeline_build` only).
Reads: `data/test_policy.json`, `data/test_dates.json`, `data/sources.json`,
`.admissions/config.json`. Never writes `essays/drafts/**`.
