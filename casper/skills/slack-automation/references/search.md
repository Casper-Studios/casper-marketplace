# Slack Search & Channel Reader

## Operations

### Search Channels
Find channels by name pattern.

### Read Messages
Fetch message history from a channel.

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Channel name to search for |
| `channel_id` | string | No | Direct channel ID (skips search) |
| `days_back` | int | No | Days of history (default: 7) |
| `limit` | int | No | Max messages (default: 50) |
| `include_threads` | bool | No | Include thread replies (default: true) |
| `user_name` | string | No | User name to highlight mentions |

## CLI Usage

```bash
# Search for channels
python scripts/slack_search.py search "internal" --limit 10

# Read channel by name
python scripts/slack_search.py read "internal-microsoft" --days 7

# Read channel by ID
python scripts/slack_search.py read-id "C08D326B98T" --days 14

# Get summary with user mentions
python scripts/slack_search.py summary "internal-client" --days 7 --user "Giorgio"
```

## Output Structure

### Channel Search
```json
{
  "id": "C08D326B98T",
  "name": "internal-client",
  "is_private": false,
  "num_members": 23,
  "purpose": "Internal discussions for Client"
}
```

### Message Read
```json
{
  "channel_id": "C08D326B98T",
  "channel_name": "internal-client",
  "message_count": 15,
  "messages": [
    {
      "timestamp": "1735123456.000100",
      "datetime": "2025-12-25T10:30:00",
      "user": "John Smith",
      "text": "Message content here",
      "reactions": [{"name": "thumbsup", "count": 2}],
      "thread_replies": []
    }
  ]
}
```

### Key Info Extraction
```json
{
  "top_discussions": [...],
  "decisions": [...],
  "action_items": [...],
  "user_mentions": [...]
}
```

## API Methods

- `conversations.list` - List/search channels
- `conversations.history` - Read channel messages
- `conversations.replies` - Get thread replies
- `users.info` - Resolve user IDs to names

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `missing_scope` | Bot lacks permissions | Add scope in Slack app settings |
| `not_in_channel` | Bot not invited | `/invite @BotName` in channel |
| `channel_not_found` | Invalid channel name/ID | Verify channel exists |
| `invalid_auth` | Token expired or revoked | Regenerate token in Slack app settings |
| `token_revoked` | Bot was removed from workspace | Reinstall app to workspace |
| `ratelimited` | Too many API requests | Wait indicated retry_after seconds |
| `account_inactive` | Workspace was deactivated | Contact workspace admin |
| `user_not_found` | Invalid user ID in mentions | Skip unknown users, log for review |

### Recovery Strategies

1. **Automatic retry**: Implement exponential backoff (1s, 2s, 4s) for rate limits
2. **Graceful degradation**: If thread replies fail, return messages without threads
3. **User resolution cache**: Cache user ID to name mappings to reduce API calls
4. **Pagination handling**: Use cursor-based pagination for channels with many messages
5. **Alerting**: Log `invalid_auth` errors for immediate attention - token refresh needed

## Testing Checklist

### Pre-flight
- [ ] `SLACK_BOT_TOKEN` set in `.env` (format: `xoxb-...`)
- [ ] Bot has required scopes: `channels:read`, `channels:history`, `users:read`
- [ ] Bot is invited to test channel (`/invite @BotName`)
- [ ] Dependencies installed (`pip install slack-sdk python-dotenv`)

### Smoke Test
```bash
# Test channel search
python scripts/slack_search.py search "general" --limit 5

# Test reading messages from a known channel
python scripts/slack_search.py read "general" --days 1 --limit 10

# Test reading by channel ID
python scripts/slack_search.py read-id "C01234ABCDE" --days 1

# Test summary with user mentions
python scripts/slack_search.py summary "general" --days 1 --user "YourName"
```

### Validation
- [ ] Channel search returns valid channel IDs and names
- [ ] `num_members` count is accurate
- [ ] Messages include `timestamp`, `user`, `text` fields
- [ ] User IDs resolved to human-readable names
- [ ] Thread replies included when `include_threads` is true
- [ ] Date range filter works (`--days` parameter)
- [ ] `--limit` parameter caps message count
- [ ] No `missing_scope` errors (bot has correct permissions)
- [ ] No `not_in_channel` errors (bot is invited)
