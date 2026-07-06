# The offer-comparison framework

This is the worksheet `decision-day` builds in `decisions.md`. It has three
row groups — **cost**, **outcomes**, **fit** — plus a weighting step. Fill
cost rows from `aid/comparison.md` (award letters decoded by `financial-aid`),
outcome rows from College Scorecard, and fit rows from the family.

Ground rule: every number in the cost rows traces to a document the family can
point at — an award letter, the college's published cost of attendance, or the
Scorecard record. If a number is projected or assumed, label it as such in the
worksheet.

## Cost rows

| Row | Where it comes from | Notes |
|---|---|---|
| Sticker cost of attendance (COA), year 1 | Award letter / college cost page | Tuition + fees + housing + food + books + travel + personal. If the letter omits travel or personal costs, add realistic estimates and label them. |
| Grants + scholarships, year 1 | Award letter | Free money only. Loans and work-study are **not** aid — never let them sit in this row. |
| **Net cost, year 1** | COA − grants/scholarships | The real price. This is the number to compare, never sticker price. |
| Renewability terms | Award letter fine print / aid office | Is each grant guaranteed for 4 years? GPA floor? Credit-hour floor? Same dollar amount or same percentage? Write the answer per grant. |
| **4-year projected net cost** | Computed (method below) | The headline cost number. |
| Loans offered / planned | Award letter + family plan | Split federal vs. private/PLUS. Current federal loan limits: verify at studentaid.gov — do not assume. |
| Work-study | Award letter | Money the student must earn; count it as reduced out-of-pocket only if the student actually plans to work. |
| **Debt at graduation** | Planned loans × 4 years (adjusted) | See outcomes comparison below. |
| Out-of-pocket per year for the family | Net cost − loans − work-study | The check the family actually writes. Stress-test it against the budget in `profile.json`. |

### Projecting the 4-year net cost

1. Start from year-1 net cost.
2. Escalate COA by a stated assumption — costs typically rise 3–5% per year;
   check the college's own cost-history or cost page, and write the assumed
   rate into the worksheet.
3. Hold each grant at its documented renewal terms: flat-dollar grants lose
   ground to rising costs every year; percentage-of-tuition awards keep pace.
   A grant with a GPA condition gets a footnote: what happens to the 4-year
   number if it is lost after year 1?
4. Sum the four years. Show the arithmetic in `decisions.md`, not just the
   total.
5. Sanity-check against the college's net price calculator
   (`net_price_calculator` field from `scorecard_search`) and note any large
   gap between calculator and letter.

## Outcome rows

Pull per college with:

```
node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs scorecard_search --id <unitid> --fields core
```

| Row | Field | How to read it |
|---|---|---|
| Graduation rate | `grad_rate` | A college where most students finish is cheaper than a "cheaper" college where a fifth year (or a transfer) is common. |
| Median earnings, 10 years after entry | `median_earnings_10yr` | Institution-wide median — majors differ widely around it. Use it for scale, not destiny. |
| **Debt vs. earnings** | computed | Debt at graduation ÷ `median_earnings_10yr`. A common rule of thumb: total student debt above expected first-year earnings is a red flag; well below it is comfortable. Say which side of the line each offer lands on. |
| Program strength for the intended major | college research | Scorecard can't see this; pull from `college-research` notes and department pages. |

## Fit rows

Scored by the family, not by data. For each row the student assigns 1–5 per
college after the visits/revisits, with one sentence of justification —
the sentence matters more than the number.

- **Academics**: intended major offered and healthy; ease of switching majors;
  class sizes; access to professors; honors options.
- **People**: did the student like the students they met; social scene they
  actually want (not the one that photographs well).
- **Place**: distance from home and true door-to-door travel cost/time;
  weather; campus setting (urban/suburban/rural); housing all four years?
- **Support**: advising, career services and co-op/internship pipeline, health
  and disability services, communities the student cares about.
- **Gut**: after an admitted-student visit, where does the student picture
  themselves? Record it — it is data too.

## Weighting — how to combine the three groups

1. **Red lines first.** Before any scoring, the family states eliminating
   conditions (e.g., "total debt over $X", "no affordable path to year 4",
   "grant lost if GPA dips below 3.5 in the major"). A college that trips a
   red line is out regardless of its score — this prevents a great campus
   visit from outvoting the math.
2. Split 100 points across the three groups as the family sees it (a common
   starting split: cost 40 / outcomes 25 / fit 35 — adjust openly).
3. Score each college 1–5 per group (cost score from the 4-year number and
   debt line; outcomes from the table; fit from the averaged fit rows).
4. Weighted total = Σ (group weight × group score). Present it as a
   **conversation-starter, not a verdict**: if the family's gut disagrees with
   the arithmetic, the disagreement is the thing to talk about.
5. The 48-hour test: pick the leader, sleep on it twice, notice relief or
   dread. Then decide.

## Sample table (fictional colleges — replace with real offers)

| | College A (public, in-state) | College B (private) |
|---|---|---|
| Sticker COA, yr 1 | $28,000 | $82,000 |
| Grants/scholarships, yr 1 | $6,000 (flat, renewable ×4) | $48,000 (need-based, re-evaluated yearly) |
| Net cost, yr 1 | $22,000 | $34,000 |
| 4-yr projected net cost (4%/yr COA growth) | $93,500 | $146,800 |
| Planned loans over 4 yrs | $19,000 | $27,000 |
| Grad rate | 71% | 88% |
| Median earnings 10-yr | $58,400 | $74,100 |
| Debt vs. earnings line | comfortably under | under |
| Fit score (family, /5) | 3.4 | 4.3 |
| **Weighted total (40/25/35)** | **3.6** | **3.8** |

Numbers above are illustrative only — the format is the point.

## Red flags to name out loud

- **Front-loaded aid**: big year-1 grant, vague renewal language. Ask the aid
  office in writing what years 2–4 look like.
- **GPA-cliff scholarships**: a 3.5 renewal floor in a hard major is a
  four-year bet, not a discount. Model the worksheet both ways.
- **Loans dressed as aid**: an award letter's "total aid" line that includes
  loans and work-study. Recompute net cost with free money only.
- **The PLUS-loan gap**: a package that "meets need" with a large Parent PLUS
  loan meets nothing — that is parent debt at parent risk.
- **Fifth-year risk**: low 4-year graduation rate quietly adds ~25% to the
  projected cost. Ask about credit requirements and course availability in
  the major.

## decisions.md template

```markdown
# Decision worksheet — <cycle>

## Offers on the table
<one line per accepted college: plan, reply deadline as printed in the offer>

## Red lines
<the family's eliminating conditions, agreed before scoring>

## Comparison
<the table above, with the arithmetic for each projected number>

## Waitlists still open
<college, CDS C2 numbers from last cycle, LOCI sent (date), deposit plan>

## Appeals in flight
<college, grounds, documents sent, date, response deadline>

## The choice
<college, date deposited, deposit confirmation noted>
## Withdrawn / declined
<college — date — method (portal/email)>
```

Reply deadlines, deposit amounts, and renewal terms all come from each
college's own portal and letters — verify there; nothing in this framework
overrides an offer document.
