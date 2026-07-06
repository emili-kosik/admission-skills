/** Shared helpers for admit plugin hooks (Node stdlib only). */
import { existsSync, readFileSync } from "node:fs";
import { dirname, join, resolve, sep } from "node:path";

/** Read all of stdin synchronously and parse as JSON; null on any failure. */
export function readStdinJson() {
  try {
    const raw = readFileSync(0, "utf8");
    if (!raw.trim()) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

/** Walk up from `start` looking for the workspace marker; null if absent. */
export function findWorkspace(start) {
  try {
    let cur = resolve(start);
    for (;;) {
      if (existsSync(join(cur, ".admissions", "config.json"))) return cur;
      const parent = dirname(cur);
      if (parent === cur) return null;
      cur = parent;
    }
  } catch {
    return null;
  }
}

/** Parse a JSON file; null on any failure. */
export function readJsonSafe(path) {
  try {
    return JSON.parse(readFileSync(path, "utf8"));
  } catch {
    return null;
  }
}

/** Case-insensitive filesystems (NTFS, default APFS) need folded comparisons —
 * otherwise a casing variant like Essays/Drafts/ bypasses path checks while
 * the OS still writes to the real directory. */
const FOLD_CASE = process.platform === "win32" || process.platform === "darwin";

/** Fold a path for comparison on case-insensitive platforms. */
export function foldPath(p) {
  return FOLD_CASE ? p.toLowerCase() : p;
}

/** Path of `file` relative to `root` using forward slashes; null if outside.
 * Containment is checked case-insensitively on win32/darwin; the returned
 * path preserves the original casing. */
export function relForward(root, file) {
  const r = resolve(root) + sep;
  const f = resolve(file);
  if (!foldPath(f).startsWith(foldPath(r))) return null;
  return f.slice(r.length).split(sep).join("/");
}

/** Days from today (local midnight) to an ISO yyyy-mm-dd date. */
export function daysUntil(isoDate, now = new Date()) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(isoDate || "");
  if (!m) return null;
  const target = new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  return Math.round((target - today) / 86400000);
}
