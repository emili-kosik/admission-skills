# UC track — how the roadmap diverges

Load this when the timeline's `tracks` include `uc`. Everything below comes from
`data/deadlines.json` (UC system override), `data/milestones.json` (`uc-*` rows),
and `data/ai_policies.json`. Primary source for all of it:
https://admission.universityofcalifornia.edu/how-to-apply/ — link it whenever a
UC date is load-bearing.

## The UC calendar in three dates

| Date | What happens | Milestone id |
|---|---|---|
| Aug 1 | UC application **opens for working** — activities, PIQ planning | `uc-open` |
| Oct 1 | **Filing window opens** (submission becomes possible) | `uc-filing-open` |
| Nov 30 | **Filing deadline, firm** — full application + all four PIQs | `uc-filing-deadline` |

One application covers all nine UC campuses. The window is occasionally extended
by a few days in unusual years — never plan on it, and say so if the family is
cutting it close.

## No rounds: there is no UC ED or EA

The UC system has no Early Decision, no Early Action, no ED2 — one filing window
for everyone, no binding commitments, no strategic timing question. When the
family asks "should we apply early to UCLA?", the answer is that the concept does
not exist: file well inside Oct 1 – Nov 30 and be done.

## The calendar lands a month before RD

Nov 30 sits a full month before the Jan 1–15 Regular Decision cluster. For a
mixed UC + Common App list, this front-loads senior fall hard:

- PIQ drafting must happen in **summer and September**, not winter break —
  winter break is for RD supplements, and the PIQs will already be filed.
- In `timeline.md`, treat Nov 30 as the anchor of November for UC families;
  render it bold-critical even when Common App early deadlines share the month.
- A UC-only list means senior year is effectively over on Nov 30 except for aid
  forms and decisions. Say that out loud — it reframes the whole fall.

## No recommendations for most applicants

The UC application takes **zero letters of recommendation for most applicants**
(`teacher_evals: 0`, no counselor rec, no mid-year report in the base
requirements). Practical consequences for the roadmap:

- The `g11-spring-recs` milestone ("ask 2 junior-year teachers") is Common App
  work; on a UC-only list it does not apply, and the dataset row already says so.
- Do not build brag-sheet or recommender-logistics items into a UC-only fall.

## Essays are PIQs: 4 of 8, 350 words each

There is no UC personal essay. Applicants answer **4 Personal Insight Questions
chosen from 8**, at **350 words each**. The verbatim prompts are in
`data/essay_prompts.json`. All PIQ work routes to `essay-coach` — the roadmap
only schedules it (summer draft window, filed by Nov 30).

## Test-free: SAT/ACT are never considered

UC is **test-free**, not test-optional: SAT/ACT scores are not used for
admission at any campus (`test_policy: "free"`). Two roadmap consequences:

- `timeline_build` drops the SAT/ACT milestones only when *every* tracked
  college is test-free — a mixed list keeps the testing arc for the non-UC
  colleges. Explain that if the family asks why test dates still appear.
- Because scores are out of the picture, the PIQs and the activities record
  carry more of the weight. Schedule them accordingly.

## Integrity screening on the PIQs

Per UC's Statement of Application Integrity
(https://apply.universityofcalifornia.edu/docs/StatementOfIntegrity.pdf, quoted
verbatim in `data/ai_policies.json`): PIQ responses must be **independently
written by the student** in the student's own style; generative AI is permitted
only "to assist with readability", and **content and final written text must be
the student's own**. UC **conducts regular screenings** of responses, may
request authentication of authorship, and takes action when integrity is
compromised.

When rendering a UC timeline, attach a one-line reminder to the PIQ milestones:
the plugin coaches PIQs but never writes them — that is both house policy and
UC's enforced policy.

## Rendering notes for timeline.md

- August: show `uc-open` as a real start item ("you can work in it from Aug 1").
- October: `uc-filing-open` plus FAFSA/CSS opening make Oct 1 a heavy day —
  group them visibly.
- November: Nov 30 is the month's anchor; warn at ≤14 days like any critical
  deadline.
- Decisions: campuses release on their own schedules through winter and spring —
  the dataset carries no per-campus decision dates, so don't state any; point to
  each campus's admissions page instead.
