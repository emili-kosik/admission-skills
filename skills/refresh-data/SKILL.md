---
name: refresh-data
description: >
  Refresh the plugin's bundled datasets (deadlines, test policies, test dates,
  essay prompts, AI policies, and more) from the GitHub repo without a plugin
  update. Use when the user says "refresh data", "update the datasets", "the
  deadlines look stale", "get the latest data", or invokes /admit:refresh-data.
disable-model-invocation: true
---

# Refresh data — pull the latest bundled datasets

Side-effectful and user-invoked only. Never run this on your own initiative.

## Steps

1. Explain what will happen before doing it, in 2-3 lines: the command downloads
   the current `data/*.json` files from the plugin's GitHub repo into
   `CLAUDE_PLUGIN_DATA` (persists across plugin updates; preferred by every
   script and skill). Bundled files stay untouched as the fallback. Nothing in
   the family's workspace is modified.
2. Run: `node ${CLAUDE_PLUGIN_ROOT}/scripts/run.mjs refresh_data`
   (add `--branch <name>` only if the user explicitly asks for a non-main branch).
3. From the JSON `report`, render an old → new diff table:

   ```
   | File | Old cycle | New cycle | Old verified | New verified | Status |
   ```

   Use each entry's `old`/`new` `{cycle, last_verified}`; for `failed`/`rejected`
   rows show the error instead. If `ok` is false, say which files kept their
   previous data (the fallback still works — nothing broke).
4. Set expectations about what "fresh" means here:
   - Deadlines derive from the Common App Requirements Grid, which is typically
     re-issued mid-cycle as members correct their entries — refreshing again
     later in the season can pick up real changes. Verify any deadline the family
     will act on at the grid (`sources.json` → `common_app.requirements_grid_pdf`)
     or the college's own page.
   - Each August, when the new application cycle typically opens, the whole
     dataset family rolls to the new cycle. If `_meta.cycle` still shows last
     cycle in September, refresh again or update the plugin.

## If the script returns `no_plugin_data`

`CLAUDE_PLUGIN_DATA` is not set, so there is nowhere persistent to put the
files. Relay the script's message and offer the alternative: update the plugin
itself, which ships the same refreshed datasets bundled.

## Cross-skill delegation

- "Where does this number come from?" / dataset provenance → `data-sources`
- Deadline changes after a refresh (re-render the board, re-export calendar) → `tracker`
- Test-date changes affecting the plan → `testing-plan`

## Persistence contract

Writes: `$CLAUDE_PLUGIN_DATA/data/*.json` (via the `refresh_data` script only —
never directly). Reads: `data/*.json` `_meta` blocks for the diff. Never touches
workspace files; never writes `essays/drafts/**`.
