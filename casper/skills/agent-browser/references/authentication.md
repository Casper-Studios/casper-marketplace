# Authentication Patterns

Patterns for handling login flows, session persistence, and authenticated testing.

## Basic Login Flow

### Standard Username/Password Login

```bash
# 1. Navigate to login page
agent-browser open https://app.example.com/login

# 2. Get form element refs
agent-browser snapshot -i

# 3. Fill credentials
agent-browser fill @e1 "user@example.com"    # Email/username field
agent-browser fill @e2 "password123" --mask  # Password field (masked)

# 4. Submit form
agent-browser click @e3                       # Submit button

# 5. Wait for redirect/dashboard
agent-browser wait url "*/dashboard*"
agent-browser wait network

# 6. Verify login success
agent-browser snapshot -i
```

### Using Semantic Locators

```bash
# More reliable than refs for login forms
agent-browser open https://app.example.com/login

agent-browser fill "$(agent-browser find label 'Email')" "user@example.com"
agent-browser fill "$(agent-browser find label 'Password')" "password123" --mask
agent-browser click "$(agent-browser find role button 'Sign In')"

agent-browser wait network
```

## Session Persistence

### Save Session After Login

```bash
# Login once
agent-browser open https://app.example.com/login
agent-browser snapshot -i
agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password123" --mask
agent-browser click @e3
agent-browser wait url "*/dashboard*"

# Save the authenticated session
agent-browser session save app-logged-in

# Close browser
agent-browser close
```

### Load Session for Future Tests

```bash
# Start new session from saved state
agent-browser session load app-logged-in

# Go directly to authenticated pages
agent-browser open https://app.example.com/dashboard
agent-browser snapshot -i
# No login required!
```

### Session Workflow for Test Suites

```bash
#!/bin/bash

# Check if session exists and is valid
agent-browser session load app-session 2>/dev/null

if agent-browser get url | grep -q "login"; then
    echo "Session expired, re-authenticating..."

    # Perform fresh login
    agent-browser fill @email "$APP_EMAIL"
    agent-browser fill @password "$APP_PASSWORD" --mask
    agent-browser click @submit
    agent-browser wait url "*/dashboard*"

    # Save new session
    agent-browser session save app-session
fi

# Continue with tests...
```

## Profile-Based Sessions

### Create Persistent Profile

Profiles maintain cookies, localStorage, and credentials across browser restarts.

```bash
# Launch with named profile (creates persistent directory)
agent-browser launch --profile myapp-testing

# Login and setup
agent-browser open https://app.example.com/login
agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password123" --mask
agent-browser click @e3
agent-browser wait network

# Close - profile is saved automatically
agent-browser close

# Next time, just launch with same profile
agent-browser launch --profile myapp-testing
agent-browser open https://app.example.com/dashboard
# Already logged in!
```

### Multiple Profiles for Different Accounts

```bash
# Admin account
agent-browser launch --profile app-admin
# ... login as admin ...
agent-browser close

# Regular user account
agent-browser launch --profile app-user
# ... login as user ...
agent-browser close

# Switch between them as needed
agent-browser launch --profile app-admin
agent-browser open https://app.example.com/admin
```

## OAuth/SSO Flows

### Google OAuth Example

```bash
# Navigate to app login
agent-browser open https://app.example.com/login

# Click Google sign-in button
agent-browser snapshot -i
agent-browser click @e1  # "Sign in with Google" button

# Wait for Google OAuth page
agent-browser wait url "*accounts.google.com*"
agent-browser snapshot -i

# Enter Google credentials
agent-browser fill @e1 "user@gmail.com"
agent-browser click @e2  # Next button
agent-browser wait visible @e3  # Password field

agent-browser fill @e3 "google-password" --mask
agent-browser click @e4  # Next button

# Wait for redirect back to app
agent-browser wait url "*app.example.com*"
agent-browser wait network

# Save authenticated session
agent-browser session save app-google-auth
```

### Handling OAuth Popups

```bash
# If OAuth opens in popup window
agent-browser open https://app.example.com/login
agent-browser click @e1  # Opens OAuth popup

# Switch to popup context
agent-browser context list
agent-browser context switch popup-1

# Complete OAuth in popup
agent-browser snapshot -i
agent-browser fill @e1 "user@example.com"
agent-browser click @e2

# Popup closes, switch back to main window
agent-browser context switch main
agent-browser wait url "*/dashboard*"
```

