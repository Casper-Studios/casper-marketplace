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
# Async hooks get no timeout from Claude Code, and stock macOS has no
# `timeout`, so a watchdog gives the probe its own deadline.
# ---------------------------------------------------------------------------
remote_head() {
  git ls-remote "$MARKETPLACE" HEAD &
  local pid=$!
  # Redirected so the watchdog doesn't hold the caller's output pipe open.
  (sleep 20 && kill "$pid") >/dev/null 2>&1 &
  local watchdog=$!
  local status=0
  wait "$pid" || status=$?
  kill "$watchdog" 2>/dev/null || true
  return "$status"
}

latest=$(remote_head 2>/dev/null | cut -f1 || true)
[ -n "$latest" ] || exit 0
[ "$latest" != "$(cat "$STAMP" 2>/dev/null || true)" ] || exit 0

# ---------------------------------------------------------------------------
# 2. Run a pinned `skills` CLI
# ---------------------------------------------------------------------------
# 1.8.0+ skips agents without a global skills dir; older versions fail every
# skill on them, so `--json` would never report success.
# ---------------------------------------------------------------------------
SKILLS_CLI="skills@1.8.1"

run_skills() {
  if command -v bunx &>/dev/null; then
    bunx "$SKILLS_CLI" "$@"
  elif command -v pnpm &>/dev/null; then
    pnpm dlx "$SKILLS_CLI" "$@"
  elif command -v npx &>/dev/null; then
    npx -y "$SKILLS_CLI" "$@"
  else
    return 1
  fi
}

# ---------------------------------------------------------------------------
# 3. Add or update all marketplace skills globally, then record the commit
# ---------------------------------------------------------------------------
# --all installs new skills and overwrites existing ones. Without --json, a
# partial failure still exits 0; with it, any failed skill exits nonzero.
# ---------------------------------------------------------------------------
if run_skills add "$MARKETPLACE" --all --global --json >/dev/null 2>&1; then
  mkdir -p "$(dirname "$STAMP")"
  echo "$latest" > "$STAMP"
fi
