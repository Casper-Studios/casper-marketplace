<p align="center">
  <img src="casper-studios-logo.png" alt="Casper Studios" width="300">
</p>

A collection of Claude Code plugins for business automation, data analysis, and productivity.

## Available Plugins

Plugins are organized by workstream under `plugins/`.

| Workstream | Plugin | Description |
|------------|--------|-------------|
| bizdev | [crm](./plugins/bizdev/crm/) | CRM operations for companies, contacts, and notes via Attio |
| bizdev | [research](./plugins/bizdev/research/) | Social media, web, and market research scraping |
| design | [doc-format](./plugins/design/doc-format/) | AI-powered document, image, and flowchart generation |
| design | [design-system](./plugins/design/design-system/) | Casper Studios design system and Liquid Glass UI guidance |
| design | [content-marketing](./plugins/design/content-marketing/) | LinkedIn posts, video production, and YouTube tooling |
| engineering | [code-review](./plugins/engineering/code-review/) | Codebase audits for AI-agent readiness and code review |
| engineering | [skill-authoring](./plugins/engineering/skill-authoring/) | Tooling for creating and updating Claude Code skills |
| engineering | [marketplace-setup](./plugins/engineering/marketplace-setup/) | Security hooks, safe .env loading, and privacy settings |
| engineering | [git-pr](./plugins/engineering/git-pr/) | Committing, PR creation and review triage, dependency upgrades, and Linear ticket extraction |
| engineering | [testing](./plugins/engineering/testing/) | Browser automation and testing |
| engineering | [integrations](./plugins/engineering/integrations/) | Google Workspace and universal third-party app integrations |
| engineering | [cf-saas-stack](./plugins/engineering/cf-saas-stack/) | Cloudflare SaaS stack patterns - auth, database, workflows, emails, Stripe, and more |
| engineering | [stack-patterns](./plugins/engineering/stack-patterns/) | Idiomatic usage patterns for React, TanStack Table, and better-all |
| product | [data-analysis](./plugins/product/data-analysis/) | Data analysis and storytelling for financial and RevOps contexts |
| product | [csv-analyzer](./plugins/product/csv-analyzer/) | CSV data analysis, profiling, and visualization |
| product | [discovery](./plugins/product/discovery/) | AI voice agent creation for client discovery and feedback calls |
| project-management | [brain](./plugins/project-management/brain/) | Context management for consulting projects - company info, project PRDs, meeting transcripts |
| project-management | [comms](./plugins/project-management/comms/) | Email triage and Slack channel automation |

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

# Install a specific plugin (see table above for the full list)
/plugin install brain
/plugin install data-analysis
/plugin install git-pr
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

Plugins are grouped by workstream under `plugins/<workstream>/<plugin-name>/`. Each plugin follows the standard Claude Code plugin structure:

```
plugins/<workstream>/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── skills/                  # Skills with SKILL.md and references/
├── commands/                # Slash commands
├── scripts/                 # Utility scripts
└── README.md               # Plugin documentation
```


## Contributing

To add a new plugin:

1. Create a new directory under `plugins/<workstream>/` (add a new workstream folder if none fits)
2. Add the required `.claude-plugin/plugin.json` manifest
3. Add commands, scripts, and documentation
4. Submit a PR

When changing an existing plugin, bump its `.claude-plugin/plugin.json` `version` (and the matching `marketplace.json` entry) following semver — MAJOR for breaking changes like renaming a skill, MINOR for new features, PATCH for fixes. Without a bump, users won't receive the update.

## License

MIT
