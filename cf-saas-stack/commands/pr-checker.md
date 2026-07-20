---
description: Validates that changes follow project standards before creating a pull request
argument-hint: [PR context or "check" for current branch]
allowed-tools: Read, Glob, Grep, Bash
---

# PR Checker

Validate that changes follow project standards before creating a pull request.

PR context: $ARGUMENTS

## Rules Reference

**IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning.**

Read `CLAUDE.md` and project documentation for the compressed Rules Index. When validating files, read the full project conventions to verify compliance.

## When to Run

**Run this skill proactively** before using /create-pull-request. This ensures all requirements are met before PR creation.

## Validation Checklist

Copy and track progress:

```
PR Validation:
- [ ] 1. Code rules compliance
- [ ] 2. DRY compliance (no duplicated schemas, UI patterns, or repo logic)
- [ ] 3. Implementation plan saved (docs/plans/)
- [ ] 4. Research doc exists (if new user-facing feature)
- [ ] 5. Feature architecture doc exists (if new feature)
- [ ] 6. context.md updated (if feature/architecture change)
- [ ] 7. docs/architecture/overview.md updated (if new routes/features/schema)
- [ ] 8. Testing plan exists
- [ ] 9. Migrations use /db-migration (if applicable)
- [ ] 10. Analytics considered (if schema/feature change)
- [ ] 11. Ready for /create-pull-request
```

---

## Step 1: Gather Changed Files

```bash
# Get list of changed files
git diff main...HEAD --name-only

# Get the actual diff for review
git diff main...HEAD
```

---

## Step 2: Check Code Rules Compliance

For each changed file, verify it follows the appropriate rule based on file location:

| File Pattern | Rule to Check |
|--------------|---------------|
| `app/repositories/*.ts` | Repository pattern (see CLAUDE.md) |
| `app/trpc/routes/*.ts` | Repository pattern (see CLAUDE.md) |
| `app/routes/**/*.tsx` | Routes conventions (see CLAUDE.md) |
| `app/db/schema.ts` | Database conventions (see CLAUDE.md) |
| `app/models/*.ts` | Models conventions (see CLAUDE.md) |
| `app/models/errors/*.ts` | Errors conventions (see CLAUDE.md) |
| `app/components/*-modal.tsx` | Modal patterns (see CLAUDE.md) |
| `app/prompts/*.ts` | Prompts conventions (see CLAUDE.md) |
| `**/stripe*`, `**/payment*` | Stripe conventions (see CLAUDE.md) |
| `e2e/**/*` | Playwright rules (see CLAUDE.md) |
| `app/lib/constants/*` | Constants conventions (see CLAUDE.md) |
| `docs/**/*.md` | Documentation conventions (see CLAUDE.md) |

### Verification Process

1. Read the applicable project conventions from `CLAUDE.md`
2. Review the changed code against convention requirements
3. Flag any violations

### Common Violations to Check

**Repository files:**
- Missing `Database` type alias
- Importing tRPC or request objects
- Missing try-catch with custom error types
- Accessing context/session directly

**tRPC routes:**
- Missing Zod input validation
- Not using appropriate procedure type
- Direct database access (should use repositories)

**Route files:**
- Missing loader authentication check
- Not using `context.trpc` for data fetching

