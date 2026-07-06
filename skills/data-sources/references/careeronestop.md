# CareerOneStop Scholarship Finder — reference

The US Department of Labor's scholarship database (9,500+ awards per the
plugin's script), queried through `scholarship_search`. API explorer:
`sources.json → federal.careeronestop_api`.

## Credentials — free signup, no demo tier

Unlike Scorecard, **there is no DEMO_KEY equivalent**. Two credentials are
required, both issued together by the free registration at
`sources.json → federal.careeronestop_registration`
(https://www.careeronestop.org/Developers/WebAPI/registration.aspx):

- `careeronestop_user_id` — becomes part of the request path
- `careeronestop_token` — sent as `Authorization: Bearer <token>`

Resolution chain per credential (first hit wins):
`CLAUDE_PLUGIN_OPTION_CAREERONESTOP_USER_ID` / `..._TOKEN` → env
`CAREERONESTOP_USER_ID` / `CAREERONESTOP_TOKEN` → workspace
`.admissions/config.json` → `keys.careeronestop_user_id` /
`keys.careeronestop_token`.

## The `needs_key` degradation path

Without both credentials the script exits nonzero with:

```json
{"error": {"code": "needs_key", "message": "...signup link + setup steps..."}}
```

Handle it in this order:

1. **Relay the message verbatim** — it contains the signup URL and the exact
   plugin-setting names. Signup is free; the user can do it in minutes.
2. **Do not block on the key.** Fall back to guided WebSearch for scholarships
   matching the student's profile, preferring primary sources: the awarding
   organization's own site, plus the aggregators in `data/sources.json` if
   listed. Label web-found deadlines and amounts as unverified.
3. Offer to retry the script once credentials are configured.

`auth_failed` (HTTP 401/403 after keys are set) means the credentials are
wrong or expired — point the user back at the plugin settings, don't retry in
a loop.

## Invocation and parameters

```
node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs scholarship_search --keyword robotics --state NJ --max 25
```

| Flag | API effect | Notes |
|---|---|---|
| `--keyword` | free-text keyword filter | interests, field of study, identity terms |
| `--state NJ` | location filter | two-letter code; omit for national awards |
| `--level` | study-level filter | `high_school` (default), `bachelors`, `graduate`, `vocational` |
| `--max` | result count | default 25 |
| `--no-cache` | bypass cache | |

Results come back **sorted by deadline, soonest first** — the top of the list
is the most time-sensitive.

## Result shape

Each result is normalized to:

```json
{
  "name": ..., "organization": ..., "purpose": ...,
  "award_type": ..., "amount": ..., "deadline": ...,
  "level_of_study": ..., "url": ...
}
```

Envelope: `{"total", "query": {...}, "results": [...]}`. Fields can be null;
`purpose` is truncated to 400 characters.

## Caching and freshness

Cache TTL is **3 days** (not the default 7) because scholarship deadlines
churn — under `<workspace>/.admissions/cache/careeronestop/`. Even so, treat
every deadline and amount as the database's claim, not ground truth: before a
student invests hours in an application, verify on the award's own page (the
`url` field) that the program is still running and the deadline holds.
Aggregator databases typically carry some stale listings.
