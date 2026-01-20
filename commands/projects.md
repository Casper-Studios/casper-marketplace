---
description: View detailed project information and PRDs (Layer 2 context)
---

# Project Context

Read and present detailed project information for all clients.

## Instructions

1. First, read `${CLAUDE_PLUGIN_ROOT}/data/clients/_index.md` to identify all clients
2. For each client, check for project files in `${CLAUDE_PLUGIN_ROOT}/data/projects/{client-name}/`
3. Read all project markdown files found
4. Present a summary of each project including:
   - Project name and status
   - Goals and requirements
   - Technical context
   - Current phase/progress

## Arguments

If the user specifies a client name, only show projects for that client:
- `/casper:projects client-a` - Show only Client A projects

## Usage Tips

For additional context, use:
- `/casper:company` - View company overview and client list
- `/casper:transcripts` - View meeting transcripts and decision logs
