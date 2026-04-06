#!/usr/bin/env python3
"""Calculate lab participation scores from attendance CSVs and autochecker task data.

Usage:
    python calculate.py \
        --tasks autochecker-lab-05-2026-03-14.csv \
        --task-columns task-1 task-2 \
        --threshold 75 \
        --attendance "Week 6/S26-SET-L5-G1-attendance.csv" ... \
        --output participation-lab05.csv \
        [--cheaters AleksKornilov07 venimu]

Scoring rules (per course syllabus):
    1    = attended AND all required tasks >= threshold
    0.5  = absent   AND all required tasks >= threshold
    0    = attended but tasks not completed
    0    = absent and tasks not completed
    0    = flagged as cheater
    ""   = non-student (no group in the tasks file)

Input formats:
    - Tasks CSV: autochecker dashboard export with columns like
      "100.0% (9/9)" or just a number. Script parses percentage from the value.
    - Attendance CSVs: columns "External user field" (email) and "status" (P = present)
"""

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path


def _parse_pct(value: str) -> float:
    """Extract percentage from strings like '100.0% (9/9)' or '85.7% (6/7)' or ''."""
    if not value or not value.strip():
        return 0.0
    m = re.match(r"([\d.]+)%", value.strip())
    if m:
        return float(m.group(1))
    try:
        return float(value.strip())
    except ValueError:
        return 0.0


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
    task_columns: list[str],
    threshold: float,
    attendance_files: list[str],
    cheaters: list[str] | None = None,
) -> tuple[list[dict], list[str]]:
    """Calculate participation and return (rows, fieldnames)."""
    attended_emails = load_attendance(attendance_files)
    cheater_set = set(cheaters or [])

    with open(tasks_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    required_count = len(task_columns)
    out_fields = ["github_alias", "email", "group"] + task_columns + ["tasks_passed", "attended", "participation", "comment"]
    out_rows = []

    for row in rows:
        email = (row.get("email") or "").strip().lower()
        group = (row.get("group") or "").strip()
        alias = row.get("github_alias", "")
        attended = email in attended_emails

        # Count how many required tasks meet the threshold
        task_pcts = []
        tasks_passed = 0
        for col in task_columns:
            pct = _parse_pct(row.get(col, ""))
            task_pcts.append(pct)
            if pct >= threshold:
                tasks_passed += 1

        att = "YES" if attended else "NO"

        att_str = "attended" if attended else "not attended"

        if not group:
            part, comment = "", "non-student"
        elif alias in cheater_set:
            part, comment = "0", "plagiarism detected"
        elif tasks_passed >= required_count and attended:
            part = "1"
            comment = f"attended, {tasks_passed}/{required_count} tasks"
        elif tasks_passed >= required_count and not attended:
            part = "0.5"
            comment = f"not attended, {tasks_passed}/{required_count} tasks"
        else:
            part = "0"
            comment = f"{att_str}, {tasks_passed}/{required_count} tasks"

        out_row = {
            "github_alias": alias,
            "email": row.get("email", ""),
            "group": row.get("group", ""),
            "tasks_passed": str(tasks_passed),
            "attended": att,
            "participation": part,
            "comment": comment,
        }
        for col in task_columns:
            out_row[col] = row.get(col, "")
        out_rows.append(out_row)

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
    parser.add_argument("--tasks", required=True, help="Path to autochecker CSV export")
    parser.add_argument("--task-columns", required=True, nargs="+", help="Task columns to check (e.g., task-1 task-2)")
    parser.add_argument("--threshold", type=float, default=75, help="Minimum percentage to pass a task (default: 75)")
    parser.add_argument("--attendance", required=True, nargs="+", help="Attendance CSV files (Moodle export)")
    parser.add_argument("--output", required=True, help="Output CSV path")
    parser.add_argument("--cheaters", nargs="*", default=[], help="GitHub aliases to flag as plagiarism")
    args = parser.parse_args()

    rows, fields = calculate_participation(
        tasks_file=args.tasks,
        task_columns=args.task_columns,
        threshold=args.threshold,
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
