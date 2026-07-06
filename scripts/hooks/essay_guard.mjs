/**
 * PreToolUse hook: the essay integrity guard.
 *
 * Blocks writes targeting essays/drafts/** inside an admit workspace:
 *  - Write/Edit/MultiEdit via tool_input.file_path
 *  - NotebookEdit via tool_input.notebook_path
 *  - Bash commands that mention an essays/drafts path together with a
 *    write-ish operation (redirect, tee, cp/mv/copy/move, Set-Content, ...)
 *
 * Essay drafts are student-authored only — the Common App fraud policy treats
 * submitting AI-generated essay content as application fraud. Claude writes
 * critique to essays/feedback/ and brainstorm notes to essays/brainstorm/.
 *
 * Path comparisons are case-folded on case-insensitive filesystems.
 * Any internal error exits 0 (never blocks unrelated work by accident).
 */
import { findWorkspace, foldPath, readStdinJson, relForward } from "./common.mjs";
import { dirname } from "node:path";

const DENY_REASON =
  "Blocked by the admit plugin: files under essays/drafts/ are student-authored only. " +
  "Submitting AI-generated essay content is application fraud under the Common App fraud policy. " +
  "Write critique memos to essays/feedback/ or brainstorm notes to essays/brainstorm/ instead, " +
  "and let the student edit their own draft.";

const BASH_WRITE_HINT =
  /(>|>>|\btee\b|\bcp\b|\bmv\b|\bcopy\b|\bmove\b|\btouch\b|\bnew-item\b|set-content|out-file|add-content)/i;

function deny() {
  process.stdout.write(
    JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: DENY_REASON,
      },
    })
  );
  process.exit(0);
}

function isDraftPath(filePath) {
  const ws = findWorkspace(dirname(filePath));
  if (!ws) return false;
  const rel = relForward(ws, filePath);
  return !!rel && foldPath(rel).startsWith("essays/drafts/");
}

try {
  const input = readStdinJson() || {};
  const toolInput = input.tool_input || {};

  if (input.tool_name === "Bash") {
    const command = String(toolInput.command || "");
    const folded = foldPath(command).replace(/\\/g, "/");
    if (folded.includes("essays/drafts") && BASH_WRITE_HINT.test(command)) deny();
    process.exit(0);
  }

  const filePath = toolInput.file_path || toolInput.notebook_path;
  if (filePath && isDraftPath(filePath)) deny();
  process.exit(0);
} catch {
  process.exit(0);
}
