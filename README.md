<p align="center">
  <img src="casper-studios-logo.png" alt="Casper Studios" width="300">
</p>

A collection of Claude Code plugins for business automation, data analysis, and productivity.

## Available Plugins

| Plugin | Description |
|--------|-------------|
| [casper](./casper/) | Context management for consulting projects - company info, project PRDs, meeting transcripts |
| [data-analysis](./data-analysis/) | Data analysis and storytelling for financial and RevOps contexts |
| [dev-toolkit](./dev-toolkit/) | Workflow automation skills for planning, commits, PR management, and code polishing |
| [stack-patterns](./stack-patterns/) | Idiomatic usage patterns for React, TanStack Table, and better-all |
| [cf-saas-stack](./cf-saas-stack/) | Cloudflare SaaS stack patterns - auth, database, workflows, emails, Stripe, and more |

## Installation

### Install all skills globally (recommended)

```bash
# Install the skills CLI, then add everything from the marketplace
npx skills add https://github.com/Casper-Studios/casper-marketplace --all -g
```

The `--all` flag is idempotent — it installs new skills and overwrites existing ones. The CLI handles cloning, diffing, and symlinking internally.

### Install a specific skill

```bash
npx skills add https://github.com/Casper-Studios/casper-marketplace --skill commit
npx skills add https://github.com/Casper-Studios/casper-marketplace --skill pr-comments
```

### Install via /plugin command

```bash
# Add the Casper Studios marketplace
/plugin marketplace add Casper-Studios/casper-marketplace

# Install a specific plugin
/plugin install casper
/plugin install data-analysis
/plugin install dev-toolkit
/plugin install stack-patterns
/plugin install cf-saas-stack
```

### Auto-sync on session start

Add `sync-skills.sh` as a [Claude Code hook](https://docs.anthropic.com/en/docs/claude-code/hooks) to keep all marketplace plugins up-to-date automatically:

```jsonc
// ~/.claude/settings.json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "bash /path/to/sync-skills.sh",
            "timeout": 60,
            "async": true
          }
        ]
      }
    ]
  }
}
```

## Plugin Structure

Each plugin follows the standard Claude Code plugin structure:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── skills/                  # Skills with SKILL.md and references/
├── commands/                # Slash commands
├── scripts/                 # Utility scripts
└── README.md               # Plugin documentation
```


## Contributing

To add a new plugin:

1. Create a new directory at the root level
2. Add the required `.claude-plugin/plugin.json` manifest
3. Add commands, scripts, and documentation
4. Submit a PR

## License

MIT
