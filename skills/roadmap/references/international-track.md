# International track — timeline divergences

Load this when `profile.json` says `student.residency: international` (the
computed `tracks` include `international`). The four `int-*` rows in
`data/milestones.json` are the source of everything here; the visa-chain facts
come from the State Department's student-visa page —
https://travel.state.gov/content/travel/en/us-visas/study/student-visa.html —
cite it whenever visa timing is load-bearing.

## English proficiency testing (`int-english-test`, senior fall — critical)

The rule that drives the schedule: **test by September–October for November 1
deadlines; by October–November for January deadlines** — colleges need delivery
time on top of the sitting.

- TOEFL scores post in roughly 4–8 days; IELTS and Duolingo English Test
  turnaround varies — build in delivery time, not just scoring time
  (https://www.ets.org/toefl, https://ielts.org,
  https://englishtest.duolingo.com).
- Each college sets its own minimum scores **and** its own waiver rules (e.g.,
  English-medium schooling) — check per college before booking a test the
  student may not need.
- In `timeline.md`, render this as a September advisory anchored to the earliest
  deadline on the family's list, not as a fixed date.

## Credential evaluation (`int-credential-eval`, senior September — high)

Some US colleges require a course-by-course evaluation of non-US transcripts
from an agency such as WES or ECE (https://www.wes.org); **many evaluate
international transcripts in-house instead**. Evaluations typically take **4–8
weeks** and cost money, so the rule is:

1. First check each college's international-applicant page — do not order an
   evaluation nobody requires.
2. If one is required, order it **4–8 weeks before the earliest application
   deadline** (early September for a Nov 1 deadline).

## Financial documentation (`int-financial-docs`, senior October — high)

Most US colleges are **need-aware for international applicants**, and many
require a certification of finances or bank statements — some at application
time, some at admission; it varies by college. Prepare the documents early
either way: **the same proof of funding is required for the I-20 after
enrollment**, so this work is never wasted. Render as an October advisory with a
per-college "check where in the process each college wants it" note.

## The post-deposit visa chain (`int-i20-chain`, May — critical)

Starts **immediately after the enrollment deposit** — this is the one sequence
where days matter and every step gates the next:

1. **Request the I-20** from the enrolling college (they issue it through
   SEVIS once finances are documented).
2. **Pay the SEVIS I-901 fee** at https://www.fmjfee.com — keep the receipt.
3. **File the DS-160** online visa application.
4. **Book the embassy/consulate interview** — wait times vary widely by post,
   so book as early as the paperwork allows.

Two timing rules from travel.state.gov to state plainly:

- An F-1 visa can be **issued up to 365 days before the program start date** —
  there is no reason to wait past May.
- The student may **enter the US no earlier than 30 days before the program
  start date**, regardless of when the visa was issued — plan flights around
  the program start, not the visa issuance.

In `timeline.md`, render the chain as a single May item right after the May 1
decision-day milestone, with the four steps inline — the family should see it as
one project, not four scattered tasks.

## Rendering notes

- All four items are `relative` (undated) rows: they appear as advisories in
  their anchor months (Sep, Sep, Oct, May). Keep the "date varies" phrasing and
  anchor each to the family's actual earliest deadline where possible.
- Everything else on the international timeline is the standard domestic
  calendar — Common App Aug 1, FAFSA/CSS where applicable, Nov/Jan deadlines,
  May 1 reply. The international rows are additions, not replacements.
- Aid nuance: FAFSA is for US citizens/eligible non-citizens; international
  applicants typically use the CSS Profile or a college's own forms where the
  college offers international aid — route specifics to `financial-aid` and
  `international`.
- Anything deeper than scheduling (visa categories, transfer credit, embassy
  specifics) → the `international` skill owns it.
