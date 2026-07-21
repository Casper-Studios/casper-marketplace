---
name: docs
description: Documentation guidelines for creating and maintaining docs folder structure
user-invocable: false
---

# Documentation Guidelines

Rules for creating and maintaining documentation in the `docs/` folder.

## File Structure
```
docs/
  features/   # Technical feature documentation and architecture
  ideas/      # Brainstorming and feature ideas
  meetings/   # Meeting notes (date-prefixed)
  plans/      # Roadmaps and project plans
  releases/   # Changelog and release notes
  research/   # Competitive research and UX analysis
  testing/    # Testing plans with screenshots
    {feature}/
      {feature}.md
      screenshots/
```

## Naming Conventions
- **meetings:** `YYYY-MM-DD-description.md`
- **releases:** `vX.Y.Z.md` or `YYYY-MM-DD-release.md`
- **testing:** `{feature-name}/{feature-name}.md`
- **research:** `{topic}-research.md`
- **features:** `{feature-name}.md` or `{feature-name}-architecture.md`
- **others:** `kebab-case.md`

## Frontmatter (REQUIRED)
All documents MUST include YAML frontmatter with at minimum a `date` field:
```markdown
---
title: Human-Readable Title
date: 2026-01-29
---
```

## Testing Documentation Structure
Testing plans live in `docs/testing/` with their own screenshots folder:
```
docs/testing/{feature-name}/
  {feature-name}.md      # Testing plan
  screenshots/           # Playwright screenshots
```

### CRITICAL: Copy Screenshots to Public Folder
Screenshots MUST also be copied to `public/docs/testing/` for the documentation viewer to display them:
```bash
mkdir -p public/docs/testing/{feature-name}/screenshots
cp docs/testing/{feature-name}/screenshots/*.png public/docs/testing/{feature-name}/screenshots/
```

## Category-Specific Templates

### Feature Documentation
```markdown
---
title: Feature Name
date: YYYY-MM-DD
---
# Feature Name
## Overview
## How It Works
## Usage
## Key Files
```

### Testing Plan
```markdown
# Testing Plan: {Feature Name}
## Overview
## Prerequisites
## Test Scenarios
### Scenario 1: {Happy Path}
## UI Elements to Verify
## Test IDs Reference
## E2E Test Coverage
```

### Release Notes
```markdown
# vX.Y.Z
## Summary
## New Features
## Bug Fixes
## Breaking Changes
```

### Meeting Notes
```markdown
# Meeting Title
**Date:** YYYY-MM-DD
**Attendees:** Names
## Agenda
## Discussion
## Action Items
## Next Meeting
```

## Formatting Standards
1. Use H1 for main title, H2 for sections, H3 for subsections
2. Include Mermaid diagrams for complex flows
3. Use tables for structured data
4. Use `- [ ]` for action items
5. Always specify language in code blocks

## Best Practices
1. Be concise: Write for clarity, not length
2. Use visuals: Mermaid diagrams help explain complex concepts
3. Link related docs
4. Keep updated: Remove outdated information
5. Screenshots in testing: Save to `docs/testing/{feature}/screenshots/` AND copy to `public/docs/testing/{feature}/screenshots/`
