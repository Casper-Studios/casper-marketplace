---
description: Audits the codebase for DRY violations and enforces folder structure conventions
argument-hint: [target area or "full" for complete audit]
allowed-tools: Read, Glob, Grep, Bash, Edit, Write
---

# DRY Audit & Folder Structure Enforcer

Audits the codebase for DRY violations and enforces folder structure conventions. Identifies duplicated schemas, repeated UI patterns, redundant repository logic, and inconsistent organization.

Audit target: $ARGUMENTS

## When to Run

- Before creating new schemas, components, repositories, or workflows
- After implementing a new feature (to catch newly introduced duplication)
- When the user asks to clean up, refactor, or audit code quality

## Audit Workflow

```
Task Progress:
- [ ] Step 1: Check folder structure compliance
- [ ] Step 2: Scan schemas for shared field opportunities
- [ ] Step 3: Scan UI components for repeated patterns
- [ ] Step 4: Scan repositories for CRUD duplication
- [ ] Step 5: Scan workflows for shared logic
- [ ] Step 6: Report findings and suggest extractions
```

---

## Step 1: Folder Structure Conventions

Verify new files follow these conventions. If a file is in the wrong place, flag it.

### Required structure

```
app/
  models/              # Zod schemas grouped by domain
    research/          #   domain subfolder
      schema.ts        #   main schemas
      common.ts        #   shared base schemas (extract here)
  repositories/        # One file per entity, pure DB functions
  trpc/routes/         # One router per domain
  routes/platform/
    components/
      <feature>/       # Feature-specific components
        common/        #   Shared UI within the feature
        results/       #   Result display components
        empty-state/   #   Empty state components
      shared/          # Cross-feature shared components
  lib/
    constants/         # Or constants.ts — centralized config values
    prompts/           # AI prompts grouped by domain subfolder
    utils.ts           # Generic pure helpers
  components/          # Global reusable UI (shadcn + custom)
workflows/             # One WorkflowEntrypoint per file
```

### Naming conventions

| Layer | Pattern | Example |
|-------|---------|---------|
| Repository functions | `getById`, `list`, `create`, `update`, `delete` | `getResearchById(db, { id })` |
| tRPC routes | domain-named router | `research.ts` exports `researchRouter` |
| Schemas | `PascalCaseSchema` | `ExecutiveSummarySchema` |
| Components | PascalCase file + export | `StatusBadge.tsx` |
| Workflows | `kebab-case.ts`, class `PascalCaseWorkflow` | `discovery-agent-gemini.ts` / `DiscoveryAgentGeminiWorkflow` |
| Prompts | `<domain>/` subfolder with descriptive files | `prompts/discovery-agent/system.ts` |

---

## Step 2: Schema DRY Checks

Search `app/models/` for these known shared patterns. If a new schema duplicates any of them, extract to `app/models/research/common.ts` (or the appropriate domain common file).

### Patterns to extract

**Base workflow payload** — shared across discovery-agent, internal-discovery, product-discovery:
```typescript
// app/models/research/common.ts
export const BaseWorkflowPayloadSchema = z.object({
  researchId: z.string(),
  productName: z.string(),
  description: z.string(),
  targetMarket: z.string().optional(),
  website: z.string().optional(),
  clientVision: z.string().optional(),
  transcript: z.string().optional(),
  documents: z.array(z.string()).optional(),
});
```

**Base executive summary** — shared `context`, `keyFindings`, `topOpportunities`, `recommendedFocus`:
```typescript
export const BaseExecutiveSummarySchema = z.object({
  context: z.string(),
  keyFindings: z.array(z.string()),
  topOpportunities: z.array(z.string()),
  recommendedFocus: z.string(),
});
```

**Base risk schema** — shared `assumptions`, `deliveryRisks`, `adoptionRisks` with `severity` enum:
```typescript
const SeverityEnum = z.enum(["low", "medium", "high", "critical"]);

export const BaseRiskItemSchema = z.object({
  risk: z.string(),
  severity: SeverityEnum,
  mitigation: z.string(),
});

export const BaseRisksSchema = z.object({
  assumptions: z.array(z.string()),
  deliveryRisks: z.array(BaseRiskItemSchema),
  adoptionRisks: z.array(BaseRiskItemSchema),
});
```

**Base opportunity map** — shared `keyOpportunities`, `prioritizationFramework`, `quickWins`, `bigBets`:
```typescript
export const BaseOpportunityMapSchema = z.object({
  keyOpportunities: z.array(z.object({
    title: z.string(),
    description: z.string(),
    impact: z.enum(["low", "medium", "high"]),
    effort: z.enum(["low", "medium", "high"]),
  })),
  quickWins: z.array(z.string()),
  bigBets: z.array(z.string()),
});
```

**How to check**: Search for `z.object` definitions containing `keyFindings`, `deliveryRisks`, `quickWins`, or `severity` across `app/models/`. If found in more than one file, extract to common.

**How to extend**: Use `.extend()` or `.merge()`:
```typescript
const DiscoveryExecutiveSummarySchema = BaseExecutiveSummarySchema.extend({
  strategicImplications: z.array(z.string()),
});
```

