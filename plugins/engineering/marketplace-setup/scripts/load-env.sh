#!/bin/bash
# load-env.sh - Securely loads .env into Claude's shell environment
# This script runs at session start and makes env vars available to subprocesses

# Exit if CLAUDE_ENV_FILE is not set
if [ -z "$CLAUDE_ENV_FILE" ]; then
  exit 0
fi

# Find .env file - check current directory and common project roots
ENV_FILE=""
if [ -f ".env" ]; then
  ENV_FILE=".env"
elif [ -f "$PWD/.env" ]; then
  ENV_FILE="$PWD/.env"
fi

# Exit if no .env file found
if [ -z "$ENV_FILE" ]; then
  exit 0
fi

# Load .env variables into Claude's environment
while IFS= read -r line || [ -n "$line" ]; do
  # Skip empty lines
  [[ -z "$line" ]] && continue

  # Skip comments
  [[ "$line" =~ ^[[:space:]]*# ]] && continue

  # Skip lines without =
  [[ ! "$line" =~ = ]] && continue

  # Extract key and value
  key="${line%%=*}"
  value="${line#*=}"

  # Remove leading/trailing whitespace from key
  key=$(echo "$key" | xargs)

  # Skip if key is empty or contains invalid characters
  [[ ! "$key" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]] && continue

  # Remove surrounding quotes from value if present
  value="${value#\"}"
  value="${value%\"}"
  value="${value#\'}"
  value="${value%\'}"

  # Export to Claude's environment file
  echo "export $key='$value'" >> "$CLAUDE_ENV_FILE"
done < "$ENV_FILE"

exit 0
