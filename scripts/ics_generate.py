"""Export the workspace timeline as an RFC 5545 .ics calendar (stdlib only).

Usage:
    node scripts/run.mjs ics_generate [--workspace DIR] [--out output/admit-calendar.ics]

Every dated milestone becomes an all-day VEVENT with two VALARMs (7 days and
1 day before). UIDs are stable, so re-importing the file updates events in
place instead of duplicating them. Imports into Google/Apple/Outlook/Proton.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

from lib.workspace import find_workspace, read_json

PRODID = "-//admission-skills//admit 1.0//EN"


def fold(line: str) -> str:
    """RFC 5545 line folding at 75 octets (UTF-8 aware)."""
    encoded = line.encode("utf-8")
    if len(encoded) <= 75:
        return line
    parts, cur = [], b""
    for ch in line:
        b = ch.encode("utf-8")
        limit = 75 if not parts else 74  # continuation lines start with a space
        if len(cur) + len(b) > limit:
            parts.append(cur.decode("utf-8"))
            cur = b
        else:
            cur += b
    parts.append(cur.decode("utf-8"))
    return "\r\n ".join(parts)


def escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:80]


def uid_for(milestone_id: str) -> str:
    """Stable, collision-proof UID: readable slug + a hash of the raw id.

    The slug alone collapses non-ASCII college names (or >80-char twins) to
    identical UIDs, and same-UID VEVENTs get silently merged by calendar apps.
    """
    digest = hashlib.sha256(milestone_id.encode("utf-8")).hexdigest()[:10]
    return f"{slug(milestone_id) or 'milestone'}-{digest}"


def event(uid: str, date: dt.date, summary: str, description: str, dtstamp: str) -> list[str]:
    end = date + dt.timedelta(days=1)
    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}@admission-skills",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART;VALUE=DATE:{date.strftime('%Y%m%d')}",
        f"DTEND;VALUE=DATE:{end.strftime('%Y%m%d')}",
        f"SUMMARY:{escape(summary)}",
    ]
    if description:
        lines.append(f"DESCRIPTION:{escape(description)}")
    for trigger, label in (("-P7D", "1 week"), ("-P1D", "1 day")):
        lines += [
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            f"DESCRIPTION:{escape(summary)} ({label} away)",
            f"TRIGGER:{trigger}",
            "END:VALARM",
        ]
    lines.append("END:VEVENT")
    return lines


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--horizon-days", type=int, default=420)
    args = ap.parse_args(argv)

    ws = Path(args.workspace) if args.workspace else find_workspace()
    if ws is None:
        print(json.dumps({"error": {"code": "no_workspace", "message": "run /admit:start first"}}))
        return 1

    milestones_path = ws / ".admissions" / "milestones.json"
    if not milestones_path.is_file():
        print(json.dumps({"error": {"code": "no_timeline",
                                    "message": "no computed timeline — run timeline_build first (/admit:roadmap)"}}))
        return 1
    doc = read_json(milestones_path)
    generated = dt.date.fromisoformat(doc["generated_at"])
    dtstamp = generated.strftime("%Y%m%dT000000Z")
    horizon = generated + dt.timedelta(days=args.horizon_days)

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:{PRODID}",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        fold("X-WR-CALNAME:College Admissions (admit)"),
    ]
    count = 0
    for m in doc.get("milestones", []):
        if m.get("done") or not m.get("date"):
            continue
        date = dt.date.fromisoformat(m["date"])
        if date > horizon:
            continue
        desc = m.get("action", "")
        if m.get("source_url"):
            desc = f"{desc} Verify: {m['source_url']}" if desc else f"Verify: {m['source_url']}"
        for line in event(uid_for(m["id"]), date, m["title"], desc, dtstamp):
            lines.append(fold(line))
        count += 1
    lines.append("END:VCALENDAR")

    out = Path(args.out) if args.out else ws / "output" / "admit-calendar.ics"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(("\r\n".join(lines) + "\r\n").encode("utf-8"))

    print(json.dumps({"ok": True, "events": count, "out": str(out),
                      "hint": "Import by double-click, or in Google Calendar: Settings -> Import & export."}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
