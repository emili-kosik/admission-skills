---
name: roadmap
description: >
  Generate or refresh the personalized admissions timeline: rebuild the milestone
  file from the rule table, render a readable timeline.md grouped by month, and
  offer a calendar export. Grade-aware — light-touch for 9th/10th grade, pivot-year
  planning for 11th, execution mode for 12th — with UC and international track
  divergences. Use when the user says "roadmap", "timeline", "plan", "what should
  we be doing now", "what's coming up", "refresh the timeline", "milestones",
  "план поступления", or after the profile, college list, or grade changes.
argument-hint: "[refresh]"
---

# Roadmap — the personalized timeline

Turn the milestone rule table into a grade-appropriate plan the family can read.
If no workspace exists, route to `start` first — the roadmap needs `profile.json`.

## Output style — quiet writes

Update workspace files quietly: gather what you need, then do a single whole-file
read-modify-write. **Never paste JSON, code blocks, raw file contents, or
field-by-field diffs into your reply** — the family should not have to read the file
format. Rendering a human-readable table or summary for them is fine; the rule is
about not exposing the raw file. Confirm what changed in one short, plain-language
sentence. (The editor's own change card may still appear — that is the app's UI,
don't narrate or add to it.)

## Step 1 — Rebuild the milestone file

```
node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs timeline_build --workspace <ws>
```

Rerun this every time the skill is invoked: it is cheap, idempotent, and preserves
`done` flags across regenerations. Handle errors:

- `no_workspace` → route to `start`.
- `no_grad_year` → ask for the graduation year, set `student.grad_year` in
  `profile.json` (read-modify-write the whole file), rerun.

The printed summary includes `grade`, `tracks`, and `next_5` — use it for the
spoken recap after rendering.

## Step 2 — Read the computed timeline

Read `.admissions/milestones.json`. Top level: `generated_at`, `grade`, `cycle`,
`tracks`, `milestones[]`. Each milestone has `id`, `title`, `action`, `priority`
(`critical|high|normal`), `tracks`, `source_url`, `verification`, `done`, and one
of two date shapes:

- **Dated**: `date` (ISO), sometimes `window_end` (a range).
- **Undated advisory**: `date: null` with `approx` (human description) and
  `approx_month` (`YYYY-MM`) — its month anchor.

College items from `colleges.json` come in a few shapes — **present them as the
timeline gives them, leading with the strategic date, not the deadline**:

- `college/<name>/recommended-submit` — the strategic "submit by" date for
  rolling/wave/priority schools (e.g. Texas A&M in August). This is the real
  target; treat it as `critical`.
- `college/<name>/deadline-backstop` — the hard deadline behind a strategic
  date, marked as the backstop (`normal`). Show it, but don't lead with it.
- `college/<name>/priority` — an earlier scholarship/honors/housing date.
- `college/<name>/<plan>` — a plain fixed deadline (ED/EA/RD).

Unverified ones already carry the caveat in the title — keep it.

## Step 3 — Load track references before rendering

- Read `references/uc-track.md` when `tracks` includes `uc`, when
  `.admissions/config.json` `systems` includes `uc`, or when any `colleges.json`
  entry has `"system": "uc"`.
- Read `references/international-track.md` when `profile.json`
  `student.residency` is `international` (`tracks` will include `international`).

Both change how you order and narrate senior fall — load them first, not after.

## Step 4 — Render `timeline.md` at the workspace root

Write the whole file fresh each time (it is generated output, safe to overwrite):

```markdown
# Admissions roadmap — Class of <grad_year>
Generated <today> · Grade <grade> · Tracks: <tracks>

<2-4 line grade framing paragraph — see Step 5>

## <Month Year>
- [ ] **<Mon D>** (in N days) — <title> — <one-line action>
- [ ] **<Mon D> – <Mon D>** — <window title> — <action>
- [ ] *This month (date varies)* — <title> — typically <approx>
- [x] <title> — done
```

Rendering rules:

1. Group by calendar month (dated items by `date`; undated by `approx_month`),
   chronologically. Undated advisories go at the end of their month group.
2. Every dated item gets a day count from today; ≤14 days gets a warning marker,
   overdue gets **overdue** in bold (don't silently drop it).
3. `done: true` → checked box, no day count. `priority: critical` → bold title.
4. Items with `verification: pattern` or `college_specific` keep "typically"
   phrasing and get a verify link from `source_url` when present.
5. End with a footer: dates come from the plugin's rule table and the family's
   own list — verify anything load-bearing on the official page, and regenerate
   with `/admit:roadmap` after list or profile changes.

Keep it scannable: one line per item, no paragraphs inside the month groups.

## Step 5 — Grade-aware framing

The opening paragraph of `timeline.md` (and your spoken recap) must match grade:

| Grade | Register |
|---|---|
| 9-10 | **Anti-pressure, explicitly.** Say that nothing this year is fatal, colleges are not watching, and the list is short on purpose: rigor, habits, a few real interests. If the timeline looks thin, that is correct — do not pad it. |
| 11 | **The pivot year.** Testing arc, first list, recs and counselor meeting in spring, net-price conversation, essay draft in summer. Steady beats heroic; the summer essay window is the single highest-leverage item. |
| 12 | **Execution.** The calendar is the plan: deadlines, logistics, buffers. Front-load everything two weeks; nothing new gets invented senior fall. Point at `tracker` for the per-college board and `checkin` for cadence. |

## Step 6 — Offer the calendar export

After writing `timeline.md`, offer reminders in the family's own calendar:

```
node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs ics_generate --workspace <ws> --out output/admit-calendar.ics
```

The .ics imports into Google/Apple/Outlook with built-in 7-day and 1-day
reminders, and re-exporting updates events in place.

## Marking milestones done

When the user reports a milestone completed ("we filed the FAFSA"), set that
item's `done: true` in `.admissions/milestones.json` (read-modify-write the whole
file) and re-render `timeline.md`. `timeline_build` preserves the flag on future
rebuilds. College application events (submitted, decisions) belong in `tracker`,
not here.

## Cross-skill delegation

- Workspace setup / missing profile → `start`
- Per-college statuses, deadlines board, "we submitted" → `tracker`
- SAT/ACT/AP/TOEFL specifics and registration → `testing-plan`
- Building or rebalancing the list → `college-list`
- Essay milestones ("draft the personal essay") → `essay-coach` — never draft here
- FAFSA/CSS items → `financial-aid`; visa and credential items → `international`
- "Why does the timeline look like this?" background → `guide`

## Persistence contract

Writes: `.admissions/milestones.json` (via `timeline_build`; may also flip `done`
flags read-modify-write), `timeline.md` at the workspace root (full overwrite),
`output/admit-calendar.ics` (via `ics_generate`). May update `profile.json`
(read-modify-write) only to set a missing `student.grad_year`. Reads:
`profile.json`, `colleges.json`, `.admissions/config.json`. Never writes
`essays/drafts/**`.
