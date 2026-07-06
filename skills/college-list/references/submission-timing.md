# Submission timing — the deadline is rarely the best date

The single most common mistake families make is treating the **application
deadline as the target**. For a large share of colleges it is the *backstop* —
the last possible moment — while the actually advantageous submission window is
weeks or months earlier. Reason about the best date per college and record it as
`recommended_submit_by` (plus `admission_type` and a short `timing_note`) in
`colleges.json`, so the roadmap and calendar surface *that*, with the hard
deadline kept only as a backstop.

## The levers that make "earlier" better

1. **Rolling / holistic-as-completed review.** Many public flagships and large
   universities read files as they are completed and release decisions in waves
   through the fall. Seats — especially in **competitive majors** — fill along
   the way, so a strong application submitted in August beats the same
   application submitted in November. Common App members that review this way are
   **auto-flagged** in `data/deadlines.json` as `admission_type: "rolling"` (or
   show `deadlines.RD == "rolling"`); when they are, set `recommended_submit_by`
   to shortly after the application opens. Nothing is hand-listed per school.
   - **Example — Texas A&M** (detect this *live*; A&M is an ApplyTexas school, so
     it is not in the auto-flagged ReqGrid data): rolling holistic review with
     wave decisions, and majors like **Mays Business / Engineering / Nursing**
     fill up; Dec 1 is the final and scholarship deadline, so submit as early as
     ApplyTexas opens (~August). Confirm on the admissions page —
     <https://admissions.tamu.edu/apply/freshman/index.html>.

2. **Priority deadlines — for money and perks, not admission.** Scholarship,
   honors-college, and housing priority dates are frequently **earlier** than the
   admission deadline. Missing them doesn't block admission but forfeits merit
   aid, honors consideration, or good housing. Record these as `priority_date`.

3. **Early rounds usually help.** EA/REA give an earlier answer and sometimes
   stronger merit than RD; some colleges fill a large fraction of the class
   early. ED is binding — the family financial conversation happens first. (These
   are `admission_type: "rounds"`; the plan itself carries the date.)

4. **Never submit on the deadline day.** Portals crash under load on Jan 1 and
   Nov 1. Aim a few days early regardless of everything above.

5. **Delivery lead time.** Test scores, transcripts, and recommendations must
   *arrive*, not just be requested, before the target date — build in the lag.

## How to record it

When adding or reviewing a college, set on its `colleges.json` entry:

| Field | Meaning |
|---|---|
| `admission_type` | `rolling` \| `priority` \| `rounds` \| `wave` \| `unknown` |
| `recommended_submit_by` | the date the family should actually aim for (ISO) |
| `priority_date` | earlier scholarship/honors/housing date, if separate (ISO) |
| `deadline` | the hard backstop deadline (unchanged) |
| `timing_note` | one sentence on *why* the recommended date differs |

Rules of thumb for `recommended_submit_by`:
- Rolling / wave → shortly after the application opens (weeks before any deadline).
- Priority scholarship school → on or before the `priority_date`.
- Fixed rounds → a few days before the round's deadline.

## Where the fact comes from

- `admission_type` may already be in `data/deadlines.json` — Common App rolling
  schools are **auto-flagged from the ReqGrid** (no per-school hand-listing).
  Copy it and derive a concrete `recommended_submit_by`.
- For everything the bundled data can't flag — ApplyTexas, UC, CSU, and
  institutional portals — **do not guess and do not hardcode**. Have the
  `college-scout` agent read the college's admissions page ("how we review",
  "dates & deadlines", "priority", "rolling") and cite it, or tell the family to
  confirm on that page. Every recommended date carries a "verify on the college's
  official page" caveat.
