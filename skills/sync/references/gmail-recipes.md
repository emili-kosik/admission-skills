# Gmail scan recipes — finding admissions email that matters

Load this before any inbox scan. Ground rules first, then the queries.

## Ground rules

- **Propose, don't apply.** The scan produces a proposal table; the user
  confirms each row before anything touches `colleges.json`.
- **Read-only inbox.** Never send, reply, draft, label, archive, or delete.
- **Never open links found in email.** Record the URL, show it to the user,
  and let them open it themselves. Admissions phishing is real.
- **Quote minimally.** Extract structured facts (college, event type, date,
  URL); do not copy email bodies into workspace files or into the chat beyond
  the sentence that carries the fact.
- **Stay on task.** Surface only admissions-related mail. If the search
  matches something unrelated or personal, skip it without summarizing it.

## Base query

```
from:(admissions OR commonapp.org) newer_than:14d
```

Widen or narrow deliberately:

- Per-college precision: add sender domains for colleges on the list, e.g.
  `from:(admissions OR commonapp.org OR umich.edu OR bu.edu) newer_than:14d`.
  Build the domain list from the entries in `colleges.json`.
- Longer look-back on a first-ever scan: `newer_than:30d`.
- Financial-aid offices often send from a different address:
  `from:(finaid OR "financial aid" OR bursar)`.

## Recipes by need

| Need | Query | Notes |
|---|---|---|
| Decision/status notices | `from:(admissions) subject:("decision" OR "status update" OR "update to your application") newer_than:7d` | These are typically portal pointers, not the decision itself — see the decision rule below |
| Portal activation / account setup | `from:(admissions) subject:("activate" OR "portal" OR "create your account" OR "set up your account") newer_than:30d` | Usually arrives days after submitting; missing one blocks everything later |
| Interview requests | `subject:(interview) newer_than:21d` | Alumni interviewers typically write from personal addresses — if a college on the list does alumni interviews, also try `"interview" "<college name>" newer_than:21d` without a `from:` filter |
| Fee waivers | `subject:("fee waiver" OR "application fee waived") newer_than:30d` | Colleges also grant these after visits or events |
| Deadline changes / extensions | `("deadline extended" OR "deadline extension" OR "extended the deadline") newer_than:30d` | Common around Nov 1 and Jan 1 crunches and after outages |
| Missing / incomplete materials | `from:(admissions) subject:("missing" OR "incomplete" OR "required materials" OR "action required") newer_than:14d` | Highest urgency — flag these first in the proposal table |
| Financial aid documents | `from:(finaid OR "financial aid") subject:(FAFSA OR "CSS Profile" OR verification OR IDOC) newer_than:30d` | Route follow-up to `financial-aid` |

Run only the recipes relevant to where the family is in the cycle (no point
scanning for decisions in October).

## Extraction checklist — per matching thread

1. **College**: resolve the sender/body against `colleges.json`. Mail from a
   college *not* on the list: mention it, but never add a college without
   asking (recruitment mail is marketing, not a commitment).
2. **Event type**: one of `portal_activation`, `interview_invite`,
   `deadline_change`, `fee_waiver`, `missing_item`, `decision_notice`,
   `aid_document_request`, `other`.
3. **Dates named**: deadline, interview slot, RSVP-by — capture the exact
   wording and the date the email was sent.
4. **Action required**: what the student must do, and where (portal URL,
   form). Record URLs; do not fetch them.
5. **Legitimacy check**: expected senders end in the college's `.edu` domain
   or `commonapp.org`. "You've been selected" scholarship blasts, requests
   for payment to claim an award, or look-alike domains → flag as suspicious
   in the table and take no action.

## Propose-don't-apply protocol

1. Render one table for the whole scan:

   ```
   | # | College | Email says | Proposed tracker change | Confidence |
   ```

   Example rows: "portal activation received → add checklist item 'activate
   portal' "; "deadline moved to Jan 8 per email dated Jan 2 → update RD
   deadline, set deadline_verified: false".
2. Ask which rows to apply ("apply 1 and 3"). Silence or ambiguity = apply
   nothing.
3. Apply confirmed rows the tracker way: read `colleges.json` whole, modify,
   write whole. Any deadline set from email gets `deadline_verified: false`
   plus the standard "verify on the college's official page" caveat.
4. **Decision rule**: never set `accepted`/`denied`/`waitlisted`/`deferred`
   from an email scan. Decision emails typically say "your status has been
   updated" — the decision itself lives in the portal. Ask the student to
   open the portal themselves and report back; then `tracker` records it and
   `decision-day` takes over.
5. If any applied change touched a deadline, offer to re-export the calendar
   (`ics_generate`) or re-sync Google Calendar/Notion in the same turn.

## What a scan never does

- Never auto-applies anything, even "obviously safe" checklist items.
- Never opens portal or tracking links.
- Never replies to admissions offices on the family's behalf.
- Never stores email content in the workspace — only the structured facts
  that end up in `colleges.json` after confirmation.
