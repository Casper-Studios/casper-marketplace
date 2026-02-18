# Dev Toolkit - Development Workflow Plugin for Claude Code

A collection of skills for automating common development workflows like planning, committing, PR management, code polishing, and session handoffs.

## Features

- **Planning & Research**: Deep codebase research with parallel sub-agents, followed by structured implementation planning
- **Git Workflows**: Conventional commits, PR creation with templates, and PR comment triage
- **Code Quality**: Automated polishing that removes AI artifacts, checks guidelines, and runs review
- **Session Continuity**: Branch context recovery and structured handoff documentation

## Setup

### Prerequisites

One of: **bun** (preferred), **pnpm**, or **npm**.

### 1. Install skills globally

```bash
npx skills add https://github.com/Casper-Studios/casper-marketplace \
  --skill commit bump-deps create-handoff extract-my-action-items \
         implement-plan polishing pr-comments pr-summary recover-branch-context \
  -g -y
```

This installs the dev-toolkit skills to `~/.agents/skills/` and symlinks them into `~/.claude/skills/`, `~/.cursor/skills/`, and `~/.codeium/windsurf/skills/` automatically.

To verify:

```bash
npx skills list -g
```

### 2. Set up auto-sync (optional)

Add a Claude Code SessionStart hook so skills stay up to date without manual intervention.

#### a. Create the sync script

```bash
mkdir -p ~/.claude/hooks
cat > ~/.claude/hooks/sync-skills.sh << 'SCRIPT'
#!/usr/bin/env bash
# Sync dev-toolkit skills from Casper marketplace on session start.
# Runs optimistically — failures are silent and never block the session.

set -euo pipefail

MARKETPLACE="https://github.com/Casper-Studios/casper-marketplace"
DEV_TOOLKIT_SKILLS="commit bump-deps create-handoff extract-my-action-items implement-plan polishing pr-comments pr-summary recover-branch-context"

# 1. Detect package manager runner (prefer bun > pnpm > npm)
if command -v bun &>/dev/null; then
  RUN="bunx"
elif command -v pnpm &>/dev/null; then
  RUN="pnpx"
elif command -v npx &>/dev/null; then
  RUN="npx"
else
  exit 0
fi

# 2. Ensure the skills CLI is installed globally
if ! command -v skills &>/dev/null; then
  case "$RUN" in
    bunx)  bun add -g skills  2>/dev/null ;;
    pnpx)  pnpm add -g skills 2>/dev/null ;;
    npx)   npm i -g skills    2>/dev/null ;;
  esac
fi

if command -v skills &>/dev/null; then
  SKILLS="skills"
else
  SKILLS="$RUN skills"
fi

# 3. Install / update all dev-toolkit skills globally
# Always run `skills add` — it installs missing skills and updates existing
# ones in a single pass. The --skill flag is additive, so this is idempotent.
$SKILLS add "$MARKETPLACE" --skill $DEV_TOOLKIT_SKILLS -g -y 2>/dev/null || true
SCRIPT
chmod +x ~/.claude/hooks/sync-skills.sh
```

#### b. Add the hook to Claude settings

Open `~/.claude/settings.json` and add the `hooks` key:

```jsonc
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/sync-skills.sh",
            "timeout": 60,
            "statusMessage": "Syncing dev-toolkit skills…",
            "async": true
          }
        ]
      }
    ]
  }
  // ... rest of your settings
}
```

#### c. Test it

```bash
~/.claude/hooks/sync-skills.sh
```

No output = success. The next time you start a Claude session, it'll sync in the background automatically.

### 3. Manual update

Pull the latest skills without restarting Claude:

```bash
npx skills update -g -y
```

## Skills

| Skill | Slash command | What it does |
|-------|--------------|--------------|
| commit | `/commit` | Conventional commits with generated messages |
| bump-deps | `/bump-deps` | Dependency upgrades with breaking change detection |
| create-handoff | `/create-handoff` | Session handoff docs for another agent |
| extract-my-action-items | `/extract-my-action-items` | Action items from Fireflies transcripts |
| implement-plan | `/implement-plan` | Execute plans from scratchpad |
| planner | `/planner` | Interactive planning with parallel research sub-agents |
| polishing | `/polishing` | Code polish, AI slop removal, final review |
| pr-comments | `/pr-comments` | Triage and fix PR review comments |
| pr-summary | `/pr-summary` | Create PRs with template |
| recover-branch-context | `/recover-branch-context` | Get up to speed on a branch |
| research-codebase | `/research-codebase` | Deep codebase research with parallel sub-agents |

## Directory Structure

```
dev-toolkit/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── skills/
│   ├── bump-deps/
│   │   ├── SKILL.md
│   │   ├── assets/
│   │   └── references/
│   ├── commit/
│   │   └── SKILL.md
│   ├── create-handoff/
│   │   └── SKILL.md
│   ├── implement-plan/
│   │   └── SKILL.md
│   ├── planner/
│   │   └── SKILL.md
│   ├── polishing/
│   │   └── SKILL.md
│   ├── pr-comments/
│   │   └── SKILL.md
│   ├── pr-summary/
│   │   ├── SKILL.md
│   │   └── assets/
│   ├── recover-branch-context/
│   │   └── SKILL.md
│   └── research-codebase/
│       └── SKILL.md
└── README.md                    # This file
```

## License

MIT
