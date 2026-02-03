# Fetch Slack News

## Overview
Fetch and summarize news/updates from Slack channels, typically from news-focused channels.

## Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `channel` | string | required | Channel name or ID |
| `days` | int | 7 | Days of history |
| `categorize` | bool | false | AI categorization |

## CLI Usage

```bash
# Fetch news from channel
python scripts/fetch_slack_news.py "news-ai-updates" --days 7

# With AI categorization
python scripts/fetch_slack_news.py "news-ai-updates" --categorize
```

## Output Structure

```json
{
  "channel": "news-ai-updates",
  "period": "last 7 days",
  "messages": [
    {
      "timestamp": "2025-12-25T10:30:00",
      "user": "NewsBot",
      "text": "OpenAI announces new model...",
      "links": ["https://openai.com/..."],
      "reactions": {"fire": 5, "eyes": 3}
    }
  ],
  "summary": {
    "top_stories": [...],
    "categories": {
      "ai_news": [...],
      "product_updates": [...]
    }
  }
}
```

## Common News Channels

- `#news-ai-updates` - AI industry news
- `#news-tech` - General tech news
- `#competitor-intel` - Competitor updates

## Testing Checklist

### Pre-flight
- [ ] `SLACK_BOT_TOKEN` set in `.env` (format: `xoxb-...`)
- [ ] Bot has required scopes: `channels:read`, `channels:history`
- [ ] Bot is invited to test news channel
- [ ] `OPENROUTER_API_KEY` set (if using `--categorize`)
- [ ] Dependencies installed (`pip install slack-sdk python-dotenv`)

### Smoke Test
```bash
# Fetch news from a known channel (basic)
python scripts/fetch_slack_news.py "general" --days 1

# Test with AI categorization (requires OpenRouter)
python scripts/fetch_slack_news.py "general" --days 1 --categorize
```

### Validation
- [ ] Response contains `channel`, `period`, `messages` fields
- [ ] Messages include `timestamp`, `user`, `text`, `links`
- [ ] Links are extracted from message text
- [ ] Reactions are counted correctly
- [ ] `--categorize` produces `summary.categories` object
- [ ] Date range filter works (`--days` parameter)
- [ ] No errors when channel has few/no messages

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `missing_scope` | Bot lacks permissions | Add `channels:read`, `channels:history` scopes |
| `not_in_channel` | Bot not invited to channel | `/invite @BotName` in channel |
| `channel_not_found` | Invalid channel name/ID | Verify channel exists and name is correct |
| `invalid_auth` | Token expired or revoked | Regenerate `SLACK_BOT_TOKEN` |
| `ratelimited` | Too many API requests | Wait `retry_after` seconds, reduce request frequency |
| `OpenRouter API error` | AI categorization failed | Check `OPENROUTER_API_KEY`, retry without `--categorize` |
| `Empty channel` | No messages in date range | Extend `--days` parameter or check channel activity |

### Recovery Strategies

1. **Automatic retry**: Implement exponential backoff (1s, 2s, 4s) for rate limits
2. **Graceful degradation**: If AI categorization fails, return raw messages without categories
3. **Link extraction fallback**: If link unfurling fails, return raw URLs
4. **Batch processing**: For large channels, process in chunks to avoid timeouts
5. **Caching**: Cache channel metadata to reduce redundant API calls
