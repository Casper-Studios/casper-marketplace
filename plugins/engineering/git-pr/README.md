# git-pr - Development Workflow Plugin for Claude Code

A collection of skills for automating common development workflows like committing, PR management, dependency upgrades, and Linear ticket extraction.

## Features

- **Git Workflows**: Conventional commits, PR creation with templates, and PR comment triage
- **Maintenance**: Safe dependency upgrades with breaking-change analysis
- **Linear Integration**: Extract and draft actionable tickets from unstructured input and transcripts

## Setup

### Prerequisites

One of: **bun** (preferred), **pnpm**, or **npm**.

### 1. Install the sync script

The bundled `sync-skills.sh` clones the marketplace, discovers every skill directory automatically, and installs/updates them all. No hardcoded list — new skills are picked up every run.

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

## Skills

### `/commit` - Commit Changes

Generate conventional commit messages and commit staged changes. Follows the conventional commits format (`feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`, `perf`) with messages focused on "why" not "what".

### `/pr-summary` - Create Pull Requests

Generate and create pull requests using a PR template. Compares against the dev branch, writes a draft to `.claude/scratchpad/PR.md` for review, then submits via GitHub API.

### `/pr-comments` - Triage PR Review Comments

Fetch unresolved PR review threads, deduplicate across bots, classify by severity (Critical/Major/Medium/Minor/Nitpick), and spawn parallel sub-agents to fix or resolve each issue.

### `/bump-deps` - Upgrade Dependencies

Analyze outdated dependencies and safely upgrade them. Detects the package manager (pnpm for frontend, uv for backend), analyzes breaking changes, and generates a PR with a safety analysis.

### `/send-to-linear` - Send to Linear

Extract actionable Linear tickets from unstructured input — Slack conversations, call transcripts, screenshots, meeting notes. Drafts tickets to a scratchpad for review, then creates them in Linear on approval. Supports `config.local.json` overrides for team, project, assignee, and labels.

### `/extract-my-action-items` - Extract Action Items

Extract action items from Fireflies transcripts using parallel subagents. Supports single-person and all-attendees modes, with an optional Linear ticket proposal workflow that matches action items to existing cycle tickets and drafts new tickets for review before creation.

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
│   ├── extract-my-action-items/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   └── scripts/
│   ├── pr-comments/
│   │   └── SKILL.md
│   ├── pr-summary/
│   │   ├── SKILL.md
│   │   └── assets/
│   └── send-to-linear/
│       ├── SKILL.md
│       └── references/
└── README.md                    # This file
```

## License

MIT
