#!/usr/bin/env bash
# Sync dev-toolkit skills from Casper marketplace on session start.
# Runs optimistically — failures are silent and never block the session.

set -euo pipefail

MARKETPLACE="https://github.com/Casper-Studios/casper-marketplace"
MARKETPLACE_LOCAL="$HOME/.claude/plugins/marketplaces/casper-studios"
DEV_TOOLKIT_DIR="$MARKETPLACE_LOCAL/dev-toolkit/skills"

# ---------------------------------------------------------------------------
# 1. Detect package manager runner (prefer bun > pnpm > npm)
# ---------------------------------------------------------------------------
if command -v bun &>/dev/null; then
  RUN="bunx"
elif command -v pnpm &>/dev/null; then
  RUN="pnpx"
elif command -v npx &>/dev/null; then
  RUN="npx"
else
  exit 0 # nothing available, skip silently
fi

# ---------------------------------------------------------------------------
# 2. Ensure the `skills` CLI is installed globally
# ---------------------------------------------------------------------------
if ! command -v skills &>/dev/null; then
  case "$RUN" in
    bunx)  bun add -g skills  2>/dev/null ;;
    pnpx)  pnpm add -g skills 2>/dev/null ;;
    npx)   npm i -g skills    2>/dev/null ;;
  esac
fi

# Prefer the global binary if available, otherwise fall back to runner
if command -v skills &>/dev/null; then
  SKILLS="skills"
else
  SKILLS="$RUN skills"
fi

# ---------------------------------------------------------------------------
# 3. Clone or pull the marketplace repo
# ---------------------------------------------------------------------------
if [ -d "$MARKETPLACE_LOCAL/.git" ]; then
  git -C "$MARKETPLACE_LOCAL" pull --ff-only --quiet 2>/dev/null || true
else
  git clone --depth 1 --quiet "$MARKETPLACE" "$MARKETPLACE_LOCAL" 2>/dev/null || exit 0
fi

# ---------------------------------------------------------------------------
# 4. Discover and install/update all dev-toolkit skills globally
# ---------------------------------------------------------------------------
if [ -d "$DEV_TOOLKIT_DIR" ]; then
  DEV_TOOLKIT_SKILLS=""
  for skill_dir in "$DEV_TOOLKIT_DIR"/*/; do
    [ -f "$skill_dir/skill.md" ] || [ -f "$skill_dir/SKILL.md" ] || continue
    DEV_TOOLKIT_SKILLS="$DEV_TOOLKIT_SKILLS $(basename "$skill_dir")"
  done
  DEV_TOOLKIT_SKILLS="${DEV_TOOLKIT_SKILLS# }"

  if [ -n "$DEV_TOOLKIT_SKILLS" ]; then
    # shellcheck disable=SC2086
    $SKILLS add "$MARKETPLACE" --skill $DEV_TOOLKIT_SKILLS -g -y 2>/dev/null || true
  fi
fi
