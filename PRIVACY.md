# Privacy

The admit plugin is built around one principle: **a family's college planning
data never needs to leave their machine.**

## Where data lives

Everything personal lives in the **workspace folder the family creates** —
profile, college list, essay drafts, award letters. Nothing personal is ever
written into the plugin's install directory, and the plugin ships no
telemetry, no analytics, and no cloud sync.

## What leaves the machine, exactly

| Call | What is sent | What is never sent |
|---|---|---|
| College Scorecard API | anonymous query filters (state, admit-rate range, a college name) + your API key | the student's name, scores, essays, or any profile field |
| Urban Institute API | a college's numeric `unitid` | anything personal |
| CareerOneStop API | search keywords, a state code, study level + your credentials | anything personal |
| `refresh-data` | a plain download of dataset files from GitHub | anything at all |

Your conversation with Claude itself is governed by Anthropic's privacy terms —
essays you paste or ask Claude to read are processed like any other
conversation content. If that matters to your family, review
[Anthropic's privacy policy](https://www.anthropic.com/legal/privacy) first.

## Data minimization by design

- `profile.json` defines no birthdate, SSN, or address fields, and a
  validation hook rejects any write that adds `birthdate`, `ssn`, `dob`,
  or `address` keys to it.
- Grade level is computed from graduation year, never stored.
- Generated artifacts that leave the workspace (the `.ics` calendar) contain
  event titles like "FAFSA opens" — never GPA, scores, or finances.
- API responses are cached inside the workspace (`.admissions/cache/`),
  which the scaffolded `.gitignore` excludes from version control.

## Git guidance

The scaffolded workspace `.gitignore` excludes caches, backups, and award
letters, and the workspace README says it plainly: local git is for history;
if you push at all, push to a **private** remote you control. Award letters
in `aid/award-letters/` are the most sensitive files in the workspace and
never need to leave the machine.

## Age requirement

Anthropic's Consumer Terms require the Claude account holder to be **18 or
older**. This plugin is therefore designed to be operated by a parent or by
a student who is already 18. Onboarding records which (`operator` in
`profile.json`) and the plugin's tone and framing follow from it.

## API keys

Keys are optional. The recommended storage is the plugin's `userConfig`
(sensitive fields are keychain-backed by Claude Code). The workspace-config
fallback (`.admissions/config.json → keys`) is plaintext on disk — the docs
say so wherever it is mentioned.
