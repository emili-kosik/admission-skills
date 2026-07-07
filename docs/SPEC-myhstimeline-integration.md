# SPEC — myhstimeline ⇄ Admit integration (skills work order)

> **Implementation notes (as shipped in v1.1.0):** followed in intent, with three
> adaptations to Admit's real architecture: (1) validation is Admit's hand-rolled
> **non-blocking** `validate_workspace.mjs` (a lenient `validateHsTimeline`
> function, not runtime jsonschema); `data/schemas/hs-timeline.schema.json` is
> documentation + a dev test. (2) No new Python script and no `.mcp.json` — the
> `myhs_*` tools are called at runtime and Claude writes
> `.admissions/hs_timeline.json` directly. (3) A **Round Rock High School (RRISD)
> pilot gate** was layered on top: everywhere the integration is offered it states
> myhstimeline currently serves only Round Rock HS and to skip otherwise.


**Target repository:** `emili-kosik/admission-skills` (the *Admit* Claude Code plugin).
**Drop this file in as:** `docs/SPEC-myhstimeline-integration.md`.
**Depends on:** the `@myhstimeline/mcp` server (this package) and the myhstimeline API endpoints `GET /api/timeline/overview` and `GET|POST|PATCH /api/auth/tokens`, `/api/timeline/*`, `/api/onboarding` (all shipped).

This is a work order for modifying Admit's skills so a student's **myhstimeline high-school timeline** flows into Admit as a distinct "High School Timeline" panel, and — after explicit confirmation — Admit can push decisions back. It follows Admit's existing conventions exactly.

---

## 0. Principles (do not violate)

1. **Optional & early.** Connecting myhstimeline is fully optional; Admit works completely without it. The link is offered **early in `start`**, *before* the manual profile interview, so already-filled myhstimeline data pre-fills the profile and the interview skips known questions (**pull-first-then-prefill**). Decline / no account / no MCP tools → one line, continue normally.
2. **Session-time MCP, never bundled.** Do **not** add a `.mcp.json` or declare an MCP server in `.claude-plugin/plugin.json`. The student runs `claude mcp add` once. The token lives in the **MCP server's** env (`MYHS_TOKEN`), never in Admit's `userConfig`.
3. **Capability probe.** Every myhstimeline action first checks whether the `myhs_*` tools are present in the session. Absent → one line + pointer to `docs/INTEGRATIONS.md`, no nagging.
4. **No silent writes.** Local workspace writes are read-modify-write of the whole file + JSON-schema validated (PostToolUse hook). External writes to myhstimeline happen **only** after the user confirms an explicit proposal table. Never auto-apply.
5. **Sources stay separate.** myhstimeline milestones render as their **own section**; never merged into `.admissions/milestones.json` or the admissions section of `timeline.md`.
6. **Essays untouched.** No change to the `essays/drafts/**` protections.

---

## 1. MCP tools this integration relies on

Read: `myhs_get_overview`, `myhs_get_profile`, `myhs_get_timeline`.
Write (needs a read&write token): `myhs_complete_block`, `myhs_rollback_block`, `myhs_update_onboarding`.

Connection command the student runs (surface it verbatim in `start` and `docs/INTEGRATIONS.md`):

```bash
claude mcp add --transport stdio --scope user myhstimeline \
  --env MYHS_API_URL=https://api.myhstimeline.com \
  --env MYHS_TOKEN=<token from myhstimeline app → Settings → Connect external tools> \
  -- npx -y @myhstimeline/mcp
```

---

## 2. New workspace file: `.admissions/hs_timeline.json`

Written by `sync` from `myhs_get_overview`. Mirrors the overview endpoint + sync metadata.

```json
{
  "schema_version": 1,
  "source": "myhstimeline",
  "synced_at": "2026-07-06",
  "student":  { "current_grade": "Grade 11", "enrollment_year": 2023 },
  "progress": { "completed": 34, "total": 58, "percent": 59 },
  "current":  { "grade_year": 11, "block_id": 210, "title": "Register for the fall SAT" },
  "phases": [
    { "grade_year": 0, "label": "Before Grade 9", "status": "done",
      "milestones": [
        { "id": 5, "title": "Choose enrollment type", "type": "decision",
          "status": "done", "chose": "Local resident", "due": null }
      ] },
    { "grade_year": 11, "label": "Grade 11", "status": "current",
      "milestones": [
        { "id": 210, "title": "Register for the fall SAT", "type": "time_sensitive",
          "status": "current", "due": "2026-09-15" }
      ] }
  ]
}
```

