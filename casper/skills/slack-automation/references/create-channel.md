# Create Slack Channel

## Overview
Create new Slack channels for projects, clients, or teams.

## Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | required | Channel name (lowercase, hyphens) |
| `private` | bool | false | Create private channel |
| `description` | string | "" | Channel purpose |
| `invite` | list | [] | Users to invite |

## CLI Usage

```bash
# Create public channel
python scripts/create_slack_channel.py "project-alpha"

# Create private channel
python scripts/create_slack_channel.py "internal-acme" --private

# With description and invites
python scripts/create_slack_channel.py "client-microsoft" \
  --description "Microsoft project discussions" \
  --invite "U123ABC" "U456DEF"
```

## Naming Conventions

| Pattern | Purpose |
|---------|---------|
| `internal-{client}` | Client-specific channels |
| `project-{name}` | Project channels |
| `team-{name}` | Team channels |
| `temp-{topic}` | Temporary channels |

## Output Structure

```json
{
  "success": true,
  "channel": {
    "id": "C08D326B98T",
    "name": "internal-acme",
    "is_private": true,
    "url": "https://workspace.slack.com/archives/C08D326B98T"
  }
}
```

## Required Scopes

- `channels:manage` - Create public channels
- `groups:write` - Create private channels

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `name_taken` | Channel already exists | Use different name or find existing channel |
| `invalid_name` | Invalid characters | Use lowercase, hyphens, underscores only |
| `missing_scope` | Insufficient permissions | Add `channels:manage` (public) or `groups:write` (private) |
| `invalid_auth` | Token expired or revoked | Regenerate `SLACK_BOT_TOKEN` |
| `user_not_found` | Invalid user ID in invite list | Verify user IDs before inviting |
| `restricted_action` | Workspace policy blocks action | Contact workspace admin for permissions |
| `name_too_long` | Channel name exceeds 80 chars | Shorten channel name |
| `no_permission` | Bot cannot create channels | Verify bot has admin/channel creation rights |

### Recovery Strategies

1. **Name collision handling**: If `name_taken`, append timestamp or find and return existing channel
2. **Validation first**: Validate channel name format before API call to avoid `invalid_name`
3. **User verification**: Verify user IDs exist before adding to invite list
4. **Fallback to public**: If private channel creation fails due to permissions, offer public alternative
5. **Idempotent operations**: Check if channel exists before creating to support retry logic

## Testing Checklist

### Pre-flight
- [ ] `SLACK_BOT_TOKEN` set in `.env` (format: `xoxb-...`)
- [ ] Bot has required scopes: `channels:manage`, `groups:write` (for private)
- [ ] Dependencies installed (`pip install slack-sdk python-dotenv`)
- [ ] Test channel name is unique (not already taken)

### Smoke Test
```bash
# Create a test public channel (use unique name)
python scripts/create_slack_channel.py "test-channel-$(date +%s)"

# Create a test private channel
python scripts/create_slack_channel.py "test-private-$(date +%s)" --private

# Create with description
python scripts/create_slack_channel.py "test-with-desc-$(date +%s)" \
  --description "Test channel for automation"
```

### Validation
- [ ] Response contains `success: true`
- [ ] `channel.id` is a valid Slack channel ID (format: `C...`)
- [ ] `channel.name` matches requested name (lowercased)
- [ ] `channel.is_private` matches `--private` flag
- [ ] `channel.url` is a valid Slack URL
- [ ] Channel appears in Slack workspace
- [ ] `--invite` successfully adds users (if specified)
- [ ] `name_taken` error returned for duplicate names
- [ ] `invalid_name` error for names with invalid characters

### Cleanup
```bash
# Archive test channels after testing (manual in Slack)
# Or use: python scripts/archive_slack_channel.py "test-channel-name"
```
