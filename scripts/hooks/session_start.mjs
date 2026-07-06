/**
 * SessionStart hook: the "what's next" digest.
 *
 * Silent (exit 0, no output) unless the session's cwd is inside an admit
 * workspace. Otherwise injects a compact briefing (≤12 lines) as
 * additionalContext: upcoming deadlines, overdue items, stale essay drafts,
 * check-in nudge, and dataset staleness warnings.
 *
 * Any internal error exits 0 silently — a hook must never break a session.
 */
import { readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { daysUntil, findWorkspace, readJsonSafe, readStdinJson } from "./common.mjs";

const HORIZON_DAYS = 21;
const STALE_DRAFT_DAYS = 14;
const STALE_LIST_DAYS = 60;
const CHECKIN_NUDGE_DAYS = 7;

function pluralDays(n) {
  if (n === 0) return "today";
  if (n === 1) return "in 1 day";
  if (n === -1) return "1 day OVERDUE";
  if (n < 0) return `${-n} days OVERDUE`;
  return `in ${n} days`;
}

try {
  const input = readStdinJson() || {};
  const cwd = input.cwd || process.cwd();
  const ws = findWorkspace(cwd);
  if (!ws) process.exit(0);

  const config = readJsonSafe(join(ws, ".admissions", "config.json")) || {};
  const colleges = readJsonSafe(join(ws, "colleges.json"));
  const milestones = readJsonSafe(join(ws, ".admissions", "milestones.json"));
  const lines = [];

  // 1. College submission targets within the horizon. Prefer the strategic
  //    recommended-submit date (rolling/wave/priority review) over the deadline.
  const openStatuses = new Set(["researching", "applying", "essays_in_progress", "ready_to_submit"]);
  const due = [];
  for (const c of colleges?.colleges || []) {
    if (!openStatuses.has(c.status)) continue;
    const strategic = c.recommended_submit_by && c.recommended_submit_by !== c.deadline;
    const target = c.recommended_submit_by || c.deadline;
    const d = daysUntil(target);
    if (d === null || d > HORIZON_DAYS) continue;
    if (strategic) {
      due.push({ d, text: `${c.name} — recommended submit ${pluralDays(d)} (earlier than the deadline; rolling/priority review)` });
    } else {
      const verify = c.deadline_verified ? "" : " (unverified — check the college's page)";
      due.push({ d, text: `${c.name} ${c.plan || ""} deadline ${pluralDays(d)}${verify}` });
    }
  }
  // 2. Computed milestones within the horizon.
  for (const m of milestones?.milestones || []) {
    if (m.done) continue;
    const d = daysUntil(m.date);
    if (d === null || d > HORIZON_DAYS || d < -7) continue;
    due.push({ d, text: `${m.title} ${pluralDays(d)}` });
  }
  due.sort((a, b) => a.d - b.d);
  for (const item of due.slice(0, 6)) lines.push(`- ${item.text}`);

  // 3. Stale essay drafts.
  try {
    const draftsDir = join(ws, "essays", "drafts");
    const now = Date.now();
    for (const f of readdirSync(draftsDir)) {
      if (!f.endsWith(".md")) continue;
      const ageDays = (now - statSync(join(draftsDir, f)).mtimeMs) / 86400000;
      if (ageDays > STALE_DRAFT_DAYS) {
        lines.push(`- Draft essays/drafts/${f} untouched for ${Math.floor(ageDays)} days`);
      }
    }
  } catch {
    /* no drafts dir yet */
  }

  // 4. List review staleness.
  const lastReview = colleges?.last_list_review;
  if (lastReview) {
    const untilReview = daysUntil(lastReview);
    const age = untilReview === null ? null : -untilReview;
    if (age !== null && age > STALE_LIST_DAYS) {
      lines.push(`- College list last reviewed ${age} days ago — worth a /admit:college-list refresh`);
    }
  }

  // 5. Check-in nudge + next actions from last check-in. A malformed
  // last_checkin date must nudge, not silently suppress (daysUntil -> null).
  const state = config.state || {};
  const untilCheckin = state.last_checkin ? daysUntil(state.last_checkin) : null;
  const sinceCheckin = untilCheckin === null ? null : -untilCheckin;
  if (sinceCheckin === null || sinceCheckin > CHECKIN_NUDGE_DAYS) {
    lines.push("- Weekly check-in due — /admit:checkin (10 minutes)");
  }
  for (const action of (state.next_actions || []).slice(0, 3)) {
    lines.push(`- Next action: ${action}`);
  }

  // 6. Dataset staleness (bundled data cycle vs workspace cycle).
  const deadlinesData = readJsonSafe(join(process.env.CLAUDE_PLUGIN_ROOT || "", "data", "deadlines.json"));
  const dataCycle = deadlinesData?._meta?.cycle;
  if (dataCycle && config.cycle && dataCycle !== config.cycle) {
    lines.push(`- Bundled deadline data is for cycle ${dataCycle}, workspace is ${config.cycle} — run /admit:refresh-data`);
  }

  if (lines.length === 0) process.exit(0);

  const header = `[admit] College planning workspace detected (cycle ${config.cycle || "?"}). Briefing:`;
  const context = [header, ...lines.slice(0, 11)].join("\n");
  process.stdout.write(
    JSON.stringify({
      hookSpecificOutput: { hookEventName: "SessionStart", additionalContext: context },
    })
  );
  process.exit(0);
} catch {
  process.exit(0);
}
