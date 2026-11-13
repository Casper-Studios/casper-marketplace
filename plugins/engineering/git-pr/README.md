# git-pr - Development Workflow Plugin for Claude Code

A collection of skills for automating common development workflows like committing, PR management, dependency upgrades, and Linear ticket extraction.

## Features

- **Git Workflows**: Conventional commits, PR creation with templates, and PR comment triage
- **Maintenance**: Safe dependency upgrades with breaking-change analysis

## Setup

### Prerequisites

One of: **bun** (preferred), **pnpm**, or **npm**.

### 1. Install the sync script

The bundled `sync-skills.sh` installs/updates every marketplace skill. No hardcoded list — new skills are picked up automatically. It checks the marketplace's latest commit first and only reinstalls when that commit has changed, so most runs do nothing.

Installing the skills globally does not copy this script, so download it to a fixed location:

```bash
mkdir -p ~/.claude/hooks
curl -sf https://raw.githubusercontent.com/Casper-Studios/casper-marketplace/main/plugins/engineering/git-pr/sync-skills.sh \
  -o ~/.claude/hooks/sync-skills.sh
chmod +x ~/.claude/hooks/sync-skills.sh
```

### 2. Run it

```bash
~/.claude/hooks/sync-skills.sh
```

No output = success. Verify with:

```bash
npx skills list -g
```

### 3. Set up auto-sync (optional)

Add a Claude Code SessionStart hook so skills stay current without manual intervention.

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
            "statusMessage": "Syncing git-pr skills…",
            "async": true
          }
        ]
      }
    ]
  }
  // ... rest of your settings
}
```

### 4. Manual update

Re-run the sync script at any time:

```bash
~/.claude/hooks/sync-skills.sh
```

The script records the last synced commit in `~/.agents/.casper-marketplace-commit` and skips the reinstall if it matches. To force a full reinstall, delete that file first:

```bash
rm -f ~/.agents/.casper-marketplace-commit && ~/.claude/hooks/sync-skills.sh
```

## Skills

### `/commit` - Commit Changes

Generate conventional commit messages and commit staged changes. Follows the conventional commits format (`feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`, `perf`) with messages focused on "why" not "what".

### `/open-pr` - Create Pull Requests

Generate and create pull requests using a PR template. Compares against the dev branch, writes a draft to `.agents/scratchpad/PR.md` for review, then submits via GitHub API.

### `/resolve-pr-comments` - Triage PR Review Comments

Fetch unresolved PR review threads, deduplicate across bots, classify by severity (Critical/Major/Medium/Minor/Nitpick), and spawn parallel sub-agents to fix or resolve each issue.

### `/bump-deps` - Upgrade Dependencies

Analyze outdated dependencies and safely upgrade them. Detects the package manager (pnpm for frontend, uv for backend), analyzes breaking changes, and generates a PR with a safety analysis.

## Directory Structure

```
git-pr/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── sync-skills.sh               # Dynamic skill sync script
├── skills/
│   ├── bump-deps/
│   │   ├── SKILL.md
│   │   ├── assets/
│   │   └── references/
│   ├── commit/
│   │   └── SKILL.md
│   ├── open-pr/
│   │   ├── SKILL.md
│   │   └── assets/
│   └── resolve-pr-comments/
│       └── SKILL.md
└── README.md                    # This file
```

## License

MIT
