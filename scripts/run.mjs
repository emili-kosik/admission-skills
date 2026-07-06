#!/usr/bin/env node
/**
 * Cross-platform Python launcher for the admit plugin.
 *
 * Usage:  node scripts/run.mjs <script-name-or-path> [args...]
 *         node scripts/run.mjs scorecard_search --name "Stanford"
 *
 * Resolves a working Python >= 3.10 interpreter ("python", then "py -3",
 * then "python3"), sets UTF-8 I/O, and executes the requested script from
 * this plugin's scripts/ directory. This is the only supported way skills
 * invoke the plugin's Python scripts — never call python directly.
 */
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, isAbsolute, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const SCRIPTS_DIR = dirname(fileURLToPath(import.meta.url));
const MIN_VERSION = [3, 10];

const CANDIDATES = [
  { cmd: "python", pre: [] },
  { cmd: "py", pre: ["-3"] },
  { cmd: "python3", pre: [] },
];

// Version check plus an SSL health check: some Windows Python builds fail to
// load the system certificate store (ssl ASN1 errors), which would break every
// API call. Prefer an interpreter whose ssl works; fall back to any
// version-compatible one for offline scripts.
const PROBE_CODE =
  "import sys\n" +
  "ok='%d.%d'%sys.version_info[:2]\n" +
  "try:\n" +
  "    import ssl; ssl.create_default_context(); ssl_ok='1'\n" +
  "except Exception:\n" +
  "    ssl_ok='0'\n" +
  "print(ok+' '+ssl_ok)";

function probe(candidate) {
  const r = spawnSync(candidate.cmd, [...candidate.pre, "-c", PROBE_CODE], {
    encoding: "utf8",
    windowsHide: true,
  });
  if (r.error || r.status !== 0) return null;
  const [version, sslFlag] = (r.stdout || "").trim().split(" ");
  const [maj, min] = (version || "").split(".").map(Number);
  if (Number.isNaN(maj)) return null;
  if (maj > MIN_VERSION[0] || (maj === MIN_VERSION[0] && min >= MIN_VERSION[1])) {
    return { ...candidate, sslOk: sslFlag === "1" };
  }
  return null;
}

function resolvePython() {
  const compatible = [];
  for (const c of CANDIDATES) {
    const ok = probe(c);
    if (!ok) continue;
    if (ok.sslOk) return ok;
    compatible.push(ok);
  }
  return compatible[0] ?? null;
}

function resolveScript(nameOrPath) {
  if (isAbsolute(nameOrPath) && existsSync(nameOrPath)) return nameOrPath;
  const base = nameOrPath.endsWith(".py") ? nameOrPath : `${nameOrPath}.py`;
  const inScripts = join(SCRIPTS_DIR, base);
  if (existsSync(inScripts)) return inScripts;
  const asGiven = resolve(process.cwd(), base);
  if (existsSync(asGiven)) return asGiven;
  return null;
}

const [scriptArg, ...rest] = process.argv.slice(2);
if (!scriptArg) {
  process.stderr.write("usage: node run.mjs <script> [args...]\n");
  process.exit(2);
}

const script = resolveScript(scriptArg);
if (!script) {
  process.stderr.write(JSON.stringify({ error: { code: "script_not_found", script: scriptArg } }) + "\n");
  process.exit(2);
}

const python = resolvePython();
if (!python) {
  process.stderr.write(
    JSON.stringify({
      error: {
        code: "python_not_found",
        message:
          "Python 3.10+ is required but was not found on PATH. Install it from https://www.python.org/downloads/ " +
          "(Windows: check 'Add python.exe to PATH', or use 'py' launcher).",
      },
    }) + "\n"
  );
  process.exit(3);
}

const r = spawnSync(python.cmd, [...python.pre, script, ...rest], {
  stdio: "inherit",
  windowsHide: true,
  env: { ...process.env, PYTHONIOENCODING: "utf-8", PYTHONUTF8: "1" },
});
process.exit(r.status ?? 1);
