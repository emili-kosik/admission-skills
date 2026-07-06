<p align="center">
  <img src="assets/cover.png" alt="Admit — Ultimate College Admissions Skills" width="100%">
</p>

# Admit — College Admissions Copilot for Families

A [Claude Code](https://claude.com/claude-code) plugin that turns a private
local folder into your family's college admissions command center: a
personalized grade-9-through-decision-day roadmap, a college list built on
live federal data, an application tracker that briefs you at the start of
every session, calendar reminders, financial-aid and scholarship tooling,
full support for Common App / UC / CSU / ApplyTexas and international (F-1)
applicants — and essay coaching that **never writes the essay**.

> 🎓 **Companion web tool:** [**myhstimeline.com**](https://myhstimeline.com/) — a
> free, personalized roadmap through high school, built by a student who learned
> the hard way. All family data in Admit stays local — see [PRIVACY.md](PRIVACY.md).

## Why this exists

1. **Primary sources, not vibes.** College stats come live from the US
   Department of Education (College Scorecard, IPEDS); deadlines are parsed
   from the Common App Requirements Grid (1,150+ colleges); test policies,
   essay prompts, and per-college AI policies ship verbatim with citations
   and `last_verified` dates. When something can't be verified, the plugin
   says "typically" and links the source instead of guessing.
2. **It remembers the whole journey.** A local workspace carries the student
   from 9th grade course planning to the May 1 decision — git-friendly,
   PII-minimized, never leaving the machine.
3. **It starts the conversation.** Open the workspace and the session begins
   with what's due: deadlines inside 21 days, stale essay drafts, this
   week's three actions. Export the `.ics` and your phone reminds you too.
4. **Integrity is enforced, not promised.** A hook physically blocks Claude
   from writing into `essays/drafts/` — coaching, critique, and grammar
   flags only, per the Common App fraud policy and each college's stated AI
   rules (bundled with quotes and links). That's also just how you get
   better essays.

## Install

```
/plugin marketplace add emili-kosik/admission-skills
/plugin install admit@admission-skills
```

Requirements: Claude Code and Python 3.10+ on PATH (`python` or the Windows
`py` launcher). No pip installs — the runtime is dependency-free.

Works out of the box (College Scorecard `DEMO_KEY`, 30 req/hour). For heavy
list-building, grab a free instant key at [api.data.gov/signup](https://api.data.gov/signup)
and add it in the plugin settings; scholarship search takes free
[CareerOneStop credentials](https://www.careeronestop.org/Developers/WebAPI/registration.aspx).

## Quick start

```
/admit:start          # 10-minute onboarding: workspace + profile + first roadmap
/admit:tracker        # what's due, what's missing, what's next
/admit:college-list   # build a reach/match/safety list on live data
/admit:essay-coach    # brainstorm -> student drafts -> rubric critique
/admit:checkin        # the weekly 10-minute ritual
```

Or just talk: "we got the Michigan decision", "is FAFSA open yet", "help my
daughter pick between these offers" — skills route themselves.

## What's inside

**20 skills** — `start`, `guide` (an 11-chapter guidebook of the whole US
admissions system), `roadmap`, `tracker`, `college-list`, `college-research`,
`essay-coach`, `testing-plan`, `financial-aid`, `scholarships`,
`international`, `interview-prep`, `activities`, `visits`, `decision-day`,
`parent-guide`, `checkin`, `sync`, `data-sources`, `refresh-data`.

**6 specialist agents** — `college-scout` (primary-source research incl.
Common Data Set hunting), `essay-reviewer` (a four-lens committee read that
*cannot* write files by construction), `deadline-auditor` (verifies every
tracked deadline against the live page), `mock-interviewer` (full roleplay +
debrief, incl. an F-1 visa mode), `aid-analyzer` (award-letter decoder),
`scholarship-scout`.

**5 hooks** — the session-start briefing, the essay-draft integrity guard,
workspace schema validation, automatic essay revision snapshots with word
counts, engagement-state upkeep.

**Verified datasets** — deadlines for 1,156 colleges, per-college test
policies, current-cycle SAT/ACT calendars, Common App prompts + UC PIQs
verbatim, per-college AI-use policies with citations, application-system
metadata, a 2,796-institution index. Refresh anytime with
`/admit:refresh-data`; maintainers rebuild from primary sources each August
(see [docs/MAINTAINERS.md](docs/MAINTAINERS.md)).

## The essay policy, up front

Submitting AI-generated essay content is application fraud under the
[Common App fraud policy](https://www.commonapp.org/fraud-policy), and
colleges publish their own rules (Brown and Caltech are the strictest; UC
runs AI checks on PIQs). Admit's coaching model: Socratic brainstorming from
the student's real experiences → the student drafts alone → rubric critique
that quotes their own sentences → grammar *flags*, never rewrites. No drafts,
no outlines, no "humanizing", no exceptions — including for parents. The
`essays/drafts/` folder is hook-protected, and each college's policy is
surfaced with its citation before essay work begins.

## Privacy in one paragraph

Everything personal lives in your workspace folder. API calls send anonymous
query filters, never the student's name, scores, or essays. No telemetry.
The profile schema refuses birthdates and SSNs. The scaffolded `.gitignore`
keeps caches, backups, and award letters out of version control, and the
workspace README tells the family exactly what should never be pushed.
Details: [PRIVACY.md](PRIVACY.md).

## Docs

[Workspace reference](docs/WORKSPACE.md) ·
[Data sources](docs/DATA_SOURCES.md) ·
[Integrations (calendar/Gmail/Notion/Docs)](docs/INTEGRATIONS.md) ·
[Authoring guide](docs/AUTHORING.md) ·
[Maintainer runbook](docs/MAINTAINERS.md) ·
[Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) ·
[Changelog](CHANGELOG.md)

## Disclaimers

Admit is an open-source planning tool, not an admissions consultancy, and
nothing here is legal, financial, or immigration advice. Every deadline
shown carries a "verify on the college's official page" caveat because
colleges change dates — the official page always wins. MIT licensed.
