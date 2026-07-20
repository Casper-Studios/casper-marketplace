---
name: testing-workflow
description: Testing workflow for generating testing plans, verification, and E2E tests
user-invocable: false
---

# Testing Workflow

After implementing a plan or feature, follow this workflow to generate a testing plan, verify with Playwright, fix issues, and write an e2e test.

## Step 1: Generate Testing Plan

Create a testing plan folder at:
```
docs/testing/{feature-name}/
  {feature-name}.md      # Testing plan document
  screenshots/           # Playwright screenshots
```

### Testing Plan Template
```markdown
# Testing Plan: {Feature Name}

## Overview
Brief description of what was implemented.

## Prerequisites
- [ ] Development server running
- [ ] Database seeded with test data
- [ ] Test user credentials available

## Test Scenarios
### Scenario 1: {Happy Path}
**Description:** ...
**Steps:** ...
**Expected Result:** ...
**Screenshot:** ![Description](./screenshots/scenario-1.png)

## UI Elements to Verify
## API/Data Verification
## Accessibility Checks
## Test IDs Reference
## E2E Test Coverage
Test file: `e2e/{feature-name}.spec.ts`
```

## Step 2: Manual Verification

Use Playwright to manually verify each scenario. Pattern:
1. Navigate to the page
2. Take snapshot to get element references
3. Interact with elements (click, type)
4. Snapshot to verify state changes
5. Take screenshot for documentation

## Step 3: Fix Issues Found

1. Document the issue in the testing plan
2. Fix the code following the repository pattern:
   - Repository layer for data issues
   - tRPC route for API issues
   - Component for UI issues
3. Re-verify the specific scenario

## Step 4: Write E2E Test

Create test file at `e2e/{feature-name}.spec.ts`:

```typescript
import { test, expect } from "@playwright/test";

test.describe("{Feature Name}", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/login");
    await page.fill('[data-testid="email"]', "admin@test.local");
    await page.fill('[data-testid="password"]', "TestAdmin123!");
    await page.click('[data-testid="login-button"]');
    await page.waitForURL("/dashboard");
  });

  test("should {happy path}", async ({ page }) => {
    await page.goto("/{feature-path}");
    await page.click('[data-testid="{element}"]');
    await expect(page.locator('[data-testid="{result}"]')).toBeVisible();
  });
});
```

### Data-TestId Convention
```tsx
<Button data-testid="submit-form">Submit</Button>
<Input data-testid="search-input" />
<TableRow data-testid={`row-${item.id}`}>
<Dialog data-testid="confirm-modal">
```

## Checklist Before Marking Complete
- [ ] Testing plan created at `docs/testing/{feature-name}/{feature-name}.md`
- [ ] Screenshots folder created
- [ ] All scenarios manually verified
- [ ] Screenshots taken and saved
- [ ] Issues found have been fixed
- [ ] E2E test file created in `e2e/`
- [ ] All e2e tests pass locally
- [ ] Data-testid attributes added to key elements

## Test Credentials
- Email: `admin@test.local`
- Password: `TestAdmin123!`
- Role: admin (local development only)
