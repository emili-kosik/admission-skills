/**
 * PostToolUse hook: schema-lite validation of workspace JSON files.
 *
 * Fires after Write/Edit. Fast-exits unless the touched file is one of the
 * structured workspace files. NON-BLOCKING by design: instead of failing the
 * tool call (which the user sees as a scary "hook error"), it exits 0 and, when
 * it finds a problem, emits a quiet additionalContext note so Claude can
 * self-correct on the next turn. Silent when everything is fine.
 *
 * Lenient during onboarding: fields that simply aren't filled in yet (null /
 * absent) are never flagged — only present-but-invalid values are.
 *
 * Deliberately dependency-free: structural checks in plain JS, not jsonschema.
 */
import { readFileSync } from "node:fs";
import { basename, dirname } from "node:path";
import { findWorkspace, foldPath, readStdinJson, relForward } from "./common.mjs";

const COLLEGE_STATUSES = new Set([
  "researching", "applying", "essays_in_progress", "ready_to_submit",
  "submitted", "decision_pending", "accepted", "denied", "waitlisted",
  "deferred", "enrolled", "declined",
]);
const SYSTEMS = new Set(["common_app", "uc", "csu", "applytexas", "coalition_scoir", "institutional"]);
const CATEGORIES = new Set([null, "reach", "match", "safety"]);
const PLANS = new Set([null, "ED", "ED2", "EA", "REA", "RD", "rolling", "uc_filing", "csu_filing"]);
const TEST_POLICIES = new Set([null, "required", "optional", "flexible", "free"]);
const ADMISSION_TYPES = new Set([null, "rolling", "priority", "rounds", "wave", "unknown"]);
const ESSAY_STATUSES = new Set([undefined, "brainstorming", "drafting", "in_review", "revising", "final"]);
const OPERATORS = new Set(["parent", "student_18plus"]);
const HS_MILESTONE_TYPES = new Set(["info", "decision", "time_sensitive"]);
const HS_STATUSES = new Set(["done", "current", "upcoming"]);
const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;

function validateColleges(doc, note) {
  if (!Array.isArray(doc.colleges)) return note("colleges.json: 'colleges' must be an array");
  doc.colleges.forEach((c, i) => {
    const tag = `colleges.json entry ${i} (${c?.name || "unnamed"})`;
    if (!c || typeof c.name !== "string" || !c.name.trim()) return note(`${tag}: 'name' is required`);
    if (c.system != null && !SYSTEMS.has(c.system)) note(`${tag}: system '${c.system}' not one of ${[...SYSTEMS].join("|")}`);
    if (c.status != null && !COLLEGE_STATUSES.has(c.status)) note(`${tag}: status '${c.status}' not one of ${[...COLLEGE_STATUSES].join("|")}`);
    if (c.category !== undefined && !CATEGORIES.has(c.category)) note(`${tag}: category '${c.category}' invalid`);
    if (c.plan !== undefined && !PLANS.has(c.plan)) note(`${tag}: plan '${c.plan}' invalid`);
    if (c.test_policy !== undefined && !TEST_POLICIES.has(c.test_policy)) note(`${tag}: test_policy '${c.test_policy}' invalid`);
    if (c.deadline != null && !ISO_DATE.test(c.deadline)) note(`${tag}: deadline '${c.deadline}' must be YYYY-MM-DD`);
    if (c.recommended_submit_by != null && !ISO_DATE.test(c.recommended_submit_by)) note(`${tag}: recommended_submit_by '${c.recommended_submit_by}' must be YYYY-MM-DD`);
    if (c.priority_date != null && !ISO_DATE.test(c.priority_date)) note(`${tag}: priority_date '${c.priority_date}' must be YYYY-MM-DD`);
    if (c.admission_type !== undefined && !ADMISSION_TYPES.has(c.admission_type)) note(`${tag}: admission_type '${c.admission_type}' not one of ${[...ADMISSION_TYPES].join("|")}`);
    if (c.unitid != null && !Number.isInteger(c.unitid)) note(`${tag}: unitid must be an integer`);
  });
}

