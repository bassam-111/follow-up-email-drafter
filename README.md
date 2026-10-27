# Follow-up Email Drafter

A small, runnable operations tool for Bassam Zafar (Operations Executive, BS AI).
It reads a CSV of pending follow-ups and generates polite, ready-to-review
email drafts for the items that are overdue or due soon.

**It never sends email.** It only drafts, so every message can be reviewed
and edited before it goes out — the same review-first habit used for
operations follow-ups and vendor coordination.

## What it does

- Reads `followups.csv`: contact, company, topic, last contact date, due date, status, notes
- Classifies each row as **overdue**, **due soon** (within 3 days by default),
  **upcoming**, or **closed**
- Skips closed rows, rows not due yet, and rows with no email address — and says why
- Generates a subject line and a short, polite follow-up body for each draft,
  referencing the topic, last contact date, and notes
- Prints drafts to the terminal and, with `--output`, saves them as Markdown

## How to run

Requires Python 3.10+ only — no external packages to install.

```bash
python3 follow_up.py --as-of 2026-10-27 --output drafts.md
```

Options:

- `--input followups.csv` — a different CSV file
- `--output drafts.md` — also write drafts to a Markdown file
- `--as-of YYYY-MM-DD` — reference date (defaults to today)
- `--due-within 3` — how many days ahead counts as "due soon"

## Sample data

`followups.csv` includes 5 sample rows covering every case: one overdue,
one due soon, one upcoming, one already closed, and one with no email address.

## Sample output

```
# Follow-up drafts — as of 2026-10-27

1 overdue, 1 due soon, 3 skipped (closed, not due yet, or no email).

## Draft 1 (overdue)

To: ayesha@example.com
Subject: Follow-up: Delivery schedule confirmation — Northwind Traders

Hi Ayesha,

I hope you are well. I am following up on Delivery schedule confirmation,
which we last discussed on 2026-10-15.
I wanted to check whether there is an update, or anything you need from
my side to move it forward.

Context: Waiting on final delivery slots
...
Summary: 1 overdue, 1 due soon, 3 skipped.
```

## Test result

Tested 2026-10-27 with:

```bash
python3 follow_up.py --as-of 2026-10-27 --output drafts.md
```

Exit code 0. Output: 1 overdue draft, 1 due-soon draft, 3 skipped
(1 closed, 1 not due yet, 1 no email address), and `drafts.md` written
with 2 drafts.

## Skills used

Python (standard library only), CSV handling, CLI design — all within
the resume's stated skills. No external services, no claimed expertise
beyond that.
