---
description: Generate LinkedIn posts from source material in your personal writing style
---

# LinkedIn Post Generator

Generate LinkedIn posts from shared source material, written in your personal style. Supports auto-pulling from Fireflies.ai, Slack, and Google Drive.

## Instructions

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/linkedin-post-generator/SKILL.md` for the complete workflow
2. Parse any flags passed with the command (see Flags section below)
3. Follow the appropriate flow based on flags and whether a style profile exists

## Flags

- `/casper:generate-linkedin-post` — Generate posts (runs style setup on first use)
- `/casper:generate-linkedin-post --setup` — Create or re-create your personal style profile
- `/casper:generate-linkedin-post --setup-sources` — Configure Fireflies, Slack, and Drive integrations
- `/casper:generate-linkedin-post --refresh` — Pull fresh source material from integrations, then generate
- `/casper:generate-linkedin-post --view-style` — View your current style profile
- `/casper:generate-linkedin-post --view-sources` — List loaded source material
- `/casper:generate-linkedin-post --add-source` — Add new source material manually

## Quick Reference

| What | Where |
|------|-------|
| Style profile | `~/.config/casper/linkedin-style.md` (local, per-user) |
| Source config | `~/.config/casper/linkedin-sources.md` (local, per-user) |
| Source material | `${CLAUDE_PLUGIN_ROOT}/skills/linkedin-post-generator/source-material/` |
| Prompt template | `${CLAUDE_PLUGIN_ROOT}/skills/linkedin-post-generator/references/prompt-template.md` |
| Integration details | `${CLAUDE_PLUGIN_ROOT}/skills/linkedin-post-generator/references/source-integrations.md` |
| Full skill docs | `${CLAUDE_PLUGIN_ROOT}/skills/linkedin-post-generator/SKILL.md` |