---

## Step 3: UI Component DRY Checks

Search `app/routes/` and `app/components/` for these repeated patterns. If found duplicated, extract or reuse.

### Loading spinner
**Search**: `animate-spin` + `IconLoader2` or `Loader2`
**Reuse**: Should be a single `<LoadingSpinner />` in `app/components/shared/` or `app/components/ui/`
```typescript
// Expected: import { LoadingSpinner } from "@/components/ui/loading-spinner"
<LoadingSpinner size="md" className="text-muted-foreground" />
```

### Error/failed state
**Search**: `IconAlertTriangle` + `"failed"` or `"error"` in JSX
**Reuse**: Should be a single `<ErrorState />` component
```typescript
<ErrorState
  title="Analysis Failed"
  message={errorMessage}
  onRetry={handleRetry}
/>
```

### Empty state
**Search**: Components named `*empty-state*` or containing "No items" / "Get started" patterns
**Reuse**: Consider a base `<EmptyState />` with variants

### Status badges
**Search**: Status config objects mapping status strings to `{ label, color, icon }`
**Reuse**: Single `<StatusBadge status={status} variant="research" />` component

### Source citations
**Search**: Tooltip-wrapped citation badges with `[n]` patterns
**Reuse**: Already exists at `market-research/common/source-citations.tsx` — use it, don't duplicate

---

## Step 4: Repository DRY Checks

Search `app/repositories/` for these patterns.

### Pagination
**Search**: `Math.ceil` + `offset` + `totalPages` pattern
**Reuse**: Extract to `app/lib/repository-utils.ts`:
```typescript
export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export function buildPaginatedResult<T>(
  items: T[],
  total: number,
  page: number,
  limit: number
): PaginatedResult<T> {
  return { items, total, page, limit, totalPages: Math.ceil(total / limit) };
}
```

### Organization access check
**Search**: `organizationId !== ` comparison patterns
**Reuse**: Extract to a shared helper:
```typescript
export function verifyOrgAccess(resourceOrgId: string, userOrgId: string): void {
  if (resourceOrgId !== userOrgId) {
    throw new ForbiddenError("Access denied");
  }
}
```

### AI service availability check
**Search**: `throw new TRPCError` + `"AI service not configured"`
**Reuse**: Extract to `app/lib/ai-utils.ts`:
```typescript
export function requireAIService<T>(service: T | null, name: string): asserts service is T {
  if (!service) {
    throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: `${name} not configured` });
  }
}
```

### JSON parsing from AI responses
**Search**: Regex extracting JSON from markdown code blocks (triple backtick patterns)
**Reuse**: Single `parseAIJsonResponse()` utility

---

## Step 5: Workflow DRY Checks

Search `workflows/` for these patterns.

### Step name constants
**Search**: `STEP_NAMES` or similar step-number-to-name maps
**Reuse**: If step names overlap between workflows, extract shared ones

### Progress update wrapper
**Search**: `updateResearchProgress` calls inside `step.do()`
**Reuse**: Wrapper function:
```typescript
export async function trackedStep<T>(
  step: WorkflowStep,
  db: Database,
  researchId: string,
  stepNumber: number,
  stepName: string,
  totalSteps: number,
  fn: () => Promise<T>
): Promise<T>
```

### Source index mapping
**Search**: Functions transforming `sourceIndices: number[]` to `sources: SourceReference[]`
**Reuse**: Single utility in `app/lib/source-utils.ts`

---

## Step 6: Report Format

After auditing, output findings in this format:

```markdown
## DRY Audit Results

### Folder Structure
- [PASS/FAIL] New files follow conventions
- [WARN] <file> should be in <expected location>

### Schema Duplication
- [DRY] <field pattern> duplicated in <file1>, <file2>
  → Extract to: <target file> using <BaseSchema>.extend()

### UI Duplication
- [DRY] Loading spinner reimplemented in <file>
  → Reuse: <shared component path>

### Repository Duplication
- [DRY] Pagination logic duplicated in <file1>, <file2>
  → Extract to: app/lib/repository-utils.ts

### Workflow Duplication
- [DRY] <pattern> duplicated in <file1>, <file2>
  → Extract to: <target utility>

### Summary
- X folder structure issues
- X schema duplications
- X UI duplications
- X repository duplications
- X workflow duplications
```

---

## Quick Reference: Where Shared Code Lives

| What | Where |
|------|-------|
| Base Zod schemas | `app/models/<domain>/common.ts` |
| Global UI components | `app/components/ui/` |
| Feature-shared UI | `app/routes/platform/components/shared/` |
| Generic utilities | `app/lib/utils.ts` |
| Repository utilities | `app/lib/repository-utils.ts` |
| AI utilities | `app/lib/ai-utils.ts` |
| Source/citation utils | `app/lib/source-utils.ts` |
| Constants | `app/lib/constants.ts` or `app/lib/constants/` |
| Prompts | `app/lib/prompts/<domain>/` |
