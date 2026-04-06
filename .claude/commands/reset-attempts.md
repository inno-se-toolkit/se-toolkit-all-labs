Reset attempt counters for a lab task on the Hetzner server. This deletes only attempt records (the retry counter), NOT submission results.

Arguments: $ARGUMENTS (format: `<lab-id> <task-id>` e.g. `lab-06 task-3`, optionally add `--tg-id <id>` for a single student)

Steps:
1. Parse the arguments to extract lab-id and task-id (and optional --tg-id)
2. SSH into the Hetzner server (nurios@188.245.43.68)
3. First do a dry run inside the bot container to show what will be affected:
   `docker exec autochecker-bot python3 scripts/reset_attempts.py --lab <lab-id> --task <task-id> --dry-run`
4. Show the user the dry run output and ask for confirmation before proceeding
5. If confirmed, run without --dry-run:
   `docker exec autochecker-bot python3 scripts/reset_attempts.py --lab <lab-id> --task <task-id>`
6. Report the result

IMPORTANT: Always run dry-run first and ask for confirmation. Never delete without showing what will be affected.
