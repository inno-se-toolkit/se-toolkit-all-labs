Calculate participation scores for a lab week.

Arguments: $ARGUMENTS (format: `<autochecker-csv-path> <attendance-zip-or-folder-path>`)

1. If attendance path is a ZIP, unzip to `/tmp/` first
2. Determine task columns from the autochecker CSV (columns after `group`)
3. Ask the user which tasks to include and any non-default thresholds
4. Run `python3 scripts/participation/calculate.py` with the appropriate arguments
5. Show the summary to the user

See `scripts/participation/calculate.py --help` for full options.
