# Scam consultants and admissions fraud: the red-flag taxonomy

For every flag: what it looks like, why it's a trap, and what to do instead.
The recurring pattern in all of them: **legitimate help improves the student's
own work; scams replace it, guarantee it, or charge for what is free.**

Primary sources to cite when advising families: the FTC's consumer guidance on
scholarship and financial-aid scams (consumer.ftc.gov), the Department of
Education's scam-awareness pages (studentaid.gov), and the Common App fraud
policy (commonapp.org/fraud-policy, quoted verbatim in `data/ai_policies.json`).

## 1. Guaranteed admission

**Looks like:** "Guaranteed acceptance to a top-20 school or your money back."
"Our students always get in." Tiered pricing by prestige of outcome.

**Why it's a trap:** Nobody outside an admissions committee can guarantee a
holistic-review outcome. The "money-back" version is priced so that the
refunds are covered by the fees of families whose students would have been
admitted anyway. At sub-15% admit rates, every applicant is a reach applicant
— a guarantee is either a lie or a signal that something fraudulent (see #4,
#5) is being sold.

**Instead:** Build reach/match/safety honesty into the list itself
(`college-list` does this from live Scorecard data). A well-built list *is*
the guarantee: it guarantees acceptable outcomes, not a specific trophy.

## 2. Pay-to-apply scholarships and paid "free money" services

**Looks like:** Application fees to enter a scholarship. "Redemption" or
"processing" fees to release an award you supposedly won (often for a contest
never entered). Paid scholarship-matching services — "we'll find money nobody
else knows about." Seminars ending in a high-pressure pitch. Paid FAFSA
filing. Official-sounding names ("National Scholarship Foundation") with
unsolicited mail.

**Why it's a trap:** Legitimate scholarships raise money to give away, not
collect it at the door. You cannot win a contest you never entered. There are
no secret scholarships — sponsors *want* applicants. The first F in FAFSA is
Free. The FTC has litigated this category for decades; see its scholarship-scam
guidance at consumer.ftc.gov.

**Instead:** The school counselor's local list and community foundations first
(less competition than national contests), the Department of Labor's free
CareerOneStop finder (the `scholarships` skill searches it directly), and the
colleges' own merit aid. FAFSA is filed free at studentaid.gov. Rule for the
family fridge: **money flows toward the student, never from them.**

## 3. Open ghostwriting — human or AI

**Looks like:** "Essay packages." "We'll draft it, your student personalizes
it." Editors whose "editing" replaces the student's voice. AI-essay services
and "humanizer" tools marketed to beat detection. Parents quietly rewriting
drafts counts too.

**Why it's a trap:** Under the Common App fraud policy, misrepresenting as
one's own "another person's thoughts, language, ideas, expressions, or
experiences" — or "the substantive content or output of an artificial
intelligence platform" — is application fraud (verbatim in
`data/ai_policies.json`; verify at commonapp.org/fraud-policy). Consequences
can include revoked admission after the fact. It also fails on its own terms:
admissions readers see thousands of 17-year-old voices a season and a
45-year-old's prose is conspicuous.

**Instead:** Coaching — brainstorming from the student's real experiences,
critique of the student's own drafts, mechanical-error flags. That's what
`essay-coach` does and the only editing a legitimate consultant should do.
The plugin refuses ghostwriting from parents and students identically.

## 4. "Insider relationships" and side doors

**Looks like:** "I know the dean of admissions." "We have a special
relationship with these schools." "Donations can be arranged." Claims of
access to application status or reader notes.

**Why it's a trap:** Admissions offices do not give consultants pull, and any
real version of this — bribery, fake athletic credentials, third parties
falsifying applications — is the Varsity Blues fact pattern: federal criminal
prosecutions, rescinded degrees, prison time. A consultant who *claims* it is
lying to you; one who *has* it is a co-defendant.

**Instead:** The legitimate channels that actually move the needle: the
student's own demonstrated interest where colleges track it (`visits`),
strong recommendations asked for early, interviews (`interview-prep`), and —
for the honest version of institutional connection — talking openly with the
admissions office as the student, from the student's email address.

## 5. Fabricated or packaged activities

**Looks like:** Consultants who "found a nonprofit" for the student, sell
officer titles in shell organizations, place students in pay-to-play journals
or "research programs" that publish anything for a fee, or pad the activities
list with roles the student never held.

**Why it's a trap:** Fabricated activities are application fraud under the
same Common App policy as fabricated essays, and admissions readers are
practiced at spotting the purchased-nonprofit pattern — a senior-year
"foundation" with no footprint reads as exactly what it is. Interviews and
recommendation letters cross-check the story.

**Instead:** Depth in fewer, real commitments beats manufactured breadth. The
`activities` skill helps present what the student actually did — with real
verbs and real numbers, which is more persuasive than invented titles. If the
student genuinely wants research or service, earlier and unglamorous beats
purchased and polished.

## 6. Large fees before deliverables

**Looks like:** Four- or five-figure packages paid entirely upfront. Contracts
with no scope, no refund terms, or a percentage-of-scholarships-won fee.
Pressure to sign today ("junior-year slots are almost gone"). Refusal to name
references or credentials.

**Why it's a trap:** Prepaid-in-full with vague scope removes every incentive
to deliver and every remedy when they don't. Percentage-of-aid fees charge the
family for money the student's own record earned. Urgency is manufactured —
admissions has real deadlines, but consultant enrollment is not one of them.

**Instead:** Pay-as-you-go or clearly staged payments against a written scope.
Before signing anything: ask for credentials and two family references, and
check membership directories at ieca.org and nacacnet.org (see below).

## Aid-specific fraud: a special warning

A "financial aid consultant" who suggests hiding assets, moving money into a
relative's name to game the FAFSA, or lying about household size is inviting
the family to commit federal fraud — the penalties land on the *family*, not
the consultant. Legitimate aid optimization exists (timing of income,
understanding the formulas) and is discussed openly; verify anything aid-form
related against studentaid.gov, and route award-letter and form questions to
`financial-aid`.

## What legitimate help looks like

| Option | Cost | How to verify |
|---|---|---|
| School counselor | Free | Already at the school; writes the school report and counselor letter — keep them informed regardless of other help |
| Independent educational consultant, IECA member | Paid | Directory and ethics standards at ieca.org — members commit to no guarantees and student-authored work |
| Independent counselor, NACAC member | Paid | Directory and ethical practices code at nacacnet.org |
| Community-based orgs and college-access nonprofits | Usually free | Ask the school counselor which ones operate locally |
| Primary sources | Free | studentaid.gov, collegescorecard.ed.gov, each college's own admissions and aid pages — the same registry this plugin cites (`data/sources.json`) |

Questions that sort legitimate from scam in one meeting:

1. "What do you guarantee?" — right answer: *process*, never outcomes.
2. "Who writes the essays?" — right answer: the student, always; we coach.
3. "How are you paid?" — right answer: stated scope, staged payments, no
   percentage of aid.
4. "What professional standards are you bound by?" — right answer: a named
   membership (IECA, NACAC) with a code you can read online.
5. "Will you work alongside our school counselor?" — right answer: yes.

If a service is already engaged and flags are flying: stop payments where the
contract allows, keep all correspondence, and report — FTC at
reportfraud.ftc.gov for scholarship/consultant scams, the state attorney
general's consumer-protection office, and studentaid.gov's reporting channels
for aid fraud. If fraudulent content already went into a submitted
application, the family should correct it with the college directly and
quickly — colleges treat self-reported corrections very differently from
discovered fraud.
