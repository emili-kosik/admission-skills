---
name: data-sources
description: >
  Shared knowledge base for the plugin's live data sources: College Scorecard,
  Urban Institute Education Data (IPEDS), CareerOneStop scholarships, and the
  Common Data Set live-fetch protocol — base URLs, API key chains, rate limits,
  filter operators, field bundles, caching, and staleness discipline. Use when
  a skill needs query parameters or key setup for scorecard_search,
  urban_lookup, or scholarship_search, when a live query fails (429, needs_key,
  no_data) and you need degradation guidance, or when the user asks "where does
  this data come from", "API key", "rate limit", "DEMO_KEY", "common data set",
  or "CDS".
user-invocable: false
---

# Data sources — the API knowledge base

This is a **read-only reference skill**. Other skills defer here for how the
plugin's live data sources work; it runs no workflow of its own. Two ground
rules travel with every fact below:

- Facts come from these sources or `data/sources.json` — never from memory.
- Every number shown to a family carries its vintage ("as of the 2023 IPEDS
  cycle") and, for anything decision-bearing, a "verify on the college's
  official page" caveat.

## The four sources at a glance

| Source | Script | Key needed | Cache TTL | Use for |
|---|---|---|---|---|
| College Scorecard (US Dept. of Ed) | `scorecard_search` | free key or DEMO_KEY | 7 days | admit rates, scores, size, net price, earnings |
| Urban Institute Education Data (IPEDS mirror) | `urban_lookup` | none | 7 days | applicants/admits counts, admission requirements, directory |
| CareerOneStop (US Dept. of Labor) | `scholarship_search` | free signup, no demo tier | 3 days | scholarship search |
| Common Data Set (per-college PDFs) | none — WebSearch | none | n/a | factor weights (C7), score submission (C9), ED/EA deadlines (C21/C22) |

All scripts run only via `node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs <script> [args]`,
print one JSON document, and on failure print `{"error": {"code", "message"}}`
with nonzero exit. `needs_key` and DEMO_KEY-429 errors include signup guidance
written to be relayed to the user verbatim — relay it, don't paraphrase.

## College Scorecard

Base URL: `https://api.data.gov/ed/collegescorecard/v1/schools`
(docs: `sources.json → federal.scorecard_api_docs`).

- **Key chain** (first hit wins): `CLAUDE_PLUGIN_OPTION_SCORECARD_API_KEY` →
  env `SCORECARD_API_KEY` → workspace `.admissions/config.json` `keys.scorecard_api_key`
  → built-in `DEMO_KEY` (**30 requests/hour, 50/day per IP**). A free key is
  instant at `https://api.data.gov/signup` — suggest it before any bulk work.
  Output includes `"demo_key": true` when running on the demo tier.
- **Operators**: exact match (`school.name=...`), comma-OR
  (`school.state=MA,CT`), numeric `__range` as `min..max` with open ends
  (`0.3..0.6`, `700..`), `sort=<field>[:desc]`.
- **Core field bundle** (`--fields core`, the default): identity, ownership,
  size, admit rate, SAT/ACT 25th–75th percentiles, net price (average and by
  income bracket), tuition, grad rate, median 10-year earnings — returned
  pre-flattened. `--fields full` returns raw Scorecard rows.
- The record `unitid` equals the Scorecard `id` — the join key for everything.

Read `references/scorecard.md` before composing non-trivial queries — it has
the flag-to-parameter map, the full field list, the normalized record shape,
caching details, and error handling.

## Urban Institute Education Data

Base: `https://educationdata.urban.org/api/v1/college-university/ipeds`.
**No key, no rate-limit ceremony.** `unitid` is the same IPEDS UNITID the
Scorecard uses as `id`, so results join across both APIs and
`data/college_index.json`.

Three endpoints (`--endpoint`): `admissions-enrollment` (applicants, admits,
enrolled), `admissions-requirements` (which factors are required/considered
per the IPEDS ADM survey), `directory` (identity/location/control). Default
`--year latest` probes back from two years ago until it finds data — IPEDS
publishes on a lag. Read `references/urban-institute.md` for details.

## CareerOneStop scholarships

`scholarship_search` queries the Dept. of Labor Scholarship Finder. **There is
no demo tier**: it needs `careeronestop_user_id` + `careeronestop_token` from
the free signup at `sources.json → federal.careeronestop_registration`.
Without them the script exits with a structured `needs_key` error — relay its
message (it contains the signup link), then **degrade gracefully**: offer
guided WebSearch against named scholarship sites instead of blocking the user
on a key. Read `references/careeronestop.md` for parameters and result shape.

## Common Data Set (live fetch)

The CDS is the standardized disclosure most colleges publish yearly — the
primary source for how a specific college weighs factors. There is no API;
fetch it live:

1. WebSearch `"<college name>" common data set 2025-2026` (substitute the most
   recent completed cycle).
2. Prefer a **.edu-hosted PDF** (usually the institutional research office).
   Fallback index: `sources.json → cds.link_index`.
3. Read the three sections that matter: **C7** (factor importance grid),
   **C9** (percent submitting SAT/ACT + score percentiles), **C21/C22**
   (ED/EA deadlines and notification dates). Match by heading text — section
   numbering typically holds but can shift between cycles
   (`sources.json → cds.definitions` has the canonical definitions).
4. Cite the college, cycle year, and URL with every fact taken from it.

Read `references/common-data-set.md` for the full protocol and how to read
each section.

## Staleness and verification discipline

- Bundled `data/*.json` files carry `_meta.cycle` and `_meta.last_verified`.
  If the cycle is behind the workspace cycle, or `last_verified` is >12 months
  old (>6 for test policies): say so, phrase facts as "as of <date>", and
  suggest `/admit:refresh-data`.
- Live API data has its own lag: Scorecard `latest.*` and Urban IPEDS figures
  typically trail the current cycle by one to two years — state the data year,
  never present it as this year's class.
- Cached responses live under `<workspace>/.admissions/cache/<source>/` with
  the TTLs above; pass `--no-cache` when the user needs a fresh pull.
- Deadlines from any source here are **never authoritative** — the college's
  own admissions page is. Say so whenever a family is about to act on one.

## Cross-skill delegation

This skill is knowledge other skills consume; it delegates workflows outward:

- Building or rebalancing a list with Scorecard/Urban queries → `college-list`
- One-college deep dive (including the CDS fetch itself) → `college-research`
- Scholarship searches and the needs_key fallback flow → `scholarships`
- Net-price and aid interpretation of Scorecard cost fields → `financial-aid`
- Test-policy questions raised by C9/CDS findings → `testing-plan`
- Refreshing the bundled datasets themselves → `refresh-data`

## Persistence contract

**Read-only skill.** Writes: none. Reads: `data/sources.json` and other
bundled `data/*.json` `_meta` blocks for staleness checks. The scripts it
documents write only to the workspace HTTP cache
(`.admissions/cache/<source>/`) as a side effect of queries. Never writes
`essays/drafts/**`.
