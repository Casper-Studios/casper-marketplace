# Brain - Client Project Context Plugin for Claude Code

Brain provides company, project, and meeting context for teams using Claude Code on consulting engagements.

## Features

- **Progressive Disclosure**: Access company, project, and meeting context at the right level of detail
- **Client Onboarding**: Data-room profiling and findings export for new client engagements
- **Meeting Follow-up**: Summaries and action items from meeting transcripts
- **Transcript Search**: Search Fireflies and Google Drive transcripts across clients

## Installation

```bash
# 1. Add the Casper Studios marketplace
/plugin marketplace add Casper-Studios/casper-marketplace

# 2. Install the plugin
/plugin install brain
```

For security hooks and privacy settings, also install the `marketplace-setup` plugin — see its README for setup instructions.

## Commands

### `/brain:company` - Layer 1: Company Overview

View high-level company information and client list.

- Company description and tech stack
- Coding standards
- List of clients with brief descriptions

### `/brain:projects` - Layer 2: Project Details

View detailed project information and requirements.

- Project goals and status
- Technical design
- Phase breakdown
- Supports filtering by client: `/brain:projects client-name`

### `/brain:transcripts` - Layer 3: Meeting History

View meeting transcripts and decision logs.

- Meeting summaries
- Key decisions
- Action items
- Supports filtering: `/brain:transcripts client-name`

## Skills

- **casper-client-onboarding**: Data-room profiling and findings export for onboarding new clients
- **meeting-followup**: Summarize meetings and extract action items from transcripts
- **transcript-search**: Search Fireflies and Google Drive transcripts by keyword, date, or client

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
brain/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── commands/
│   ├── company.md               # Layer 1 command
│   ├── projects.md              # Layer 2 command
│   └── transcripts.md           # Layer 3 command
├── skills/
│   ├── casper-client-onboarding/
│   ├── meeting-followup/
│   └── transcript-search/
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
└── README.md                    # This file
```

## Verification

After installing, verify the plugin is working:

1. **Check commands appear:** Run `/help` and look for `brain` commands
2. **Test context commands:** Run `/brain:company` to see company info

## Troubleshooting

### Commands not appearing

- Ensure the plugin directory is correctly specified with `--plugin-dir`
- Check that `.claude-plugin/plugin.json` exists and is valid JSON

## License

MIT
