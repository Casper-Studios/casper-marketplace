---
name: test-credentials
description: Test credentials and setup instructions for local browser testing
user-invocable: false
---

# Test Credentials for Browser Testing

When testing authenticated pages locally, use these credentials:

## Test Admin User
| Field    | Value              |
|----------|-------------------|
| Email    | `admin@test.local` |
| Password | `TestAdmin123!`    |
| Role     | `admin`            |

## Setup (First Time or After DB Reset)

The test admin must be created through the sign-up flow, then upgraded:

### Option 1: Automated via Playwright
1. Navigate to http://localhost:5173/sign-up
2. Fill form with Name: "Test Admin", Email: "admin@test.local", Password: "TestAdmin123!", Confirm Password: "TestAdmin123!"
3. Click Sign up
4. Run SQL to upgrade: `UPDATE user SET role = 'admin', email_verified = 1 WHERE email = 'admin@test.local';`

### Option 2: Manual SQL After Sign-Up
```bash
bunx wrangler d1 execute version-two-db --local --command "UPDATE user SET role = 'admin', email_verified = 1 WHERE email = 'admin@test.local';"
```

## Login Flow for Testing
1. Navigate to `http://localhost:5173/login`
2. Enter email: `admin@test.local`
3. Enter password: `TestAdmin123!`
4. Click Login
5. Verify redirect to dashboard

## Cleanup (If User Already Exists)
```bash
bunx wrangler d1 execute version-two-db --local --command "DELETE FROM account WHERE user_id IN (SELECT id FROM user WHERE email = 'admin@test.local'); DELETE FROM session WHERE user_id IN (SELECT id FROM user WHERE email = 'admin@test.local'); DELETE FROM user WHERE email = 'admin@test.local';"
```

## Important Notes
- These credentials are for **local development only**
- Better Auth requires users to be created through the API (not direct DB insert)
- The user has `role: admin` so all admin pages are accessible
- Database name: `version-two-db` (check wrangler.jsonc if different)
