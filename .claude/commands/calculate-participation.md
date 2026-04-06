Calculate participation scores for a lab week.

Arguments: $ARGUMENTS (the autochecker CSV path and attendance ZIP/folder path, e.g. `~/Downloads/autochecker-lab-06.csv ~/Downloads/Week\ 6.zip`)

## Scoring rules

From the course syllabus (README.md P.4.2):

- **1.0** — attended + completed all required tasks
- **0.5** — completed all required tasks without attendance
- **0.0** — did not complete all required tasks (regardless of attendance)
- **0.0** — plagiarism detected (case filed to DoE)
- Skip students with no group (non-students)

"Completed all required tasks" = every obligatory task in the autochecker CSV passes at >=75%.
Individual labs may override the threshold (e.g. task-3 at >=66%) — ask the user.

The user may also apply more lenient criteria (e.g. count partial completion). Always confirm the exact passing criteria before calculating.

## Inputs

**Autochecker CSV** — exported from the dashboard. Columns: `github_alias`, `email`, `group`, then task columns (`setup`, `task-1`, `task-2`, ...) with values like `100.0% (5/5)`.

**Attendance** — Moodle export. Either a ZIP (containing per-group CSVs) or a folder of CSVs. Each CSV has columns `External user field` (email) and `status` (`P` = present).

## Procedure

1. Parse arguments. If attendance is a ZIP, unzip to `/tmp/`.
2. Read the autochecker CSV. Show the user the task columns found and ask which to include and what thresholds to use.
3. Read all attendance CSVs. Normalize emails with `unicodedata.normalize("NFC", ...)` — Moodle uses NFD.
4. Try running the script: `python3 scripts/participation/calculate.py --tasks <csv> --task-columns <cols> --threshold <N> --attendance <files> --output <path>`
5. If the script doesn't exist or fails, calculate inline using the same logic.
6. If the user specifies cheaters, add `--cheaters alias1 alias2`.
7. Show: total students, count at 1.0 / 0.5 / 0.0, breakdown by group.
8. Save to the path the user specifies (default: `~/Downloads/participation-labXX.csv`).

## Output

CSV with columns: `email`, `group`, `score`, `comment`.
Comment format: `attended, 3/3 tasks` or `not attended, 2/3 tasks`.

## Legal excuses

Not handled by this script. Students with legal excuses get extended deadlines — their submissions may arrive after the initial export. Re-run after the extension period if needed. Legal excuse data comes from the Dean's Office.
