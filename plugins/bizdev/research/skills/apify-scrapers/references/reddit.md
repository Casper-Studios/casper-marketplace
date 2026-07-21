# Reddit Scraping

## Actor
`trudax/reddit-scraper`

## Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `subreddits` | string | AI subs | Comma-separated subreddits |
| `search_terms` | string | - | Keywords to filter |
| `max_posts` | int | 50 | Posts per subreddit |
| `max_comments` | int | 20 | Comments per post |
| `sort` | string | "hot" | hot, top, new, relevance |
| `time` | string | "day" | hour, day, week, month, year |

## CLI Usage

```bash
# Default AI subreddits
python scripts/scrape_reddit_ai_tech.py

# Specific subreddits
python scripts/scrape_reddit_ai_tech.py --subreddits "MachineLearning,LocalLLaMA,ClaudeAI"

# With time filter
python scripts/scrape_reddit_ai_tech.py --time week --sort top
```

## Output Structure

```json
{
  "posts": [
    {
      "id": "post_id",
      "title": "post title",
      "subreddit": "MachineLearning",
      "author": "username",
      "score": 1234,
      "num_comments": 56,
      "url": "post_url",
      "created_utc": "timestamp",
      "selftext": "post content",
      "top_comments": []
    }
  ],
  "scraped_at": "timestamp",
  "total_count": 0
}
```

## Best Subreddits for AI/Tech
- r/artificial - AI news
- r/MachineLearning - ML research
- r/LocalLLaMA - Local AI models
- r/ChatGPT, r/OpenAI, r/ClaudeAI - Specific tools
- r/technology, r/Futurology - General tech

## Cost
~$0.001-0.005 per post

## Testing Checklist

### Pre-flight
- [ ] `APIFY_API_TOKEN` set in `.env`
- [ ] Dependencies installed (`pip install apify-client python-dotenv`)
- [ ] Network connectivity to `api.apify.com`

### Smoke Test
```bash
# Quick test with default AI subreddits (minimal posts)
python scripts/scrape_reddit_ai_tech.py --max-posts 5

# Test specific subreddit
python scripts/scrape_reddit_ai_tech.py --subreddits "MachineLearning" --max-posts 5 --sort hot
```

### Validation
- [ ] Response contains `posts` array with expected fields (`id`, `title`, `subreddit`, `score`)
- [ ] `scraped_at` timestamp is present and valid
- [ ] `total_count` matches actual posts returned
- [ ] Posts are from correct subreddit(s)
- [ ] Sort order matches requested (`hot`, `top`, `new`)
- [ ] Time filter applied correctly (`day`, `week`, etc.)
- [ ] `top_comments` included when requested
- [ ] Cost estimate: ~$0.005-0.025 for 5 posts

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid or expired Apify API token | Verify `APIFY_API_TOKEN` in .env, regenerate token |
| `402 Payment Required` | Insufficient Apify credits | Add credits to Apify account |
| `Actor timeout` | Too many posts/comments requested | Reduce `max_posts` and `max_comments` |
| `Subreddit not found` | Invalid subreddit name or private | Verify subreddit exists and is public |
| `403 Forbidden` | Subreddit is private or quarantined | Choose alternative subreddit |
| `Rate limited` | Too many requests to Reddit | Wait 60 seconds, reduce request frequency |
| `Empty results` | Subreddit has no matching content | Check time filter, try `all` instead of `day` |

### Recovery Strategies

1. **Automatic retry**: Implement exponential backoff (30s, 60s, 120s) for rate limits
2. **Graceful degradation**: If a subreddit fails, continue with remaining subreddits
3. **Fallback subreddits**: Maintain list of alternative subs for each topic
4. **Batch processing**: Split large requests into smaller chunks (10 posts at a time)

## Performance Tips

### Batch Processing
- Combine multiple URLs in single actor run
- Use `maxItems` to limit results when testing
- Process results as they stream (if supported)

### Rate Limit Handling
- Implement exponential backoff between requests
- Use proxies to distribute load
- Respect platform rate limits (Twitter: 300/15min)

### Cost Optimization
- Start with `maxItems: 10` for testing
- Use date filters to reduce volume
- Cache results locally to avoid re-scraping

### Memory Usage
- Process large result sets in chunks
- Stream to file instead of memory for >1000 items
