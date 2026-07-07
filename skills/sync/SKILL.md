---
name: sync
description: >
  Integrations hub: export the deadline calendar as an .ics file with built-in
  reminders (always available), and — when the matching connector tools are
  present in the session — scan Gmail for admissions email and propose tracker
  updates, write deadline events straight to Google Calendar, mirror the
  college tracker to a Notion database, or read a link-shared Google Docs
  essay draft for critique. Use when the user says "sync", "export the
  calendar", "add deadlines to my calendar", "import to Google Calendar",
  "check my email", "scan my inbox", "any admissions emails?", "connect
  Notion", "mirror to Notion", "read my Google Doc", "connect myhstimeline",
  "sync my high school timeline", "pull my timeline", "update my timeline",
  "я сделал выбор в таймлайне", "обнови мой таймлайн", or asks about connecting
  Gmail, Google Calendar, Notion, or myhstimeline.
argument-hint: "[calendar|gmail|gcal|notion|gdoc|myhs] [args]"
---

# Sync — calendars, inboxes, and mirrors

Everything here is opt-in plumbing around the workspace. The workspace stays
the source of truth; integrations export from it or propose changes to it —
they never silently write it. If no workspace exists, route to `start` first.

## Output style — quiet writes

Update workspace files quietly: gather what you need, then do a single whole-file
read-modify-write. **Never paste JSON, code blocks, raw file contents, or
field-by-field diffs into your reply** — the family should not have to read the file
format. Rendering a human-readable table or summary for them is fine; the rule is
about not exposing the raw file. Confirm what changed in one short, plain-language
sentence. (The editor's own change card may still appear — that is the app's UI,
don't narrate or add to it.)

## Capability probe — do this before promising anything

- **Tier 0 (always works):** the bundled `.ics` exporter. No network, no auth.
- **Tier 1/2 (probe):** an integration is available **only if its tools are
  visible in this session** — Gmail (thread search/read tools), Google
  Calendar (event create/list tools), Notion (`notion-*` tools). Never assume;
  never simulate a connector that is not there.
- If the user asks for an integration whose tools are absent: say so in one
  line, point to `docs/INTEGRATIONS.md` for connector setup, offer the Tier 0
  `.ics` route instead, and move on. Mention setup once — do not nag.

## Tier 0 — calendar export (`calendar`)

```
node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs ics_generate --workspace <ws> --out output/admit-calendar.ics
```

- Every dated, not-done milestone becomes an all-day event with two built-in
  reminders (7 days and 1 day before). UIDs are stable, so re-importing
  updates events in place instead of duplicating them.
- If the script returns `no_timeline`, the timeline hasn't been computed —
  run `timeline_build` (or route to `roadmap`), then re-export.
- After export, give import instructions for the family's calendar app
  (menu paths move; the app's own import help page governs):
  - **Google Calendar** (desktop web): gear icon → Settings → Import & export
    → Import → select the file and the target calendar.
  - **Apple Calendar**: double-click the `.ics`, or File → Import.
  - **Outlook**: File → Open & Export → Import/Export → "Import an iCalendar
    (.ics)" — or in new Outlook/web, Add calendar → Upload from file.
- Re-export whenever deadlines change (`tracker` offers this automatically).

## Tier 1 — Gmail scan (`gmail`): propose, never apply

Only if a Gmail connector is visible. Read `references/gmail-recipes.md`
before scanning — it has the query patterns, the extraction checklist, and
the propose-don't-apply protocol. The short version:

1. Start from the base query: `from:(admissions OR commonapp.org) newer_than:14d`,
   plus per-college domains from `colleges.json` when useful.
2. Read matching threads and extract only structured facts: portal
   activations, interview invites, deadline changes, fee waivers, missing-item
   notices. Quote minimally; never copy full email bodies into the workspace.
3. Cross-check against `colleges.json` and present a **proposal table**
   (college → what the email says → proposed tracker change). Apply only the
   rows the user explicitly confirms, via tracker-style read-modify-write.
4. **Never auto-apply. Never set a decision status from an email** — decision
   emails are typically just "there's an update in your portal" notices; ask
   the student to open the portal and report back.
5. Read-only inbox: never send, label, archive, or delete mail, and never
   open links found in email — record URLs and let the user open them.

## Tier 1 — Google Calendar direct write (`gcal`)

Only if a Google Calendar connector is visible. The `.ics` route is still the
default (stable UIDs make updates clean); use direct writes when the family
prefers zero-import convenience.

- Before creating anything, show the exact list of events (title, date,
  reminder offsets) and get confirmation.
- Prefix every event title with `admit:` and search for that prefix before
  creating, so re-syncs update rather than duplicate.
- Put the milestone action and its verify-URL in the event description.

## Tier 1 — Notion mirror (`notion`): one-way, tracker out

Only if Notion tools are visible. This is a **one-way mirror**: `colleges.json`
→ Notion, never back. Say so explicitly — edits made in Notion will be
overwritten on the next sync and never flow into the workspace.

1. First run: create a database (suggested properties: College, Plan,
   Deadline, Status, Test policy, Fee, Notes) and fill one page per entry in
   `colleges.json`.
2. Later runs: upsert by college name — update changed rows, add new ones,
   and note (don't delete) rows for colleges removed from the list.
3. Confirm the target page/workspace with the user before the first write.

## Tier 1 — myhstimeline (High School Timeline · Round Rock HS pilot) (`myhs`)

Bidirectional and capability-probed. **Pilot scope: myhstimeline currently has
data only for students at Round Rock High School (Round Rock ISD, TX)** — if that
isn't the student's school, there's nothing to connect; skip it. Read
`references/myhstimeline-recipes.md` for the tool list, the field-mapping table,
the proposal templates, and the label-vs-value rule.

**Probe.** If `myhs_get_overview` is not visible in this session, say in one line:
*"myhstimeline isn't connected — see docs/INTEGRATIONS.md to connect it (Round Rock
HS pilot)."* and stop. Never nag.

**Pull (read).** Call `myhs_get_overview`; read-modify-write the whole
`.admissions/hs_timeline.json` with the returned overview plus
`"source": "myhstimeline"` and today's `synced_at` (use the real date, don't invent
one). On first link, also call `myhs_get_profile` and offer the profile prefill
(mapping in the recipes reference). Then tell the user: *"Pulled — run
/admit:roadmap to see your High School Timeline panel."*

**Push (write) — confirmation-gated.** When the family makes a decision that maps to
a myhstimeline block (chose an enrollment type; finished a deadline milestone;
changed onboarding), build a proposal table and apply only the confirmed rows:

```text
Proposed updates to your High School Timeline (myhstimeline):
| Block (grade, type)                     | Action    | Value            |
| Choose enrollment type (G0, decision)   | complete  | "Local resident" |
| Register for the fall SAT (G11, dline)  | mark done | —                |
Apply these 2 updates? (all / pick rows / cancel)
```

On confirmation, call `myhs_complete_block` / `myhs_rollback_block` /
`myhs_update_onboarding` for the chosen rows, then re-pull to refresh
`.admissions/hs_timeline.json`. For a **decision** block, resolve the option's
**`value`** (not its label) from `myhs_get_timeline`'s `options[]` before calling
`myhs_complete_block` (label-vs-value rule in the recipes). Never write without
confirmation. A `403` means the student issued a read-only token — tell them to
generate a read&write token; do not retry silently. Show any validation error
verbatim.

## Tier 2 — Google Docs essay drafts (`gdoc`): read-only, zero auth

If the student drafts essays in Google Docs, read a **link-shared** doc
without any connector: take the doc ID from its URL and fetch

```
https://docs.google.com/document/d/{ID}/export?format=txt
```

- Works only when sharing is "Anyone with the link — Viewer". If the fetch
  returns a sign-in page or HTML instead of plain text, it isn't link-shared:
  ask the student to enable viewer link access or paste the text.
- Strictly read-only. Never attempt to edit the doc.
- The ethics floor is unchanged: the draft is the student's own writing, and
  all critique goes through `essay-coach`, which writes feedback to
  `essays/feedback/`. Reading from Google Docs instead of a local file
  changes nothing — no generating, outlining, or rewriting, ever.

## Cross-skill delegation

- Status board, applying confirmed email-scan updates, decision events → `tracker`
- Timeline missing or stale (`no_timeline`) → `roadmap`
- Viewing the High School Timeline panel after a myhstimeline pull → `roadmap`
- Weaving HS milestones into the weekly picks → `checkin`
- Critique of a fetched Google Docs draft → `essay-coach` (owns the ruleset)
- Aid/verification emails surfaced by a scan → `financial-aid`
- Decision notices surfaced by a scan → `decision-day` (after portal check)
- Folding the Gmail scan into a weekly ritual → `checkin`

## Persistence contract

Writes: `output/admit-calendar.ics` (via `ics_generate` only); `colleges.json`
(read-modify-write, whole file, **only** for user-confirmed proposals from a
Gmail scan); `.admissions/hs_timeline.json` (whole-file, from a myhstimeline
pull). Reads: `colleges.json`, `profile.json`, `essays/index.json`,
`.admissions/config.json`, `.admissions/milestones.json`,
`.admissions/hs_timeline.json`, bundled `data/*.json`. Never writes
`essays/drafts/**` or `essays/feedback/**` (feedback belongs to `essay-coach`).
External writes (Google Calendar events, Notion pages, and myhstimeline blocks
via `myhs_complete_block` / `myhs_rollback_block` / `myhs_update_onboarding`)
happen only after the user confirms exactly what will be created or changed.
