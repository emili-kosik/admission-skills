---
name: decision-day
description: >
  Decisions season and the final choice: compare admission offers side by side
  (4-year projected net cost, debt at graduation vs. earnings, fit worksheet),
  run the waitlist and deferral playbooks, request financial aid reconsideration,
  and execute the May 1 mechanics — exactly one deposit, then withdraw the rest.
  Use when the user says "compare offers", "we got into X and Y", "which college
  should we choose", "waitlisted", "deferred", "letter of continued interest",
  "LOCI", "appeal the aid offer", "decision day", "May 1", "deposit", or
  "withdraw the other applications".
argument-hint: "[compare|waitlist|deferral|appeal|choose]"
---

# Decision Day — offers, waitlists, and the May 1 choice

Division of labor: `tracker` records each decision as it arrives (accepted /
denied / waitlisted / deferred). This skill owns what happens next: comparing
offers, working waitlists and deferrals, appealing aid, and making the choice.
If the user reports a new decision, update `colleges.json` via the `tracker`
flow first, then continue here.

## Output style — quiet writes

Update workspace files quietly: gather what you need, then do a single whole-file
read-modify-write. **Never paste JSON, code blocks, raw file contents, or
field-by-field diffs into your reply** — the family should not have to read the file
format. Rendering a human-readable table or summary for them is fine; the rule is
about not exposing the raw file. Confirm what changed in one short, plain-language
sentence. (The editor's own change card may still appear — that is the app's UI,
don't narrate or add to it.)

Reply deadlines are typically May 1 ("decision day"), but the binding date is
the one printed in each offer letter and portal — read it there, and say so.

## `compare` — put the offers side by side

1. Read `colleges.json` and `profile.json`. The comparison set = colleges with
   status `accepted` (note waitlisted ones separately — they are options, not
   offers).
2. Read `aid/comparison.md` (built by `financial-aid`'s award-letter analysis).
   If it is missing or stale, route there first: the comparison is only as good
   as the decoded award letters in `aid/award-letters/`.
3. For each offer, pull outcomes data:
   `node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs scorecard_search --id <unitid> --fields core`
   — you want `grad_rate` and `median_earnings_10yr`.
4. Read `references/comparison-framework.md` and build the worksheet:
   - **4-year projected net cost** — year-1 net cost from the award letter,
     projected forward (costs typically rise 3–5% per year while grants often
     stay flat; verify renewal terms per college).
   - **Debt at graduation** — sum planned loans across four years; compare to
     `median_earnings_10yr`. Rule of thumb: total debt above expected
     first-year earnings is a red flag worth saying out loud.
   - **Fit rows** — academics, people, place, logistics, scored by the family.
5. Write the completed worksheet to `decisions.md` in the workspace root and
   render the summary table in chat.
6. Present trade-offs plainly; do not pick the college. Surface red flags
   (front-loaded aid, GPA-cliff scholarships, unmet need filled with loans),
   name what the numbers say, and let the family decide. If money is the
   blocker, offer the `appeal` path before they settle.

## `waitlist` — the playbook

Being waitlisted is a real maybe, not a soft yes. Keep it honest:

1. **Odds honesty.** Waitlist admit rates swing wildly year to year and are
   typically low at selective colleges — some years zero. Look up last cycle's
   numbers in the college's Common Data Set, section C2 (registry:
   `data/sources.json` → `cds.link_index`), and share them straight.
2. **Accept the spot** (there's usually an opt-in form), then send **one**
   letter of continued interest (LOCI). Coach it, never write it — essay rules
   apply (`essay-coach` owns the ruleset): the student drafts; you brainstorm
   real updates (new grades, awards, roles) and critique their draft in
   `essays/feedback/`. Include "I will enroll if admitted" **only if it is
   true**.
3. **Deposit somewhere by the reply deadline regardless.** A waitlist is not a
   plan. Choose from actual offers and deposit; if the waitlist later converts,
   the family can switch — the first deposit is typically forfeited, and the
   first college must be told promptly. That sequence is legitimate;
   double-depositing (below) is not.
4. **Movement window**: typically May through early July, after colleges see
   their deposit yield. After that, waitlists close quietly. Also warn: aid for
   waitlist admits can be limited — ask before accepting a late offer.

## `deferral` — deferred from ED/EA to RD

1. A deferral means "read again in RD" — and a deferral from ED typically
   releases the student from the binding agreement (verify on the college's
   deferral FAQ).
2. **Mid-year grades are the biggest lever.** Confirm the counselor sends the
   mid-year report with strong first-semester grades; keep rigor up.
3. Send **one** LOCI to the deferring college — same coaching rules as above:
   student-written, concrete new information, no repetition of the application.
4. **Keep the RD slate alive.** A deferral is statistically closer to a denial
   than an admit at most selective colleges; the RD applications are the plan,
   not the backup. Check `tracker` that every RD item is on track.

## `appeal` — asking for aid reconsideration

Admission decisions are rarely appealable; money often is. The ask is a
"professional judgment review" or "aid reconsideration" — colleges typically
have a form or named contact on the aid office page.

1. Grounds, strongest first: **changed circumstances** (job loss, medical
   costs, family changes since filing), **errors or missing context** in the
   FAFSA/CSS picture, and **competing offers** from peer institutions.
2. With competing offers: send the other college's actual award letter, name
   the gap in dollars, and ask specifically — "Is there anything you can do to
   close a $6,000/year difference?" Polite, factual, one page. Never invent or
   inflate an offer; offices verify with each other.
3. Set expectations: need-based appeals with documentation move most; merit
   matching is college-dependent (some publicly refuse). No penalty for asking.
4. Timing: before the reply deadline, and ask the aid office whether the
   deadline can be extended while the appeal is reviewed — some will.

Route letter-drafting mechanics and document prep to `financial-aid`.

## `choose` — May 1 mechanics

1. Confirm the decision with the family, then: **exactly one enrollment
   deposit**, by the date and method in that college's portal.
2. **Never double-deposit.** Depositing at two colleges to buy time
   misrepresents intent, typically violates the enrollment agreement, and can
   get both offers rescinded. (Staying on a waitlist while deposited elsewhere
   is the one accepted exception.)
3. After depositing: **withdraw every other pending application and decline
   the other offers** — portal button or a two-line email to admissions. It
   frees waitlist seats for other students and closes the loop cleanly.
4. Update `colleges.json`: chosen college → `enrolled`; all others →
   `declined` (waitlist stays `waitlisted` only if the family is genuinely
   staying on it). Record the outcome and date in `decisions.md`.
5. Point out the post-deposit checklist typically waiting in the new portal:
   housing application, final transcript, orientation registration, and any
   enrollment-contingency terms ("keep your grades up" is real — admits are
   revocable for a collapsed final semester).
6. Offer a calendar refresh via `tracker` and, for international students, an
   immediate handoff to `international` (I-20 and visa timing starts now).

## Cross-skill delegation

- Recording decisions, status board, calendar export → `tracker`
- Award-letter decoding, `aid/comparison.md`, appeal paperwork → `financial-aid`
- LOCI coaching (student writes; critique only) → `essay-coach`
- Revisit questions, admitted-student-day prep → `college-research` and `visits`
- Outside scholarships that change the math → `scholarships`
- Talking a family through a hard or emotional choice → `parent-guide`
- Post-deposit visa/I-20 steps → `international`

## Persistence contract

Writes: `decisions.md` (workspace root; the comparison worksheet and final
choice record) and `colleges.json` (read-modify-write, whole file, statuses
only). Reads: `profile.json`, `aid/comparison.md`, `aid/award-letters/` (never
moved or modified), `essays/index.json`, bundled `data/sources.json`. LOCI
critique memos go to `essays/feedback/` under `essay-coach` conventions. Never
writes `essays/drafts/**`.
