---
name: checkin
description: >
  The 10-minute weekly review ritual: look at what moved since last week, what
  stalled, keep the streak honest, and pick exactly three small dated actions
  for the coming week. Use when the user says "check in", "checkin", "weekly
  check-in", "weekly review", "what did we get done", "plan this week",
  "set this week's goals", or the session-start briefing says a check-in is due.
---

# Weekly check-in — the 10-minute review

One sitting, three outputs: a look back, a streak update, and exactly three
next actions written to state. Keep the whole thing under 10 minutes — this is
a ritual, not a planning session. If no workspace exists, route to `start`.

## Output style — quiet writes

Update workspace files quietly: gather what you need, then do a single whole-file
read-modify-write. **Never paste JSON, code blocks, raw file contents, or
field-by-field diffs into your reply** — the family should not have to read the file
format. Rendering a human-readable table or summary for them is fine; the rule is
about not exposing the raw file. Confirm what changed in one short, plain-language
sentence. (The editor's own change card may still appear — that is the app's UI,
don't narrate or add to it.)

## 1. Load state

Read all four files up front:

- `.admissions/config.json` — `state.last_checkin`, `state.checkin_streak_weeks`,
  `state.next_actions` (last week's three)
- `colleges.json` — statuses, deadlines, checklists
- `essays/index.json` — per-essay `status` and `last_reviewed`
- `.admissions/milestones.json` — computed timeline (`milestones[].date`, `.done`)
- `.admissions/hs_timeline.json` — the myhstimeline High School Timeline, **if it
  exists** (`current` focus + nearest `upcoming` milestones)

If `state.last_checkin` is today, this is a revision, not a new check-in: skip
the streak math, re-open step 4, and rewrite the three actions.

## 2. Review the week — deltas since `last_checkin`

Walk last week's `next_actions` first, one by one: done, moved, or stalled?
Then scan for anything else that changed:

- Colleges whose `status` advanced (especially into `submitted` or a decision).
- Essays whose `status` advanced or that were reviewed since last check-in.
- Milestones now `done`; milestones or deadlines that slipped past undone.

Report it as two short lists: **moved** and **stalled**. Celebrate the moved
list briefly and concretely — name the actual thing ("Common App essay went
from drafting to in_review"), one or two lines total, then move on. For the
stalled list, no blame; just carry the facts into step 4. If the same action
has stalled two weeks running, say so and suggest shrinking it or dropping it.

## 3. Streak

Compute days since `last_checkin`:

- **First check-in ever** (`last_checkin` null) → `checkin_streak_weeks: 1`.
- **8 days or fewer** → increment by 1.
- **More than 8 days** → reset to 1 and say: "streak reset — this is a
  marathon; here are this week's three things."

One dry line for the streak, e.g. "Week 5 of weekly check-ins." No badges, no
confetti, no streak-guilt.

## 4. Pick exactly three next actions — with the user, not for them

Propose candidates from the nearest undone milestones, soonest deadlines,
stalled items, and unchecked checklist boxes — and, if `hs_timeline.json` is
present, the `current` and nearest `upcoming` High School Timeline milestones
alongside the admissions ones — then let the user pick and reshape. Rules for
each action:

- **Small**: finishable in one sitting ("email Ms. Rivera about the rec", not
  "do the Common App").
- **Dated**: carries a concrete day within the next week, embedded in the
  string, e.g. `"Outline UC PIQ 2 — by Wed Jul 8"`.
- **Exactly three.** Not two, not five. If the week is packed, the fourth thing
  waits; if the week is quiet, a list-research or visit-planning action fills in.

## 5. Write state and close

Read-modify-write the whole `.admissions/config.json`, changing only:

- `state.last_checkin` → today (`YYYY-MM-DD`)
- `state.checkin_streak_weeks` → the value from step 3
- `state.next_actions` → the three agreed strings (the validator caps this at 3)

Leave `cycle`, `systems`, `keys`, and everything else untouched. Close with one
line: the three actions will appear automatically in the next session-start
briefing, so nothing needs to be remembered.

## Cross-skill delegation

- An action turns out to be a whole project → `roadmap` for sequencing
- Status changes or new deadlines surfaced during review → `tracker`
- Essay actions (brainstorm, review a draft) → `essay-coach`
- Test registration or prep actions → `testing-plan`
- Aid form deadlines (FAFSA/CSS) → `financial-aid`
- List feels thin or lopsided during review → `college-list`
- A parent wants the wider view beyond this week → `parent-guide`

## Persistence contract

Writes: `.admissions/config.json` (read-modify-write, whole file; touches only
`state.last_checkin`, `state.checkin_streak_weeks`, `state.next_actions`).
Reads: `colleges.json`, `essays/index.json`, `.admissions/milestones.json`,
`.admissions/hs_timeline.json` (if present). Never writes `essays/drafts/**`.
