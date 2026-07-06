---
name: scholarships
description: >
  Find and track outside scholarships: local-first search strategy, the free
  federal CareerOneStop scholarship database, a scam filter, and a tracker in
  aid/scholarships.json with essay-reuse mapping. Use when the user says
  "scholarships", "find scholarships", "free money for college", "local
  scholarships", "scholarship deadline", "we won a scholarship", "scholarship
  essay", or "is this scholarship legit".
argument-hint: "[find|add|status|update] [keyword or scholarship name]"
---

# Scholarships — find money, skip scams, reuse essays

Outside scholarships are won mostly through volume and locality, not prestige.
The order of operations below is deliberate: local lists first (low competition),
the free federal database second (breadth), open web search last (noise).

If no workspace exists, route to `start` first.

## Output style — quiet writes

Update workspace files quietly: gather what you need, then do a single whole-file
read-modify-write. **Never paste JSON, code blocks, raw file contents, or
field-by-field diffs into your reply** — the family should not have to read the file
format. Rendering a human-readable table or summary for them is fine; the rule is
about not exposing the raw file. Confirm what changed in one short, plain-language
sentence. (The editor's own change card may still appear — that is the app's UI,
don't narrate or add to it.)

## The never-pay rule (state it early, every session)

Any scholarship, matching service, or "guaranteed" search that charges an
application fee, processing fee, or unlock fee is **presumptively a scam** —
legitimate scholarships pay you, never the reverse. Same for services that
demand a credit card, bank account, or Social Security number to "check
eligibility". If the user asks about a specific offer that wants money,
say plainly that this is the signature of a scam and move on.

## `find` (default) — the three-tier search

### Tier 1 — local first (always start here)

Before any database, walk through the local checklist with the family. These
awards are smaller but dramatically less competitive, and many local deadlines
typically land in winter of senior year (background: the money reference in
the `guide` skill):

- The high school counselor's scholarship list or bulletin — ask for it by name.
- The community foundation for their city or county.
- Parents' employers, unions, and professional associations.
- Civic and service organizations the family touches (Rotary, Legion, Elks, etc.).
- Religious organizations and local credit unions.
- Local businesses that sponsor a named award at the student's school.

Capture anything promising straight into the tracker (below) with status
`interested`, even without a URL yet.

### Tier 2 — the federal database

CareerOneStop is the US Department of Labor's free scholarship finder. Read
`profile.json` first and build keywords from `interests.majors`,
`interests.special_tracks`, and `narrative.spike`; use `student.state`:

```
node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs scholarship_search --keyword "<term>" --state <XX> --max 25
```

- Run one call per distinct keyword, not one mega-query. Omit `--state` for
  national awards; run both a state-scoped and a national pass.
- `--level` defaults to `high_school`; if results are thin, retry with
  `--level bachelors` (awards for entering undergrads).
- Results come back as `{total, query, results: [{name, organization, purpose,
  award_type, amount, deadline, level_of_study, url}]}` sorted by deadline.
  Present a shortlist (name, org, amount, deadline, url); skip anything already
  past deadline. Every deadline gets the caveat: verify on the sponsor's page.
- On a `needs_key` error, **relay the message's signup guidance verbatim** —
  credentials are free (`data/sources.json` →
  `federal.careeronestop_registration`) — then fall back to Tier 3. Also offer
  the no-key manual route: the finder's public web UI at
  careeronestop.org/Toolkit/Training/find-scholarships.aspx.
- On `auth_failed` or `http_*`, say the service errored and fall back to Tier 3.
- For a batch pass across several keywords, dispatch the `scholarship-scout`
  agent instead of running the calls inline: pass state, level, the interest
  keywords, and the path to `aid/scholarships.json` (for dedupe). It returns a
  ranked JSON shortlist; apply the never-pay filter and the verify-on-sponsor-page
  caveat before showing or recording anything from it.

### Tier 3 — guided WebSearch (fallback only)

Search patterns: `"<county> community foundation scholarship"`,
`"<state> scholarship class of <grad year>"`, `"<major/interest> scholarship
high school senior"`. Apply quality filters before showing anything:

- Prefer the sponsoring organization's own site (.org, .gov, .edu, a named
  company or foundation) over aggregators.
- Reject anything charging a fee (never-pay rule) or whose primary product is
  harvesting the student's personal data to resell.
- Confirm amount and deadline on the sponsor's page before recording them —
  never carry numbers from an aggregator listing or from memory.

## `add` / `status` / `update` — the tracker

Single source of truth: `aid/scholarships.json`. Read the whole file, modify,
write the whole file back. If it does not exist, create it exactly as:

```json
{
  "schema_version": 1,
  "scholarships": [
    {
      "name": "", "org": "", "amount": null, "deadline": null,
      "status": "interested", "url": null, "essay_reuse": null
    }
  ]
}
```

- `status` flow: `interested` → `applying` → `submitted` → `won` | `declined`.
- `status` view: table sorted by deadline (name, org, amount, deadline, status,
  essay reuse), warn on deadlines within 14 days, bold overdue.
- On `won`: congratulate briefly, then two reminders — (1) the student must
  report outside awards to every college they enroll at or applied to for aid;
  (2) ask each aid office how outside scholarships are treated (displacement:
  loans/work-study reduced first is good, grants reduced first is not) →
  hand off to `financial-aid`.
- Record `amount` and `deadline` only as verified on the sponsor's page; leave
  `null` rather than guess.

## Essay reuse mapping

When a tracked scholarship has an essay prompt, read `essays/index.json` and
look for an existing essay whose theme and word limit are close (personal
statement, community essay, challenge essay). Record the match in that
scholarship's `essay_reuse` field as the essay's `file` path plus a one-line
adaptation note (e.g. `"drafts/common-app-v1.md — retarget closing to service
theme, cut to 500 words"`). No match → `essay_reuse: null` and suggest a
brainstorm session.

The ethics floor applies to scholarship essays exactly as to application
essays: the student adapts their own draft; route all critique and
brainstorming to `essay-coach`. Never write, outline, or rewrite scholarship
essay text.

## Cross-skill delegation

- FAFSA/CSS Profile, award letters, displacement questions → `financial-aid`
- Adapting an essay for a scholarship prompt → `essay-coach`
- How aid and net price work (background for the family) → `guide`
- College application deadlines and statuses → `tracker`
- Adding scholarship checkpoints to the weekly ritual → `checkin`

## Persistence contract

Writes: `aid/scholarships.json` (read-modify-write, whole file; create with the
shape above if missing). Reads: `profile.json`, `essays/index.json`,
`data/sources.json`. Runs `scholarship_search` via `run.mjs` (network, cached).
Never writes `essays/drafts/**`.
