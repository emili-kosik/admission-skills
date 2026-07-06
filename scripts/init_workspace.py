"""Scaffold a college-planning workspace from templates/ (stdlib only).

Usage:
    node scripts/run.mjs init_workspace [--dir DIR] [--grad-year YYYY] [--force]

Behavior:
  - Refuses to overwrite existing files unless --force.
  - Computes the application cycle from --grad-year (senior-fall year), or
    from today's date if omitted (assumes a current 9th-12th grader is set
    up later via profile).
  - Writes .admissions/config.json LAST so a half-scaffold is never detected
    as a valid workspace by hooks.
  - If the target dir is inside a git repo that isn't the workspace itself,
    prints a warning so the caller can add the workspace to that repo's
    .gitignore.

Output: single JSON document on stdout.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = PLUGIN_ROOT / "templates"

SUBDIRS = [
    "essays/drafts",
    "essays/brainstorm",
    "essays/feedback",
    "essays/.history",
    "aid/award-letters",
    "output",
    ".admissions/cache",
    ".admissions/backups",
]

# template file -> destination (relative to workspace)
FILES = {
    "profile.json": "profile.json",
    "colleges.json": "colleges.json",
    "essays-index.json": "essays/index.json",
    "workspace-gitignore": ".gitignore",
    "WORKSPACE-README.md": "README.md",
}


def compute_cycle(grad_year: int | None, today: dt.date | None = None) -> str:
    """Application cycle string, e.g. 2026-27 = apply fall 2026, enroll fall 2027.

    A student graduating (and enrolling) in `grad_year` applies in the fall of
    grad_year - 1.
    """
    if grad_year is not None:
        apply_year = grad_year - 1
    else:
        today = today or dt.date.today()
        # Without a grad year, assume the upcoming cycle from June onward:
        # a June/July setup is almost always a rising senior preparing for
        # fall applications, and the previous cycle effectively ended May 1.
        apply_year = today.year if today.month >= 6 else today.year - 1
    return f"{apply_year}-{str(apply_year + 1)[-2:]}"


def inside_foreign_git_repo(target: Path) -> Path | None:
    """Return the enclosing git root if target sits inside a repo above it."""
    for parent in target.resolve().parents:
        if (parent / ".git").exists():
            return parent
    return None


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=".", help="workspace directory (default: cwd)")
    ap.add_argument("--grad-year", type=int, default=None)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)

    target = Path(args.dir).resolve()
    marker = target / ".admissions" / "config.json"

    if marker.is_file() and not args.force:
        print(json.dumps({"error": {"code": "already_workspace", "dir": str(target)}}))
        return 1

    existing = [dest for dest in FILES.values() if (target / dest).is_file()]
    if existing and not args.force:
        print(json.dumps({"error": {"code": "files_exist", "files": existing,
                                    "hint": "re-run with --force to overwrite"}}))
        return 1

    target.mkdir(parents=True, exist_ok=True)
    for sub in SUBDIRS:
        (target / sub).mkdir(parents=True, exist_ok=True)

    for src_name, dest_rel in FILES.items():
        shutil.copyfile(TEMPLATES / src_name, target / dest_rel)

    if args.grad_year:
        profile_path = target / "profile.json"
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        profile["student"]["grad_year"] = args.grad_year
        profile_path.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")

    cycle = compute_cycle(args.grad_year)
    config = json.loads((TEMPLATES / "config.json").read_text(encoding="utf-8"))
    config["cycle"] = cycle
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    result = {
        "ok": True,
        "workspace": str(target),
        "cycle": cycle,
        "created": sorted({*FILES.values(), ".admissions/config.json"}),
    }
    git_root = inside_foreign_git_repo(target)
    if git_root is not None:
        result["warning"] = (
            f"Workspace sits inside the git repository at {git_root}. "
            f"Add '{target.name}/' to that repo's .gitignore to keep family data out of it."
        )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
