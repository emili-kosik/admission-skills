/**
 * PostToolUse hook: essay revision history + word-count feedback.
 *
 * After any Write/Edit under essays/ (excluding .history/), snapshots the new
 * version into essays/.history/ (timestamped) and reports the word count
 * against the essay's limit from essays/index.json when known.
 */
import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { basename, dirname, join } from "node:path";
import { findWorkspace, readJsonSafe, readStdinJson, relForward } from "./common.mjs";

try {
  const input = readStdinJson() || {};
  const filePath = input?.tool_input?.file_path;
  if (!filePath || !filePath.endsWith(".md")) process.exit(0);

  const ws = findWorkspace(dirname(filePath));
  if (!ws) process.exit(0);
  const rel = relForward(ws, filePath);
  if (!rel || !rel.startsWith("essays/") || rel.startsWith("essays/.history/")) process.exit(0);

  // Snapshot. The name keys on the path inside essays/ (drafts__x, feedback__x
  // stay distinct) with millisecond resolution so rapid saves don't overwrite.
  const historyDir = join(ws, "essays", ".history");
  mkdirSync(historyDir, { recursive: true });
  const key = rel.slice("essays/".length).replace(/\.md$/, "").replace(/[\\/]/g, "__");
  const stamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 23);
  copyFileSync(filePath, join(historyDir, `${key}.${stamp}.md`));

  // Word count vs limit (drafts only — feedback memos have no limits).
  if (!rel.startsWith("essays/drafts/")) process.exit(0);
  const text = readFileSync(filePath, "utf8");
  const words = (text.match(/\S+/g) || []).length;
  const index = readJsonSafe(join(ws, "essays", "index.json"));
  const relInEssays = rel.slice("essays/".length);
  const entry = (index?.essays || []).find((e) => e.file === relInEssays);
  const limit = entry?.word_limit;

  let note = `essays/.history snapshot saved. ${rel}: ${words} words`;
  if (limit) {
    const delta = limit - words;
    note += delta >= 0 ? ` (${delta} under the ${limit} limit)` : ` (${-delta} OVER the ${limit} limit)`;
  }
  process.stdout.write(
    JSON.stringify({ hookSpecificOutput: { hookEventName: "PostToolUse", additionalContext: note } })
  );
  process.exit(0);
} catch {
  process.exit(0);
}
