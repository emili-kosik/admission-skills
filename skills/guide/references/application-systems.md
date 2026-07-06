# The Application Systems

A college application travels through a *platform* — and colleges, not platforms, make
the decisions. Each college chooses which platform(s) it accepts, so your list decides
which systems you'll use. Most families end up in one or two; a list that spans
California publics, Texas publics, and private colleges can touch four. None of them is
harder than the others — they're just different containers with different rules for
essays, recommendations, testing, deadlines, and fees. This chapter maps each one.

One rule above all: **verify every deadline on the college's own admissions page.**
Platforms display dates, but the college's page is the source of truth.

## Common App — the default for most private and many public colleges

[Common App](https://www.commonapp.org) serves roughly 1,100 member colleges. One
account holds your profile, activities list, and a personal essay (typically 250–650
words, chosen from seven prompts); each college then adds its own supplement — extra
essays, recommendation requirements, and its own deadline.

- **Opens August 1** every year. Accounts created earlier
  [roll over](https://www.commonapp.org/rollover) — juniors can create an account in
  spring, enter activities and draft the essay over the summer, and keep all of it
  when the new cycle opens.
- **Deadlines are per college**, following the usual rounds: ED and EA mostly Nov 1
  or Nov 15, RD mostly Jan 1–15. **ED is binding** — one ED application, and you
  enroll if admitted.
- **Recommendations**: typically one counselor plus one or two teachers, invited and
  submitted inside the platform. Each college sets its own count.
- **Testing**: each member sets its own policy — required, optional, or not
  considered. Check the college's page and [fairtest.org](https://fairtest.org/test-optional-list/).
- **Fees**: set per college; some charge nothing. Fee waivers for eligible students
  are built into the application (international eligibility varies by college).
- Common App publishes a free [requirements grid](https://appsupport.commonapp.org/applicantsupport/s/article/Where-can-I-find-the-Requirements-Grid)
  of every member's deadlines, fees, testing policy, and recommendation counts — a
  good cross-check, still second to the college's own page.
- House rule, enforced by the platform itself: the [Common App fraud policy](https://www.commonapp.org/fraud-policy)
  defines submitting AI-generated essay content as application fraud. Essays are
  coached, never ghostwritten.

## University of California — one application, nine campuses, its own physics

The [UC application](https://admission.universityofcalifornia.edu) is a different
species, and if any UC is on your list, your fall calendar changes:

- **One application covers all nine undergraduate campuses** — you check boxes for
  the campuses you want; each reviews you independently.
- **Opens August 1; the filing window is October 1 – November 30.** No ED, no EA, no
  rolling — everyone files in the same window, a full month before most RD deadlines.
- **No essays in the Common App sense.** Instead: eight **Personal Insight Questions
  (PIQs)** — you answer any four, 350 words each. These are direct, advice-style
  responses, not a narrative personal statement; a Common App essay does not paste in.
  UC runs plagiarism and AI checks on PIQs.
- **No letters of recommendation for most applicants**, and **test-free**: SAT/ACT
  scores are not used in admission decisions.
- **Fees are per campus selected**, with waivers for eligible students — check
  current amounts and waiver rules on the UC admissions site (international
  applicants typically pay a higher per-campus fee and generally aren't waiver-eligible;
  verify there).

## California State University — Cal State Apply

The 23-campus CSU system uses [Cal State Apply](https://www.calstate.edu/apply). The
pattern: priority filing typically opens October 1 and runs into early December for
fall admission, admission is largely GPA/course-pattern driven, CSU is test-free, and
most first-year applicants submit no essays and no recommendations. Fees are per
campus with income-based waivers. Some campuses and programs (and impacted majors)
add requirements — verify per campus on Cal State Apply.

## ApplyTexas

Texas public universities (and some private ones) share the
[ApplyTexas](https://goapplytexas.org) portal. Essay requirements and deadlines vary
by campus more than in other systems — some campuses require essays, others don't,
and deadlines don't cluster on a single date. Treat every ApplyTexas college as its
own deadline to verify.

## Coalition on Scoir

The Coalition application runs on the Scoir platform and serves a smaller membership
list; most Coalition members also accept the Common App, so few students *need* it.
If a college on your list offers both, pick one — colleges state no preference. Check
current membership at the college's admissions page.

## Institutional portals — MIT, Georgetown, and others

A handful of colleges use only their own application — MIT
([mitadmissions.org](https://mitadmissions.org)) and Georgetown
([uadmissions.georgetown.edu](https://uadmissions.georgetown.edu)) are the best-known.
Expect a separate account, separate essay prompts, and the college's own calendar and
recommendation process. For the 2026–27 cycle both MIT and Georgetown require SAT/ACT
scores; confirm on their sites. These portals are easy to forget precisely because
they sit outside the platform you use for everything else — track them explicitly.

## Side-by-side

| System | Essays | Recommendations | Testing | Deadline pattern | Fee model |
|---|---|---|---|---|---|
| Common App | 1 personal essay + per-college supplements | Counselor + 1–2 teachers (per college) | Per college (required/optional/not considered) | Per college: ED/EA Nov, RD Jan 1–15 | Per college; waivers in-app |
| UC | 4 of 8 PIQs, 350 words each | None for most applicants | Test-free | Oct 1 – Nov 30, one window, no rounds | Per campus; waivers for eligible |
| CSU (Cal State Apply) | Generally none | Generally none | Test-free | Priority window typically Oct 1 – early Dec | Per campus; income-based waivers |
| ApplyTexas | Varies by campus | Varies by campus | Varies by campus | Varies by campus | Per college |
| Coalition on Scoir | Per college (mirrors member requirements) | Per college | Per college | Per college | Per college |
| Institutional (MIT, Georgetown…) | Own prompts | Own process | Own policy (MIT & Georgetown require SAT/ACT in 2026–27) | Own calendar | Own fee |

Every "per college" and "varies" in this table is an instruction: look it up on the
college's admissions page, not on a third-party summary.

## How the tracker uses this

Each college entry in `colleges.json` carries a `system` field that mirrors this
chapter — `common_app`, `uc`, `csu`, `apply_texas`, `coalition`, or `institutional`.
That field drives which requirements the tracker expects (PIQs vs. personal
statement, whether recommendation slots appear, which deadline window applies), so a
UC campus never nags you about teacher recommendations and an MIT entry never assumes
a Common App date.

## Practical notes for the operator

- **Count your systems early.** Each additional system means re-entering biographical
  data and, usually, different writing. Budget essay time by system, not by college.
- **The UC/CSU window comes first.** If California publics are on the list, PIQs and
  the application must be done by Nov 30 — overlapping ED/EA season. Plan the fall
  around that collision, calmly and early.
- **Writing transfers imperfectly.** Ideas and stories reuse across systems; the
  words usually don't (650-word narrative vs. 350-word PIQ answers). And on every
  platform the same integrity rule holds: brainstorm and critique with any help you
  like, but the words submitted must be the student's own.
- **International applicants** use these same systems and portals; only the
  surrounding requirements differ (English proficiency tests, credential evaluation,
  and fee-waiver eligibility vary by college — verify each on the college's
  international-applicant page).
