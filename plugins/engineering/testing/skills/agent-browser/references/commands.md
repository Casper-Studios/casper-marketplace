# Agent Browser Command Reference

Complete reference for all agent-browser CLI commands.

## Navigation Commands

### open
Navigate to a URL.

```bash
agent-browser open <url> [options]

# Examples
agent-browser open https://example.com
agent-browser open https://example.com --timeout 30000
agent-browser open https://example.com --wait-until networkidle

# Options
--timeout <ms>       Maximum wait time (default: 30000)
--wait-until <event> When to consider navigation done:
                     - load (default)
                     - domcontentloaded
                     - networkidle
```

### back / forward
Navigate browser history.

```bash
agent-browser back
agent-browser forward
```

### refresh
Reload the current page.

```bash
agent-browser refresh
agent-browser refresh --hard  # Clear cache
```

### goto
Alias for open.

```bash
agent-browser goto https://example.com
```

## Snapshot Commands

### snapshot
Capture page content as text with optional interactive element refs.

```bash
agent-browser snapshot [options]

# Examples
agent-browser snapshot              # Text only
agent-browser snapshot -i           # With interactive refs
agent-browser snapshot --full       # Include hidden elements
agent-browser snapshot --format json

# Options
-i, --interactive    Include refs for interactive elements
--full               Include all elements (not just visible)
--format <type>      Output format: text (default), json, markdown
--selector <css>     Snapshot specific element only
```

**Output with `-i` flag:**
```
Page: Example Form

@e1: [input type="text"] placeholder="Full Name"
@e2: [input type="email"] placeholder="Email Address"
@e3: [select] Country dropdown
@e4: [checkbox] "I agree to terms"
@e5: [button] "Submit"

Visible text:
Welcome to our registration form...
```

### screenshot
Capture visual screenshot.

```bash
agent-browser screenshot [path] [options]

# Examples
agent-browser screenshot                          # Auto-named
agent-browser screenshot ./screenshots/login.png
agent-browser screenshot --full-page
agent-browser screenshot --element @e1

# Options
--full-page         Capture entire scrollable page
--element <ref>     Capture specific element only
--quality <1-100>   JPEG quality (default: 80)
--type <format>     png (default), jpeg, webp
```

## Interaction Commands

### click
Click an element.

```bash
agent-browser click <ref|selector> [options]

# Examples
agent-browser click @e1
agent-browser click @e1 --double
agent-browser click @e1 --right
agent-browser click @e1 --force

# Options
--double         Double click
--right          Right click
--force          Click even if element is covered
--position x,y   Click at specific position within element
--delay <ms>     Delay between mousedown and mouseup
```

### fill
Fill a text input field.

```bash
agent-browser fill <ref|selector> <value> [options]

# Examples
agent-browser fill @e1 "John Doe"
agent-browser fill @e2 "user@example.com"
agent-browser fill @e3 "password123" --mask

# Options
--clear          Clear field before filling (default: true)
--no-clear       Append to existing value
--mask           Hide value in output (for passwords)
--delay <ms>     Delay between keystrokes
```

### type
Type text character by character (slower than fill, but more realistic).

```bash
agent-browser type <ref|selector> <text> [options]

# Examples
agent-browser type @e1 "Hello World"
agent-browser type @e1 "Test" --delay 100

# Options
--delay <ms>     Delay between keystrokes (default: 50)
```

### select
Select option in a dropdown.

```bash
agent-browser select <ref|selector> <value|label|index>

# Examples
agent-browser select @e1 "United States"     # By visible text
agent-browser select @e1 value:us            # By value attribute
agent-browser select @e1 index:3             # By index (0-based)
```

### check / uncheck
Toggle checkbox or radio button.

```bash
agent-browser check @e1
agent-browser uncheck @e1
```

### hover
Hover over an element.

```bash
agent-browser hover <ref|selector>

# Examples
agent-browser hover @e1
agent-browser hover @e1 --position 10,10
```

### press
Press keyboard key(s).

```bash
agent-browser press <key>

# Examples
agent-browser press Enter
agent-browser press Tab
agent-browser press Escape
agent-browser press Control+a
agent-browser press Shift+Tab
agent-browser press Meta+v        # Cmd+v on Mac

# Common keys:
# Enter, Tab, Escape, Backspace, Delete
# ArrowUp, ArrowDown, ArrowLeft, ArrowRight
# Home, End, PageUp, PageDown
# F1-F12
```

### scroll
Scroll the page or element.

```bash
agent-browser scroll [options]

# Examples
agent-browser scroll down
agent-browser scroll up
agent-browser scroll --to @e1        # Scroll element into view
agent-browser scroll --by 0,500      # Scroll by pixels (x,y)
agent-browser scroll --to-bottom     # Scroll to page bottom

# Options
--to <ref>       Scroll element into view
--by <x>,<y>     Scroll by pixel amount
--to-top         Scroll to top
--to-bottom      Scroll to bottom
```

### focus
Focus an element.

```bash
agent-browser focus <ref|selector>
```

### clear
Clear an input field.

```bash
agent-browser clear <ref|selector>
```

## Semantic Locators

Find elements by semantic attributes rather than refs.

### find role
Find by ARIA role.

```bash
agent-browser find role <role> [name]

# Examples
agent-browser find role button
agent-browser find role button "Submit"
agent-browser find role textbox "Email"
agent-browser find role link "Sign up"
agent-browser find role checkbox "Remember me"

# Common roles:
# button, link, textbox, checkbox, radio
# combobox, listbox, option, menu, menuitem
# tab, tabpanel, dialog, alert, navigation
```

