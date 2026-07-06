---
name: visits
description: >
  Campus visit playbook and demonstrated-interest tracking: what to actually do
  on a visit (class sit-in, dining hall, non-tour students, why-us notes),
  virtual alternatives when travel is impractical, which interest signals count,
  and which colleges track them (CDS item C7). Files visit notes and interest
  signals into colleges.json. Use when the user says "campus visit", "we're
  visiting", "campus tour", "info session", "virtual tour", "demonstrated
  interest", "does this college track interest", "should we visit", or reports
  attending any admissions event.
argument-hint: "[college]"
---

# Visits — campus visits and demonstrated interest

A visit has two jobs: gather real information the family can't get from a
website (this feeds the list and future why-us essays), and — at colleges that
track interest — register a signal. Keep the two separate in your advice:
information is always worth collecting; performing interest only matters where
it is actually considered. If no workspace exists, route to `start` first.

## Output style — quiet writes

Update workspace files quietly: gather what you need, then do a single whole-file
read-modify-write. **Never paste JSON, code blocks, raw file contents, or
field-by-field diffs into your reply** — the family should not have to read the file
format. Rendering a human-readable table or summary for them is fine; the rule is
about not exposing the raw file. Confirm what changed in one short, plain-language
sentence. (The editor's own change card may still appear — that is the app's UI,
don't narrate or add to it.)

## Before the visit

1. Read `colleges.json`. If they're traveling, mention other list colleges
   within reach of the same trip (statuses `researching` or `applying`).
2. Register through the admissions office's official visit page — registered
   visits are typically the ones that count for interest tracking, while
   unregistered walk-arounds typically are not. Verify on the college's
   admissions site.
3. Where offered, book the extras: a class visit in the intended major, a
   department or lab tour, lunch with a current student, an overnight.

## On campus — the playbook

Beyond the standard tour + info session, push for the unscripted:

- **Sit in on a class** in the intended major. Note the course title, the
  professor's name, class size, and whether students talked or typed.
- **Eat in a dining hall.** It's the most honest 30 minutes on campus.
- **Talk to students who aren't tour guides** — in line, in the library café.
  Good openers: "What do you do on a random Tuesday night?", "What would you
  change here?", "Why did you pick this over your other options?"
- **Collect specifics, not vibes**: named programs, research centers, courses,
  traditions, professors. Specifics are the raw material for a credible why-us
  essay later; "beautiful campus and great people" is not.
- **Gut-check honestly**: could the student see themselves here on a gray
  February Tuesday, not just on a sunny admitted-students day?

## After the visit — file the notes

Within a day or two, while it's fresh:

1. Read `colleges.json`, find the college's entry, and append dated visit
   notes to its `notes` field (read-modify-write the whole file). Capture:
   date, what they attended, 3-5 specifics collected, gut reaction.
2. Record the registered events in `demonstrated_interest` (see below).
3. If the visit changed how the student feels — stronger, weaker, off the
   list — say so plainly and suggest revisiting category or status via
   `college-list` or `tracker`.

## Virtual options

When travel is impractical (cost, distance, international families), the
information-gathering and the interest signal both have remote substitutes:
official virtual tours and live virtual info sessions on the admissions site
(registration typically tracked like in-person), regional rep visits to the
student's high school, college-fair conversations, and emailing the regional
admissions rep with a specific, genuine question. Prefer official channels —
third-party tour videos inform but don't register anywhere.

## Demonstrated interest — what counts, and where it counts

Signals that typically count, where interest is tracked at all: registered
campus or virtual visits, info sessions, opening and clicking admissions
emails, completing optional "why us" essays, contact with the regional rep,
and applying in an early round (ED especially).

**Which colleges track it:** check the college's Common Data Set, section C7,
row "Level of applicant's interest" — marked Considered / Important / Very
Important, or Not Considered. Definitions: `data/sources.json` →
`cds.definitions`; per-college CDS archive index → `cds.link_index`; or search
"<college name> common data set". Most ultra-selective colleges mark it **Not
Considered** — at those schools, stop performing interest. Visit for
information, apply early only if it fits the strategy, and spend the saved
effort where it moves the needle.

Log signals in the college's `demonstrated_interest` object (free-form; use
this shape consistently):

```json
{
  "tracked": "considered | not_considered | unknown",
  "cds_checked": "<date the CDS was checked>",
  "signals": [
    { "date": "2026-07-15", "type": "campus_visit", "detail": "registered tour + CS class sit-in" }
  ]
}
```

Set `tracked` only after checking the CDS; default is `"unknown"`.

## Cross-skill delegation

- Recategorize or rebalance the list after a visit → `college-list`
- Deep dive on one college before or after visiting → `college-research`
- Turning visit notes into a why-us essay → `essay-coach` (the student writes;
  notes are raw material — never draft essay text here)
- Interview scheduled during or after a visit → `interview-prep`
- Deadline or status changes the visit prompts → `tracker`
- International families weighing a US trip → `international`

## Persistence contract

Writes: `colleges.json` (read-modify-write, whole file — only the `notes` and
`demonstrated_interest` fields of existing entries; adding colleges belongs to
`tracker`). Reads: `colleges.json`, `profile.json`, `.admissions/config.json`,
bundled `data/sources.json`. Never writes `essays/drafts/**`.
