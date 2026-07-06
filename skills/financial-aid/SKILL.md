---
name: financial-aid
description: >
  Financial aid navigator: FAFSA and CSS Profile filing, net-price reality checks
  by income bracket, award-letter decoding with side-by-side offer comparison, aid
  appeals, and aid rules for international families. Use when the user says
  "FAFSA", "CSS Profile", "financial aid", "net price", "can we afford it",
  "how much will it actually cost", "SAI", "EFC", "award letter", "compare
  offers", "aid appeal", "IDOC", or drops an award letter into the workspace.
argument-hint: "[fafsa|css|net-price|awards|appeal]"
---

# Financial aid — the real price, the forms, the offers

Money questions decide more college outcomes than essays do. Lead with the four
sentences below, then go deep via `references/`. Never state a fee, threshold,
or state deadline from memory — cite `data/sources.json` URLs and say "verify".

## Output style — quiet writes

Update workspace files quietly: gather what you need, then do a single whole-file
read-modify-write. **Never paste JSON, code blocks, raw file contents, or
field-by-field diffs into your reply** — the family should not have to read the file
format. Rendering a human-readable table or summary for them is fine; the rule is
about not exposing the raw file. Confirm what changed in one short, plain-language
sentence. (The editor's own change card may still appear — that is the app's UI,
don't narrate or add to it.)

## The four sentences every family needs

1. **Sticker price is fiction.** The number that matters is *net price for your
   income bracket* — what families like yours actually paid after grants. A
   $65k private college is often cheaper than a $30k public one.
2. **FAFSA opens October 1 of senior year, and everyone files** — it is the key
   to federal grants, loans, and work-study, and many colleges and states won't
   release even *merit* money without it. File in the first weeks: some state
   money is first-come, first-served.
3. **Many private colleges also require the CSS Profile** (opens Oct 1) for
   their own institutional aid — with fee waivers below an income threshold.
   Skipping it forfeits the largest grants a private college can give.
4. **In April, compare offers — not prestige.** The decision is made on a
   line-by-line comparison table, not the brochure. Loans are not aid.

## Net-price reality check (any time, ideally junior spring)

1. Read `profile.json` → `finances` (`income_bracket`, `budget_per_year_usd`,
   `need_based_aid`) and `colleges.json`. If finances are empty, ask for a
   rough household income bracket first — nothing works without it.
2. For each college in question:

   ```
   node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs scorecard_search --name "<college>" --fields core
   ```

   Each result carries `net_price_by_income` (average net price for the
   $48–75k and $75–110k brackets), `avg_net_price`, `tuition`, and
   `net_price_calculator` — that college's own calculator URL. For all five
   income brackets, rerun with `--fields full`. Relay any `needs_key` or
   DEMO_KEY rate-limit guidance the script prints.
3. Present a small table: college | sticker | net price for their bracket |
   family budget | gap. Label Scorecard figures as **averages for past
   freshmen** — the personal number comes from each college's Net Price
   Calculator (federal law requires every college to post one; index at
   https://collegecost.ed.gov/net-price). Link the `net_price_calculator` URL
   and suggest running it for the top three candidates.
4. If the gap is structural across the list, route to `college-list` to add
   generous-aid or lower-net-price options while there is still time.

## The forms — route by situation

| Situation | Read first |
|---|---|
| Filing the FAFSA: FSA IDs, contributors, SAI, deadlines | `references/fafsa.md` |
| CSS Profile: who requires it, fee waivers, IDOC | `references/css-profile.md` |
| Student is not a US citizen or permanent resident | `references/international-aid.md` |
| An award letter arrived / comparing offers / appealing | `references/award-letters.md` |

Answer the family's question from the reference, not from memory. For "when is
our state's FAFSA deadline?" the answer is **always** the live page at
https://studentaid.gov/apply-for-aid/fafsa/fafsa-deadlines — open it or link
it; never quote a state date from memory or from this repo.

## Award letters (typically March–April)

1. Tell the family to drop each offer PDF into `aid/award-letters/` — these are
   the most sensitive files in the workspace; they stay local.
2. Spawn the `aid-analyzer` agent with the file paths. It returns one
   normalized record per letter (cost of attendance, gift aid, loans,
   work-study, net price, conditions) — the agent returns data; you write the
   files.
3. Merge the records into a comparison table and write it to
   `aid/comparison.md`. Use the table format and decoder checklist in
   `references/award-letters.md`; recompute the agent's arithmetic yourself.
4. Walk the family through it: gift aid vs. loans, 4-year cost not year-1,
   renewal conditions, unmet need — and whether an appeal is worth writing
   (`references/award-letters.md` has the how).

## Timing beats

- **Junior spring**: net-price checks + the budget conversation, before the
  list is final.
- **October 1, senior year**: FAFSA and CSS Profile open. FSA IDs a week
  earlier. Aid milestones are already in `.admissions/milestones.json`
  (rebuild via `timeline_build` if the family's aid track changed).
- **Per college**: aid *priority* deadlines often track the application round
  (typically Nov for ED/EA, Jan–Feb for RD) — verify on each college's aid
  page; the tracker's checklist should carry them.
- **April**: compare offers; reply by the national May 1 deposit date.

## Cross-skill delegation

- Outside/merit scholarships beyond college aid offers → `scholarships`
- Choosing among offers, waitlist math, the May 1 decision → `decision-day`
- I-20 funding documents, visa mechanics → `international`
- Recording aid deadlines per college, status board → `tracker`
- Budget conversation framing for parents → `parent-guide`
- Rebalancing the list for affordability → `college-list`

## Persistence contract

Writes: `aid/comparison.md`, other notes under `aid/` (never
`aid/award-letters/` — the family drops files there), and `profile.json`
`finances` fields (read-modify-write, whole file). Reads: `profile.json`,
`colleges.json`, `aid/award-letters/*`, `.admissions/config.json`,
`data/sources.json`. Never writes `essays/drafts/**`.
