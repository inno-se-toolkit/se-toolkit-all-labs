Update all lab submodules to their latest upstream commits.

Arguments: $ARGUMENTS (optional: specific submodule names to update, e.g. `se-toolkit-lab-8 autochecker`)

## Submodules in this repo

- `se-toolkit-lab-1` through `se-toolkit-lab-9` — lab repositories
- `autochecker` — autochecker bot, dashboard, and specs

## Procedure

1. If specific submodules are given, update only those. Otherwise update all.
2. For each submodule:
   ```bash
   git submodule update --remote <name>
   ```
3. Check which submodules changed:
   ```bash
   git diff --submodule
   ```
4. Show the user what changed (commit messages in each submodule)
5. Stage and commit:
   ```bash
   git add <changed-submodules>
   git commit -m "chore(submodule): update <names> pointers"
   ```
6. Push if the user confirms

## Notes

- Submodule URLs use both HTTPS and SSH — if a fetch fails, check the URL in `.gitmodules`
- After updating, the parent repo tracks new commits but doesn't modify the submodule content
- If a submodule has local modifications (dirty working tree), resolve those first before updating
