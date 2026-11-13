#!/usr/bin/env bash
# Sync all Casper marketplace skills on session start.
# Runs optimistically — failures are silent and never block the session.
#
# `skills add --all` deletes and rewrites every skill folder. Running it on
# every session start races the starting session's skill loading, which can
# then miss skills. So we only reinstall when the marketplace has a new commit.

set -euo pipefail

MARKETPLACE="https://github.com/Casper-Studios/casper-marketplace"
STAMP="$HOME/.agents/.casper-marketplace-commit"

# ---------------------------------------------------------------------------
# 1. Skip if the marketplace hasn't changed since the last successful sync
# ---------------------------------------------------------------------------
# Delete the stamp file to force a full resync.
# ---------------------------------------------------------------------------
latest=$(timeout 20 git ls-remote "$MARKETPLACE" HEAD 2>/dev/null | cut -f1 || true)
[ -n "$latest" ] || exit 0
[ "$latest" != "$(cat "$STAMP" 2>/dev/null || true)" ] || exit 0

# ---------------------------------------------------------------------------
# 2. Ensure the `skills` CLI is available
# ---------------------------------------------------------------------------
if ! command -v skills &>/dev/null; then
  if command -v bun &>/dev/null; then
    bun add -g skills 2>/dev/null || true
  elif command -v pnpm &>/dev/null; then
    pnpm add -g skills 2>/dev/null || true
  elif command -v npm &>/dev/null; then
    npm i -g skills 2>/dev/null || true
  else
    exit 0
  fi
fi

command -v skills &>/dev/null || exit 0

# ---------------------------------------------------------------------------
# 3. Add or update all marketplace skills globally, then record the commit
# ---------------------------------------------------------------------------
# --all installs new skills and overwrites existing ones.
# The CLI handles cloning, diffing, and symlinking internally.
# ---------------------------------------------------------------------------
if skills add "$MARKETPLACE" --all -g 2>/dev/null; then
  mkdir -p "$(dirname "$STAMP")"
  echo "$latest" > "$STAMP"
fi
