---
description: View meeting transcripts and decision logs (Layer 3 context)
---

# Meeting Transcripts

Read and present meeting transcripts for deep historical context.

## Instructions

1. First, read `${CLAUDE_PLUGIN_ROOT}/data/clients/_index.md` to identify all clients
2. For each client, check for transcript files in `${CLAUDE_PLUGIN_ROOT}/data/transcripts/{client-name}/`
3. Read all transcript markdown files found
4. Present a summary of each meeting including:
   - Meeting date and attendees
   - Key discussion points
   - Decisions made
   - Action items

## Arguments

If the user specifies a client name, only show transcripts for that client:
- `/casper:transcripts client-a` - Show only Client A transcripts

If the user specifies a date or meeting name, filter accordingly:
- `/casper:transcripts kickoff` - Show only kickoff meeting transcripts

## Usage Tips

For higher-level context, use:
- `/casper:company` - View company overview and client list
- `/casper:projects` - View detailed project information and PRDs
