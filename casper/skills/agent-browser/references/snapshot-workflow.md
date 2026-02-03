# Snapshot Workflow

Understanding the ref system, when refs invalidate, and efficient snapshot usage.

## How Refs Work

### What is a Ref?

A ref is a temporary identifier (like `@e1`, `@e2`, `@e3`) assigned to interactive elements on the page when you take a snapshot.

```bash
# Take a snapshot with refs
agent-browser snapshot -i

# Output:
# @e1: [input type="text"] placeholder="Username"
# @e2: [input type="password"] placeholder="Password"
# @e3: [button] "Sign In"
# @e4: [a] "Forgot password?"
# @e5: [a] "Create account"
```

### Ref Assignment

Refs are assigned in DOM order (top-to-bottom, left-to-right):
- `@e1` - First interactive element
- `@e2` - Second interactive element
- And so on...

**Interactive elements include:**
- Buttons (`<button>`, `<input type="submit">`)
- Input fields (`<input>`, `<textarea>`, `<select>`)
- Links (`<a>`)
- Clickable elements with handlers
- Elements with `tabindex`

### Using Refs

```bash
# Click by ref
agent-browser click @e3

# Fill by ref
agent-browser fill @e1 "username"

# Get text by ref
agent-browser get text @e4

# Check visibility by ref
agent-browser get visible @e5
```

## When Refs Invalidate

**Refs are invalidated whenever the DOM changes significantly.** You must re-snapshot to get new refs.

### Common Invalidation Scenarios

#### 1. Page Navigation
```bash
agent-browser snapshot -i    # Refs: @e1, @e2, @e3
agent-browser click @e3      # Navigate to new page
# REFS ARE NOW INVALID
agent-browser snapshot -i    # Get new refs: @e1, @e2, @e3...
```

#### 2. AJAX Content Loading
```bash
agent-browser snapshot -i    # @e1: Load More button
agent-browser click @e1      # Load more items via AJAX
agent-browser wait network   # Wait for content
# REFS ARE NOW INVALID - new elements added
agent-browser snapshot -i    # @e1 now points to different element
```

#### 3. Modal/Dialog Opening
```bash
agent-browser snapshot -i    # @e1: Open Modal button
agent-browser click @e1      # Open modal
# REFS PARTIALLY INVALID - modal adds new elements
agent-browser snapshot -i    # Re-snapshot to target modal elements
```

#### 4. Form State Changes
```bash
agent-browser snapshot -i
agent-browser fill @e1 "test"
# Refs usually still valid for simple fills

agent-browser select @e2 "Option A"
# If this triggers conditional fields to appear:
# REFS MAY BE INVALID
agent-browser snapshot -i
```

#### 5. Single Page App Navigation
```bash
agent-browser click @nav-link   # SPA route change
# DOM is replaced without full page load
# REFS ARE INVALID
agent-browser wait network
agent-browser snapshot -i
```

### Safe Operations (Refs Usually Remain Valid)

