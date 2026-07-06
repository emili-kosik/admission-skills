# Workspace reference

The workspace is the family-owned folder scaffolded by `/admit:start`. Every
skill reads and writes here; the plugin install directory never holds
personal data.

```
college-planning/
├── profile.json            # who the student is (PII-minimized; no DOB/SSN)
├── colleges.json           # the college list + application tracker
├── timeline.md             # generated human-readable roadmap
├── activities.json         # activities/honors/recommenders (created on first use)
├── essays/
│   ├── drafts/             # STUDENT-AUTHORED ONLY — plugin-blocked for Claude
│   ├── brainstorm/         # coaching session notes (Claude writes)
│   ├── feedback/           # critique memos (Claude writes)
│   ├── .history/           # automatic timestamped snapshots
│   └── index.json          # essay inventory: file, target, prompt, limit, status
├── aid/
│   ├── award-letters/      # drop offer PDFs here (gitignored)
│   ├── comparison.md       # normalized offer comparison
│   └── scholarships.json   # scholarship pipeline
├── decisions.md            # decision-day worksheet
├── output/
│   └── admit-calendar.ics  # calendar export with reminders
├── .admissions/
│   ├── config.json         # cycle, systems, engagement state, optional keys
│   ├── milestones.json     # computed timeline (regenerate via /admit:roadmap)
│   ├── cache/              # API response cache (gitignored)
│   └── backups/            # last-3 rotating backups of mutated files (gitignored)
├── .gitignore              # protective defaults
└── README.md               # privacy rules for the family
```

## Schemas

Machine-validated schemas live in the plugin repo under `data/schemas/`
(`profile.schema.json`, `colleges.schema.json`, `config.schema.json`,
`essays-index.schema.json`). A PostToolUse hook re-checks every write to these
files and, if a value looks off, quietly nudges Claude to fix it on the next
turn — it never blocks the write or surfaces an error to the family.

Key enums:

- `colleges[].status`: researching → applying → essays_in_progress →
  ready_to_submit → submitted → decision_pending → accepted | denied |
  waitlisted | deferred → enrolled | declined
- `colleges[].system`: common_app | uc | csu | applytexas | coalition_scoir |
  institutional
- `colleges[].plan`: ED | ED2 | EA | REA | RD | rolling | uc_filing | csu_filing
- `colleges[].test_policy`: required | optional | flexible | free
- `profile.operator`: parent | student_18plus

## Invariants

- Whole-file read-modify-write for the JSON files (atomic replace + backup
  when done through the plugin's scripts).
- `deadline_verified: false` until a human (or the deadline-auditor agent's
  confirmed patch) verifies the date on the college's page.
- `essays/drafts/**` is writable only by humans — a PreToolUse guard blocks
  Claude's Write/Edit/NotebookEdit calls and write-like Bash commands that
  target the folder, regardless of what any prompt says. (Defense in depth:
  the skills' persistence contracts are the policy layer on top.)
- The engagement state (`config.state.next_actions`, streak, last check-in)
  is written by `checkin` and read by the SessionStart digest.
