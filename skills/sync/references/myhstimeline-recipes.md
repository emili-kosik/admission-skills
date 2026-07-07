# myhstimeline recipes (High School Timeline integration)

**Pilot scope (canonical statement — echo this wherever myhstimeline is offered):**
myhstimeline is a pilot and **currently has data only for students at Round Rock
High School (Round Rock ISD, TX)**. If that isn't the student's school, there is
nothing to connect — skip it; Admit works fully without it.

## Connect (the student runs this once)

The token lives in the **MCP server's** env, never in Admit's `plugin.json`
`userConfig` and never written to the workspace.

```bash
claude mcp add --transport stdio --scope user myhstimeline \
  --env MYHS_API_URL=https://api.myhstimeline.com \
  --env MYHS_TOKEN=<token from myhstimeline app -> Settings -> Connect external tools> \
  -- npx -y @myhstimeline/mcp
```

## Tools

| Tool | Access | Use |
|---|---|---|
| `myhs_get_overview` | read | pull the whole timeline → `.admissions/hs_timeline.json` |
| `myhs_get_profile` | read | onboarding fields for the profile prefill |
| `myhs_get_timeline` | read | full block detail incl. decision `options[]` (for the value rule) |
| `myhs_complete_block` | write | complete a block (decisions pass the option **value**) |
| `myhs_rollback_block` | write | undo a completed block |
| `myhs_update_onboarding` | write | change onboarding fields myhstimeline owns |

Write tools need a **read&write** token. A `403` from a write means the student
issued a read-only token → tell them to generate a read&write token; never retry
silently.

## Profile prefill mapping (`myhs_get_profile` → `profile.json`)

Prefill **missing fields only** — never overwrite an existing value without asking.

| myhstimeline | Admit `profile.json` | Rule |
|---|---|---|
| `onboarding.enrollment_year` (Grade 9 start) | `student.grad_year` | `grad_year = enrollment_year + 4` |
| `onboarding.enrollment_type` = `local` / `domestic` | `student.residency = "domestic"` | |
| `onboarding.enrollment_type` = `international` | `student.residency = "international"` + set `.admissions/config.json` `international: true` | |
| `onboarding.english_first_language` / `english_proficiency` | `testing.english_proficiency` | native → `null`/native; else map `beginner` / `conversational` / `fluent` |
| school → state (if exposed) | `student.state` | |
| `onboarding.goals` contains `college` | (informational — signals admissions engagement) | no field write |

## Reverse writes (confirmation-gated) — enum values must match myhstimeline exactly

`myhs_update_onboarding` touches only fields myhstimeline owns and validates:
`enrollment_type`, `english_first_language`, `english_proficiency`, `goals`,
`enrollment_year`, `last_grade_completed`, `school_id`.

- `enrollment_type ∈ {local, domestic, international}`
- `english_proficiency ∈ {beginner, conversational, fluent}`
- `goals ⊆ {adapt, socialize, college}`

The **primary** write path is `myhs_complete_block` on decisions — not onboarding
writes.

## Label-vs-value rule (decisions)

A decision block's options have a human **label** and a machine **value**. When
completing a decision block, `myhs_complete_block` needs the **value**, not the
label the family said out loud. Resolve it from `myhs_get_timeline` → the block's
`options[]` (each `{label, value}`) before writing. Example: family says
"Local resident" (label) → look up `options[]` → pass `value: "local"` (or whatever
the API returns), never the label string.

## Proposal-table templates

Always confirm before any external write. Apply only the rows the user picks.

```text
Proposed updates to your High School Timeline (myhstimeline):
| Block (grade, type)                     | Action    | Value            |
| Choose enrollment type (G0, decision)   | complete  | "Local resident" |
| Register for the fall SAT (G11, dline)  | mark done | —                |
Apply these 2 updates? (all / pick rows / cancel)
```

For a rollback:

```text
Undo this completed block on myhstimeline?
| Block                          | Action   |
| Register for the fall SAT (G11)| rollback |
Confirm? (yes / no)
```

After any confirmed write, re-pull with `myhs_get_overview` and rewrite the whole
`.admissions/hs_timeline.json` so the local mirror matches. Show any validation
error verbatim; do not retry silently.
