---
description: Orchestrates documentation, analytics, and test sync with latest codebase changes
argument-hint: [feature name or "all" for full sync]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task
---

# Sync Changes

Orchestrates multiple tasks to ensure documentation, analytics, and tests stay in sync with the latest codebase changes.

Sync context: $ARGUMENTS

## Rules Reference

**IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning.**

Read `CLAUDE.md` for the compressed Rules Index. When syncing, ensure updates follow project documentation and testing conventions.

## When to Use

- After completing a feature implementation
- After making significant architectural changes
- When asked to "sync changes" or "update everything"
- Before creating a pull request (ensures completeness)
- Periodically to catch up on undocumented work

## What Gets Synced

| Task | Purpose | Output |
|----------------|---------|--------|
| Context update | Update technical documentation | Updated project docs |
| Architecture tracker | Update visual architecture docs | Updated `docs/architecture/overview.md` |
| DRY audit | Check for DRY violations | DRY compliance report + refactoring |
| Analytics | Update admin dashboard | New/updated analytics components |
| Testing | Ensure test coverage | E2E tests + test documentation |

## Workflow

### Step 1: Analyze Recent Changes

Before delegating, understand what changed:

```bash
# Check recent git changes
git diff --name-only HEAD~5  # Last 5 commits
git log --oneline -10        # Recent commit messages

# Or check uncommitted changes
git status
git diff --stat
```

Identify:
- **New files** → Need documentation, possibly analytics and tests
- **Modified schema** → May need analytics updates
- **New routes/features** → Need tests and documentation
- **API changes** → Need documentation updates

### Step 2: Delegate Tasks

