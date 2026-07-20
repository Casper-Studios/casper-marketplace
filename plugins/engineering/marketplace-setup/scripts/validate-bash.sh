#!/bin/bash
# validate-bash.sh - Blocks catastrophic/irreversible bash commands
# Exit code 2 = block command, Exit code 0 = allow command
#
# Philosophy: Focus on truly dangerous, irreversible operations.
# Denylists are inherently bypassable - this is a safety net, not a security boundary.

# Locale is set via LC_ALL=C in hooks.json to prevent bash startup warnings

# Read the command from stdin (tool input JSON)
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | grep -oP '"command"\s*:\s*"\K[^"]+' | head -1)

# If we couldn't extract the command, allow it (fail open for parsing issues)
if [ -z "$COMMAND" ]; then
  exit 0
fi

# Dangerous patterns to block - only truly catastrophic commands
DANGEROUS_PATTERNS=(
  # === CATASTROPHIC FILE DELETION ===
  # rm -rf with root or home directory
  'rm[[:space:]]+-rf[[:space:]]+/'
  'rm[[:space:]]+-rf[[:space:]]+/\*'
  'rm[[:space:]]+-rf[[:space:]]+~'
  'rm[[:space:]]+-rf[[:space:]]+\*'
  'rm[[:space:]]+-fr[[:space:]]+/'
  'rm[[:space:]]+-r[[:space:]]+-f[[:space:]]+/'

  # === REMOTE CODE EXECUTION ===
  # Piping downloads directly to shell (the actual danger with curl/wget)
  'curl[[:space:]].*\|[[:space:]]*sh'
  'curl[[:space:]].*\|[[:space:]]*bash'
  'curl[[:space:]].*\|[[:space:]]*zsh'
  'wget[[:space:]].*\|[[:space:]]*sh'
  'wget[[:space:]].*\|[[:space:]]*bash'
  'wget[[:space:]].*\|[[:space:]]*zsh'

  # === DISK DESTRUCTION ===
  # dd writing to block devices (can destroy entire drives)
  'dd[[:space:]].*of=/dev/sd'
  'dd[[:space:]].*of=/dev/nvme'
  'dd[[:space:]].*of=/dev/hd'
  'dd[[:space:]].*of=/dev/vd'

  # Direct writes to block devices
  '>[[:space:]]*/dev/sd'
  '>[[:space:]]*/dev/nvme'
  '>[[:space:]]*/dev/hd'

  # mkfs on main drives without explicit partition
  'mkfs[[:space:]].*[[:space:]]/dev/sd[a-z][[:space:]]*$'
  'mkfs[[:space:]].*[[:space:]]/dev/nvme[0-9]n[0-9][[:space:]]*$'

  # === FORK BOMBS ===
  ':\(\)[[:space:]]*\{.*:\|:.*\}'
  '\.()[[:space:]]*\{.*\.\|\..*\}'
)

# Check each pattern
for pattern in "${DANGEROUS_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qiE "$pattern"; then
    echo "BLOCKED: Command matches dangerous pattern"
    echo "Pattern: $pattern"
    echo "Command: $COMMAND"
    echo ""
    echo "This command could cause irreversible damage. If you need to run it,"
    echo "please execute it manually in your terminal."
    exit 2
  fi
done

# Allow the command
exit 0
