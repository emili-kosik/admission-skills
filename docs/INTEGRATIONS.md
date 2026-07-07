# Integrations

The plugin's default stack requires **zero external accounts**. Everything
below is optional and layered.

## Tier 0 — built in, no setup (recommended baseline for everyone)

- **Local workspace** — the source of truth for everything.
- **Session briefings** — every Claude Code session opened in the workspace
  starts with a deadline digest (SessionStart hook).
- **Calendar export** — `/admit:sync` (or the tracker) generates
  `output/admit-calendar.ics` with built-in reminders 7 days and 1 day before
  each deadline. Import it into Google Calendar (Settings → Import & export),
  Apple Calendar, or Outlook by double-click. Re-importing after changes
  updates events in place (stable UIDs).
- **Recurring rituals** — run `/loop 1w /admit:checkin` in a session for a
  weekly cadence, or open the workspace on Sundays; the digest does the rest.
- Cloud "routines"/scheduled agents are **not** used: they run on fresh
  clones without access to the local workspace.

## Tier 1 — one-click Claude connectors (optional)

If these connectors are enabled in your Claude Code session, the `sync` skill
detects and uses them; if not, it quietly sticks to Tier 0.

- **Gmail** — scan for admissions email
  (`from:(admissions OR commonapp.org) newer_than:14d`): portal activations,
  interview invites, deadline changes. The skill *proposes* tracker updates;
  it never applies them without confirmation.
- **Google Calendar** — write deadline events directly instead of the .ics
  file.
- **Notion** (hosted MCP: `claude mcp add --transport http --scope user
  notion https://mcp.notion.com/mcp`) — a one-way visual mirror of the
  college tracker for family sharing. `colleges.json` remains the source of
  truth; the mirror is regenerated, never read back.

Each of these sends the relevant slice of data to that provider — the skill
states what it's about to sync before doing it.

## Tier 1 — myhstimeline (High School Timeline) · Round Rock HS pilot

[myhstimeline](https://myhstimeline.com/) is a student's structured visual
high-school milestone timeline. Connected, it flows into Admit as a distinct
**High School Timeline** panel (in `/admit:roadmap`), pre-fills onboarding, and —
after explicit confirmation — lets Admit push completed decisions back.

> **Pilot scope:** myhstimeline currently has data only for students at **Round
> Rock High School (Round Rock ISD, TX)**. If that isn't your school, skip it —
> Admit works fully without it.

It's a **session-time MCP**, connected once by the student (the token lives in the
MCP server's own env, **never** in Admit's `plugin.json` `userConfig` and never
written to the workspace):

```bash
claude mcp add --transport stdio --scope user myhstimeline \
  --env MYHS_API_URL=https://api.myhstimeline.com \
  --env MYHS_TOKEN=<token from myhstimeline app -> Settings -> Connect external tools> \
  -- npx -y @myhstimeline/mcp
```

Read/write model: Admit **pulls** the overview into `.admissions/hs_timeline.json`
and renders it as its own panel; **writes back** (completing a decision, marking a
milestone done) happen only after you confirm an explicit proposal table — never
automatically. A read-only token still allows the panel; write-back needs a
read&write token. Details and the field mapping:
`skills/sync/references/myhstimeline-recipes.md`.

## Tier 2 — power users

- **Google Docs essay drafts.** The default recommendation is local Markdown
  drafts (git history = revision tracking, and the essays/.history/ snapshots
  come free). For families wedded to Docs: a link-shared document can be read
  with zero auth via its export URL —
  `https://docs.google.com/document/d/<ID>/export?format=txt`.
  Critique still lands in `essays/feedback/`; the student edits in Docs.
  For comment round-trips, a community Google Workspace MCP server (e.g.
  `taylorwilsdon/google_workspace_mcp`) works but requires setting up a
  Google Cloud project — only worth it if you'll use it weekly.
- Avoid the archived `@modelcontextprotocol/server-gdrive` — unmaintained.

## What is deliberately not integrated

- No bundled `.mcp.json`: shipping one would push auth prompts on every user
  for optional functionality.
- No auto-sending email, no auto-applying inbox-derived changes, no writes to
  any external system without an explicit per-action confirmation.
