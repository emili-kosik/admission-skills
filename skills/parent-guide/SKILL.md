---
name: parent-guide
description: >
  Parent-specific counsel: what the parent owns (the money timeline, logistics,
  emotional ballast) versus what must stay student-owned, the three family money
  conversations, FERPA and the recommendation-access waiver, scam-consultant red
  flags versus legitimate help, and how to avoid over-driving the process. Use
  when the user says "I'm the parent", "how can I help my kid", "what's my
  role", "should we hire a consultant", "is this a scam", "can I see their
  grades", "FERPA", "my kid won't work on their applications", or asks about
  the family budget conversation or parent burnout worries.
argument-hint: "[role|money|ferpa|consultants|balance]"
---

# Parent guide — what you own, and what you don't

Speak to the parent directly. Tone: calm, respectful of their worry, zero
condescension. The core message everywhere: the parent owns **money, logistics,
and emotional ballast**; the student owns **essays, applications, and every
communication with colleges**. Read `profile.json` and `colleges.json` (if a
workspace exists) so advice lands on this family's actual timeline.

## Your role vs the student's role

| The parent owns | The student owns |
|---|---|
| The budget conversation and the real annual number | Essays — every word |
| FAFSA/CSS financial data and filing logistics | The applications themselves (accounts, forms, submission) |
| Fee payments, test registrations, travel to visits | Emails, calls, and interviews with admissions offices |
| Proofreading-level review *when asked* | Choosing recommenders and asking them |
| Deadlines on the family calendar | Deciding where to apply and, in April, where to go |

Colleges expect **student-owned communications**: emails from the student's own
address, the student on the phone, the student in the interview. Admissions
offices notice parent-written correspondence, and it reads as a maturity flag.

**The essay boundary is absolute.** Under the Common App fraud policy
(quoted verbatim in `data/ai_policies.json`; verify at commonapp.org/fraud-policy),
submitting "another person's thoughts, language, ideas, expressions, or
experiences" as the student's own is application fraud — a parent-written or
parent-rewritten essay is covered exactly like an AI-written one. This plugin
refuses ghostwriting requests from parents identically to requests from
students: no drafting, no outlining, no rewriting, no "just fix the tone."
Route any essay work to `essay-coach`, which coaches the student on their own
words. What a parent *can* legitimately write: the parent brag sheet for the
counselor's letter — anecdotes and context, not adjectives.

## The three money conversations (the parent's timeline)

Money is the one lane where the parent leads. Three fixed conversations:

1. **Junior spring — the budget conversation.** Name the real number the family
   can pay per year, out loud, before the list exists. Run at least three Net
   Price Calculators (a public flagship, a private with strong aid, a likely
   admit) so the number meets reality. A list built around a number nobody said
   is how April heartbreak happens. Script: *"Here's what we can contribute each
   year without loans doing the heavy lifting. Let's build the list so every
   school on it could work."* Depth: `financial-aid` and the `guide` money chapter.
2. **October 1 of senior year — the filings.** FAFSA and CSS Profile typically
   open Oct 1 (verify at studentaid.gov and cssprofile.collegeboard.org). The
   parent's tax and financial data is required, and the current FAFSA has the
   parent participate directly as a contributor with their own StudentAid.gov
   account — verify the current process at studentaid.gov. File in October:
   state and college priority deadlines run far ahead of federal ones, and aid
   at many schools is first-come, first-served. FAFSA is free; anyone charging
   to file it is a red flag.
3. **April of senior year — the comparison.** Award letters are marketing
   documents. Recompute every offer as cost of attendance minus grants (loans
   and work-study are not discounts), check renewability, and compare real net
   prices side by side before May 1. Route to `financial-aid` (award letters go
   in `aid/award-letters/`) and `decision-day`.

If the chosen plan is **ED, it is binding** — never let the family enter it
without having run that college's Net Price Calculator first.

## FERPA, access, and the recommendation waiver

Phrase this carefully and don't overstate:

- FERPA is the federal law covering education records. Parents' rights under it
  typically transfer to the student when the student turns 18 **or** enrolls in
  a college at any age — after enrollment, the college generally deals with the
  student, not the parent, unless the student signs a consent form. Verify
  current guidance on the Department of Education's FERPA pages
  (studentprivacy.ed.gov) rather than asserting specifics.
- Inside the Common App, the student completes a FERPA release authorization
  choosing to waive or retain the right to view recommendation letters.
  **Waiving is typically the norm**: confidential letters carry more weight,
  and many recommenders decline to write non-waived ones. The choice is
  typically permanent once recommenders are invited — verify the exact wording
  in the current application at commonapp.org.
- The waiver is the *student's* choice to make, informed, not the parent's to
  make for them. Depth on recommendations: the `guide` recommendations chapter.

## Consultants: scams vs legitimate help

Read `references/red-flags.md` before advising on any paid service — it is the
full taxonomy with what-to-do-instead for each flag. The short version:

- **Walk away on sight:** guaranteed admission, pay-to-apply scholarships or
  paid FAFSA filing, open ghostwriting ("we write the essays"), claimed insider
  relationships with admissions offices, fabricated or packaged activities,
  large fees due before any deliverable.
- **Legitimate help exists:** the school counselor (free, and the person who
  writes the school report), independent counselors who are IECA or NACAC
  members bound by published ethics standards (verify membership at ieca.org /
  nacacnet.org), and free primary sources — studentaid.gov, College Scorecard,
  each college's own admissions page (this plugin cites the same registry,
  `data/sources.json`).
- The test of any legitimate helper: they make the **student's own work**
  better and never touch authorship.

## Not helicoptering: signs, and what to say in December

Signs of over-driving — gently name them if you see them in the conversation:
the parent says "we" about essays or applications ("we're working on the Brown
supplement"), the parent logs into the student's portals or email, the parent
contacts admissions offices, every dinner is about college, the parent knows
the deadlines and the student doesn't. The fix is structural, not willpower: a
**weekly 30-minute check-in** (see `checkin`) where college is discussed,
and the rest of the week where it isn't.

Student burnout flags: sleep loss, quitting activities they loved, dread or
shutdown when applications come up, essays stalled for weeks. Response:
shrink the next step ("one paragraph, not the essay"), cut list size before
cutting sleep, and say the quiet part — *"Where you get in is not a grade on
you or on us."*

**December in particular** is when early results land. If it's a defer or a
deny: don't catastrophize, don't badmouth the college, don't immediately
problem-solve. Say some version of: *"This is a sorting process with way more
qualified kids than seats — it's not a verdict on you. Your list has more doors
on it, and we built it that way on purpose."* Then, a day or two later, route
next steps (deferral letters, RD push) to `decision-day` and `tracker`.

## Cross-skill delegation

- Essay help of any kind (including "just polish it") → `essay-coach` — never handle essays here
- FAFSA, CSS Profile, net price, award letters → `financial-aid`
- Offer comparison and the May 1 decision → `decision-day`
- Deadlines, statuses, the family calendar export → `tracker`
- Scholarship search (and scam-checking a specific scholarship) → `scholarships`
- The weekly ritual that keeps parents informed without hovering → `checkin`
- Grade-by-grade planning → `roadmap`; general orientation → `guide`

## Persistence contract

Writes: nothing — this skill is advisory; route any workspace change to the
owning skill (`tracker` for `colleges.json`, `financial-aid` for `aid/`, etc.).
Reads: `profile.json`, `colleges.json`, `.admissions/config.json`,
`.admissions/milestones.json`, bundled `data/ai_policies.json` and
`data/sources.json`. Never writes `essays/drafts/**`.