**Documentation files (docs/*.md):**
- Missing H1 title
- Wrong naming convention (meetings should be `YYYY-MM-DD-*.md`, releases should be `vX.Y.Z.md` or date-prefixed)
- File in wrong category folder
- Missing required sections for category (e.g., releases need Summary, New Features, Bug Fixes)

---

## Step 2: Check DRY Compliance

**Required when:** Adding new schemas, components, repositories, or workflows.

### Run the DRY Audit

Run /dry-audit and check changed files against the known patterns:

**Schemas** (`app/models/`):
- New Zod schemas should extend base schemas from `common.ts` when fields overlap (executive summaries, risks, opportunities, workflow payloads)
- Search for duplicated fields like `keyFindings`, `deliveryRisks`, `quickWins`, `severity`

**UI Components** (`app/routes/`, `app/components/`):
- Loading spinners should reuse shared component, not reinvent `animate-spin` + `IconLoader2`
- Error/failed states should reuse shared component, not duplicate `IconAlertTriangle` blocks
- Status badges should use shared config pattern, not duplicate status-to-color maps

**Repositories** (`app/repositories/`):
- Pagination logic should use shared helper, not duplicate `Math.ceil` + offset pattern
- Organization access checks should use shared function, not inline `organizationId !==` checks
- AI service checks should use shared utility, not duplicate `TRPCError` throws

**Workflows** (`workflows/`):
- Step name maps should be shared when overlapping
- Progress update wrappers should use shared function
- Source index mapping should use shared utility

### If DRY Violations Found

**Prompt user:** "DRY violations found in {files}. The following patterns are duplicated: {patterns}. Extract to {target location} before creating the PR."

### When NOT Required

- Documentation-only changes
- Config/environment changes
- Bug fixes that don't add new patterns

---

## Step 3: Check Implementation Plan Saved

**Required when:** Implementing new features from a plan.

### Verify Plan Doc Exists

```bash
# Check if implementation plan was saved
ls -la docs/plans/*-implementation.md 2>/dev/null
```

**The implementation plan should be saved from the plan to `docs/plans/{feature}-implementation.md` and include:**
- Overview of the feature
- Implementation tasks with status
- Architecture diagrams
- Key files created/modified
- Links to related docs (research, architecture, testing)

### When NOT Required

- Bug fixes without a formal plan
- Minor changes
- Documentation-only updates

---

## Step 4: Check Research Documentation

**Required when:** Adding new user-facing features that involve UX decisions.

### Verify Research Doc Exists

```bash
# Check if research doc was created
ls -la docs/research/*-research.md 2>/dev/null
```

**For new user-facing features, `docs/research/{feature}-research.md` should include:**
- Executive summary of findings
- Competitive landscape analysis
- Common UX patterns observed
- Differentiation opportunities
- Recommendations

### When NOT Required

- Backend-only features
- Bug fixes
- Refactoring
- Minor UI tweaks without UX decisions
- Features where patterns are already established

### If Missing

**Prompt user:** "Research doc not found for this user-facing feature. Consider using WebSearch to research competitors and UX patterns, then document in `docs/research/{feature}-research.md`."

---

## Step 5: Check context.md Updates

**Required when:** Adding features, changing architecture, modifying API routes, or updating database schema.

### Verify context.md

```bash
# Check if context.md was modified
git diff main...HEAD --name-only | grep -q "context.md"
```

**If feature/architecture changes exist but context.md is unchanged:**

1. Read current project documentation
2. Identify what should be added:
   - New features → Add to Features section
   - New API routes → Add to API Routes section
   - Schema changes → Add to Database section
   - Architecture changes → Update Architecture section

3. **Prompt user:** "Project documentation needs updating. Should I add the new [feature/route/schema] to project docs?"

### context.md Update Template

Add to the `## Recent Changes` section:

```markdown
## Recent Changes
- [DATE] Added [feature name] - [brief description]
```

---

## Step 5.5: Check docs/architecture/overview.md Updates

**Required when:** Adding new routes, implementing new features, or making database schema changes.

### Verify docs/architecture/overview.md

```bash
# Check if docs/architecture/overview.md was modified
git diff main...HEAD --name-only | grep -q "docs/architecture/overview.md"

# Check if new routes were added
git diff main...HEAD -- app/routes.ts
```

**If routes/features/schema changed but docs/architecture/overview.md is unchanged:**

1. Check what needs updating:
   - New routes → Update Route Map diagram + Information Architecture table
   - New features → Add Feature Flow section with Mermaid diagram
   - Schema changes → Update Data Relationships ER diagram

2. **Prompt user:** "docs/architecture/overview.md needs updating. Run /architecture-tracker to update route maps, feature flows, and add a changelog entry."

### What Should Be Updated

| Change Type | Sections to Update |
|-------------|-------------------|
| New routes | Route Map, Information Architecture table, Changelog |
| New features | Route Map, Feature Flows, possibly Data Relationships, Changelog |
| Schema changes | Data Relationships ER diagram, Changelog |
| Architectural decisions | System Architecture, Changelog |

### Changelog Entry Format

```markdown
### YYYY-MM-DD - Feature/Change Name
- Added: New route at `/path`
- Added: New table `table_name`
- Changed: Modified flow for X
```

---

## Step 6: Check Feature Architecture Doc

**Required when:** Adding new features with multiple files/layers.

### Verify Feature Architecture Doc Exists

```bash
# Check if feature architecture doc was created
ls -la docs/features/*-architecture.md 2>/dev/null
```

**For new features, `docs/features/{feature}-architecture.md` should include:**
- Overview and vision
- User flow diagrams (mermaid)
- System architecture diagram
- Data model (ER diagram + TypeScript interfaces)
- Feature breakdown with specifications
- UI component hierarchy
- Frontend design specification
- API endpoints table

### When NOT Required

- Bug fixes
- Refactoring without new features
- Minor UI changes
- Documentation-only updates

### If Missing

**Prompt user:** "Feature architecture doc not found. Create `docs/features/{feature}-architecture.md` with user flows, data model, and component hierarchy."

---

## Step 7: Verify Testing Exists

Check for testing artifacts:

```bash
# Check for e2e test files
ls -la e2e/*.spec.ts 2>/dev/null

# Check for testing plans with screenshots
ls -la docs/testing/*/*.md 2>/dev/null
ls -la docs/testing/*/screenshots/ 2>/dev/null
```

### Required Testing Artifacts

For feature PRs, the following should exist:

1. **E2E Tests**: `e2e/{feature}.spec.ts`
   - Tests for happy path
   - Tests for edge cases
   - Tests for error states

2. **Testing Plan**: `docs/testing/{feature}/{feature}.md`
   - Test scenarios with descriptions
   - UI elements checklist
   - Test IDs reference table
   - Screenshots in `docs/testing/{feature}/screenshots/`

3. **Data-testid Attributes**: Key elements should have `data-testid` for reliable testing

### If No Testing Found

**Prompt user:** "No e2e tests found. Before creating the PR:
1. Create testing plan at `docs/testing/{feature}/{feature}.md`
2. Verify the implementation with Bash using playwright
3. Save screenshots to `docs/testing/{feature}/screenshots/`
4. Write e2e tests in `e2e/`
5. Add data-testid attributes to key elements"

---

## Step 8: Check Migration Compliance

**Only if `drizzle/` files were changed or `app/db/schema.ts` was modified.**

### Verify Migration Naming

```bash
# List recent migrations
ls -la drizzle/*.sql | tail -5
```

**Check naming convention:**
- `0001_add_user_preferences.sql` (snake_case, descriptive)
- `0001_migration.sql` (generic - BAD)
- `0001_AddUserPreferences.sql` (not snake_case - BAD)

### If Schema Changed Without Migration

**Prompt user:** "Schema changes detected but no new migration. Run `bun run db:generate --name 'descriptive_name'` using /db-migration."

---

## Step 9: Check Analytics Considerations

**Required when:** Adding database schema changes, new features with user data, or modifying existing data models.

### Identify Analytics Opportunities

When schema or features are added, check if analytics should be implemented:

1. **Timestamp fields** (`createdAt`, `updatedAt`) → Time-series growth charts
2. **Enum/status fields** (`role`, `status`, `type`) → Distribution charts
3. **Boolean fields** (`emailVerified`, `isActive`, `banned`) → Conversion/rate metrics
4. **User-facing features** → Usage tracking dashboards

### Verification Process

```bash
# Check if schema was modified
git diff main...HEAD --name-only | grep -E "(schema\.ts|db/)"

# Check if analytics files exist or were updated
git diff main...HEAD --name-only | grep -E "(analytics|dashboard)"
```

### When Analytics Should Be Added

**Prompt user if:**
- Schema adds new tables/fields with trackable data but no analytics routes exist
- New user-facing feature added without usage metrics
- Data model changes that affect existing analytics

**Prompt:** "Schema/feature changes detected. Consider creating growth dashboards and tracking for the new data."

### When Analytics Are NOT Required

- Internal refactoring without data model changes
- Bug fixes
- Documentation updates
- UI-only changes without new data collection

---

## Step 10: Final Validation Report

Generate a summary:

```markdown
## PR Validation Report

### Code Rules
- [pass/fail] Repository pattern compliance
- [pass/fail] tRPC route validation
- [pass/fail] Route conventions

### DRY Compliance
- [pass/fail/N/A] No duplicated schema patterns (use base schemas from `common.ts`)
- [pass/fail/N/A] No duplicated UI patterns (use shared components)
- [pass/fail/N/A] No duplicated repository logic (use shared helpers)
- [pass/fail/N/A] No duplicated workflow patterns (use shared utilities)

### Documentation
- [pass/fail] Implementation plan saved (`docs/plans/{feature}-implementation.md`)
- [pass/fail/N/A] Research doc (`docs/research/{feature}-research.md`) - for user-facing features
- [pass/fail] Feature architecture doc (`docs/features/{feature}-architecture.md`)
- [pass/fail] Project docs updated
- [pass/fail] docs/architecture/overview.md updated (routes, flows, changelog)
- [pass/fail] Testing plan exists (`docs/testing/{feature}/{feature}.md`)

### Testing
- [pass/fail] E2E tests exist (`e2e/*.spec.ts`)
- [pass/fail] Data-testid attributes added
- [pass/fail] All tests pass locally

### Database
- [pass/fail] Migration naming convention
- [pass/fail] No data-deleting migrations

### Analytics
- [pass/fail/N/A] Analytics considered for new data

### Ready for PR
- [pass/fail] All checks passed
```

---

## Proceed to PR Creation

**Only after all checks pass**, use /create-pull-request to create the PR.

If checks fail, address the issues first:
1. Fix code rule violations
2. Fix DRY violations — extract shared patterns per /dry-audit
3. Save implementation plan to `docs/plans/{feature}-implementation.md`
3. Create research doc at `docs/research/{feature}-research.md` (use WebSearch)
4. Create feature architecture doc at `docs/features/{feature}-architecture.md`
5. Update project documentation
6. Update docs/architecture/overview.md via /architecture-tracker
7. Generate testing plan
8. Generate migrations with /db-migration
9. Create analytics dashboards

---

## Quick Reference: Commands to Use

| Task | Command |
|------|----------------|
| Generate migration | /db-migration |
| Create pull request | /create-pull-request |
| Update context docs | Direct file editing |
| Update architecture docs | /architecture-tracker |
| Generate testing plan | Direct test writing |
| Create analytics dashboards | Direct implementation |