function validateProfile(doc, note) {
  // operator may be unset mid-onboarding; only flag a present, invalid value.
  if (doc.operator != null && !OPERATORS.has(doc.operator)) {
    note(`profile.json: operator '${doc.operator}' should be parent or student_18plus`);
  }
  const gy = doc?.student?.grad_year;
  if (gy != null && (!Number.isInteger(gy) || gy < 2024 || gy > 2040)) {
    note(`profile.json: student.grad_year '${gy}' should be a year between 2024 and 2040 (a number, not a string)`);
  }
  const flat = JSON.stringify(doc).toLowerCase();
  for (const key of ["birthdate", "ssn", "dob", "address"]) {
    if (flat.includes(`"${key}"`)) {
      note(`profile.json: remove '${key}' — the profile is PII-minimized by design (keep it out of the file)`);
    }
  }
}

function validateEssaysIndex(doc, note) {
  if (!Array.isArray(doc.essays)) return note("essays/index.json: 'essays' must be an array");
  doc.essays.forEach((e, i) => {
    if (!e || typeof e.file !== "string") return note(`essays/index.json entry ${i}: 'file' is required`);
    if (typeof e.target !== "string" || !e.target) note(`essays/index.json entry ${i}: 'target' is required`);
    if (!ESSAY_STATUSES.has(e.status)) note(`essays/index.json entry ${i}: status '${e.status}' invalid`);
  });
}

function validateConfig(doc, note) {
  if (doc.cycle != null && !/^\d{4}-\d{2}$/.test(doc.cycle)) {
    note(`.admissions/config.json: cycle '${doc.cycle}' should look like 2026-27`);
  }
}

function validateHsTimeline(doc, note) {
  if (doc.source !== "myhstimeline") {
    note('.admissions/hs_timeline.json: source should be "myhstimeline" (it mirrors the myhstimeline overview)');
  }
  if (!Array.isArray(doc.phases)) {
    return note(".admissions/hs_timeline.json: 'phases' must be an array");
  }
  doc.phases.forEach((p, i) => {
    const tag = `.admissions/hs_timeline.json phase ${i} (${p?.label || "unlabeled"})`;
    if (p.status != null && !HS_STATUSES.has(p.status)) note(`${tag}: status '${p.status}' not one of ${[...HS_STATUSES].join("|")}`);
    if (!Array.isArray(p.milestones)) return note(`${tag}: 'milestones' must be an array`);
    p.milestones.forEach((m, j) => {
      const mt = `${tag} milestone ${j}`;
      if (m.type != null && !HS_MILESTONE_TYPES.has(m.type)) note(`${mt}: type '${m.type}' not one of ${[...HS_MILESTONE_TYPES].join("|")}`);
      if (m.status != null && !HS_STATUSES.has(m.status)) note(`${mt}: status '${m.status}' not one of ${[...HS_STATUSES].join("|")}`);
      if (m.due != null && !ISO_DATE.test(m.due)) note(`${mt}: due '${m.due}' must be YYYY-MM-DD`);
    });
  });
}

function emit(issues) {
  if (issues.length === 0) return; // silent when all good
  const msg = "admit workspace check (fix quietly, do not show the user code): " + issues.join("; ") + ".";
  process.stdout.write(
    JSON.stringify({ hookSpecificOutput: { hookEventName: "PostToolUse", additionalContext: msg } })
  );
}

try {
  const input = readStdinJson() || {};
  const filePath = input?.tool_input?.file_path;
  if (!filePath) process.exit(0);

  // Fold names so a casing variant (Profile.json on NTFS) is still checked.
  const name = foldPath(basename(filePath));
  const interesting = new Set(["profile.json", "colleges.json", "index.json", "config.json", "hs_timeline.json"]);
  if (!interesting.has(name)) process.exit(0);

  const ws = findWorkspace(dirname(filePath));
  if (!ws) process.exit(0);
  const rel = relForward(ws, filePath);
  if (!rel) process.exit(0);
  const relCmp = foldPath(rel);

  const issues = [];
  const note = (m) => issues.push(m);

  let doc;
  try {
    doc = JSON.parse(readFileSync(filePath, "utf8"));
  } catch (e) {
    // Never block — just nudge Claude to repair the JSON on the next turn.
    emit([`${rel} is not valid JSON (${e.message}); rewrite the whole file with valid JSON`]);
    process.exit(0);
  }

  if (relCmp === "colleges.json") validateColleges(doc, note);
  else if (relCmp === "profile.json") validateProfile(doc, note);
  else if (relCmp === "essays/index.json") validateEssaysIndex(doc, note);
  else if (relCmp === ".admissions/config.json") validateConfig(doc, note);
  else if (relCmp === ".admissions/hs_timeline.json") validateHsTimeline(doc, note);

  emit(issues);
  process.exit(0);
} catch {
  process.exit(0);
}
