#!/usr/bin/env python3
"""Calculate lab participation scores from attendance CSVs and autochecker task data.

Usage:
    python calculate.py \
        --tasks tasks-lab03-lab04.csv \
        --task-column lab04_obligatory_passed \
        --attendance "S26-SET-L4-G1-attendance.csv" "S26-SET-L4-G2-attendance.csv" ... \
        --output participation-lab04.csv \
        [--cheaters AleksKornilov07 venimu]

Scoring rules:
    1    = attended AND obligatory_tasks_passed >= 2
    0.5  = attended AND obligatory_tasks_passed == 1
    0.5  = absent   AND obligatory_tasks_passed >= 2
    0    = attended AND obligatory_tasks_passed == 0
    0    = absent   AND obligatory_tasks_passed  < 2
    0    = flagged as cheater (plagiarism detected, case to be filed to DoE)
    ""   = non-student (no group in the tasks file)

Input formats:
    - Tasks CSV: columns must include github_alias, email, group, <task-column>
      (exported from autochecker dashboard or prepared manually)
    - Attendance CSVs: columns "External user field" (email) and "status" (P = present)
      (exported from Moodle / attendance tracking tool)
"""

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path


def load_attendance(files: list[str]) -> set[str]:
    """Return set of lowercase emails marked present (P) across all attendance files."""
    attended = set()
    for fpath in files:
        with open(fpath, "r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                email = (row.get("External user field") or "").strip().lower()
                status = (row.get("status") or "").strip().upper()
                if email and status == "P":
                    attended.add(email)
    return attended


def calculate_participation(
    tasks_file: str,
    task_column: str,
    attendance_files: list[str],
    cheaters: list[str] | None = None,
) -> tuple[list[dict], list[str]]:
    """Calculate participation and return (rows, fieldnames)."""
    attended_emails = load_attendance(attendance_files)
    cheater_set = set(cheaters or [])

    with open(tasks_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    out_fields = ["github_alias", "email", "group", task_column, "attended", "participation", "comment"]
    out_rows = []

    for row in rows:
        email = (row.get("email") or "").strip().lower()
        group = (row.get("group") or "").strip()
        alias = row.get("github_alias", "")
        attended = email in attended_emails
        tasks_passed = int(row.get(task_column, 0))

        att = "YES" if attended else "NO"

        if not group:
            part, comment = "", "non-student"
        elif alias in cheater_set:
            part, comment = "0", "plagiarism detected, case to be filed to DoE"
        elif attended and tasks_passed >= 2:
            part = "1"
            comment = f"attended + {tasks_passed} tasks done (>=2)"
        elif attended and tasks_passed >= 1:
            part = "0.5"
            comment = f"attended but only {tasks_passed} task done (<2)"
        elif not attended and tasks_passed >= 2:
            part = "0.5"
            comment = f"absent but {tasks_passed} tasks done (>=2)"
        elif attended and tasks_passed == 0:
            part = "0"
            comment = "attended but 0 tasks done"
        elif not attended and tasks_passed >= 1:
            part = "0"
            comment = f"absent + only {tasks_passed} task done"
        else:
            part = "0"
            comment = "absent + 0 tasks done"

        out_rows.append({
            "github_alias": alias,
            "email": row.get("email", ""),
            "group": row.get("group", ""),
            task_column: str(tasks_passed),
            "attended": att,
            "participation": part,
            "comment": comment,
        })

    return out_rows, out_fields


def print_summary(rows: list[dict]) -> None:
    """Print score breakdown to stderr."""
    scores = Counter()
    comments = Counter()
    for r in rows:
        if not r["group"].strip():
            continue
        scores[r["participation"]] += 1
        comments[r["comment"]] += 1

    total = sum(scores.values())
    print(f"\nTotal students (with group): {total}", file=sys.stderr)
    print("\nScore breakdown:", file=sys.stderr)
    for score in sorted(scores, key=lambda s: (-float(s) if s else -999)):
        print(f"  {score:>4s}: {scores[score]}", file=sys.stderr)

    print("\nBy comment:", file=sys.stderr)
    for comment, count in comments.most_common():
        print(f"  {count:3d}  {comment}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate lab participation scores.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--tasks", required=True, help="Path to tasks CSV (autochecker export)")
    parser.add_argument("--task-column", required=True, help="Column name for obligatory tasks passed count")
    parser.add_argument("--attendance", required=True, nargs="+", help="Attendance CSV files (Moodle export)")
    parser.add_argument("--output", required=True, help="Output CSV path")
    parser.add_argument("--cheaters", nargs="*", default=[], help="GitHub aliases to flag as plagiarism")
    args = parser.parse_args()

    rows, fields = calculate_participation(
        tasks_file=args.tasks,
        task_column=args.task_column,
        attendance_files=args.attendance,
        cheaters=args.cheaters,
    )

    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print_summary(rows)
    print(f"\nWritten to: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
