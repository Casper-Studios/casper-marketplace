# Testing Patterns

Common patterns for end-to-end testing, form validation, and multi-page workflows.

## Form Testing Workflow

### Complete Form Test

```bash
#!/bin/bash
set -e

echo "=== Form Submission Test ==="

# Navigate to form
agent-browser open https://app.example.com/contact
agent-browser wait network
agent-browser snapshot -i

# Fill all fields
agent-browser fill @e1 "John Doe"                    # Name
agent-browser fill @e2 "john@example.com"            # Email
agent-browser fill @e3 "555-123-4567"                # Phone
agent-browser select @e4 "Sales Inquiry"             # Subject dropdown
agent-browser fill @e5 "I'd like to learn more..."   # Message

# Check required checkbox
agent-browser check @e6                              # Terms agreement

# Take pre-submission screenshot
agent-browser screenshot pre-submit.png

# Submit form
agent-browser click @e7
agent-browser wait network

# Verify success
agent-browser snapshot -i
SUCCESS_TEXT=$(agent-browser find text "Thank you" 2>/dev/null || echo "")

if [[ -n "$SUCCESS_TEXT" ]]; then
    echo "PASS: Form submitted successfully"
    agent-browser screenshot success.png
else
    echo "FAIL: Success message not found"
    agent-browser screenshot failure.png
    exit 1
fi
```

### Form Validation Testing

```bash
#!/bin/bash

echo "=== Testing Form Validation ==="

agent-browser open https://app.example.com/register
agent-browser snapshot -i

# Test: Empty required field
echo "Test: Empty email validation"
agent-browser fill @name "John Doe"
agent-browser click @submit
agent-browser wait time 500

ERROR=$(agent-browser find text "Email is required" 2>/dev/null || echo "")
if [[ -n "$ERROR" ]]; then
    echo "  PASS: Email required error shown"
else
    echo "  FAIL: No validation error"
fi

# Test: Invalid email format
echo "Test: Invalid email format"
agent-browser fill @email "not-an-email"
agent-browser click @submit
agent-browser wait time 500

ERROR=$(agent-browser find text "valid email" 2>/dev/null || echo "")
if [[ -n "$ERROR" ]]; then
    echo "  PASS: Invalid email error shown"
else
    echo "  FAIL: No format validation"
fi

# Test: Password mismatch
echo "Test: Password mismatch"
agent-browser fill @email "john@example.com"
agent-browser fill @password "Password123"
agent-browser fill @confirm "DifferentPass"
agent-browser click @submit
agent-browser wait time 500

ERROR=$(agent-browser find text "Passwords must match" 2>/dev/null || echo "")
if [[ -n "$ERROR" ]]; then
    echo "  PASS: Password mismatch error shown"
else
    echo "  FAIL: No mismatch validation"
fi
```

## E2E Test Workflow

### User Journey Test

```bash
#!/bin/bash
set -e

echo "=== E2E User Journey: Signup to Purchase ==="

# Step 1: Visit homepage
echo "Step 1: Homepage"
agent-browser open https://shop.example.com
agent-browser wait network
agent-browser screenshot 01-homepage.png

# Step 2: Navigate to signup
echo "Step 2: Signup"
agent-browser snapshot -i
agent-browser click "$(agent-browser find text 'Sign Up')"
agent-browser wait network

agent-browser snapshot -i
agent-browser fill @email "test-$RANDOM@example.com"
agent-browser fill @password "TestPass123!" --mask
agent-browser fill @confirm "TestPass123!" --mask
agent-browser click @submit
agent-browser wait url "*/welcome*"
agent-browser screenshot 02-signup-complete.png

# Step 3: Browse products
echo "Step 3: Browse Products"
agent-browser open https://shop.example.com/products
agent-browser wait network
agent-browser snapshot -i
agent-browser screenshot 03-products.png

# Step 4: Add to cart
echo "Step 4: Add to Cart"
agent-browser click @e1  # First product
agent-browser wait network
agent-browser snapshot -i
agent-browser click "$(agent-browser find role button 'Add to Cart')"
agent-browser wait visible "$(agent-browser find text 'Added')"
agent-browser screenshot 04-added-to-cart.png

# Step 5: Checkout
echo "Step 5: Checkout"
agent-browser click "$(agent-browser find text 'Cart')"
agent-browser wait network
agent-browser snapshot -i
agent-browser click "$(agent-browser find role button 'Checkout')"
agent-browser wait network

# Fill checkout form
agent-browser snapshot -i
agent-browser fill @address "123 Test St"
agent-browser fill @city "Test City"
agent-browser fill @zip "12345"
agent-browser select @country "United States"
agent-browser screenshot 05-checkout.png

# Step 6: Complete order
echo "Step 6: Complete Order"
agent-browser click @submit
agent-browser wait url "*/confirmation*"
agent-browser snapshot -i
agent-browser screenshot 06-confirmation.png

ORDER_ID=$(agent-browser get text @order-id)
echo "Order ID: $ORDER_ID"
echo "=== Test Complete ==="
```