### 2a. New schema file: `data/schemas/hs-timeline.schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "hs_timeline",
  "type": "object",
  "required": ["schema_version", "source", "phases"],
  "additionalProperties": false,
  "properties": {
    "schema_version": { "const": 1 },
    "source": { "const": "myhstimeline" },
    "synced_at": { "type": "string" },
    "student": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "current_grade": { "type": ["string", "null"] },
        "enrollment_year": { "type": ["integer", "null"] }
      }
    },
    "progress": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "completed": { "type": "integer" },
        "total": { "type": "integer" },
        "percent": { "type": "integer" }
      }
    },
    "current": {
      "type": ["object", "null"],
      "additionalProperties": false,
      "properties": {
        "grade_year": { "type": ["integer", "null"] },
        "block_id": { "type": "integer" },
        "title": { "type": "string" }
      }
    },
    "phases": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["label", "status", "milestones"],
        "additionalProperties": false,
        "properties": {
          "grade_year": { "type": ["integer", "null"] },
          "label": { "type": "string" },
          "status": { "enum": ["done", "current", "upcoming"] },
          "milestones": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["id", "title", "type", "status"],
              "additionalProperties": false,
              "properties": {
                "id": { "type": "integer" },
                "title": { "type": "string" },
                "type": { "enum": ["info", "decision", "time_sensitive"] },
                "status": { "enum": ["done", "current", "upcoming"] },
                "chose": { "type": ["string", "null"] },
                "due": { "type": ["string", "null"] }
              }
            }
          }
        }
      }
    }
  }
}
```

### 2b. Register the schema in the validation hook

In `scripts/hooks/validate_workspace.mjs`, add `.admissions/hs_timeline.json` → `hs-timeline.schema.json` to the file→schema map used to re-validate on every write. (Same mechanism used for `profile.json`, `colleges.json`, etc.)

---

## 3. `skills/sync/SKILL.md` — new Tier-1 section "myhstimeline (High School Timeline)"

### Frontmatter
Extend `description` trigger phrases with: `"connect myhstimeline"`, `"sync my high school timeline"`, `"pull my timeline"`, `"update my timeline"`, `"я сделал выбор в таймлайне"`, `"обнови мой таймлайн"`. Extend `argument-hint` to include `myhs`.

### Body — add this section (after the Notion section)

> **myhstimeline (High School Timeline)** — bidirectional, capability-probed.
>
> **Probe.** If the `myhs_get_overview` tool is not present in this session, say in one line: *"myhstimeline isn't connected — see docs/INTEGRATIONS.md to connect it."* and stop. Never nag.
>
> **Pull (read).** Call `myhs_get_overview`. Read-modify-write the whole `.admissions/hs_timeline.json` with the returned overview plus `"source":"myhstimeline"` and today's `synced_at` (passed in — do not invent dates). On first link, also call `myhs_get_profile` and offer the profile prefill from §6. Then tell the user: *"Pulled — run /admit:roadmap to see your High School Timeline panel."*
>
> **Push (write) — confirmation-gated.** When, during the session, the family makes a decision that maps to a myhstimeline block (chose an enrollment type; finished a deadline milestone; changed onboarding), build a **proposal table** and apply only the rows the user confirms:
>
> ```
> Proposed updates to your High School Timeline (myhstimeline):
> | Block (grade, type)                    | Action    | Value            |
> | Choose enrollment type (G0, decision)  | complete  | "Local resident" |
> | Register for the fall SAT (G11, dline) | mark done | —                |
> Apply these 2 updates? (all / pick rows / cancel)
> ```
>
> On confirmation, call `myhs_complete_block` / `myhs_rollback_block` / `myhs_update_onboarding` for the chosen rows, then re-pull to refresh `.admissions/hs_timeline.json`. For a decision block, resolve the option's **`value`** (not its label) from `myhs_get_timeline`'s `options[]` before calling `myhs_complete_block`. If a write returns a validation error, show it verbatim and do not retry silently. Never write without confirmation; never write when only a read token is present (a 403 means the student issued a read-only token — tell them to generate a read&write token).

### Persistence contract (update the section)
Add: *Writes `.admissions/hs_timeline.json` (whole-file, via myhstimeline pull). External writes to myhstimeline happen only after the user confirms exact rows. Reads `.admissions/hs_timeline.json`, `profile.json`.*

### Reference file — new `skills/sync/references/myhstimeline-recipes.md`
Contains: the exact tool list, the field-mapping table (§6), the proposal-table templates above, and the **label-vs-value rule** for decision options.

---

## 4. `skills/roadmap/SKILL.md` — render a separate HS panel

After the skill builds its own `.admissions/milestones.json`, if `.admissions/hs_timeline.json` exists, append a **separate section** to `timeline.md` (do not merge into the admissions milestones):

```
## High School Timeline  (from myhstimeline — updated {synced_at})

### Grade 11  ← you are here
- [x] Choose enrollment type → Local resident
- [»] Register for the fall SAT            (due 2026-09-15)   ← current
- [ ] Shortlist colleges