## Two-Factor Authentication (2FA)

### TOTP Code Entry

```bash
# After entering username/password
agent-browser wait visible @e1  # 2FA code input

# Get TOTP code (you'd generate this externally)
TOTP_CODE=$(your-totp-generator)

agent-browser fill @e1 "$TOTP_CODE"
agent-browser click @e2  # Verify button

agent-browser wait url "*/dashboard*"
```

### SMS Code Waiting

```bash
# Wait for SMS input to appear
agent-browser wait visible @sms-code-input

echo "Enter SMS code when received:"
read SMS_CODE

agent-browser fill @e1 "$SMS_CODE"
agent-browser click @e2
```

## Security Best Practices

### Never Commit Credentials

```bash
# Use environment variables
agent-browser fill @email "$APP_TEST_EMAIL"
agent-browser fill @password "$APP_TEST_PASSWORD" --mask
```

### Gitignore Session Files

Add to `.gitignore`:
```gitignore
# Agent browser state files
*.state
.agent-browser/
agent-browser-profile/

# Named profiles
*-profile/

# Screenshots with potentially sensitive data
screenshots/*.png
```

### Mask Sensitive Input

```bash
# Always use --mask for passwords
agent-browser fill @password "secret" --mask
# Output shows: fill @password "****"
```

### Rotate Test Credentials

```bash
# Use dedicated test accounts, not personal accounts
# Rotate passwords regularly
# Use minimal permissions for test accounts
```

### Clean Up Sessions

```bash
# After tests, clean up saved sessions
agent-browser session delete app-session
agent-browser session delete temp-auth

# Or clear all
agent-browser session list | xargs -I {} agent-browser session delete {}
```

## Testing Authentication Flows

### Test Login Success

```bash
#!/bin/bash
agent-browser open https://app.example.com/login
agent-browser snapshot -i

agent-browser fill @email "valid@example.com"
agent-browser fill @password "correct-password" --mask
agent-browser click @submit

agent-browser wait network
URL=$(agent-browser get url)

if [[ "$URL" == *"dashboard"* ]]; then
    echo "PASS: Login successful"
else
    echo "FAIL: Not redirected to dashboard"
    exit 1
fi
```

### Test Login Failure

```bash
#!/bin/bash
agent-browser open https://app.example.com/login
agent-browser snapshot -i

agent-browser fill @email "invalid@example.com"
agent-browser fill @password "wrong-password" --mask
agent-browser click @submit

agent-browser wait network

# Check for error message
ERROR=$(agent-browser find text "Invalid credentials" 2>/dev/null)

if [[ -n "$ERROR" ]]; then
    echo "PASS: Error message displayed"
else
    echo "FAIL: No error message"
    exit 1
fi
```

### Test Session Expiry

```bash
#!/bin/bash
# Load old session
agent-browser session load old-session

# Navigate to authenticated page
agent-browser open https://app.example.com/dashboard

# Check if redirected to login
URL=$(agent-browser get url)

if [[ "$URL" == *"login"* ]]; then
    echo "Session expired correctly"
else
    echo "WARNING: Old session still valid"
fi
```

## Environment Setup for CI/CD

### GitHub Actions Example

```yaml
- name: Setup agent-browser
  run: |
    npm install -g agent-browser
    agent-browser install

- name: Run authenticated tests
  env:
    APP_EMAIL: ${{ secrets.TEST_APP_EMAIL }}
    APP_PASSWORD: ${{ secrets.TEST_APP_PASSWORD }}
  run: |
    agent-browser open https://app.example.com/login
    agent-browser fill @email "$APP_EMAIL"
    agent-browser fill @password "$APP_PASSWORD" --mask
    agent-browser click @submit
    agent-browser wait url "*/dashboard*"

    # Run tests...
```

### Pre-authenticated State in CI

```yaml
# Decrypt and use pre-saved session state
- name: Restore auth session
  run: |
    gpg --decrypt .github/test-session.gpg > /tmp/test.state
    agent-browser session load /tmp/test.state
    rm /tmp/test.state
```
