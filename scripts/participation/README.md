# Participation Calculation

Calculate lab participation scores by combining **attendance** data with **autochecker task** data.

## Scoring Rules

Per the [course syllabus](../../README.md#p42-participation-scoring), the following rules apply across all labs unless specified otherwise:

| Condition | Points |
|-----------|--------|
| Attended + completed all required tasks | 1.0 |
| Completed tasks without attendance | 0.5 |
| Attended but tasks not completed | 0.0 |
| Not attended, tasks not completed | 0.0 |
| Plagiarism detected | 0.0 (case filed to DoE) |
| Non-student (no group) | *skipped* |

"Completed all required tasks" means all obligatory tasks passed at >=75% in the autochecker. The specific threshold per lab is defined in the lab instructions (e.g., for some labs task 3 requires >=66%).

## Input Files

### Attendance CSVs (Moodle export)

One ZIP per week from Moodle, containing one CSV per lab group:

```
External user field,status
a.student@innopolis.university,P
```

- `External user field` — student email
- `status` — `P` for present

### Autochecker CSV (dashboard export)

Single file with autochecker results:

```
github_alias,email,group,setup,task-1,task-2,task-3
StudentAlias,s.student@innopolis.university,B25-CSE-01,100.0% (5/5),80.0% (4/5),,
```

## Usage

```bash
python scripts/participation/calculate.py \
    --tasks /path/to/autochecker-lab-06-2026-03-21.csv \
    --attendance /path/to/Week\ 6/*.csv \
    --output participation-lab06.csv \
    --cheaters alias1 alias2
```

## Output

CSV with columns: `email`, `group`, `score`, `comment`.

Each row has a concise comment (e.g., "attended, 3/3 tasks").

## Procedure

1. **Export attendance** — download the Week N ZIP from Moodle, unzip
2. **Export autochecker results** — download CSV from the autochecker dashboard
3. **Run plagiarism check** (if applicable) — document confirmed cases in `autochecker/reports/`
4. **Run the script** — pass attendance CSVs and autochecker CSV
5. **Review output** — check summary, inspect edge cases (0.5 scores, cheaters)
6. **Upload to Moodle** — use the output CSV for grade entry

## Legal Excuses

Students with a legal excuse get a deadline extension. The extension equals the number of excused days counted from the lab day. Legal excuse info is collected from DoE when finalizing the course.
