# Marketplace Setup - Security & Privacy Plugin for Claude Code

Security-focused settings for teams using Claude Code: catastrophic-command blocking, safe `.env` loading, and privacy defaults.

## Features

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
/plugin marketplace add Casper-Studios/casper-marketplace
/plugin install marketplace-setup
/marketplace-setup:apply-security-settings
```

You'll be prompted to log in to GitHub - use your Casper Studios credentials.

---

## Installation

```bash
# 1. Add the Casper Studios marketplace
/plugin marketplace add Casper-Studios/casper-marketplace

# 2. Install the plugin
/plugin install marketplace-setup

# 3. Run setup to apply security settings
/marketplace-setup:apply-security-settings
```

## Setup

After installing, run the setup skill to apply security settings:

```
/marketplace-setup:apply-security-settings
```

This will:

1. Apply security deny rules (blocks dangerous commands)
2. Apply security allow rules (permits safe git/npm operations)
3. Set environment variables to disable telemetry
4. Merge settings with your existing `.claude/settings.json`

**Important:** Restart Claude Code after running setup for changes to take effect.

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

## Directory Structure

```
marketplace-setup/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── skills/
│   └── apply-security-settings/
│       └── SKILL.md             # Setup skill
├── hooks/
│   └── hooks.json               # Security hooks config
├── scripts/
│   ├── validate-bash.sh         # Dangerous command blocker
│   └── load-env.sh              # Secure env loader
├── settings-template.json       # Security settings template
└── README.md                    # This file
```

## Verification

After setup, verify the plugin is working:

1. **Test command blocking:** Try `rm -rf /` - should be blocked by hook
2. **Test env protection:** Try to read `.env` directly - should be denied
3. **Test legitimate commands work:** `curl https://example.com` should work (only `curl | bash` is blocked)

## Troubleshooting

### Hooks not working

- Run `/marketplace-setup:apply-security-settings` and restart Claude Code
- Check that scripts have execute permissions: `chmod +x scripts/*.sh`

### Settings not applied

- Run `/marketplace-setup:apply-security-settings` to merge settings
- Restart Claude Code after setup
- Check `~/.claude/settings.json` for the applied rules

## License

MIT
