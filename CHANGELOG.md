# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[SemVer](https://semver.org/). Dataset refreshes ship as patch releases.

## [1.0.0] - 2026-07-06

### Added

- **Plugin core**: 20 skills, 6 specialist subagents, 5 hooks, single-plugin
  marketplace (`/plugin marketplace add emili-kosik/admission-skills`).
- **Workspace layer**: private local family workspace (profile, college
  tracker, essays, aid) with JSON schemas, atomic writes, rotating backups,
  protective `.gitignore`, and a PII-minimized profile.
- **Proactivity**: SessionStart deadline digest; `.ics` calendar export with
  7-day/1-day alarms and stable UIDs; weekly check-in ritual feeding the next
  session's briefing.
- **Essay integrity architecture**: PreToolUse hook mechanically blocks
  writes to `essays/drafts/**`; essay-reviewer agent ships without write
  tools; coaching rules E1–E10 grounded in the Common App fraud policy and
  per-college AI policies (bundled verbatim with citations).
- **Primary-source data layer**: College Scorecard client (DEMO_KEY
  out-of-the-box), Urban Institute IPEDS client (no key), CareerOneStop
  scholarship search, and bundled verified datasets — 1,156 college
  deadlines parsed from the Common App Requirements Grid, per-college test
  policies, current-cycle SAT/ACT calendars, Common App prompts + UC PIQs
  verbatim, application-system metadata, 2,796-institution index.
- **Timeline engine**: grade-aware rule table (9th grade → decision day)
  with UC and international tracks, test-date expansion with registration
  companions, and done-flag preservation across regenerations.
- **Docs**: guidebook (11 chapters), AUTHORING contract, INTEGRATIONS tiers,
  WORKSPACE reference, MAINTAINERS runbook, PRIVACY, SECURITY.
- **Quality**: fully offline pytest suite (manifests, frontmatter contracts,
  dataset anchor facts, hook subprocess tests, golden `.ics`), ruff, 3-OS CI,
  `claude plugin validate --strict` gate.
