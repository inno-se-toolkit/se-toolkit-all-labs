# Participation Calculation

Calculate lab participation scores by combining **attendance** data with **autochecker task** data.

## Scoring rules

| Score | Rule |
|-------|------|
| **1** | attended AND obligatory_tasks_passed >= 2 |
| **0.5** | attended AND obligatory_tasks_passed == 1 |
| **0.5** | absent AND obligatory_tasks_passed >= 2 |
| **0** | attended AND obligatory_tasks_passed == 0 |
| **0** | absent AND obligatory_tasks_passed < 2 |
| **0** | plagiarism detected, case to be filed to DoE |
| *blank* | non-student (no group) |

## Input files

### Attendance CSVs (Moodle export)

One file per lab group. Columns:

```
External user field,status
a.student@innopolis.university,P
```

- `External user field` — student email
- `status` — `P` for present

### Tasks CSV (autochecker export)

Single file with autochecker results. Columns:

```
github_alias,email,group,lab04_obligatory_passed
StudentAlias,s.student@innopolis.university,B25-CSE-01,3
```

- `github_alias` — GitHub username
- `email` — university email (used to join with attendance)
- `group` — student group (empty = non-student, skipped)
- `labXX_obligatory_passed` — count of obligatory tasks passed at >=75%

## Usage

```bash
python scripts/participation/calculate.py \
    --tasks data/tasks-lab03-lab04.csv \
    --task-column lab04_obligatory_passed \
    --attendance data/attendance/L4-G1.csv data/attendance/L4-G2.csv ... \
    --output participation-lab04.csv \
    --cheaters AleksKornilov07 venimu
```

## Output

CSV with columns: `github_alias`, `email`, `group`, `<task-column>`, `attended`, `participation`, `comment`.

Each row has a human-readable `comment` explaining how the score was derived.

## Procedure (step by step)

1. **Export attendance** — download per-group attendance CSVs from Moodle
2. **Export tasks** — use the autochecker dashboard CSV export (`/export/csv?lab=lab-XX`) or the existing `participation-labXX.csv` file
3. **Run plagiarism check** (if applicable) — `autochecker batch --plagiarism`, then manual investigation. Document confirmed cases in `autochecker/reports/`
4. **Run the script** — pass attendance files, task file, task column, and any cheater aliases
5. **Review output** — check the summary breakdown, inspect edge cases (0.5 scores, cheaters)
6. **Upload to Moodle** — use the output CSV for grade entry
