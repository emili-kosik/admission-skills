# Data sources

Every fact the plugin asserts traces to one of these. Live APIs are queried
at use time; bundled datasets are rebuilt from primary sources by maintainer
tools and carry `_meta.last_verified`.

## Live APIs (queried by scripts at use time)

| Source | What | Key | Limits | Client |
|---|---|---|---|---|
| [College Scorecard](https://collegescorecard.ed.gov/data/api-documentation/) (US Dept. of Education) | admit rates, SAT/ACT percentiles, net price by income, completion, earnings | free instant key ([api.data.gov/signup](https://api.data.gov/signup)); `DEMO_KEY` fallback | 1,000/h with key; 30/h + 50/day/IP on DEMO_KEY | `scripts/scorecard_search.py` |
| [Urban Institute Education Data](https://educationdata.urban.org/documentation/colleges.html) (IPEDS mirror) | applicants/admits/enrolled, admissions requirements, directory | none | none published; be polite | `scripts/urban_lookup.py` |
| [CareerOneStop](https://www.careeronestop.org/Developers/WebAPI/registration.aspx) (US Dept. of Labor) | 9,500+ scholarships | free registration (User ID + token) | per their terms | `scripts/scholarship_search.py` |

`unitid` (IPEDS) = College Scorecard `id` — the join key everywhere.

## Bundled datasets (`data/*.json`)

| File | Primary source | Rebuild tool | Cadence |
|---|---|---|---|
| `deadlines.json` | [Common App Requirements Grid PDF](https://content.commonapp.org/Files/ReqGrid.pdf) + hand-verified overrides for non-members | `tools/build_reqgrid.py` | each Aug 1 + mid-cycle re-issues |
| `test_policy.json` | ReqGrid testing column + per-institution admissions pages (cited per override) | `tools/build_test_policy.py` | Aug 1; 6-month staleness rule on "required" claims |
| `test_dates.json` | [SAT dates](https://satsuite.collegeboard.org/sat/dates-deadlines), [ACT dates](https://www.act.org/content/act/en/products-and-services/the-act/registration.html), PSAT/AP pages | verified fetch (see MAINTAINERS) | annually |
| `essay_prompts.json` | [Common App prompts](https://www.commonapp.org/apply/essay-prompts), [UC PIQs](https://admission.universityofcalifornia.edu/how-to-apply/applying-as-a-freshman/personal-insight-questions.html) | verified fetch, verbatim | when announced (typically late Feb) |
| `ai_policies.json` | commonapp.org fraud policy + institution AI-policy pages, quoted verbatim with citation URLs | verified fetch | annually + on policy news |
| `milestones.json` | rule synthesis: commonapp.org, studentaid.gov, cssprofile.collegeboard.org, UC, travel.state.gov, BigFuture conventions | hand-maintained | annually reviewed |
| `systems.json` | application-system portals' own pages | hand-maintained | annually |
| `college_index.json` | Urban Institute IPEDS directory | `tools/build_college_index.py` | annually (new IPEDS year) |
| `sources.json` | — (it *is* the URL registry) | hand-maintained | rolling |

## Fetched live per college, never bundled

- **Common Data Set** (C7 admission-factor weights, C9 score-submission
  rates): WebSearch `"<college> common data set 2025-2026"` → the college's
  own .edu PDF/Excel. Used at list-finalization and submit-or-withhold
  decisions only.
- **State FAFSA deadlines**: always the live
  [studentaid.gov deadlines page](https://studentaid.gov/apply-for-aid/fafsa/fafsa-deadlines).
- **Net price for a specific family**: each college's own Net Price
  Calculator (linked in Scorecard results).
- **Visa interview wait times**: travel.state.gov, live only.

## The staleness discipline

If a dataset's `_meta.cycle` is behind the workspace cycle, or
`last_verified` is older than 12 months (6 for test policies), skills must
say so, downgrade assertions to "as of <date>", and point at
`/admit:refresh-data`. The SessionStart digest surfaces this automatically.
