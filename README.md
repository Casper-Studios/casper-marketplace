# Casper Studios Plugin Marketplace

A collection of Claude Code plugins for business automation, data analysis, and productivity.

## Available Plugins

| Plugin | Description |
|--------|-------------|
| [casper](./casper/) | Context management for consulting projects - company info, project PRDs, meeting transcripts |
| [thats-my-quant](./thats-my-quant/) | Data analysis and storytelling for financial and RevOps contexts |
| [dev-toolkit](./dev-toolkit/) | Workflow automation skills for planning, commits, PR management, and code polishing |
| [stack-patterns](./stack-patterns/) | Idiomatic usage patterns for React, TanStack Table, and better-all |

## Installation

### Install from Marketplace

```bash
# Add the Casper Studios marketplace
/plugin marketplace add Casper-Studios/plugin-marketplace

# Install a specific plugin
/plugin install casper
/plugin install thats-my-quant
/plugin install dev-toolkit
/plugin install stack-patterns
```

### Install via Git Clone

```bash
# Clone the repository
git clone git@github.com:Casper-Studios/plugin-marketplace.git

# Run Claude Code with the plugin directory
claude --plugin-dir ./plugin-marketplace
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

> **Note:** `dev-toolkit` and `stack-patterns` were created by the Ardmore Pod to share workflow skills and coding patterns across their repos. They're available to the whole team — install whichever ones are useful for your workflow.

## Contributing

To add a new plugin:

1. Create a new directory at the root level
2. Add the required `.claude-plugin/plugin.json` manifest
3. Add commands, scripts, and documentation
4. Submit a PR

## License

MIT
