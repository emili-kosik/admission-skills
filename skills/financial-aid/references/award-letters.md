# Award letters — decoding offers and comparing them honestly

Award letters are deliberately hard to compare: no standard format, loans
styled to look like grants, year-1 numbers standing in for four years. This
file is the decoder. The goal is one table in `aid/comparison.md` that a
family can read in two minutes.

## Intake flow

1. Family drops each offer PDF into `aid/award-letters/` (most sensitive files
   in the workspace — they never need to leave the machine).
2. Spawn the `aid-analyzer` agent with the file paths. It returns one
   normalized record per letter; **you** write the workspace files, and you
   recompute its arithmetic — extraction from PDFs is error-prone, and the
   stakes are a four-year financial commitment.
3. If a letter omits cost of attendance, pull the college's published COA from
   its aid page (or its Net Price Calculator page) and mark it "COA from
   website, not letter".

## The decoder checklist — run it line by line on every letter

**Cost of attendance (COA) — is it complete?**
Tuition, fees, housing, food, books, travel, personal expenses. Letters that
show only tuition+fees make their aid look bigger. Normalize every offer to
full COA before comparing anything.

**Gift aid — the only real discount.**
Grants and scholarships: money that is never repaid. For each one ask:
- Renewable for four years, or freshman-only (**front-loading**)?
- Conditions? (GPA floor, specific major, enrollment level)
- Outside scholarships: does the college reduce its own grant when outside
  money arrives ("scholarship displacement")? Ask the aid office.

**Loans are not aid.**
They appear in the "award" but they are the family's own future money:
- *Direct Subsidized* (no interest while enrolled) vs. *Unsubsidized* (interest
  from day one) — student loans in the student's name, capped by federal
  limits.
- **Parent PLUS loans listed as an award are the biggest trap**: some letters
  "meet need" by including a five-figure parent loan at full cost. It is not a
  discount; it is a suggestion that the parents borrow the gap.
- Never subtract loans when computing what a college *costs*.

**Work-study is earned, not granted.**
It is a permission to earn wages during the year — it never pays the fall
bill, and the student may or may not find the hours. Count it as $0 in the
cost comparison; mention it as a nice-to-have.

**The two numbers that decide.**
- **Net price** = COA − gift aid. The true annual cost of attending.
- **Out-of-pocket now** = net price − loans/work-study accepted. Useful for
  cash-flow planning only — the loans still cost money later.

**Unmet need (the gap).**
Need = COA − SAI. If gift aid + student loans + work-study still leave a gap,
the college is "gapping" the family — the gap lands on parents as cash or
PLUS borrowing. Name it explicitly in the table.

**Four-year cost, not year-1.**
`4 × net price` is the floor. Adjust for: front-loaded grants (re-ask net
price for year 2), renewal conditions the student might miss, and tuition
increases (published prices typically rise a few percent a year — check the
college's own recent history rather than assuming). A $3k/year cheaper offer
that front-loads is often the more expensive college.

## The comparison table (`aid/comparison.md`)

| | College A | College B | College C |
|---|---|---|---|
| Cost of attendance | | | |
| Gift aid (grants + scholarships) | | | |
| — renewable? conditions? | | | |
| **Net price (COA − gift)** | | | |
| Student loans offered | | | |
| Work-study | | | |
| Parent loan (PLUS) implied | | | |
| Unmet need / gap | | | |
| **Estimated 4-year net cost** | | | |
| vs. family budget (`profile.json`) | | | |

Below the table, write 2–3 calm sentences: which offer is actually cheapest
over four years, what assumption that rests on, and what to verify with each
aid office before May 1.

## Appeals and reconsideration — they exist, and asking is normal

Aid offices expect these conversations every spring. Two distinct doors:

- **Professional judgment (need-based appeal)**: circumstances the forms
  missed or that changed — job loss, medical bills, a death, currency
  collapse, one-time income spike in the tax year used. Available essentially
  everywhere, including for internationals at colleges that gave aid.
- **Reconsideration with a competing offer**: some colleges — typically
  well-endowed privates — will revisit a package when shown a better offer
  from a peer college; public universities typically have no room. The
  college's own aid page often says which word it prefers ("appeal",
  "reconsideration", "review").

How to ask, in the family's voice:
1. Call or email the aid office and ask for their process — many have a form.
2. Be specific and documented: "Our 2025 return shows $X, but the employer
   closed in January; current income is $Y (letter attached)" beats any plea.
3. Attach the competing letter if that's the basis; peer-college offers carry
   the most weight.
4. Be polite, be brief, state what number would make attendance possible.
   This is a request, not a negotiation-show; the reader is a professional
   who does this all day.
5. Mind the calendar: start well before **May 1**, and if a decision is close,
   ask the admissions office for a short deposit-deadline extension —
   colleges grant these more often than families expect.

Never double-deposit at two colleges to buy time; it violates the deposit
agreement and can void both offers. For the final choice itself — waitlists,
tie-breaks, the May 1 mechanics — route to `decision-day`.
