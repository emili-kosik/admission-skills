---
name: activities
description: >
  Build and polish the Common App activities list (10 slots) and honors section
  (5 slots), and run recommender strategy: who to ask, when, how, and per-college
  letter counts. Use when the user says "activities list", "extracurriculars",
  "honors", "awards section", "150 characters", "activity description", "who
  should write my recommendations", "ask a teacher for a letter", "brag sheet",
  "recommenders", or "UC activities".
argument-hint: "[list|honors|recommenders|status]"
---

# Activities — the 10-slot list, honors, and recommenders

This skill owns `activities.json` in the workspace. If it doesn't exist, create it
with the schema below. Always read the whole file, modify, write the whole file
back. If no workspace exists, route to `start` first.

## Output style — quiet writes

Update workspace files quietly: gather what you need, then do a single whole-file
read-modify-write. **Never paste JSON, code blocks, raw file contents, or
field-by-field diffs into your reply** — the family should not have to read the file
format. Rendering a human-readable table or summary for them is fine; the rule is
about not exposing the raw file. Confirm what changed in one short, plain-language
sentence. (The editor's own change card may still appear — that is the app's UI,
don't narrate or add to it.)

```json
{
  "schema_version": 1,
  "activities": [
    {
      "order": 1,
      "position": "",
      "organization": "",
      "description": "",
      "grades": [9, 10, 11, 12],
      "timing": "school_year | break | all_year",
      "hours_per_week": 0,
      "weeks_per_year": 0,
      "continue_in_college": true
    }
  ],
  "honors": [
    { "order": 1, "title": "", "grades": [11], "level": "school | state_regional | national | international" }
  ],
  "recommenders": [
    { "name": "", "subject": "", "asked_on": "YYYY-MM-DD", "status": "planned | asked | agreed | submitted | declined" }
  ]
}
```

## `list` (default) — build and polish the activities list

The Common App gives 10 activity slots. Per slot:

| Field | Limit |
|---|---|
| Position/leadership description | 50 characters |
| Organization name | 100 characters |
| Activity description | 150 characters |
| Grade levels, timing (school year / break / all year) | checkboxes |
| Hours/week, weeks/year | numbers |
| Intend to participate in college | yes/no |

These limits have been stable for years, but confirm inside the current
application (see `data/sources.json` → `common_app.first_year_help`).

1. Read `activities.json` and `profile.json` (the `narrative` section tells you
   what the list should reinforce).
2. **Inventory first, slots second.** Ask for everything the student actually
   does: clubs, sports, arts, jobs, research, volunteering, religious life,
   **family responsibilities** (caring for siblings, translating for parents) and
   **paid work** — both are real activities and admissions readers value them.
3. **Order by depth, not prestige.** Slot 1 is the activity with the most
   sustained commitment and impact — readers skim top-down and anchor on the
   first two or three entries. Depth in a few things beats a padded ten; leaving
   slots empty is fine, filling them with one-meeting trivia is not.
4. Draft each description. Read `references/activities-craft.md` before writing
   or editing any description — it has the verb-first formula, quantification
   patterns, before/after examples, and the common mistakes.
5. **Count characters (including spaces) for every field before presenting it.**
   State the count next to each draft, e.g. `(142/150)`. Never show an
   over-limit line as done.
6. Write the file and summarize what still needs numbers or student confirmation.

**Integrity guardrail:** every activity, number, and title comes from the
student. Compress and sharpen what they did; never invent activities, inflate
hours, or upgrade titles. If hours/week x weeks/year looks implausible, query it
— readers do the same arithmetic.

## `honors` — the 5 slots

The Common App honors section (inside Education) holds up to 5 academic honors,
each with a title, grade level(s), and recognition level (school, state/regional,
national, international — verify the exact options in the application).

- Order strongest first: national beats state beats school.
- Genuine, named honors only (AP Scholar, NMSQT Commended, olympiad ranks,
  juried awards). Attendance certificates and participation trophies cost more
  credibility than they add. Non-academic awards usually belong in the relevant
  activity's description instead.

## UC applicants — different format, don't copy-paste

The UC application has its own "Activities & Awards" section: 20 entries across
six categories with different fields and character limits than the Common App's
10 slots. Entries need rewriting, not pasting — and UC gives more room, so
compressed Common App lines can be usefully expanded. Verify the current fields
inside the UC application (`data/sources.json` → `uc.how_to_apply`).

## `recommenders` — who, when, how, and per-college counts

**Who (default recipe):** two junior-year teachers in core academic subjects who
know how the student *thinks* — engagement beats the grade — plus the school
counselor. Different subject areas (one STEM, one humanities) is the safe pattern;
some colleges require it.

**When:** spring of 11th grade. This is the most time-sensitive move in the
whole recommendation process — good writers get booked, and May memories beat
September ones.

**How:** ask in person (or live video), not by email: *"Would you feel
comfortable writing me a strong letter of recommendation?"* — "strong" gives a
lukewarm writer a graceful exit. Follow up within a day or two in writing with a
brag sheet (specific classroom moments, activities with what the student actually
did, intended major), the college list with the earliest deadline flagged, and
how the invite arrives (e.g. "through Common App by September 1").

**Per-college counts:** read `data/deadlines.json` — each college's `recs`
object has `teacher_evals` (count), `other_evals`, `counselor_rec`, and
`midyear_report`. Many entries are `null` (not listed in the grid) and
non-Common-App colleges may have no `recs` data at all — for any college the
family relies on, verify the count on its admissions page. Two anchors:

- **UC accepts no letters of recommendation for most freshman applicants**
  (`data/systems.json`); a UC-heavy list shrinks the letter workload.
- Extra "other" recommenders only where a college explicitly allows one and the
  person adds something teachers can't. More letters are not better letters.

**Track it:** maintain the `recommenders` array in `activities.json` — status
flow `planned → asked → agreed → submitted` (or `declined`, which just means ask
someone else early). For the counselor entry use `"subject": "counselor"`.
When asks are overdue relative to the timeline, say so plainly.

For depth — FERPA waiver (waive is the norm), brag-sheet templates, mid-year
reports, international recommender notes — delegate to `guide`, whose
recommendations chapter covers all of it.

## Cross-skill delegation

- Deadline board, per-college checklists, calendar export → `tracker`
- "Activity elaboration" supplemental essays → `essay-coach` (never draft them here)
- Background chapters (recommendations, four-year arc) → `guide`
- One college's exact requirements → `college-research`
- Recommenders at non-US schools, English-translation rules → `international`
- Building the activity resume in 9th-11th grade → `roadmap`

## Persistence contract

Writes: `activities.json` (read-modify-write, whole file; create with
`schema_version: 1` if absent). Reads: `profile.json`, `colleges.json`,
`data/deadlines.json`, `data/systems.json`, `data/sources.json`.
Never writes `essays/drafts/**`.
