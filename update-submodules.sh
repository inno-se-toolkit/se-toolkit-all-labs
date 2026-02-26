#!/bin/bash
# Pull latest for all submodules and commit if anything changed.
# Usage: bash update-submodules.sh
set -e

cd "$(dirname "$0")"

echo "Pulling latest submodules..."
git submodule update --remote --merge

CHANGED=$(git diff --name-only)
if [ -z "$CHANGED" ]; then
    echo "All submodules up to date."
    exit 0
fi

echo ""
echo "Updated submodules:"
echo "$CHANGED"
echo ""

git add .gitmodules $CHANGED
git commit -m "chore: update submodules"
git push origin main

echo "Done."
