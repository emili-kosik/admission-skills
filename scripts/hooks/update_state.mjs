/**
 * SessionEnd hook: record last_session in the workspace engagement state.
 * Best-effort and silent; any failure exits 0.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { findWorkspace, readStdinJson } from "./common.mjs";

try {
  const input = readStdinJson() || {};
  const cwd = input.cwd || process.cwd();
  const ws = findWorkspace(cwd);
  if (!ws) process.exit(0);

  const cfgPath = join(ws, ".admissions", "config.json");
  const cfg = JSON.parse(readFileSync(cfgPath, "utf8"));
  cfg.state = cfg.state || {};
  cfg.state.last_session = new Date().toISOString().slice(0, 10);
  writeFileSync(cfgPath, JSON.stringify(cfg, null, 2) + "\n", "utf8");
  process.exit(0);
} catch {
  process.exit(0);
}
