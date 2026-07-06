# Common Data Set — live-fetch protocol

The Common Data Set (CDS) is a standardized disclosure form that most US
colleges fill out and publish every year — the closest thing to a primary
source for *how a specific college admits*. Canonical definitions:
`sources.json → cds.definitions` (https://commondataset.org/).

There is no API and no bundled dataset. Fetch it live, per college, when a
skill needs factor weights, score-submission rates, or plan deadlines straight
from the institution.

## Fetch protocol

1. **Search**: WebSearch `"<college name>" common data set 2025-2026` —
   substitute the most recent completed academic year (colleges typically
   publish each cycle's CDS during or after that year's spring).
2. **Prefer .edu**: pick the PDF (sometimes .xlsx or HTML) hosted on the
   college's own domain, usually under the institutional research or "facts"
   office. A .edu-hosted CDS is a primary source; a third-party repost is not.
3. **Fallback**: if no current .edu copy surfaces, try the community link
   index at `sources.json → cds.link_index`
   (https://github.com/AlexiaAdams/cds-archive), then search one cycle back.
   An older cycle is usable for factor weights (they move slowly) but **not**
   for deadlines.
4. **Label the vintage**: every fact quoted from a CDS carries the college,
   the cycle year, and the URL — "per <college>'s 2025-2026 CDS (<url>)".

If a college publishes no CDS at all (a minority do not), say so and fall back
to Scorecard/Urban data plus the college's admissions pages.

## The three sections that matter

Match sections by **heading text**, not number alone — numbering typically
holds across colleges but occasionally shifts between cycles.

### C7 — Relative importance of admission factors

A grid rating each factor **Very Important / Important / Considered / Not
Considered**, split into academic factors (rigor of secondary school record,
class rank, GPA, test scores, essay, recommendations) and nonacademic
(interview, extracurriculars, talent, character, first generation, alumni
relation, geography, state residency, religion, volunteer work, work
experience, **level of applicant's interest**).

How to read it: the *differences between colleges* are the signal. "Level of
applicant's interest = Considered" changes visit/contact strategy
(→ `visits`); "interview = Not Considered" deprioritizes interview prep for
that school. Don't over-model a coarse four-level grid — it ranks emphases, it
doesn't score applicants.

### C9 — First-year profile: score submission and ranges

Reports the **percent of enrolled first-years who submitted SAT and ACT
scores** and the 25th/50th/75th percentile scores of those submitters.

How to read it: at a test-optional college, submission percent is the context
the published range hides — a 60%-submitting class means the range describes
the self-selected stronger-testing half. Pair C9 with `data/test_policy.json`
and route strategy questions ("should we submit a 1400 here?") to
`testing-plan`. Remember submitter percentiles run higher than the full class
would.

### C21 / C22 — Early Decision and Early Action

C21 covers **Early Decision** (binding): whether the college offers it,
application deadline(s) including any ED II round, and notification dates.
C22 covers **Early Action** (non-binding, sometimes restrictive): the same
structure. Regular-decision closing dates appear earlier in section C (the
"application closing date" item).

How to read it: these are the college's own published dates — stronger than
any aggregator — but the CDS is a snapshot too. Cross-check against
`data/deadlines.json`, and for any date a family will act on (especially a
binding ED commitment), verify on the college's live admissions page. Route
plan-selection consequences to `tracker` and `college-list`.

## Other sections worth a glance while you have the PDF open

- **C1–C2**: applicants, admits, enrolled, and waitlist counts — fresher than
  Scorecard's `latest.*` when the CDS cycle is newer.
- **C8**: the college's stated test-score policies, in its own words.
- Section **H**: financial aid detail (route interpretation to
  `financial-aid`).

## Citation discipline

- One CDS = one college = one cycle. Never blend cycles silently.
- Quote the grid values as written ("Important"), don't translate them into
  invented percentages — chancing honesty applies (reach/match/safety bands,
  no fake precision).
- Cache nothing: CDS facts a skill wants to keep go into the workspace file
  that skill owns (e.g. `colleges.json` notes via `tracker`), always with the
  cycle year and URL attached.
