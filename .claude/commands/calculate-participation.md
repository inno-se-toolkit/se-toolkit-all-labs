Calculate participation scores for a lab week.

Arguments: $ARGUMENTS (format: `<autochecker-csv-path> <attendance-zip-or-folder-path>`)

## What to do

1. Parse the arguments to get the autochecker CSV path and attendance path
2. If the attendance path is a ZIP, unzip it to `/tmp/` first and find the CSVs inside
3. Determine which task columns to check from the autochecker CSV (all columns after `group` — typically `setup`, `task-1`, `task-2`, etc.)
4. Ask the user which tasks to include and if any have non-default thresholds (default is 75%)
5. Run the script:

```bash
python3 scripts/participation/calculate.py \
    --tasks <autochecker-csv> \
    --task-columns <task1> <task2> ... \
    --threshold 75 \
    --attendance <csv1> <csv2> ... \
    --output ~/Downloads/participation-labXX.csv
```

6. Show the summary output to the user
7. If the user mentions cheaters, re-run with `--cheaters alias1 alias2`

## Notes

- The script is at `scripts/participation/calculate.py` in this repo
- See `scripts/participation/README.md` for full documentation
- Scoring rules follow the course syllabus (README.md P.4.2):
  - attended + all tasks completed = 1.0
  - all tasks completed without attendance = 0.5
  - otherwise = 0.0
