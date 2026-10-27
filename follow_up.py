#!/usr/bin/env python3
"""Follow-up Email Drafter — an operations helper.

Reads a CSV of pending follow-ups and generates polite, ready-to-send
email drafts for the ones that are overdue or due soon. It never sends
email: it only prints drafts and optionally writes them to a file, so
the user can review and edit each one before sending.

Usage:
    python3 follow_up.py [--input followups.csv] [--output drafts.md]
                         [--as-of YYYY-MM-DD] [--due-within DAYS]

CSV columns (header row required):
    id, contact_name, contact_email, company, topic,
    last_contact_date, due_date, status, notes

Dates use ISO format (YYYY-MM-DD). Rows with status "done" or
"completed" are skipped. Rows without an email address are reported
and skipped instead of producing a broken draft.
"""

import argparse
import csv
import sys
from datetime import date, timedelta
from pathlib import Path


def parse_date(text, field, row_id):
    """Parse an ISO date, raising a clear error for bad input."""
    try:
        return date.fromisoformat(text.strip())
    except (ValueError, AttributeError):
        raise ValueError(
            f"Row {row_id}: invalid {field} date {text!r} "
            "(expected YYYY-MM-DD)"
        ) from None


def load_followups(path):
    """Load follow-up rows from a CSV file."""
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {
            "id", "contact_name", "contact_email", "company", "topic",
            "last_contact_date", "due_date", "status", "notes",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"Missing CSV columns: {', '.join(sorted(missing))}"
            )
        return list(reader)


def classify(row, as_of, due_within):
    """Return 'overdue', 'due-soon', 'upcoming', or 'skip' for a row."""
    if row["status"].strip().lower() in {"done", "completed", "cancelled"}:
        return "skip"
    due = parse_date(row["due_date"], "due_date", row["id"])
    if due < as_of:
        return "overdue"
    if due <= as_of + timedelta(days=due_within):
        return "due-soon"
    return "upcoming"


def draft_email(row, category, as_of):
    """Build a subject line and body for one follow-up row."""
    name = row["contact_name"].strip()
    company = row["company"].strip()
    topic = row["topic"].strip()
    last = row["last_contact_date"].strip()
    due = row["due_date"].strip()
    notes = row["notes"].strip()

    if category == "overdue":
        opener = (
            f"I hope you are well. I am following up on {topic}, "
            f"which we last discussed on {last}."
        )
        ask = (
            "I wanted to check whether there is an update, or anything "
            "you need from my side to move it forward."
        )
    else:  # due-soon
        opener = (
            f"I hope you are well. I am checking in ahead of {due} "
            f"on {topic}, which we last discussed on {last}."
        )
        ask = (
            "Could you let me know if the current timeline still works, "
            "or if anything has changed on your side?"
        )

    lines = [
        f"To: {row['contact_email'].strip()}",
        f"Subject: Follow-up: {topic}" + (f" — {company}" if company else ""),
        "",
        f"Hi {name.split()[0] if name else 'there'},",
        "",
        opener,
        ask,
    ]
    if notes:
        lines += ["", f"Context: {notes}"]
    lines += [
        "",
        "Thanks for your time, and please let me know a good time "
        "to reconnect if that helps.",
        "",
        "Best regards,",
        "Bassam Zafar",
    ]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="followups.csv",
                        help="Input CSV file (default: followups.csv)")
    parser.add_argument("--output", default=None,
                        help="Optional Markdown file to write drafts to")
    parser.add_argument("--as-of", default=None,
                        help="Reference date YYYY-MM-DD (default: today)")
    parser.add_argument("--due-within", type=int, default=3,
                        help="Days ahead that count as due soon (default: 3)")
    args = parser.parse_args(argv)

    as_of = date.fromisoformat(args.as_of) if args.as_of else date.today()

    try:
        rows = load_followups(args.input)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    drafts = []
    skipped = []
    for row in rows:
        category = classify(row, as_of, args.due_within)
        if category == "skip":
            skipped.append((row["id"], "already closed"))
            continue
        if category == "upcoming":
            skipped.append((row["id"], "not due yet"))
            continue
        if not row["contact_email"].strip():
            skipped.append((row["id"], "no email address — draft not made"))
            continue
        drafts.append((row["id"], category, draft_email(row, category, as_of)))

    overdue = sum(1 for _, c, _ in drafts if c == "overdue")
    due_soon = len(drafts) - overdue

    output_lines = [
        f"# Follow-up drafts — as of {as_of.isoformat()}",
        "",
        f"{overdue} overdue, {due_soon} due soon, "
        f"{len(skipped)} skipped (closed, not due yet, or no email).",
        "",
    ]
    for row_id, category, draft in drafts:
        output_lines += [f"## Draft {row_id} ({category})", "", draft, "", "---", ""]

    text = "\n".join(output_lines)
    print(text)

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Wrote {len(drafts)} draft(s) to {args.output}")

    print(f"Summary: {overdue} overdue, {due_soon} due soon, "
          f"{len(skipped)} skipped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
