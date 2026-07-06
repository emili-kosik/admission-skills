---
name: international
description: >
  The international-applicant (F-1) track: what changes when the student applies
  from outside the US — need-aware financial aid, English proficiency tests
  (TOEFL/IELTS/Duolingo), credential evaluation of non-US transcripts, Common App
  school-report differences, and the post-admission I-20 → SEVIS → DS-160 →
  embassy-interview chain. Use when the user says "international student",
  "we're not US citizens", "F-1", "student visa", "I-20", "SEVIS", "DS-160",
  "TOEFL", "IELTS", "Duolingo English Test", "credential evaluation", "WES",
  "our school has no counselor", or asks how US admissions differs for a
  student applying from abroad.
argument-hint: "[setup|english-tests|credential-eval|visa]"
---

# International — the F-1 applicant track

Orientation and routing for families applying from outside the US. Everything in
`guide` still applies — holistic review, rounds, essays, the May 1 reply date.
This skill covers only the deltas. If no workspace exists, route to `start` first.

## First: switch the international track on

1. Read `profile.json`. If `student.residency` is not `"international"`, confirm
   with the family (will the student need an F-1 visa to study in the US?), then
   set `student.residency` and `student.country` (read-modify-write the whole file).
2. Read `.admissions/config.json`; set `"international": true` if it isn't.
3. Recompute the timeline so the international milestones (English test,
   credential evaluation, financial documents, the visa chain) appear:

   ```
   node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs timeline_build --workspace <ws>
   ```

   Then offer a calendar re-export via `tracker`.

## The five deltas — what actually changes

| Delta | The short version | Depth |
|---|---|---|
| **Aid is usually need-aware** | At most colleges, an international's aid request can affect the admission decision; only a short list are need-blind for internationals. Decide whether/where to apply for aid per college. | `financial-aid` |
| **English proficiency** | Most colleges require TOEFL, IELTS, or Duolingo unless waived; scores must be *delivered* by the deadline. | `references/english-tests.md` |
| **Credential evaluation** | Some colleges require a WES/ECE course-by-course evaluation of non-US transcripts; many evaluate in-house. Typically 4–8 weeks plus a fee. | `references/credential-eval.md` |
| **The school report** | The Common App expects the school — not the family — to submit reports and transcripts. Many schools abroad have never done this. | below |
| **The visa chain** | Admission is not the finish line: I-20 → SEVIS fee → DS-160 → embassy interview, each step gated by the previous. | `references/visa-sequence.md` |

Read the matching reference before answering in depth: `references/english-tests.md`
when planning proficiency testing, `references/credential-eval.md` when a transcript
question comes up, `references/visa-sequence.md` when a college is accepted/enrolled
or the family asks about visas.

## Per-college homework (never assert from memory)

Three facts vary by college and change year to year: the English-test policy
(minimums, accepted tests, waivers), whether a credential evaluation is required,
and the international aid policy (need-aware? aid form?). For each college on the
list:

1. Check its own international admissions page (WebSearch
   `"<college> international first-year requirements"`, prefer the `.edu` result).
2. Record findings in that college's `notes` in `colleges.json`, and track the
   work with extra checklist keys — the schema accepts them — such as
   `english_scores_sent`, `credential_eval_ordered`, `financial_docs_submitted`.
3. State bundled or remembered patterns as "typically" and point to the college's
   page as the contract. Canonical URLs live in `data/sources.json` under
   `international` (travel.state.gov, fmjfee.com, ets.org/toefl, ielts.org,
   englishtest.duolingo.com, wes.org).

## Common App school-report differences

- The Common App expects the **school** to upload a School Report, official
  transcript, and counselor recommendation through its recommender system. Brief
  the counselor or head of school in September; walk them through the system if
  they've never seen it.
- No "counselor" role exists at many schools abroad — a principal, head teacher,
  or director of studies can serve as the counselor recommender.
- Transcripts not in English typically need a certified English translation
  submitted alongside the original.
- A one-page **school profile** explaining the grading scale and curriculum helps
  US readers calibrate; if the school has none, encourage them to write one.
- IB / A-level and similar systems: colleges typically work from **predicted
  grades** submitted by the school at application time.

## Timing rules (the international overlay on the normal calendar)

- **English tests**: delivered-by-the-deadline, not taken-by. Typically test
  Sept–Oct for Nov 1 ED/EA, Oct–Nov for January RD, leaving room for one retake.
- **Credential evaluation**: typically 4–8 weeks end to end — confirm each
  college's requirement in early September and order immediately if needed.
- **Financial documents do double duty**: the certification of finances and bank
  statements colleges request at application are the same documents that later
  support the I-20. Prepare them once, carefully → `financial-aid`.
- **FAFSA is not for you**: it's limited to US citizens and eligible noncitizens.
  Internationals seeking aid typically file the CSS Profile (opens Oct 1) or the
  college's own form — check which per college → `financial-aid`.
- **After the deposit, move the same week**: embassy interview wait times vary
  enormously by post; late booking is the step that strands people.

## Post-admission: the chain in one line

Deposit → request the I-20 from the college → the school registers the student in
SEVIS → pay the SEVIS I-901 fee at fmjfee.com → complete the DS-160 → book the
embassy/consulate interview early → F-1 issuable up to 365 days before program
start → enter the US within 30 days of the program start date
([travel.state.gov](https://travel.state.gov/content/travel/en/us-visas/study/student-visa.html)).
Read `references/visa-sequence.md` for the step-by-step version and the interview
document checklist — proactively, when any college's status becomes `accepted` or
`enrolled`.

## Cross-skill delegation

- Financial documentation depth — certification of finances, bank statements,
  CSS Profile for internationals, the need-blind short list → `financial-aid`
  (read its `international-aid.md` reference).
- SAT/ACT planning and test-date logistics → `testing-plan` (English proficiency
  tests live here; SAT/ACT live there).
- Adding colleges, statuses, deadlines, calendar export → `tracker`.
- Concept-level orientation and glossary for the family → `guide` (its
  `international-orientation` chapter).
- Building a list that accounts for international aid policies → `college-list`;
  one-college deep dives → `college-research`.
- Scholarships open to non-US citizens → `scholarships`.
- Comparing offers before the deposit → `decision-day`.
- Essay questions of any kind → `essay-coach` (coaching only, never ghostwriting).

## Persistence contract

Writes: `profile.json` (`student.residency`, `student.country`,
`testing.english_proficiency` — read-modify-write, whole file),
`.admissions/config.json` (`international` flag — read-modify-write, whole file),
`colleges.json` (per-college `notes` and international checklist keys —
read-modify-write, whole file), `.admissions/milestones.json` only via the
`timeline_build` script. Reads: `essays/index.json`, bundled `data/sources.json`,
`data/systems.json`, `data/test_policy.json`. Never writes `essays/drafts/**`.
