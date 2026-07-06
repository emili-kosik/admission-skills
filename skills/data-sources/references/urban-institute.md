# Urban Institute Education Data API — reference

The Urban Institute mirrors the federal IPEDS surveys behind a clean REST API.
It fills the gaps Scorecard leaves: raw applicant/admit counts and the IPEDS
admission-requirements survey. Upstream documentation:
`sources.json → federal.urban_education_data_api`
(https://educationdata.urban.org/api/v1/).

## Endpoint and invocation

- Base: `https://educationdata.urban.org/api/v1/college-university/ipeds`
- URL shape: `<base>/<endpoint>/<year>/?unitid=<n>`
- **No API key.** Nothing to configure, no rate-limit chain to explain.

```
node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs urban_lookup --unitid 166027 --endpoint admissions-enrollment
node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs urban_lookup --unitid 243744 --endpoint admissions-requirements --year 2022
```

## The join key

`unitid` here **is** the College Scorecard `id` and the `unitid` in
`data/college_index.json` — all three are the IPEDS UNITID. Resolve a college
once (index fuzzy match or `scorecard_search --name`), then reuse the unitid
across both APIs.

## The three endpoints

| `--endpoint` | IPEDS source | What you get |
|---|---|---|
| `admissions-enrollment` (default) | ADM survey | applicant, admit, and enrolled counts — compute the real admit rate (`admits / applicants`) and yield (`enrolled / admits`) yourself |
| `admissions-requirements` | ADM survey | which admission factors the college requires/recommends/considers, and its test-score stance, as self-reported to IPEDS |
| `directory` | directory file | institutional identity: name, location, control/sector metadata |

Field names inside `results` are IPEDS variable names; when a coded value is
ambiguous, check the Urban Institute documentation page for that endpoint
rather than guessing the code table.

## Year handling

- `--year latest` (default): probes from **two years before today's date**
  backward, four years, and returns the first year with data. IPEDS publishes
  on roughly a two-year lag, so this finds the newest available survey.
- `--year <yyyy>`: exact survey year, no probing.
- Whichever year is returned appears in the output envelope — **quote it**
  ("per the <year> IPEDS survey") so families don't mistake it for the current
  cycle.

Output envelope: `{"year", "endpoint", "results": [...]}`.

## Caching and errors

- Responses cache under `<workspace>/.admissions/cache/urban/` (7-day TTL,
  canonical-URL key), same mechanism as Scorecard.
- On failure the script returns `{"error": {"code": "no_data", "message": ...}}`
  — either the API errored for every probed year or the unitid has no rows.
  Verify the unitid against `data/college_index.json` before concluding the
  college is missing; very new or merged institutions genuinely lack rows.

## When to prefer Urban over Scorecard

- You need **counts** (applicants, admits) rather than the pre-computed rate —
  e.g. to show class-size context or compute yield.
- You need the college's self-reported **admission requirements** stance from
  a federal survey rather than a marketing page.
- You're already rate-limited on DEMO_KEY: Urban has no key and no demo tier
  to exhaust.

For anything cost- or outcome-related (net price, earnings, graduation rate),
stay with Scorecard — Urban's IPEDS mirror is admissions/directory data here.
