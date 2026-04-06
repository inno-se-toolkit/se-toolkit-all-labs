Calculate participation scores for a lab week.

Arguments: $ARGUMENTS (format: `<autochecker-csv-path> <attendance-zip-or-folder-path>`)

## Scoring Rules

Per the course syllabus (README.md):
- Attended + completed all required tasks = 1.0 point
- Completed tasks without attendance = 0.5 point
- Otherwise = 0.0

"Completed" means all obligatory tasks passed at >=75% in the autochecker CSV. Each lab may have specific thresholds (e.g., task 3 at >=66%).

## Steps

1. Parse the arguments to get the autochecker CSV path and attendance path
2. If the attendance path is a ZIP, unzip it to a temp directory first
3. Read all attendance CSVs — extract emails with status `P` (present). Normalize with `unicodedata.normalize("NFC", email)`
4. Read the autochecker CSV — for each student (skip rows with empty group), parse task scores from columns like `setup`, `task-1`, `task-2`, etc. Extract percentage from format like `100.0% (5/5)`
5. Determine task pass thresholds: by default all tasks need >=75%. Ask the user if any tasks have different thresholds (e.g., task-3 at 66%)
6. For each student calculate:
   - `attended`: whether their email appears in attendance
   - `tasks_passed`: count of tasks meeting the threshold
   - `all_tasks_done`: whether ALL tasks (excluding empty/not-attempted) meet thresholds
   - Score: attended + all_tasks_done = 1.0, not attended + all_tasks_done = 0.5, otherwise = 0.0
7. Generate output CSV with columns: `email`, `group`, `score`, `comment`
   - Comment format: "attended, 3/3 tasks" or "not attended, 2/3 tasks"
8. Print summary: total students, count at 1.0/0.5/0.0, breakdown by group
9. Save to the path specified by user (or default to `~/Downloads/participation-labXX.csv`)

## Important

- Students with empty `group` field are non-students — skip them
- Use `unicodedata.normalize("NFC", ...)` on all email comparisons (Moodle uses NFD)
- Do NOT install any packages — use only Python stdlib (csv, pathlib, unicodedata, re, zipfile)
