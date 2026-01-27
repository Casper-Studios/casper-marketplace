# Casper - Company Context Plugin for Claude Code

Casper provides company/client context and security-focused settings for teams using Claude Code.

## Features

- **Progressive Disclosure**: Access company, project, and meeting context at the right level of detail
- **Security Hooks**: Auto-block dangerous commands like `rm -rf`, `curl | bash`, etc.
- **Secure .env Loading**: Environment variables available to subprocesses without exposing raw values
- **Privacy Settings**: Telemetry and error reporting disabled by default

## Getting Started (New to Git?)

If you're new to Git and GitHub, follow these steps first:

### 1. Join the Casper Studios GitHub Organization

- Check your email for an invite from GitHub/Casper-Studios
- If you haven't received one, ask eng to add you to the org

### 2. Install Git

**Mac:**
Open Terminal and run:

```bash
xcode-select --install
```

**Windows:**
Download and install from https://git-scm.com/download/win (use all default options)

### 3. Set Up Git (one-time)

Open Terminal (Mac) or Git Bash (Windows) and run:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@casper-studios.com"
```

### 4. Install the Plugin

Open Claude Code and run:
```
/plugin marketplace add git@github.com:Casper-Studios/plugin-marketplace.git
/plugin install casper
/casper:setup
```

You'll be prompted to log in to GitHub - use your Casper Studios credentials.

---

## Installation

### Option 1: Marketplace (Recommended)

```bash
# 1. Add the Casper Studios marketplace
/plugin marketplace add Casper-Studios/plugin-marketplace

# 2. Install the plugin
/plugin install casper

# 3. Run setup to apply security settings
/casper:setup
```

### Option 2: Git Clone + Local Plugin Directory

```bash
# Clone the repository
git clone git@github.com:Casper-Studios/plugin-marketplace.git

# Run Claude Code with the plugin directory
claude --plugin-dir ./plugin-marketplace
```

### Option 3: Copy to Claude Plugins Directory

```bash
# Clone and copy to your home plugins directory
git clone git@github.com:Casper-Studios/plugin-marketplace.git
cp -r plugin-marketplace ~/.claude/plugins/casper
```

## Setup

After installing, run the setup command to apply security settings:

```
/casper:setup
```

This will:

1. Apply security deny rules (blocks dangerous commands)
2. Apply security allow rules (permits safe git/npm operations)
3. Set environment variables to disable telemetry
4. Merge settings with your existing `.claude/settings.json`

**Important:** Restart Claude Code after running setup for changes to take effect.

## Commands

### `/casper:company` - Layer 1: Company Overview

View high-level company information and client list.

- Company description and tech stack
- Coding standards
- List of clients with brief descriptions

### `/casper:projects` - Layer 2: Project Details

View detailed project information and requirements.

- Project goals and status
- Technical design
- Phase breakdown
- Supports filtering by client: `/casper:projects client-name`

### `/casper:transcripts` - Layer 3: Meeting History

View meeting transcripts and decision logs.

- Meeting summaries
- Key decisions
- Action items
- Supports filtering: `/casper:transcripts client-name`

## Security Features

### Philosophy

This plugin focuses on preventing **irreversible, catastrophic** operations rather than blocking everything potentially dangerous. [Research shows](https://flatt.tech/research/posts/pwning-claude-code-in-8-different-ways/) that denylists are inherently bypassable through encoding, subshells, or script files. These rules are a safety net, not a security boundary.

### Catastrophic Command Blocking

The bash validator hook blocks truly dangerous commands:

- **System destruction**: `rm -rf /`, `rm -rf ~`, `rm -rf *`
- **Remote code execution**: `curl | bash`, `wget | sh` (piped to shell)
- **Disk destruction**: `dd of=/dev/sd*`, `mkfs` on unmounted drives
- **Fork bombs**: `:(){:|:&};:` patterns

Commands like `curl`, `wget`, `chmod`, and `sudo` are **not** blocked because they have many legitimate uses.

### .env Protection

Defense for secrets:

1. **SessionStart Hook**: Loads `.env` into subprocess environment
2. **Read Deny Rules**: Blocks direct reading of `.env`, `.env.*`, `**/secrets/**`

**Result**: Claude can run `npm run build` (which uses env vars internally) but cannot directly read `.env` files.

## Customizing Your Data

### Company Information

Edit `data/company.md` with your company's:

- Overview and mission
- Tech stack
- Coding standards
- Key contacts

### Adding Clients

1. Edit `data/clients/_index.md` to add client summaries
2. Create `data/clients/{client-name}.md` with detailed client info

### Adding Projects

Create files in `data/projects/{client-name}/{project-name}.md` with:

- Project goals and status
- Requirements (P0/P1/P2)
- Technical design
- Phase breakdown

### Adding Transcripts

Create files in `data/transcripts/{client-name}/{meeting-date-topic}.md` with:

- Date, attendees, agenda
- Discussion summary
- Decisions made
- Action items

## Directory Structure

```
casper/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── commands/
│   ├── setup.md                 # Setup wizard
│   ├── company.md               # Layer 1 command
│   ├── projects.md              # Layer 2 command
│   └── transcripts.md           # Layer 3 command
├── hooks/
│   └── hooks.json               # Security hooks config
├── scripts/
│   ├── validate-bash.sh         # Dangerous command blocker
│   └── load-env.sh              # Secure env loader
├── data/
│   ├── company.md               # Company overview
│   ├── clients/
│   │   ├── _index.md            # Client list
│   │   └── example-client.md    # Example client details
│   ├── projects/
│   │   └── example-client/
│   │       └── example-project.md
│   └── transcripts/
│       └── example-client/
│           └── example-meeting.md
├── settings-template.json       # Security settings template
└── README.md                    # This file
```

## Verification

After setup, verify the plugin is working:

1. **Check commands appear:** Run `/help` and look for casper commands
2. **Test command blocking:** Try `rm -rf /` - should be blocked by hook
3. **Test context commands:** Run `/casper:company` to see company info
4. **Test env protection:** Try to read `.env` directly - should be denied
5. **Test legitimate commands work:** `curl https://example.com` should work (only `curl | bash` is blocked)

## Troubleshooting

### Commands not appearing

- Ensure plugin directory is correctly specified with `--plugin-dir`
- Check that `.claude-plugin/plugin.json` exists and is valid JSON

### Hooks not working

- Run `/casper:setup` and restart Claude Code
- Check that scripts have execute permissions: `chmod +x scripts/*.sh`

### Settings not applied

- Run `/casper:setup` to merge settings
- Restart Claude Code after setup
- Check `~/.claude/settings.json` for the applied rules

## License

MIT
