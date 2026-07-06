---
name: tracker
description: >
  Application status board and college tracker: show what's due, add colleges with
  auto-filled deadlines, advance application statuses, manage per-college checklists,
  export the deadline calendar. Use when the user says "status", "what's due",
  "add a college", "we submitted", "got a decision", "tracker", "application
  checklist", "deadlines", or reports any application event.
argument-hint: "[add|status|update|calendar] [college]"
---

# Tracker — the application status board

Single source of truth: `colleges.json` in the workspace. Always read the whole
file, modify, and write the whole file back (the plugin validates every write).
If no workspace exists, route to `start` first.

## Output style — quiet writes

Update workspace files quietly: gather what you need, then do a single whole-file
read-modify-write. **Never paste JSON, code blocks, raw file contents, or
field-by-field diffs into your reply** — the family should not have to read the file
format. Rendering a human-readable table or summary for them is fine; the rule is
about not exposing the raw file. Confirm what changed in one short, plain-language
sentence. (The editor's own change card may still appear — that is the app's UI,
don't narrate or add to it.)

## `status` (default) — render the board

1. Read `colleges.json`, `profile.json`, and `.admissions/config.json`.
2. Render a compact board grouped by status, sorted by deadline within groups:

   ```
   ## Applications — <today>
   | College | Plan | Deadline | Status | Missing |
   ```

   - Compute days-remaining per deadline; mark ≤14 days with a warning, overdue in bold.
   - "Missing" = unchecked checklist items + essays not `final` (from `essays/index.json`).
   - Flag `deadline_verified: false` entries: "unverified — check the college's page".
3. After the table: 1-3 line "do next" summary — the nearest hard commitment first.
4. If any college has status `decision_pending` and its typical decision window has
   arrived, mention it gently.

## `add <college>` — add to the list

1. Resolve the college:
   - Look up `data/college_index.json` (name/alias fuzzy match → `unitid`).
   - For live stats (admit rate, scores, net price):
     `node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs scorecard_search --name "<name>" --fields core`
2. Auto-fill from bundled datasets when present:
   - `data/deadlines.json` (by unitid or name): ED/ED2/EA/REA/RD dates, fee,
     rec counts, writing requirements → set `requirements` and the `deadline` for
     the chosen plan, with `deadline_verified: false` and a spoken caveat.
   - `data/test_policy.json`: set `test_policy` (required|optional|flexible|free).
   - `data/deadlines.json` `admission_type` (Common App rolling schools are
     auto-flagged from the ReqGrid) → copy onto the entry.
   - Determine `system`: UC campuses → `uc` (plan `uc_filing`, window Oct 1–Nov 30);
     CSU → `csu`; MIT/Georgetown and other non-members → `institutional`;
     otherwise `common_app`.
3. Ask which plan (ED/EA/RD…) they intend, note ED is **binding** if chosen.
4. **Set the strategic submission date, not just the deadline.** If the college is
   `rolling`/`priority` (or reviews in waves / fills competitive majors early),
   set `recommended_submit_by` to well before the deadline — the deadline becomes
   the backstop. Set `priority_date` for an earlier scholarship/honors/housing
   date. When unsure of the review timing, offer the `college-scout` agent or tell
   the family to verify on the admissions page. See `college-list`'s
   submission-timing guidance for the framework.
5. Append the entry (status `researching`), write the file, confirm what was
   auto-filled and what still needs verification.

## `update <college>` — advance status or record events

- Status flow: researching → applying → essays_in_progress → ready_to_submit →
  submitted → decision_pending → accepted | denied | waitlisted | deferred →
  enrolled | declined.
- "We submitted X" → status `submitted`, ask about fee/waiver checkbox, congratulate briefly.
- Decision events: record in `decision.result`; on `accepted`, remind about
  `aid/award-letters/` for the offer letter (→ `financial-aid`); on `deferred` or
  `waitlisted`, point to `decision-day` for the playbook.
- On any deadline-bearing change, offer to regenerate the calendar (below).

## `calendar` — export deadlines to the family's calendar

```
node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs ics_generate --workspace <ws> --out output/admit-calendar.ics
```

The .ics contains every deadline and milestone with built-in reminders (7 days and
1 day before) and imports into Google/Apple/Outlook by double-click. Re-exporting
updates events in place rather than duplicating them.

## Verification discipline

Bundled deadline data is refreshed but **never authoritative**: any deadline the
family is about to rely on (booking tests, planning ED) should be verified on the
college's admissions page. Offer a deadline audit (spawn the `deadline-auditor`
agent, then apply its patch list) when the list stabilizes or in early September.

## Cross-skill delegation

- Building/rebalancing the list with live data → `college-list`
- One-college deep dive → `college-research`
- Essay work for a college's supplements → `essay-coach`
- Aid forms and award letters → `financial-aid`
- Offer comparison after decisions → `decision-day`

## Persistence contract

Writes: `colleges.json` (read-modify-write, whole file), `output/admit-calendar.ics`
(via script). Reads: `profile.json`, `essays/index.json`, bundled `data/*.json`.
Never writes `essays/drafts/**`.