## Multi-Page Navigation

### Tab/Window Management

```bash
# Open link in new tab
agent-browser click @link --new-tab
agent-browser context list
agent-browser context switch tab-1

# Do something in new tab
agent-browser snapshot -i
agent-browser screenshot new-tab.png

# Switch back to original
agent-browser context switch main
```

### Iframe Handling

```bash
# List frames on page
agent-browser snapshot -i

# If element is in iframe, use frame selector
agent-browser click "iframe#payment >> @e1"

# Or switch to frame context
agent-browser frame switch payment-iframe
agent-browser snapshot -i
agent-browser fill @card "4111111111111111"
agent-browser frame switch main
```

### Pagination Testing

```bash
#!/bin/bash

echo "Testing pagination..."

agent-browser open https://app.example.com/users
agent-browser wait network

PAGE=1
while true; do
    echo "Page $PAGE"
    agent-browser snapshot -i
    agent-browser screenshot "page-$PAGE.png"

    ITEM_COUNT=$(agent-browser get count ".user-row")
    echo "  Items: $ITEM_COUNT"

    # Try to go to next page
    NEXT_BUTTON=$(agent-browser find role button "Next" 2>/dev/null || echo "")
    if [[ -z "$NEXT_BUTTON" ]]; then
        echo "No more pages"
        break
    fi

    agent-browser click "$NEXT_BUTTON"
    agent-browser wait network
    PAGE=$((PAGE + 1))

    # Safety limit
    if [[ $PAGE -gt 10 ]]; then
        echo "Reached page limit"
        break
    fi
done

echo "Total pages: $PAGE"
```

## Screenshot Comparison

### Visual Regression Testing

```bash
#!/bin/bash

BASELINE_DIR="./baseline"
CURRENT_DIR="./current"
DIFF_DIR="./diff"

mkdir -p "$CURRENT_DIR" "$DIFF_DIR"

# Capture current state
agent-browser open https://app.example.com
agent-browser screenshot "$CURRENT_DIR/homepage.png"

agent-browser open https://app.example.com/login
agent-browser screenshot "$CURRENT_DIR/login.png"

agent-browser open https://app.example.com/dashboard
agent-browser screenshot "$CURRENT_DIR/dashboard.png"

# Compare with baseline (using ImageMagick)
for file in "$CURRENT_DIR"/*.png; do
    name=$(basename "$file")
    baseline="$BASELINE_DIR/$name"

    if [[ -f "$baseline" ]]; then
        # Compare images, output diff
        compare -metric RMSE "$baseline" "$file" "$DIFF_DIR/$name" 2>&1 | {
            read diff_value
            if (( $(echo "$diff_value > 0.01" | bc -l) )); then
                echo "DIFF: $name - $diff_value"
            else
                echo "OK: $name"
            fi
        }
    else
        echo "NEW: $name (no baseline)"
        cp "$file" "$baseline"
    fi
done
```

### Responsive Testing

```bash
#!/bin/bash

VIEWPORTS=(
    "375x667:mobile"
    "768x1024:tablet"
    "1920x1080:desktop"
)

URL="https://app.example.com"

for viewport in "${VIEWPORTS[@]}"; do
    IFS=':' read -r size name <<< "$viewport"
    echo "Testing $name ($size)"

    agent-browser launch --viewport "$size"
    agent-browser open "$URL"
    agent-browser wait network
    agent-browser screenshot "responsive-$name.png"
    agent-browser close
done
```

## Error Handling Patterns

### Retry on Failure

```bash
#!/bin/bash

retry_command() {
    local max_attempts=$1
    shift
    local cmd="$@"

    for ((i=1; i<=max_attempts; i++)); do
        if eval "$cmd"; then
            return 0
        fi
        echo "Attempt $i failed, retrying..."
        sleep 2
    done
    return 1
}

# Usage
retry_command 3 agent-browser click @submit
retry_command 3 agent-browser wait visible @success-message
```

### Graceful Error Recovery

```bash
#!/bin/bash

test_with_recovery() {
    # Try the happy path
    agent-browser click @submit
    agent-browser wait network

    # Check for error modal
    ERROR_MODAL=$(agent-browser find role dialog 2>/dev/null || echo "")
    if [[ -n "$ERROR_MODAL" ]]; then
        echo "Error modal detected, closing..."
        agent-browser click "$(agent-browser find role button 'Close')"
        agent-browser wait hidden "$ERROR_MODAL"
        return 1
    fi

    # Check for error message
    ERROR_MSG=$(agent-browser find text "error" 2>/dev/null || echo "")
    if [[ -n "$ERROR_MSG" ]]; then
        echo "Error message: $(agent-browser get text "$ERROR_MSG")"
        agent-browser screenshot error-state.png
        return 1
    fi

    return 0
}
```

