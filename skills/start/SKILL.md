---
name: start
description: >
  Set up a family college-planning workspace: onboarding interview, student profile,
  privacy defaults, and optional free API keys. Use when the user says "get started",
  "set up college planning", "new student profile", "onboard", "start college prep",
  "начать подготовку к поступлению", or asks how to begin using the admit plugin.
argument-hint: "[grad-year]"
---

# Start — Workspace Onboarding

You are setting up a private, local college-planning workspace for a family.

## Output style (applies to the whole onboarding)

Keep it human, not technical. **Never paste JSON, file contents, code blocks, or
field-by-field diffs into your replies** — the family should not have to read the
file format. When you record an answer, just save it and confirm in one short,
plain-language line (e.g. "Записал: SAT 1370, пересдача в августе."). Collect the
answers conversationally and write `profile.json` in a **single quiet update at the
end** of the interview rather than editing after every question. (The editor may
still show its own change card — that is the app's UI, not something to narrate;
don't add to it.)

## Before anything else: who is operating

Ask (once, conversationally): **"Who will be running these sessions — a parent, or a
student who is already 18?"** Anthropic's Consumer Terms require the account holder
to be 18+, so this workspace is designed to be parent-operated or used by an 18+
senior. Record the answer as `operator: parent | student_18plus`. Do not invite
under-18 self-use.

## Step 1 — Choose and scaffold the workspace

1. Recommend a dedicated folder (e.g. `college-planning/`) rather than an existing
   code repo. Confirm the location with the user.
2. Scaffold it:
   ```
   node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs init_workspace --dir <folder> [--grad-year YYYY]
   ```
3. If the output contains a `warning` about an enclosing git repository, relay it and
   offer to add the workspace folder to that repo's `.gitignore`.
4. Point the user at the scaffolded `README.md` — it documents the privacy rules.
   State the one-liner yourself: **everything stays local; never push this folder to
   a public remote.**

## Step 1b — Connect myhstimeline (optional · Round Rock HS pilot)

**myhstimeline** is a visual high-school-progress timeline. It is a pilot and
**currently has data only for students at Round Rock High School (Round Rock ISD,
TX)**. Offer it in one line and let the family self-select — do not push it:

> "Do you use myhstimeline? It's a visual HS-progress timeline — right now it only
> works for **Round Rock High School (RRISD)**. If that's your student's school you
> can connect it so I don't re-ask what it already knows; otherwise we'll skip it."

- **Skip / not Round Rock HS / no account** (the common case): say "No problem — you
  can connect it later with `/admit:sync`" and go straight to the interview. Nothing
  is blocked.
- **Connect:** show this one-time command verbatim, then wait for the tools:

  ```bash
  claude mcp add --transport stdio --scope user myhstimeline \
    --env MYHS_API_URL=https://api.myhstimeline.com \
    --env MYHS_TOKEN=<token from myhstimeline app -> Settings -> Connect external tools> \
    -- npx -y @myhstimeline/mcp
  ```

  Once the `myhs_*` tools are present (pull-first-then-prefill):
  1. Call `myhs_get_profile` and `myhs_get_overview`.
  2. Write the whole `.admissions/hs_timeline.json` from the overview (add
     `"source": "myhstimeline"` and today's `synced_at`).
  3. **Prefill `profile.json` — missing fields only, never overwrite without
     asking** — using the field mapping in the `sync` skill's myhstimeline recipes
     (e.g. `grad_year = enrollment_year + 4`, residency, state, English
     proficiency).
  4. Run the interview below but **skip questions already answered**.

  If the command was run but the tools don't appear, say so in one line and
  continue with the normal interview. Keeping it current later is `/admit:sync`;
  the High School Timeline panel shows in `/admit:roadmap`.

## Step 2 — Profile interview (10 minutes, conversational)

Fill `profile.json` by asking, in this order (skip what the user volunteers):

1. **Graduation year** (drives everything — grade is computed, never stored).
2. **Residency**: domestic or international? If international: country, and whether
   they'll need an F-1 visa. Set `residency` accordingly.
3. **State** (drives UC/CSU track for CA, in-state options, state aid deadlines).
4. **Academics**: unweighted GPA (approximate is fine), current course rigor,
   AP/IB/honors taken or planned.
5. **Testing so far**: PSAT/SAT/ACT scores if any; English proficiency test plans if
   international.
6. **Interests**: possible majors (2-3), campus size/region/setting preferences,
   must-haves.
7. **Money — normalize this early**: is need-based aid expected? A comfortable
   budget per year? Income bracket only if the family volunteers it (it powers
   net-price estimates). Never press.
8. **Narrative**: what the student is known for ("spike"), any hooks.

Once you have the answers, write them to `profile.json` in **one** read-modify-write
of the whole file (per the output-style rule above — no running commentary, no JSON
in chat, one confirming sentence). The plugin validates the file quietly in the
background and will nudge you privately if a value is off. PII rules: preferred name
or initials only, **never** birthdate/SSN/address — keep them out of the file.

## Step 3 — Optional free API keys (never block on this)

The plugin works out of the box (College Scorecard DEMO_KEY: 30 requests/hour).
Offer the upgrades once:

- **College Scorecard** (college list data, 1,000 req/h): instant free key at
  https://api.data.gov/signup — set it in the plugin settings (`/plugin` →
  admit → Configure) or as env var `SCORECARD_API_KEY`.
- **CareerOneStop** (scholarship search): free at
  https://www.careeronestop.org/Developers/WebAPI/registration.aspx

## Step 4 — First roadmap and calendar

1. Generate the grade-appropriate roadmap: follow the `roadmap` skill
   (`/admit:roadmap`). For a 9th/10th grader this is deliberately light.
2. Offer the calendar export (`/admit:sync`) so deadlines appear in the family's
   own calendar app with built-in reminders.
3. Close with the weekly rhythm: `/admit:checkin` once a week, `/admit:tracker`
   any time. The plugin will brief them automatically at the start of each session.

## Cross-skill delegation

- Roadmap/timeline generation → `roadmap`
- Building the college list → `college-list`
- "How does US admissions work at all?" → `guide`
- International specifics (F-1, TOEFL, credential evaluation) → `international`

## Persistence contract

Writes: `profile.json`, `.admissions/config.json` (via `init_workspace`), and the
scaffold files. May write `.admissions/hs_timeline.json` and prefill `profile.json`
from myhstimeline (missing fields only) when the student links their account.
Never writes into `essays/drafts/`.