### find text
Find by visible text content.

```bash
agent-browser find text <text> [options]

# Examples
agent-browser find text "Welcome"
agent-browser find text "Sign In" --exact
agent-browser find text "price" --case-insensitive

# Options
--exact              Exact match (not substring)
--case-insensitive   Ignore case
```

### find label
Find input by associated label.

```bash
agent-browser find label <label-text>

# Examples
agent-browser find label "Email Address"
agent-browser find label "Password"
```

### find placeholder
Find input by placeholder text.

```bash
agent-browser find placeholder <text>

# Examples
agent-browser find placeholder "Enter your email"
```

### find title
Find by title attribute.

```bash
agent-browser find title <text>
```

### find alt
Find image by alt text.

```bash
agent-browser find alt "Company Logo"
```

## Information Retrieval

### get
Get element properties or page info.

```bash
agent-browser get <property> [ref]

# Examples
agent-browser get url                  # Current page URL
agent-browser get title                # Page title
agent-browser get text @e1             # Element text content
agent-browser get value @e1            # Input value
agent-browser get html @e1             # Element HTML
agent-browser get attribute @e1 href   # Specific attribute
agent-browser get visible @e1          # Boolean visibility
agent-browser get enabled @e1          # Boolean enabled state
agent-browser get checked @e1          # Checkbox/radio state
agent-browser get count @e1            # Number of matching elements
```

### eval
Execute JavaScript and get result.

```bash
agent-browser eval <javascript>

# Examples
agent-browser eval "document.title"
agent-browser eval "window.location.href"
agent-browser eval "document.querySelectorAll('a').length"
```

## Wait Commands

### wait visible
Wait for element to become visible.

```bash
agent-browser wait visible <ref|selector> [options]

# Examples
agent-browser wait visible @e1
agent-browser wait visible @e1 --timeout 10000

# Options
--timeout <ms>    Maximum wait time (default: 30000)
```

### wait hidden
Wait for element to be hidden or removed.

```bash
agent-browser wait hidden <ref|selector> [options]
```

### wait enabled
Wait for element to become enabled.

```bash
agent-browser wait enabled <ref|selector>
```

### wait text
Wait for specific text to appear.

```bash
agent-browser wait text <text> [options]

# Examples
agent-browser wait text "Success"
agent-browser wait text "Loading" --hidden  # Wait for text to disappear
```

### wait network
Wait for network to be idle.

```bash
agent-browser wait network [options]

# Options
--idle-time <ms>     Consider idle after this duration (default: 500)
--max-inflight <n>   Max concurrent requests to consider idle (default: 0)
```

### wait time
Wait for specified duration.

```bash
agent-browser wait time <milliseconds>

# Examples
agent-browser wait time 1000   # Wait 1 second
agent-browser wait time 5000   # Wait 5 seconds
```

### wait url
Wait for URL to match pattern.

```bash
agent-browser wait url <pattern>

# Examples
agent-browser wait url "*/dashboard*"
agent-browser wait url "https://example.com/success"
```

### wait load
Wait for page load event.

```bash
agent-browser wait load
```

## Session Management

### session save
Save browser state (cookies, localStorage, sessionStorage).

```bash
agent-browser session save <name>

# Examples
agent-browser session save myapp-logged-in
agent-browser session save test-state
```

### session load
Load previously saved browser state.

```bash
agent-browser session load <name>

# Examples
agent-browser session load myapp-logged-in
```

### session list
List saved sessions.

```bash
agent-browser session list
```

### session delete
Delete a saved session.

```bash
agent-browser session delete <name>
```

### close
Close the browser.

```bash
agent-browser close
```

## Browser Management

### launch
Explicitly launch browser with options.

```bash
agent-browser launch [options]

# Options
--headless           Run without visible window (default: false)
--devtools           Open developer tools
--slow-mo <ms>       Slow down operations
--viewport <w>x<h>   Set viewport size (e.g., 1920x1080)
--user-agent <ua>    Custom user agent
--locale <locale>    Browser locale (e.g., en-US)
--timezone <tz>      Timezone (e.g., America/New_York)
--geolocation <loc>  Geolocation (lat,long)
--profile <name>     Use named profile directory
```

### context
Manage browser contexts (isolated sessions).

```bash
agent-browser context new          # Create new context
agent-browser context switch <id>  # Switch to context
agent-browser context list         # List contexts
agent-browser context close <id>   # Close context
```

## Output Formats

### JSON Mode
Get structured output for programmatic use.

```bash
agent-browser snapshot --format json
agent-browser get url --json
agent-browser find role button --json
```

**Example JSON snapshot output:**
```json
{
  "url": "https://example.com/form",
  "title": "Registration Form",
  "elements": [
    {
      "ref": "@e1",
      "tag": "input",
      "type": "text",
      "placeholder": "Full Name",
      "visible": true,
      "enabled": true
    },
    {
      "ref": "@e2",
      "tag": "button",
      "text": "Submit",
      "visible": true,
      "enabled": true
    }
  ]
}
```

## Debugging

### debug
Enable debug mode with verbose output.

```bash
agent-browser --debug open https://example.com
```

### trace
Record a trace file for debugging.

```bash
agent-browser open https://example.com --trace
# Creates trace.zip that can be viewed at trace.playwright.dev
```

## Environment Variables

```bash
# Set default timeout
AGENT_BROWSER_TIMEOUT=60000

# Run headless by default
AGENT_BROWSER_HEADLESS=true

# Set default viewport
AGENT_BROWSER_VIEWPORT=1920x1080

# Debug output
AGENT_BROWSER_DEBUG=true
```
