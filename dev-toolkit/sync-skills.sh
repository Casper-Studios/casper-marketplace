#!/usr/bin/env bash
# Sync dev-toolkit skills from Casper marketplace on session start.
# Runs optimistically — failures are silent and never block the session.

set -euo pipefail

MARKETPLACE="https://github.com/Casper-Studios/casper-marketplace"

# ---------------------------------------------------------------------------
# 1. Ensure the `skills` CLI is available
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
# 2. Add or update all marketplace skills globally
# ---------------------------------------------------------------------------
# --all is idempotent: installs new skills, overwrites existing ones.
# The CLI handles cloning, diffing, and symlinking internally.
# ---------------------------------------------------------------------------
skills add "$MARKETPLACE" --all -g 2>/dev/null || true
