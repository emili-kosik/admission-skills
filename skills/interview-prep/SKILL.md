---
name: interview-prep
description: >
  College interview preparation: figure out which tracked colleges interview and
  what kind (evaluative vs informational; alumni, admissions, or student
  interviewers), build talking points from the student's real profile and
  activities, run a full mock interview with a debrief, and cover questions to
  ask the interviewer, logistics, etiquette, and thank-you notes — plus the F-1
  visa interview for international students. Use when the user says "interview",
  "mock interview", "alumni interview", "interview prep", "what will they ask",
  "questions to ask the interviewer", "thank-you note", "visa interview", or
  reports receiving an interview invitation.
argument-hint: "[college] [prep|mock|questions]"
---

# Interview prep — real stories, not scripts

Interviews are conversations, not exams. The goal of prep is that the student
can talk naturally about their own life and why this college — never to
memorize answers. Read `profile.json` and `colleges.json` before anything else;
if no workspace exists, route to `start`.

## Step 1 — Which colleges interview, and what kind

For each college the family asks about (or every entry with status `applying`
or later):

1. Check the college's own admissions site — WebSearch `"<college> admissions
   interview"` and prefer the official domain. The interview page states
   whether interviews exist, who conducts them, how to sign up, and whether
   skipping one hurts.
2. Cross-check the college's Common Data Set, item C7 ("Interview" —
   considered / not considered), via the CDS link index in `data/sources.json`
   (`cds.link_index`).
3. Explain what you found with this decoder:

| What the page says | What it means for prep |
|---|---|
| **Evaluative** | The interviewer writes a report that joins the application file. Prep matters; treat it as a real data point. |
| **Informational** | For the student's benefit; little or no report. Lower stakes — use it to gather material for "why us" essays and demonstrated interest. |
| **Alumni interviewer** | A volunteer, usually off-campus or virtual, who typically has not seen the application. Expect broad get-to-know-you questions; the student introduces themselves from scratch. |
| **Admissions staff / senior interviewer** | Typically more structured and more likely evaluative; on campus or virtual. |
| **Current-student interviewer** | Trained by admissions; conversational; a great source of candid campus answers. |
| **Not offered / not guaranteed** | Typically the case at large publics, and common even at selective colleges with limited alumni coverage. The page usually says missing one does not hurt — take that at face value. |

The pattern facts above are "typically" — the college's own page is the
authority. Some colleges direct international applicants to a third-party
recorded interview (e.g., InitialView or Vericant); if the page says so, that
recording substitutes for a live interview and the same prep applies.

Record what you learn on the college's entry in `colleges.json` (see
Persistence contract) so it is not re-researched next time.

## Step 2 — Prep from the student's own material

No scripts. Build **story anchors**: 4–6 real episodes the student can speak
about for 60–90 seconds each, drawn from their actual record:

1. From `profile.json`: `narrative.spike`, `narrative.hooks`,
   `interests.majors`, `academics` (favorite courses, rigor arc), and any
   activities data the `activities` skill has recorded there. If the profile
   is thin, ask the student to name their 2–3 most meaningful activities and
   one academic experience they would gladly talk about.
2. For each anchor, have the student say — out loud, not in writing — what
   happened, what they did, and what changed in them. Specifics beat polish.
3. Map anchors to question groups: read `references/question-bank.md` (~30
   real questions grouped by what they actually probe) and check that every
   group has at least one anchor that answers it.
4. "Why us" is the one question that needs homework: 2–3 specific, true
   reasons — a program, a professor's work, a curriculum feature. If the
   student cannot name any, do a `college-research` pass first. Rankings and
   prestige are not reasons.

Parent note: if the operator is a parent, prep only works if the student does
the talking. Suggest handing the session to the student, or going straight to
the mock below with the student at the keyboard.

## Step 3 — Full mock with the mock-interviewer agent

When the student wants live practice, launch the `mock-interviewer` agent and
pass it:

- the college name and the interview type from Step 1 (evaluative or
  informational; alumni, admissions, or student interviewer),
- a 3–5 sentence profile summary: intended major, spike, 2–3 story anchors,
  grad year — nothing beyond what the workspace already holds,
- any question groups the student wants drilled (e.g., curveballs).

The agent roleplays the interviewer in character, then breaks character and
debriefs: what landed, what rambled, which anchors never surfaced, and one
thing to fix next time. After it returns, offer to save the top debrief
takeaways into the college's `notes` in `colleges.json`.

## Questions the student should ask (have three ready)

Genuine questions only — things the homepage cannot answer:

- "What did you study or do here, and what surprised you about it?"
- "What kind of student struggles here?"
- "How hard is it really to join X lab / double major / switch programs?"
- "What do students complain about?"
- For alumni: "What has stuck with you years later?"

Skip questions about admit rates, the student's chances, or anything answered
on the admissions page.

## Logistics, etiquette, thank-you

- **Scheduling**: reply to interview invitations within about 48 hours — the
  student replies, not the parent. For virtual interviews, confirm the time
  zone explicitly.
- **Virtual**: laptop rather than phone, camera at eye level, quiet room, join
  3–5 minutes early, account display name set to the student's real name.
- **In person** (typically a café or library for alumni interviews): a parent
  may drive but waits elsewhere. Smart-casual dress. No résumé unless the
  interviewer asks for one — some do; follow their lead.
- **Thank-you note**: within 24–48 hours, 3–5 sentences, from the student's
  own email — thank them, mention one specific moment from the conversation,
  restate interest in a single line. Give the student that structure and let
  them write it; do not draft it for them.

## International students — the other interview

The F-1 **visa interview** at a US consulate is a different animal: not
holistic, but a short screening for nonimmigrant intent, funding, and program
fit. The consular question set and how to think about it are in
`references/question-bank.md` (visa section). For the full process — I-20,
SEVIS fee, DS-160, timing — delegate to `international`. Primary source: the
State Department student-visa page (`data/sources.json` →
`international.student_visa`).

## Keep it calm

Interviews typically carry modest weight next to the transcript and essays; a
normal-but-unremarkable interview almost never sinks an application, and not
being offered one typically costs nothing (verify on the college's interview
page — most say exactly this). Prep is still worth doing: it lowers anxiety
and sharpens the "why us" thinking that also feeds supplemental essays.

## Cross-skill delegation

- F-1 visa process, I-20, SEVIS, credential evaluation → `international`
- "Why us" substance for a specific college → `college-research`
- Demonstrated-interest strategy and campus visits → `visits`
- Status changes, deadlines, and the board → `tracker`
- Story anchors that turn into essay material → `essay-coach` (interview prep
  never becomes essay drafting)
- Building or updating the activities record → `activities`

## Persistence contract

Writes: `colleges.json` only (read-modify-write the whole file; interview
findings, scheduled dates, and debrief takeaways go under the college entry's
`demonstrated_interest` and `notes` fields). Reads: `profile.json`,
`colleges.json`, `.admissions/config.json`, bundled `data/sources.json` and
`data/college_index.json`, and `references/question-bank.md`. Never writes
`essays/drafts/**`.
