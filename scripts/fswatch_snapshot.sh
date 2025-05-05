#!/usr/bin/env bash
# Live snapshot every time a file changes (macOS/Linux).
repo_root="$(git rev-parse --show-toplevel)"
fswatch -o "$repo_root" | while read; do
  python "$repo_root/scripts/repo2md.py" > "$repo_root/context/latest.md"
  git add context/latest.md
  git commit -m "auto snapshot (fswatch)" --no-verify || true
  git push || true
done