- `fill` - Typing into input
- `click` on non-navigating buttons
- `hover` - Mouse hover
- `focus` - Element focus
- `get` - Reading element properties
- `wait` - Waiting (doesn't change DOM)

### Risky Operations (Re-snapshot After)

- `click` on links/buttons (may navigate)
- `select` on dynamic dropdowns
- `submit` forms
- Any action that triggers AJAX
- Any navigation command

## Efficient Snapshot Usage

### Pattern: Snapshot Sparingly

```bash
# Bad: Excessive snapshots
agent-browser open https://example.com
agent-browser snapshot -i
agent-browser fill @e1 "John"
agent-browser snapshot -i      # Unnecessary
agent-browser fill @e2 "Doe"
agent-browser snapshot -i      # Unnecessary
agent-browser click @e3
agent-browser snapshot -i      # Necessary - after click

# Good: Strategic snapshots
agent-browser open https://example.com
agent-browser snapshot -i      # Initial refs
agent-browser fill @e1 "John"
agent-browser fill @e2 "Doe"
agent-browser click @e3
agent-browser wait network
agent-browser snapshot -i      # Only after navigation/change
```

### Pattern: Batch Similar Operations

```bash
# Get all refs at once
agent-browser snapshot -i

# Perform multiple operations without re-snapshotting
agent-browser fill @e1 "First Name"
agent-browser fill @e2 "Last Name"
agent-browser fill @e3 "email@example.com"
agent-browser fill @e4 "password" --mask
agent-browser check @e5
agent-browser click @e6

# Now re-snapshot after the action
agent-browser wait network
agent-browser snapshot -i
```

### Pattern: Conditional Snapshotting

```bash
#!/bin/bash

# Only snapshot if we need to interact
if need_to_interact; then
    agent-browser snapshot -i
    agent-browser click @e1
fi

# Only snapshot if page changed
OLD_URL=$(agent-browser get url)
agent-browser click @e1
NEW_URL=$(agent-browser get url)

if [[ "$OLD_URL" != "$NEW_URL" ]]; then
    agent-browser snapshot -i
fi
```

## Token Optimization

Snapshots consume tokens when used with AI. Optimize usage:

### Use Targeted Snapshots

```bash
# Full page snapshot (more tokens)
agent-browser snapshot -i

# Targeted element snapshot (fewer tokens)
agent-browser snapshot -i --selector "#login-form"
```

### Skip Interactive Mode When Not Needed

```bash
# Need to interact? Use -i
agent-browser snapshot -i

# Just reading content? Skip -i
agent-browser snapshot
```

### Use JSON for Processing

```bash
# Human-readable (larger)
agent-browser snapshot -i

# Structured, processable (can be smaller)
agent-browser snapshot -i --format json | jq '.elements | length'
```

### Limit Snapshot Depth

```bash
# Only visible elements (smaller)
agent-browser snapshot -i

# Include hidden elements (larger)
agent-browser snapshot -i --full
```

## Ref Strategies

### Strategy 1: Semantic Locators Instead of Refs

When refs are unstable, use semantic locators:

```bash
# Instead of:
agent-browser snapshot -i
agent-browser click @e3   # Which button is @e3?

# Use:
agent-browser click "$(agent-browser find role button 'Submit')"
```

### Strategy 2: Verify Refs Before Use

```bash
# Get ref text to verify it's correct element
agent-browser snapshot -i
SUBMIT_TEXT=$(agent-browser get text @e3)
if [[ "$SUBMIT_TEXT" == "Submit" ]]; then
    agent-browser click @e3
else
    echo "Wrong element at @e3: $SUBMIT_TEXT"
    exit 1
fi
```

### Strategy 3: Combined Approach

```bash
# Use ref for speed, semantic for verification
agent-browser snapshot -i

# Quick operations with refs
agent-browser fill @e1 "username"
agent-browser fill @e2 "password" --mask

# Use semantic for critical action
agent-browser click "$(agent-browser find role button 'Sign In')"
```

## Troubleshooting Ref Issues

### "Element not found" Error

```bash
# Re-snapshot and try again
agent-browser snapshot -i
agent-browser click @e1  # Try again with fresh refs

# If still failing, element may not be visible
agent-browser wait visible @e1
agent-browser click @e1
```

### Wrong Element Clicked

```bash
# Verify what element the ref points to
agent-browser snapshot -i
agent-browser get text @e1      # Check text
agent-browser get html @e1      # Check HTML
agent-browser screenshot check.png  # Visual verification

# Use semantic locator for precision
agent-browser click "$(agent-browser find text 'Exact Button Text')"
```

### Refs Changed After Action

```bash
# Always re-snapshot after DOM-modifying actions
agent-browser click @e1
agent-browser wait network
agent-browser wait time 500    # Allow for JS to settle
agent-browser snapshot -i      # Get fresh refs
```

### Dynamic Content Issues

```bash
# Wait for dynamic content to load
agent-browser wait visible @loading-indicator --timeout 5000
agent-browser wait hidden @loading-indicator

# Then snapshot
agent-browser snapshot -i
```

## Best Practices Summary

1. **Snapshot after navigation** - Always re-snapshot after clicking links or submitting forms

2. **Batch operations** - Perform multiple fills/checks before re-snapshotting

3. **Wait before snapshot** - Use `wait network` to ensure content is loaded

4. **Verify critical refs** - Check element text/properties before important actions

5. **Use semantic locators for stability** - `find role`, `find text` are more reliable than refs for critical actions

6. **Minimize snapshots** - Each snapshot consumes resources; use strategically

7. **Handle errors gracefully** - If ref fails, re-snapshot and retry

8. **Document ref assumptions** - Comment what element each ref represents in your scripts
