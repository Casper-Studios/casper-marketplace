# Categorize Slack Messages

## Overview
Use AI to categorize and extract insights from Slack message history.

## Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `channel` | string | required | Channel name or ID |
| `days` | int | 7 | Days of history |
| `categories` | list | auto | Custom categories |
| `extract` | list | ["decisions", "action_items"] | What to extract |

## CLI Usage

```bash
# Auto-categorize messages
python scripts/categorize_slack_messages.py "internal-client" --days 14

# Custom categories
python scripts/categorize_slack_messages.py "project-alpha" \
  --categories "bugs,features,questions,updates"

# Extract specific items
python scripts/categorize_slack_messages.py "internal-client" \
  --extract "decisions" "action_items" "mentions"
```

## Output Structure

```json
{
  "channel": "internal-client",
  "period": "2025-12-11 to 2025-12-25",
  "message_count": 47,
  "categories": {
    "decisions": [
      {
        "message": "Decided to use React for the frontend",
        "timestamp": "2025-12-20T14:30:00",
        "user": "John Smith",
        "confidence": 0.95
      }
    ],
    "action_items": [
      {
        "message": "Need to follow up with client on requirements",
        "timestamp": "2025-12-22T09:15:00",
        "user": "Jane Doe",
        "assigned_to": "Giorgio"
      }
    ],
    "questions": [...],
    "updates": [...]
  },
  "user_activity": {
    "Giorgio": {"messages": 15, "reactions": 8},
    "John": {"messages": 12, "reactions": 5}
  },
  "top_reactions": [
    {"emoji": "thumbsup", "count": 23},
    {"emoji": "eyes", "count": 12}
  ]
}
```

## Extraction Keywords

### Decisions
- "decided", "agreed", "confirmed", "approved", "will go with"

### Action Items
- "todo", "need to", "follow up", "action item", "will do"

### Questions
- "?", "how do we", "what is", "can we", "should we"

## AI Model Used
Uses OpenRouter for categorization (Claude or GPT-4).

## Testing Checklist

### Pre-flight
- [ ] `SLACK_BOT_TOKEN` set in `.env` (format: `xoxb-...`)
- [ ] `OPENROUTER_API_KEY` set in `.env` (for AI categorization)
- [ ] Bot has required scopes: `channels:read`, `channels:history`
- [ ] Bot is invited to test channel
- [ ] Dependencies installed (`pip install slack-sdk openai python-dotenv`)

### Smoke Test
```bash
# Auto-categorize a channel with messages
python scripts/categorize_slack_messages.py "general" --days 7

# Test with custom categories
python scripts/categorize_slack_messages.py "general" --days 3 \
  --categories "questions,updates,announcements"

# Test specific extractions
python scripts/categorize_slack_messages.py "general" --days 3 \
  --extract "decisions" "action_items"
```

### Validation
- [ ] Response contains `channel`, `period`, `message_count` fields
- [ ] `categories` object includes requested categories
- [ ] Each categorized item has `message`, `timestamp`, `user`, `confidence`
- [ ] `confidence` scores are between 0 and 1
- [ ] `user_activity` shows message and reaction counts per user
- [ ] `top_reactions` lists emojis with counts (sorted)
- [ ] Decisions contain keywords like "decided", "agreed", "confirmed"
- [ ] Action items contain keywords like "todo", "need to", "follow up"
- [ ] Custom categories override default categories
- [ ] AI model handles empty channels gracefully

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `missing_scope` | Bot lacks Slack permissions | Add `channels:read`, `channels:history` scopes |
| `not_in_channel` | Bot not invited to channel | `/invite @BotName` in channel |
| `channel_not_found` | Invalid channel name/ID | Verify channel exists |
| `invalid_auth` | Slack token expired | Regenerate `SLACK_BOT_TOKEN` |
| `ratelimited` | Too many Slack API requests | Wait `retry_after` seconds |
| `OpenRouter API error` | AI model unavailable | Check `OPENROUTER_API_KEY`, try different model |
| `Context too long` | Too many messages for AI | Reduce `--days` or increase chunk size |
| `Invalid categories` | Unrecognized category names | Use supported categories or define custom ones |

### Recovery Strategies

1. **Automatic retry**: Implement exponential backoff for both Slack and OpenRouter rate limits
2. **Graceful degradation**: If AI fails, return raw message data without categorization
3. **Chunked processing**: Split large message sets into smaller batches for AI processing
4. **Confidence thresholds**: Filter out low-confidence categorizations (< 0.7)
5. **Fallback model**: If primary AI model fails, try secondary model (e.g., GPT-4 -> Claude)
6. **Caching**: Cache categorization results to avoid reprocessing same messages
