# Score-send strategy — submit, withhold, and which sittings

The submit/withhold decision is made **per college, not per student**. A
score that strengthens one application can be dead weight on another, and
score sends to one school never force sends to the rest of the list.

## Get the numbers before giving an opinion

1. **Mid-50% ranges** — pull per college:

   ```
   node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs scorecard_search --name "<name>" --fields core
   ```

   Returns `sat.ebrw_25/ebrw_75`, `sat.math_25/math_75`, and
   `act.comp_25/comp_75`. Approximate the SAT **total** range by summing the
   section 25ths and 75ths (a rough proxy — real total distributions are
   tighter than the sum suggests). Take the midpoint of a range as the
   average of its 25th and 75th.
2. **Submission-rate context** — the college's Common Data Set, section C9,
   reports both the score percentiles and the **share of enrolled first-years
   who submitted** SAT/ACT scores. At schools where only a minority
   submitted, withholding is demonstrably normal, not a red flag. CDS
   definitions: commondataset.org; a maintained per-college link index is in
   `data/sources.json` → `cds.link_index`.
3. **Self-selection caveat:** at test-optional colleges the published ranges
   describe *submitters only*, which typically inflates them — students
   below the range simply didn't send scores. A result just under the
   published 25th is typically closer to the real enrolled median than it
   looks. Say this when a family is discouraged by a range.

## The decision tree

```
What is the college's test_policy?
│
├─ required ──→ SUBMIT — there is no decision. The only questions are
│               which sittings to send (Score Choice) and whether the
│               college superscores. See below.
│
├─ free ─────→ DO NOT SEND for admission — scores are never read
│               (UC/CSU). Don't pay for score reports to these schools.
│               UC states that scores submitted anyway may be used only
│               after enrollment (eligibility/course placement), never
│               for admission or scholarships — verify current language
│               at admission.universityofcalifornia.edu/how-to-apply/.
│
├─ flexible ─→ First check WHAT the college accepts: "flexible" means
│               alternatives count (AP/IB/other exams) or scores are
│               required only for some applicants (by major, program,
│               or residency). Resolve which case applies on the
│               college's testing page, then treat the SAT/ACT path
│               like "optional" below.
│
└─ optional ─→ Compare the student's best score to the college's
                mid-50% range:
                │
                ├─ at/above the 75th ────────→ submit; clear asset.
                ├─ midpoint to 75th ─────────→ submit; typically helps.
                ├─ 25th to midpoint ─────────→ judgment call (below).
                └─ below the 25th ───────────→ typically withhold.
```

**The judgment band (25th → midpoint).** Lean submit when: the intended
major is less competitive than the college's headline pool, the student is
in-state at a public flagship, one section is exceptional even if the total
is middling (a few colleges read sections separately), or the rest of the
academic file needs corroboration (grade dip, unfamiliar school). Lean
withhold when: the score contradicts an otherwise stronger narrative
(e.g., a math-heavy applicant with a soft math section), or C9 shows most
enrolled students didn't submit. "Optional" is genuinely optional — colleges
admit large numbers of non-submitters — so frame this as a numbers decision,
not a character test.

## Superscore (concept — policy is per-college)

Superscoring means the college recombines the **highest section scores
across multiple sittings** into a new composite: best SAT math from March +
best EBRW from October, or a recomputed ACT composite from the best English/
math/reading/science across dates. Consequences:

- Retakes are lower-risk at superscoring colleges — a weaker overall retake
  can still raise one section.
- ACT score reports can include a calculated superscore; whether a college
  *uses* it is that college's choice.
- Whether a college superscores at all, and whether it superscores across
  SAT and ACT paper/digital variants, is stated on its standardized-testing
  page. **Verify per college before planning retakes around it.**

## Score Choice and "all scores" policies (concept — verify per college)

Score Choice is College Board's option to send only chosen SAT **test
dates** (whole sittings — sections within one date can't be split). ACT
reports are likewise ordered per test event. Two caveats:

- A small number of colleges ask applicants to send their **full testing
  history** rather than a chosen subset — Georgetown has historically been
  the best-known example. Check each college's testing page before relying
  on Score Choice.
- Self-reported scores on the application typically carry the process until
  a college requires official reports (often only at enrollment for
  matriculants) — but some require official scores with the application.
  Per-college; verify.

## Mechanics and costs

- Both testing programs typically include a few free score sends around
  registration time; after that window each report costs a fee, and rush
  delivery costs more. Current fees:
  satsuite.collegeboard.org/sat/dates-deadlines (SAT) and act.org (ACT).
- Official reports take days to generate and for colleges to process —
  don't leave first-time sends to deadline week.
- Fee-waiver-eligible students typically get score sends free — check the
  current terms on each testing program's site.

## Mixed-list playbook (the common case)

1. Send scores to every `required` school — non-negotiable.
2. Run the decision tree per `optional`/`flexible` school; record each
   verdict so the family isn't re-litigating it in deadline week.
3. Send nothing to `free` schools.
4. Note the verdicts in conversation and keep `profile.json` → `testing`
   current with actual scores so future sessions can re-run the comparison
   as new results arrive.
