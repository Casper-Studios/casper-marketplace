# Dev Toolkit - Development Workflow Plugin for Claude Code

A collection of skills for automating common development workflows like planning, committing, PR management, code polishing, and session handoffs.

## Features

- **Planning & Research**: Deep codebase research with parallel sub-agents, followed by structured implementation planning
- **Git Workflows**: Conventional commits, PR creation with templates, and PR comment triage
- **Code Quality**: Automated polishing that removes AI artifacts, checks guidelines, and runs review
- **Session Continuity**: Branch context recovery and structured handoff documentation

## Installation

### Option 1: Marketplace (Recommended)

```bash
# 1. Add the Casper Studios marketplace
/plugin marketplace add Casper-Studios/plugin-marketplace

# 2. Install the plugin
/plugin install dev-toolkit
```

### Option 2: Git Clone + Local Plugin Directory

```bash
# Clone the repository
git clone git@github.com:Casper-Studios/plugin-marketplace.git

# Run Claude Code with the plugin directory
claude --plugin-dir ./plugin-marketplace
```

## Skills

### `/commit` - Commit Changes

Generate conventional commit messages and commit staged changes. Follows the conventional commits format (`feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`, `perf`) with messages focused on "why" not "what".

### `/planner` - Create Implementation Plans

Interactive planning workflow that spawns parallel research sub-agents (codebase-locator, codebase-analyzer, codebase-pattern-finder) to produce detailed, phase-based implementation plans saved to `.claude/scratchpad/`.

### `/implement-plan` - Execute Plans

Execute approved implementation plans phase-by-phase with progress tracking. Reads plans from `.claude/scratchpad/` and adapts to codebase reality while maintaining plan intent.

### `/research-codebase` - Deep Codebase Research

Conduct comprehensive codebase research using parallel sub-agents. Produces research documents with `file:line` references and GitHub permalinks.

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
