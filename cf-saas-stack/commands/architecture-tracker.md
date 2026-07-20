---
description: Maintains the living high-level architecture document with route maps, feature flows, and changelog
argument-hint: <feature or change to document>
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task
---

# Architecture Tracker

Maintain the project's living high-level architecture document at `docs/architecture/overview.md`.

Update context: $ARGUMENTS

## When to Use

Invoke **after** completing:
- New feature implementation
- New routes added
- Database schema changes
- Architectural decisions
- Navigation or flow changes

## Quick Start

1. **Check the document exists**: `docs/architecture/overview.md`
2. **Review recent changes**: What routes, features, or tables were added?
3. **Update relevant sections**: Route Map, Feature Flows, Data Relationships
4. **Add changelog entry**: Document what changed with date

## Document Sections

| Section | What It Shows | When to Update |
|---------|---------------|----------------|
| Product Overview | Mindmap of capabilities | New feature areas |
| Route Map | Visual route hierarchy | New routes added |
| Information Architecture | Route table with details | New/changed routes |
| Feature Flows | Diagrams per feature | New features |
| Data Relationships | ER diagram | Schema changes |
| System Architecture | Tech layer diagram | Architectural changes |
| Changelog | Dated list of changes | Every update |

## Workflow

### After New Feature

```
1. Read the feature's architecture doc (if exists):
   docs/features/[feature]-architecture.md

2. Update docs/architecture/overview.md:
   - Add to Product Overview mindmap
   - Add new routes to Route Map
   - Add row(s) to Information Architecture table
   - Add Feature Flow section with diagram
   - Update Data Relationships if new tables
   - Add Changelog entry
```

### After New Routes Only

```
1. Update Route Map flowchart
2. Add row(s) to Information Architecture table
3. Add Changelog entry
```

### After Schema Changes

```
1. Update Data Relationships ER diagram
2. Add Changelog entry
```

## Changelog Entry Format

```markdown
### YYYY-MM-DD - Feature/Change Name
- Added: Description of what was added
- Changed: Description of what changed
- Removed: Description of what was removed
```

## How to Run

Use the Task tool to delegate this work:

```
Update the architecture overview document (docs/architecture/overview.md) after implementing [feature name].

Changes made:
- New routes: [list routes]
- New tables: [list tables]
- New features: [describe]

Reference: docs/features/[feature]-architecture.md (if exists)
```

## Integration with Other Commands

**After /implement-feature**: The architecture-tracker should run to update the high-level view.

**After context update**: Context update handles detailed technical docs; architecture-tracker updates the visual overview.

Execution order:
```
implement-feature → context update → architecture-tracker
```

## What Makes This Different from Context Update

| Aspect | Context Update | Architecture Tracker |
|--------|----------------|---------------------|
| Audience | AI agents | Human developers |
| Format | Compressed text indices | Visual diagrams |
| Focus | Technical details | High-level structure |
| Primary content | API, security, data models | Route maps, flows, changelog |
| Update frequency | After any change | After architectural changes |

## Checklist

Before completing an architecture update:

- [ ] Product Overview mindmap reflects current capabilities
- [ ] Route Map includes all routes (check `app/routes.ts`)
- [ ] Information Architecture table is complete
- [ ] Feature Flows exist for each major feature
- [ ] Data Relationships matches current schema
- [ ] Changelog entry added with today's date
- [ ] All Mermaid diagrams render correctly
