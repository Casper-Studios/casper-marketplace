---
name: context-docs
description: Documentation hierarchy and maintenance rules for context docs and architecture files
user-invocable: false
---

# Context Documentation Maintenance

## Documentation Hierarchy

**Source of Truth**: `.cursor/context/` folder contains detailed documentation:
- `api.md` - tRPC routes, auth endpoints, procedure types, error responses
- `architecture.md` - System overview, data flow patterns, layer responsibilities
- `high-level-architecture.md` - Living visual doc with route map, feature flows, data relationships, changelog (canonical version at `docs/architecture/overview.md`)
- `data-models.md` - Schema, entity relationships, tables overview, migrations
- `features.md` - Feature documentation with flow diagrams and key files
- `integrations.md` - External services (Cloudflare, Better Auth, Stripe, PostHog)
- `security.md` - Auth flow, session management, authorization, RBAC
- `user-journeys.md` - User flows, admin journeys, error states

**Quick Reference**: `.cursor/context.md` is a compressed index that:
- Points agents to detailed docs in `.cursor/context/`
- Provides compressed indices of rules and context docs
- Contains brief overview, tech stack summary, and recent changes

## When to Update

### Update detailed docs when:
- Implementing new features -> `features.md`
- Adding API routes -> `api.md`
- Changing architecture -> `architecture.md`
- Modifying schema -> `data-models.md`
- Adding integrations -> `integrations.md`
- Changing auth/security -> `security.md`
- New user flows -> `user-journeys.md`

### Update context.md index when:
- A context doc's scope changes
- Adding new rules
- Adding significant new features
- Adding new tech stack components

### Update docs/architecture/overview.md when:
- Adding new routes (update Route Map)
- Implementing new features (add Feature Flow section)
- Schema changes (update Data Relationships ER diagram)
- Architectural decisions (update System Architecture)
- **Always add a Changelog entry with date**

### Update docs/architecture/ when:
- Updating corresponding `.cursor/context/` files (dual sync)
- Architecture, API, schema, features, integrations, security, or user flows change

### Update docs/design/design-system-overview.md when:
- Modifying `app/app.css` (color variables, typography)
- Adding new ShadCN components
- Changing icon sets or spacing conventions

## Pipe-Delimited Index Format (for context.md)
```
[Index Name]|root: path/to/files/
|IMPORTANT: Key instruction
|file1.ext: brief description
|subdir/:{file-a.ext,file-b.ext,...}
```

## context.md Required Sections
1. Agent Instructions
2. Context Docs Index
3. Rules Index
4. Overview (one sentence)
5. Tech Stack
6. Architecture (2-4 bullets)
7. Features (3-5 lines max each)
8. Recent Changes (last 3-4)

## Human Documentation (`docs/`)

The `docs/` directory contains human-readable documentation visible in the admin docs viewer at `/admin/docs`:

```
docs/
|-- architecture/         # System architecture docs (mirrors .cursor/context/)
|   |-- overview.md       # Master doc: route map, feature flows, changelog
|   |-- system.md         # System architecture (from architecture.md)
|   |-- api.md            # API reference (from api.md)
|   |-- data-models.md    # Data models (from data-models.md)
|   |-- features.md       # Feature catalog (from features.md)
|   |-- integrations.md   # Integrations (from integrations.md)
|   |-- security.md       # Security model (from security.md)
|   |-- user-journeys.md  # User journeys (from user-journeys.md)
|-- design/               # Design system docs
|   |-- design-system-overview.md  # Colors, typography, components
|-- features/             # Feature documentation
|-- ideas/                # Ideas and brainstorms
|-- meetings/             # Meeting notes
|-- plans/                # Roadmaps and plans
|-- releases/             # Release notes
```

### Dual Documentation Pattern

`.cursor/context/` files are optimized for AI agent consumption (compressed, indexed).
`docs/architecture/` files are optimized for human reading (prose, Mermaid diagrams, frontmatter).

When updating `.cursor/context/`, also update the corresponding `docs/architecture/` file.
When making design system changes, update `docs/design/design-system-overview.md`.
Always add a changelog entry to `docs/architecture/overview.md`.

## Compression Philosophy
- Target 80%+ reduction from verbose docs
- Agent should quickly understand project structure and know where to look
