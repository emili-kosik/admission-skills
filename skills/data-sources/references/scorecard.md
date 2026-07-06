# College Scorecard API — full reference

The US Department of Education's institution-level dataset, queried through
`scorecard_search`. Everything here describes what the script actually sends
and returns; the upstream API documentation is at
`sources.json → federal.scorecard_api_docs`
(https://collegescorecard.ed.gov/data/api-documentation/).

## Endpoint and invocation

- Base URL: `https://api.data.gov/ed/collegescorecard/v1/schools`
- Always via the shim:

  ```
  node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs scorecard_search --name "Stanford"
  node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs scorecard_search \
      --state MA,CT --admit-rate 0.3..0.6 --size 2000..15000 \
      --sort admission_rate --per-page 50
  node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs scorecard_search --id 166027 --fields full
  ```

## Key resolution chain

First hit wins:

1. `CLAUDE_PLUGIN_OPTION_SCORECARD_API_KEY` (plugin userConfig, keychain-backed)
2. env `SCORECARD_API_KEY` (power users, CI)
3. workspace `.admissions/config.json` → `keys.scorecard_api_key` (plaintext fallback)
4. `DEMO_KEY` — built-in default, **30 requests/hour and 50/day per IP**

The output document includes `"demo_key": true|false`. When it's `true` and
the session involves more than a handful of queries (list-building, comparing
many colleges), proactively suggest the free instant key at
https://api.data.gov/signup before the limit bites. On HTTP 429 under
DEMO_KEY, the script's error message already contains that guidance — relay it
verbatim. Cached results keep working during a rate-limit window.

## Flag → API parameter map

| Script flag | API parameter | Notes |
|---|---|---|
| `--name "<str>"` | `school.name=<str>` | substring match on the name |
| `--id <n>` | `id=<n>` | exact unitid lookup |
| `--state MA,CT` | `school.state=MA,CT` | comma = OR list |
| `--admit-rate 0.3..0.6` | `latest.admissions.admission_rate.overall__range=0.3..0.6` | fractions, not percents |
| `--size 2000..15000` | `latest.student.size__range=2000..15000` | |
| `--sat-math-75 700..` | `latest.admissions.sat_scores.75th_percentile.math__range=700..` | open-ended ranges allowed |
| `--sort <alias>[:desc]` | `sort=<field>[:desc]` | aliases below |
| `--per-page` / `--page` | `per_page` / `page` | page is 0-based; per-page default 50 |
| `--fields core\|full` | `fields=<core bundle>` or omitted | `full` = raw rows, no field limit |
| `--no-cache` | — | bypass the workspace cache |

Sort aliases: `admission_rate`, `size`, `earnings`, `net_price_public`,
`net_price_private`, `name` — each optionally suffixed `:desc`.

### API operator rules (for reasoning about queries)

- **Exact match**: `field=value`.
- **Comma-OR**: `field=a,b,c` matches any of the values (used by `--state`).
- **Range**: `field__range=min..max`; either end may be omitted (`700..`,
  `..0.3`). Admission rates are fractions (0.35, not 35).
- **Sort**: `sort=field` ascending, `sort=field:desc` descending.

### Default scope filter

When neither `--id` nor `--name` is given, the script adds
`school.degrees_awarded.predominant=3` — bachelor's-predominant institutions —
so broad filter searches return four-year colleges, not the whole IPEDS
universe. Name and id lookups are unfiltered.

## The core field bundle

`--fields core` (the default) requests exactly these Scorecard fields and
flattens them into the normalized record below:

| Normalized key | Scorecard field(s) |
|---|---|
| `unitid` | `id` (IPEDS UNITID — joins to Urban Institute and `college_index.json`) |
| `name`, `state`, `city`, `url` | `school.name/state/city/school_url` |
| `net_price_calculator` | `school.price_calculator_url` |
| `ownership` | `school.ownership` → `public` (1) / `private_nonprofit` (2) / `private_forprofit` (3) |
| `size` | `latest.student.size` |
| `admit_rate` | `latest.admissions.admission_rate.overall` (fraction) |
| `sat.ebrw_25/ebrw_75/math_25/math_75` | `latest.admissions.sat_scores.{25th,75th}_percentile.{critical_reading,math}` |
| `act.comp_25/comp_75` | `latest.admissions.act_scores.{25th,75th}_percentile.cumulative` |
| `avg_net_price` | `latest.cost.avg_net_price.public` or `.private` (whichever is set) |
| `net_price_by_income["48001-75000"/"75001-110000"]` | `latest.cost.net_price.{public,private}.by_income_level.*` |
| `tuition.in_state/out_of_state` | `latest.cost.tuition.*` |
| `grad_rate` | `latest.completion.consumer_rate` |
| `median_earnings_10yr` | `latest.earnings.10_yrs_after_entry.median` |

Any field can be `null` — test-blind and nonreporting colleges have null score
ranges; open-admission colleges have null admit rates. Say "not reported"
rather than treating null as zero.

Output envelope: `{"total", "page", "per_page", "demo_key", "results": [...]}`.
`total` counts all matches, not just the returned page.

## Caching behavior

- Responses cache under `<workspace>/.admissions/cache/scorecard/<sha256>.json`
  keyed by the canonical URL (sorted query string), **TTL 7 days**.
- Cache hits cost no rate-limit budget and work offline.
- `--no-cache` forces a live fetch (still writes the fresh copy back).

## Data vintage

`latest.*` means the newest reporting year the Department has published —
typically one to two years behind the current admissions cycle. Always state
the vintage in user-facing numbers ("Scorecard's latest reported cycle") and
never present `admit_rate` as this year's rate. Deadlines and test policies
are **not** in Scorecard at all — those come from `data/deadlines.json`,
`data/test_policy.json`, or the college's own pages.

## Errors

| Condition | Error code | What to do |
|---|---|---|
| 429 on DEMO_KEY | `http_429` | relay the built-in message (signup link + wait-an-hour option); cached queries still work |
| 403 | `http_403` | key rejected — check the `scorecard_api_key` plugin setting |
| other | `http_<status>` | show the message; retry once after a moment if transient |
