# College Planning Workspace

This folder is your family's private college admissions command center, managed
with the **Admit** plugin for Claude Code (`/admit:*` commands).

## What lives here

| File / folder | Purpose | Who writes it |
|---|---|---|
| `profile.json` | Who the student is: grad year, academics, interests, budget | Claude, with you |
| `colleges.json` | The college list and application tracker (single source of truth) | Claude, with you |
| `essays/drafts/` | Essay drafts — **student-authored only**; the plugin blocks Claude from writing here | The student |
| `essays/brainstorm/` | Brainstorm notes from coaching sessions | Claude |
| `essays/feedback/` | Critique memos on drafts | Claude |
| `aid/` | Award letters (you drop PDFs in), comparisons, scholarship tracker | You + Claude |
| `timeline.md` | The generated roadmap | Claude |
| `output/admit-calendar.ics` | Calendar export — import into Google/Apple/Outlook Calendar for reminders | Claude |
| `.admissions/` | Plugin internals: settings, computed milestones, caches, backups | The plugin |

## Privacy rules (read this once)

1. **This folder contains a minor's personal information. Keep it local.**
2. The scaffolded `.gitignore` already excludes caches, backups, and award
   letters. If you use git here, use it for local history only, or push to a
   **private** remote you control.
3. Financial aid documents in `aid/award-letters/` are the most sensitive
   files here — they never need to leave this machine.
4. Per Anthropic's Consumer Terms, the Claude account holder must be 18+.
   This workspace is designed to be operated by a parent, or by a student
   who is already 18.

## Getting started

- `/admit:tracker` — what's due and what's next
- `/admit:roadmap` — regenerate the grade-appropriate timeline
- `/admit:guide` — how US admissions works, start to finish
- `/admit:checkin` — weekly 10-minute review ritual

Every deadline the plugin shows you comes with a "verify on the college's
official page" caveat — dates change, and the official page always wins.
