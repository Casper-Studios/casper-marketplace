# Dev Toolkit - Development Workflow Plugin for Claude Code

A collection of skills for automating common development workflows like planning, committing, PR management, code polishing, and session handoffs.

## Features

- **Git Workflows**: Conventional commits, PR creation with templates, and PR comment triage
- **Code Quality**: Automated polishing that removes AI artifacts, checks guidelines, and runs review
- **Session Continuity**: Branch context recovery and structured handoff documentation

## Setup

### Prerequisites

One of: **bun** (preferred), **pnpm**, or **npm**.

### 1. Install the sync script

The bundled `sync-skills.sh` clones the marketplace, discovers every skill directory automatically, and installs/updates them all. No hardcoded list — new skills are picked up every run.

```bash
mkdir -p ~/.claude/hooks
curl -sf https://raw.githubusercontent.com/Casper-Studios/casper-marketplace/main/dev-toolkit/sync-skills.sh \
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

### 4. Manual update

Re-run the sync script at any time:

```bash
~/.claude/hooks/sync-skills.sh
```

## Skills

### `/commit` - Commit Changes

Generate conventional commit messages and commit staged changes. Follows the conventional commits format (`feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`, `perf`) with messages focused on "why" not "what".

### `/implement-plan` - Execute Plans

Execute approved implementation plans phase-by-phase with progress tracking. Reads plans from `.claude/scratchpad/` and adapts to codebase reality while maintaining plan intent.

### `/pr-summary` - Create Pull Requests

Generate and create pull requests using a PR template. Compares against the dev branch, writes a draft to `.claude/scratchpad/PR.md` for review, then submits via GitHub API.

### `/pr-comments` - Triage PR Review Comments

Fetch unresolved PR review threads, deduplicate across bots, classify by severity (Critical/Major/Medium/Minor/Nitpick), and spawn parallel sub-agents to fix or resolve each issue.

### `/polishing` - Polish Code Changes

End-to-end code polishing that recovers branch context, checks against skill guidelines, removes AI artifacts (unnecessary comments, defensive code), and runs a final review pass.

### `/bump-deps` - Upgrade Dependencies

Analyze outdated dependencies and safely upgrade them. Detects the package manager (pnpm for frontend, uv for backend), analyzes breaking changes, and generates a PR with a safety analysis.

### `/recover-branch-context` - Recover Branch Context

Get up to speed on the current branch by analyzing commit history, uncommitted changes, and optional Linear tickets. Groups changes by intent and suggests next steps.

### `/create-handoff` - Create Session Handoffs

Create structured handoff documentation with YAML frontmatter for transitioning work-in-progress to another agent. Includes task status, critical references, learnings, and next steps.

### `/extract-my-action-items` - Extract Action Items

Extract action items from Fireflies transcripts.

### `/planner` - Interactive Planning

Interactive planning with parallel research sub-agents.

### `/research-codebase` - Deep Codebase Research

Deep codebase research with parallel sub-agents.

## Directory Structure

```
dev-toolkit/
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
│   ├── create-handoff/
│   │   └── SKILL.md
│   ├── extract-my-action-items/
│   │   ├── skill.md
│   │   └── scripts/
│   ├── implement-plan/
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
└── README.md                    # This file
```

## License

MIT
