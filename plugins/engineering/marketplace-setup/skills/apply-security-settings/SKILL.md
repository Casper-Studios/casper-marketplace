---
name: apply-security-settings
description: Apply Casper security settings (deny rules, allow rules, telemetry env vars) to the user's Claude Code configuration. Use this skill when setting up a new machine, onboarding to Casper Studios, or when the user asks to apply/install/run marketplace security setup. Triggers on "set up security settings", "apply casper settings", "run marketplace setup", or first-time plugin installation.
---

# Apply Security Settings

Read the settings template at `${CLAUDE_PLUGIN_ROOT}/settings-template.json`.

Then apply these settings to the user's `.claude/settings.json`:

1. If `.claude/settings.json` doesn't exist, create it with the template contents
2. If it exists, MERGE the settings (don't overwrite existing user settings):
   - Add any deny rules from the template that aren't already present
   - Add any allow rules from the template that aren't already present
   - Set env vars for telemetry if not already set

After applying, confirm what was added and remind the user to restart Claude Code for the changes to take effect.

## Security Settings Applied

The setup applies the following protections:

### Denied File Reads
- `.env`, `.env.*`, `.env.local`, `.env.production`
- `**/secrets/**`, `**/.secrets/**`
- `**/*credentials*`

### Allowed Commands (Pre-approved Operations)
- Casper skills/commands: `marketplace-setup:apply-security-settings`, `brain:company`, `brain:projects`, `brain:transcripts`
- `npm run:*`, `npm test:*`, `npm install:*`
- `git status:*`, `git diff:*`, `git log:*`, `git add:*`, `git commit:*`

### Hook-Based Protections
The bash validator hook blocks catastrophic commands:
- `rm -rf /` and similar system-destroying patterns
- `curl | bash` (remote code execution)
- `dd` to block devices (disk destruction)
- Fork bombs

### Environment Variables
- `DISABLE_TELEMETRY=1`
- `DISABLE_ERROR_REPORTING=1`

## Philosophy

This plugin focuses on preventing **irreversible, catastrophic** operations rather than trying to block everything potentially dangerous. Denylists are inherently bypassable - these rules are a safety net, not a security boundary.