Run tasks in parallel when possible (they're independent):

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           SYNC PHASE (Parallel)                               │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────┐ ┌────────────────┐ ┌─────────────┐ ┌───────────┐ ┌─────────┐ │
│  │Context Update│ │ Architecture   │ │  DRY Audit  │ │Analytics  │ │ Testing │ │
│  │              │ │ Tracker        │ │  (/dry-audit)│ │           │ │         │ │
│  │ Update docs  │ │ Update visual  │ │ Check DRY   │ │ Update    │ │ Ensure  │ │
│  │ - project    │ │ architecture   │ │ - schemas   │ │ admin     │ │ tests   │ │
│  │   docs       │ │ - Route map    │ │ - UI parts  │ │ dashboard │ │ exist   │ │
│  │ - API,schema │ │ - Feature flow │ │ - repos     │ │ metrics   │ │         │ │
│  │ - Features   │ │ - Changelog    │ │ - workflows │ │           │ │         │ │
│  └──────────────┘ └────────────────┘ └─────────────┘ └───────────┘ └─────────┘ │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Step 3: Execute Tasks

**Context Update:**
```
Review recent changes and update project documentation:

Changes to document:
- {list of changed files/features}

1. Read current project docs
2. Review the changed files
3. Update relevant sections (Features, API Routes, Database, etc.)
4. Add to Recent Changes section
5. Add Mermaid diagrams if helpful
```

**Analytics:**
```
Check if recent schema/feature changes need analytics:

Recent changes:
- {list of changed files}

1. Read app/db/schema.ts for new tables/fields
2. Identify analytics opportunities:
   - New timestamp fields → time-series charts
   - New enum fields → distribution charts
   - New boolean fields → conversion metrics
3. If new analytics needed:
   - Add repository functions
   - Add tRPC routes
   - Update admin dashboard
4. If no new analytics needed, report "No analytics updates required"
```

**Documentation Sync:**
```
Sync .cursor/context/ changes to docs/architecture/:

For each updated .cursor/context/ file, update the corresponding docs/architecture/ file:
- architecture.md -> docs/architecture/system.md
- api.md -> docs/architecture/api.md
- data-models.md -> docs/architecture/data-models.md
- features.md -> docs/architecture/features.md
- integrations.md -> docs/architecture/integrations.md
- security.md -> docs/architecture/security.md
- user-journeys.md -> docs/architecture/user-journeys.md

If design system changed (app.css, new components):
- Update docs/design/design-system-overview.md
```

**Architecture Tracker:**
```
Update architecture overview document for recent changes:

Recent changes:
- {list of changed files}

1. Read docs/architecture/overview.md
2. Check app/routes.ts for new routes
3. Update relevant sections:
   - Route Map diagram (if new routes)
   - Information Architecture table (if new routes)
   - Feature Flows section (if new features)
   - Data Relationships (if schema changes)
4. Add Changelog entry with today's date
```

**Testing:**
```
Verify test coverage for recent changes:

Recent changes:
- {list of changed files}

1. Check if e2e tests exist for new/changed routes
2. For each untested feature:
   - Create testing plan at docs/testing/{feature}/{feature}.md
   - Create screenshots folder at docs/testing/{feature}/screenshots/
   - Write e2e test in e2e/
   - Add data-testid attributes if missing
3. Run tests to verify they pass: bun run test:e2e
4. Save Playwright screenshots to docs/testing/{feature}/screenshots/
5. CRITICAL: Copy screenshots to public folder for docs viewer:
   mkdir -p public/docs/testing/{feature}/screenshots
   cp docs/testing/{feature}/screenshots/*.png public/docs/testing/{feature}/screenshots/
```

---

## Decision Matrix

| Change Type | Context Update | Architecture Tracker | DRY Audit | Analytics | Design System | Testing |
|-------------|----------------|---------------------|-----------|-----------|---------------|---------|
| New feature | Required | Required | Required | Check schema | Skip | Required |
| Schema change | Required | Required | Required | Required | Skip | Maybe |
| New routes | Required | Required | Maybe | Skip | Skip | Required |
| UI-only change | Required | Skip | Required | Skip | Maybe | Required |
| Bug fix | Maybe | Skip | Skip | Skip | Skip | Required |
| API change | Required | Maybe | Maybe | Maybe | Skip | Required |
| Config change | Required | Skip | Skip | Skip | Skip | Skip |
| CSS/theme change | Maybe | Skip | Skip | Skip | Required | Maybe |
| New components | Maybe | Skip | Maybe | Skip | Required | Maybe |

---

## Quick Sync Commands

For quick syncs, you can run a simplified version:

**Documentation only:**
```
Review git diff and update project docs with recent changes.
```

**Architecture only:**
```
Review app/routes.ts and update docs/architecture/overview.md with any new routes. Add changelog entry.
```

**DRY audit:**
```
Run /dry-audit against recently changed files. Check for duplicated schemas, UI patterns, repository logic, and workflow code. Report findings and refactor.
```

**Analytics check:**
```
Review schema.ts and check if any new fields need analytics tracking.
```

**Test coverage check:**
```
Check e2e/ folder against app/routes/ and identify missing test coverage.
```

---

## Full Sync Example

```markdown
**User Request:** "Sync changes after recipe extraction feature"

**Analysis:**
- New files: app/lib/content-extractor.ts, app/lib/claude.ts
- Modified: app/trpc/routes/recipes.ts, app/repositories/recipe.ts
- New schema fields: recipes table with createdAt

**Execution (Parallel):**

1. **Context Update** → Document:
   - Recipe extraction feature
   - Claude AI integration
   - Content extractor architecture

2. **Architecture Tracker** → Update:
   - Add /recipes/new route to Route Map
   - Add Recipe Extraction feature flow diagram
   - Add changelog entry

3. **Analytics** → Add:
   - Recipe creation time-series chart
   - Source type distribution (YouTube vs URL)

4. **Testing** → Create:
   - e2e/recipes.spec.ts tests
   - Testing plan for extraction flow
   - Test documentation with screenshots
```

---

## Checklist

After sync completes, verify:

- [ ] Project documentation reflects current state of codebase
- [ ] `docs/architecture/overview.md` has all routes and features
- [ ] Changelog has entry for recent changes
- [ ] Recent Changes section is up to date
- [ ] DRY audit passed — no duplicated schemas, UI patterns, or repo logic (run /dry-audit)
- [ ] Analytics dashboard shows relevant metrics (if applicable)
- [ ] E2E tests exist for all user-facing features
- [ ] Test documentation with screenshots at `docs/testing/{feature}/`
- [ ] **Screenshots copied to `public/docs/testing/{feature}/screenshots/`** (required for docs viewer)
- [ ] No broken tests (run `bun run test:e2e`)

---

## When to Skip Tasks

**Skip context update if:**
- Only fixing typos or minor bugs
- Changes are purely internal (no user impact)

**Skip architecture tracker if:**
- No new routes added
- No new features implemented
- No schema changes
- Changes are UI-only tweaks (not new pages)
- Bug fixes or refactors

**Skip DRY audit if:**
- Changes are documentation-only
- Changes are config/environment only
- Bug fixes that don't add new code patterns

**Skip analytics if:**
- No schema changes
- No new trackable data
- Changes are UI-only

**Skip testing if:**
- Changes are documentation-only
- Changes are config/environment only
- Tests already exist and still pass
