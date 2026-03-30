---
name: playwright-tests
description: Playwright E2E testing rules including self-contained tests and element selection
user-invocable: false
---

# Playwright E2E Testing Rules

## Test File Structure
- Place tests in `e2e/` directory with `*.spec.ts` naming pattern
- Use `@playwright/test` framework
- Group related tests using `test.describe()` blocks
- Use `test.beforeEach()` for common setup (e.g., navigation, login)

## Self-Contained Tests (CRITICAL)
- **Every test file MUST include a login step** — never assume an active session exists
- **Every test file MUST seed its own data** — never depend on pre-existing data in the database
  - Use API calls, UI flows, or direct DB setup to create the data each test needs
  - Tests should be runnable on a fresh database with only the test admin user
- **Tests MUST clean up after themselves** when they create data that could interfere with other tests
- The login step goes in `test.beforeEach()` so every test starts authenticated
- Data seeding can happen in `test.beforeEach()` or at the start of individual tests depending on scope

### Login + Seed Pattern
```typescript
test.beforeEach(async ({ page }) => {
  // 1. Always login first
  await page.goto("/login");
  await page.fill('[data-testid="email"]', "admin@test.local");
  await page.fill('[data-testid="password"]', "TestAdmin123!");
  await page.click('[data-testid="login-button"]');
  await page.waitForURL("/dashboard");

  // 2. Seed data required by the tests (example: create a research)
  // Use UI flows or API calls to ensure required data exists
});
```

## Element Selection (CRITICAL)
- **ALWAYS prefer locating elements by id or data-testid attributes to avoid duplication errors**
  - Use `getByTestId()` for elements with `data-testid` attributes
  - Use `locator('#element-id')` for elements with `id` attributes
  - Avoid `getByLabel()` and `getByText()` as labels and text can be duplicated
  - Only use semantic selectors (e.g., `getByRole`) when ids are not available

## Test Quality
- Write comprehensive tests that verify:
  - UI components render correctly
  - User interactions work as expected
  - Form submissions and validations
  - Navigation and routing behavior
  - Error states and edge cases
- Use descriptive test names that clearly indicate what is being tested
- Use `expect()` assertions to verify expected behavior

## Test Credentials
- Test admin user: `admin@test.local` / `TestAdmin123!` (role: admin)
- These are for **local development only**
- Better Auth requires users to be created through the API (not direct DB insert)
- Database name: `version-two-db`

## Login Flow in Tests
See the "Self-Contained Tests" section above for the required login + seed pattern.

## Data-TestId Convention
```tsx
<Button data-testid="submit-form">Submit</Button>
<Input data-testid="search-input" />
<TableRow data-testid={`row-${item.id}`}>
<Dialog data-testid="confirm-modal">
<form data-testid="edit-profile-form">
```

## Test Categories
1. **Smoke Tests** - Critical paths that must always work
2. **Feature Tests** - Complete feature workflows
3. **Regression Tests** - Previously broken scenarios
4. **Edge Case Tests** - Boundary conditions and unusual inputs

## Running Tests
- `bunx playwright test` - Run all e2e tests
- `bunx playwright test e2e/some-test.spec.ts` - Run a single test file