### Timeout Handling

```bash
#!/bin/bash

# Set aggressive timeout for flaky elements
agent-browser wait visible @slow-loading --timeout 60000 || {
    echo "Element did not appear in time"
    agent-browser screenshot timeout-state.png

    # Try refresh
    agent-browser refresh
    agent-browser wait visible @slow-loading --timeout 30000 || {
        echo "Failed after refresh"
        exit 1
    }
}
```

## Data-Driven Testing

### CSV Test Data

```bash
#!/bin/bash

# test-data.csv:
# name,email,expected_result
# Valid User,valid@example.com,success
# Invalid Email,not-an-email,error

while IFS=',' read -r name email expected; do
    [[ "$name" == "name" ]] && continue  # Skip header

    echo "Testing: $name"

    agent-browser open https://app.example.com/form
    agent-browser fill @name "$name"
    agent-browser fill @email "$email"
    agent-browser click @submit
    agent-browser wait network

    if [[ "$expected" == "success" ]]; then
        if agent-browser find text "Thank you" >/dev/null 2>&1; then
            echo "  PASS"
        else
            echo "  FAIL: Expected success"
        fi
    else
        if agent-browser find text "error" >/dev/null 2>&1; then
            echo "  PASS"
        else
            echo "  FAIL: Expected error"
        fi
    fi
done < test-data.csv
```

### JSON Test Scenarios

```bash
#!/bin/bash

# test-scenarios.json:
# [{"action": "fill", "ref": "@email", "value": "test@example.com"}, ...]

SCENARIOS=$(cat test-scenarios.json)

echo "$SCENARIOS" | jq -c '.[]' | while read -r step; do
    action=$(echo "$step" | jq -r '.action')
    ref=$(echo "$step" | jq -r '.ref')
    value=$(echo "$step" | jq -r '.value // empty')

    case "$action" in
        fill)
            agent-browser fill "$ref" "$value"
            ;;
        click)
            agent-browser click "$ref"
            ;;
        wait)
            agent-browser wait visible "$ref"
            ;;
        snapshot)
            agent-browser snapshot -i
            ;;
    esac
done
```

## Accessibility Testing

### Check for ARIA Labels

```bash
#!/bin/bash

agent-browser open https://app.example.com
agent-browser snapshot --format json > snapshot.json

# Check all interactive elements have accessible names
jq -r '.elements[] | select(.tag == "button" or .tag == "input" or .tag == "a") |
    if .ariaLabel or .text or .placeholder then empty else .ref end' snapshot.json | {
    while read -r ref; do
        [[ -n "$ref" ]] && echo "WARNING: $ref missing accessible name"
    done
}
```

### Keyboard Navigation Test

```bash
#!/bin/bash

agent-browser open https://app.example.com
agent-browser snapshot -i

# Tab through all interactive elements
for i in {1..20}; do
    agent-browser press Tab

    # Get focused element
    FOCUSED=$(agent-browser eval "document.activeElement.tagName")
    echo "Tab $i: $FOCUSED"

    # Check for skip link
    if [[ "$FOCUSED" == "A" ]]; then
        TEXT=$(agent-browser eval "document.activeElement.innerText")
        if [[ "$TEXT" == *"Skip"* ]]; then
            echo "  Found skip link: $TEXT"
        fi
    fi
done
```

## Performance Testing

### Page Load Timing

```bash
#!/bin/bash

agent-browser open https://app.example.com

# Get performance metrics
TIMING=$(agent-browser eval "JSON.stringify(window.performance.timing)")

# Parse timing
DOM_READY=$(echo "$TIMING" | jq '.domContentLoadedEventEnd - .navigationStart')
FULL_LOAD=$(echo "$TIMING" | jq '.loadEventEnd - .navigationStart')

echo "DOM Ready: ${DOM_READY}ms"
echo "Full Load: ${FULL_LOAD}ms"

if (( FULL_LOAD > 3000 )); then
    echo "WARNING: Page load exceeds 3s threshold"
fi
```

### Resource Counting

```bash
#!/bin/bash

agent-browser open https://app.example.com

# Count resources
RESOURCES=$(agent-browser eval "performance.getEntriesByType('resource').length")
IMAGES=$(agent-browser eval "document.images.length")
SCRIPTS=$(agent-browser eval "document.scripts.length")

echo "Total resources: $RESOURCES"
echo "Images: $IMAGES"
echo "Scripts: $SCRIPTS"
```