Overall: 34/58 milestones (59%)
```

Render rules: iterate `phases` in order; per milestone, `done → [x]`, `current → [»]`, `upcoming → [ ]`; append `→ {chose}` for decisions, `(due {due})` where present; mark the phase whose `status == current` with `← you are here`. Do not pull these into the admissions section.

### Persistence contract (update)
Add: *Reads `.admissions/hs_timeline.json` (if present) and renders a separate "High School Timeline" section in `timeline.md`.*

---

## 5. `skills/start/SKILL.md` — early optional link + prefill

Insert a step **immediately after operator-verification and before the 8-step profile interview**:

> **Step: Connect myhstimeline (optional).** Ask: *"Do you already use myhstimeline? You can connect it now so I don't re-ask what it already knows — or skip."*
> - **Yes/connect:** show the `claude mcp add` command (from §1). Once the `myhs_*` tools are present, immediately call `myhs_get_profile` + `myhs_get_overview`; write `.admissions/hs_timeline.json`; **prefill** `profile.json` per §6 (missing fields only, never overwrite without asking). Then run the profile interview but **skip questions already answered** (grad_year, residency, state, English proficiency may arrive pre-filled).
> - **Skip / no account / tools absent:** say *"No problem — you can connect later with /admit:sync"* and continue the normal interview. Nothing is blocked.
> - Cross-skill delegation: *"…then /admit:sync to keep it current, /admit:roadmap to view the High School Timeline panel."*

### Persistence contract (update)
Add: *May write `.admissions/hs_timeline.json` and prefill `profile.json` from myhstimeline (missing fields only) when the student links their account.*

---

## 6. Field mapping (`references/myhstimeline-recipes.md`)

| myhstimeline (`myhs_get_profile`) | Admit `profile.json` | Rule |
|---|---|---|
| `onboarding.enrollment_year` (Grade 9 start) | `student.grad_year` | `grad_year = enrollment_year + 4` |
| `onboarding.enrollment_type` `local`/`domestic` | `student.residency = "domestic"` | |
| `onboarding.enrollment_type` `international` | `student.residency = "international"`; set `config.international = true` | |
| `onboarding.english_first_language` / `english_proficiency` | `testing.english_proficiency` | native → `null`/native; else map `beginner`/`conversational`/`fluent` |
| school → state (if exposed) | `student.state` | |
| `onboarding.goals` contains `college` | signals admissions engagement | informational |

**Reverse writes** (`myhs_update_onboarding`, confirmation-gated) touch only fields myhstimeline owns and validates: `enrollment_type`, `english_first_language`, `english_proficiency`, `goals`, `enrollment_year`, `last_grade_completed`, `school_id`. Enum values must match myhstimeline exactly (`enrollment_type ∈ {local,domestic,international}`, `english_proficiency ∈ {beginner,conversational,fluent}`, `goals ⊆ {adapt,socialize,college}`). The primary write path is `myhs_complete_block` on decisions, not onboarding writes.

---

## 7. `skills/checkin/SKILL.md` — weave HS milestones into the weekly picks

When choosing the 3 weekly actions, also consider the `current` milestone and nearest `upcoming` milestones from `.admissions/hs_timeline.json`, alongside admissions deadlines. Persistence contract is unchanged (still writes only `.admissions/config.json` state); add `.admissions/hs_timeline.json` to **Reads**.

---

## 8. `scripts/hooks/session_start.mjs` — surface the current HS focus

In the ≤12-line briefing, if `.admissions/hs_timeline.json` exists, add up to two lines:
- the current focus: `current.title` (+ `due` if within the horizon);
- optionally `HS timeline {percent}% complete`.

Keep it silent and idempotent; on any internal error `exit 0` (never break a session), exactly like the other hooks. This gives a "check-in"-style nudge for the myhstimeline side.

---

## 9. `docs/INTEGRATIONS.md` — new subsection

Add "**myhstimeline (High School Timeline)**": what it is (a student's structured HS milestone timeline), the `claude mcp add` command (§1), why the token lives in the MCP server config and not Admit's `userConfig`, the read/write model with confirmation gates, and a pointer to `skills/sync/references/myhstimeline-recipes.md`. Note it is optional and layered, like every other integration.

---

## 10. (Optional) `agents/hs-timeline-mapper.md`

If mapping free-text family decisions to `block_id` + option `value` gets non-trivial, add a small read-only agent (frontmatter per Admit's convention: `tools: Read` + the `myhs_*` read tools, `model: sonnet`, `maxTurns: 15`). It returns the proposed `{block_id, selected_option}` rows; the calling `sync` skill renders the proposal table and performs the confirmed writes. Start inline in `sync`; extract to an agent only if warranted.

---

## 11. Acceptance criteria

1. Fresh workspace, no MCP → `start`/`sync`/`roadmap` behave exactly as today (one-line "not connected" where relevant). No regressions.
2. `claude mcp add … @myhstimeline/mcp` with a valid token, then `/admit:sync` → `.admissions/hs_timeline.json` is written and passes `hs-timeline.schema.json` validation.
3. `/admit:roadmap` → `timeline.md` contains a separate "High School Timeline" section with `← you are here` on the current phase; admissions milestones are unchanged and unmixed.
4. In `start`, linking a myhstimeline account prefills `profile.json` (grad_year/residency/etc.) and the interview skips those questions.
5. A family decision → `sync` shows a proposal table; on confirm, `myhs_complete_block` runs (decision uses the option **value**), the block completes in myhstimeline, and a re-pull reflects it. A read-only token yields a clear "need read&write token" message, not a silent failure.
6. Session start with a linked workspace shows the current HS focus line in the briefing.
