# Classification methodology — how a college gets its band

Apply these steps in order to every candidate. The output of steps 0–2 is a
five-band label used in discussion (**reach, lean-reach, match, lean-safety,
safety**); step 3 decides what may be written to `colleges.json` (whose
`category` enum is only `reach | match | safety`); step 4 annotates money.
Bands are honest ranges — never translate them into percentages.

## Inputs

| From | Fields |
|---|---|
| `profile.json` | best SAT (EBRW + Math) and/or ACT composite, `gpa_unweighted`, `rigor_arc`, `budget_per_year_usd`, `income_bracket`, `residency` |
| `scorecard_search` result | `admit_rate`, `sat.ebrw_25/75`, `sat.math_25/75`, `act.comp_25/75`, `avg_net_price`, `net_price_by_income`, `net_price_calculator` |
| `data/test_policy.json` | `required \| optional \| flexible \| free` |

## STEP 0 — the hard rule

**If `admit_rate` < 0.15, the college is a reach for everyone. No exceptions,
ever.** Not for a 1600, not for a 4.0 with twelve APs, not for legacy, not for
"the counselor thinks it's likely." Below 15%, fully qualified applicants
outnumber seats so heavily that no profile makes an offer predictable. Steps 1–2
modifiers never move a sub-15% school out of reach.

Sub-15% schools may stay on the list, labeled **lottery picks** in discussion —
maximum 2 per list. They are bought tickets, not plans.

## STEP 1 — score position vs the 25th/75th percentiles

**Skip this step entirely when the college's test policy is `free`** — scores are
never considered there, even spectacular ones. Classify on GPA and rigor instead.

Otherwise:

1. Compute the student's best SAT total (best EBRW + best Math from
   `profile.json`) and/or best ACT composite.
2. Compute the college's SAT 25th/75th totals (`ebrw_25 + math_25`,
   `ebrw_75 + math_75`) and ACT `comp_25`/`comp_75`. Use whichever test
   positions the student better. Midpoint = (25th + 75th) / 2.
3. Position:

   | Student score | Position |
   |---|---|
   | at/above the 75th percentile | **strong** |
   | midpoint to 75th | **solid** |
   | 25th to midpoint | **below midpoint** |
   | below the 25th percentile | **weak** |

Policy handling:

- **required** — the position stands as computed; scores will be seen.
- **optional** (and **flexible**, unless an accepted alternative positions the
  student better) — if the position is **below midpoint**: advise **withholding
  scores at this college**, classify on GPA and rigor instead, and apply a
  **one-notch shift toward reach** in STEP 2. A withheld score can't help, and a
  below-midpoint score submitted anyway actively hurts. Finalize each
  submit-or-withhold call with `testing-plan` and the college's live CDS section
  C9 (share of enrolled students who submitted scores).
- **free** — already skipped above.

When classifying on GPA/rigor (test-free colleges or withholding cases): compare
`gpa_unweighted` and `rigor_arc` against the college's typical admitted profile
(from `college-research` or the college's published class profile — verify live;
Scorecard does not carry GPA).

## STEP 2 — base band from admit rate, then modifier shifts

| Admit rate | Base band |
|---|---|
| < 15% | **reach** (STEP 0 — immovable) |
| 15–30% | **lean-reach** |
| 30–60% | **match** |
| 60–80% | **lean-safety** |
| > 80% | **safety** |

Modifier shifts — one notch on the ladder
`reach ↔ lean-reach ↔ match ↔ lean-safety ↔ safety`, net shift of at most one
notch, and never any shift for a sub-15% school:

| Modifier | Shift |
|---|---|
| Position **strong** (≥ 75th percentile) | one notch toward safety |
| Position **weak** (below 25th, at a school that will see the score) | one notch toward reach |
| Test-optional + below midpoint (withholding, from STEP 1) | one notch toward reach |
| GPA clearly below the typical admitted range (test-free / withholding cases) | one notch toward reach |

Mapping the final band to the workspace `category` enum:

| Final band | `category` written |
|---|---|
| reach, lean-reach | `reach` |
| match | `match` |
| lean-safety, safety | `safety` **only if certified in STEP 3**, otherwise `match` |

## STEP 3 — safety certification (ALL four must pass)

`safety` is a certification, not an impression. Record a college as `safety`
only when **every** test passes:

1. **Admissible with room to spare** — `admit_rate` ≥ 0.50 **and** stats at or
   above the 75th percentile (or: the college is test-free **and** GPA is clearly
   above its typical admitted profile).
2. **Affordable** — the net price for the family's income bracket
   (`net_price_by_income`) is at or below `budget_per_year_usd`. A college the
   family cannot pay for is not a safety at any admit rate.
3. **Would genuinely attend** — asked out loud and answered yes: "If this were
   the only acceptance in April, would the student enroll happily?" A safety
   nobody would attend is list decoration.
4. **International check** (when `residency` is international) — the college
   admits international applicants at a rate similar to its overall rate, **and**
   either meets demonstrated need for internationals or the family documents
   ability to pay the full cost of attendance. International admit rates at US
   colleges typically run well below the published overall rate, and most
   need-based aid formulas exclude internationals — verify on the college's
   international admissions page before certifying.

Any failure → **cap at `match`**, and say which test failed so the family can fix
it (retest, verify aid, find a school they'd actually attend).

## STEP 4 — financial-fit annotation (every school, no exceptions)

Every school on the list gets exactly one annotation:

| Annotation | Meaning |
|---|---|
| **affordable** | bracket net price ≤ `budget_per_year_usd` |
| **stretch** | bracket net price above budget, but the family names a concrete plan for the gap (savings, modest federal loans) — state the gap in dollars |
| **requires-aid-outcome** | affordability depends on a merit or need award that cannot be known before decisions arrive — say so plainly; this school can never be the financial safety |

Always attach the college's own **Net Price Calculator** link — the
`net_price_calculator` field in every scorecard result — and recommend the family
run it before the list is finalized. Scorecard net prices are averages from past
cycles; the NPC is the college's own current-year estimate and always wins.

Bracket note: scorecard core output carries the $48,001–75,000 and
$75,001–110,000 brackets. For incomes outside those, rerun with `--fields full`
(the raw Scorecard row carries all income brackets) or rely on the NPC, and say
which number you used.

## Demonstrated interest — CDS item C7

The Common Data Set, item C7, rates "Level of applicant's interest" from Very
Important down to Not Considered (definitions and link index:
`data/sources.json` → `cds`).

- **Considered / Important / Very Important** → interest is a real admission
  input. Log concrete actions as checklist items in `tracker`: virtual info
  session attended, campus visit, optional interview taken, admissions emails
  opened.
- **Not Considered** → stop performing. No visit, email-open, or "why us"
  enthusiasm changes the outcome; redirect those hours to essays.

**When to fetch the CDS live** (search "<college> Common Data Set" and prefer the
college's own institutional-research page):

1. **List finalization** — confirm C7 for every school on the list.
2. **Submit-or-withhold decisions** at test-optional colleges — section C9 shows
   the share of enrolled students who submitted SAT/ACT scores and their score
   ranges, which is better evidence than the Scorecard percentiles alone.

Outside those two moments, bundled data plus scorecard results are sufficient —
do not burn a session fetching a dozen PDFs during early exploration.
