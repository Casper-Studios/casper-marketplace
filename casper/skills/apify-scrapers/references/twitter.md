# Twitter/X Scraping

## Actor
`kaitoeasyapi/twitter-x-data-tweet-scraper-pay-per-result-cheapest`

## Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | Search term |
| `max_tweets` | int | 50 | Maximum tweets (25-100) |
| `engagement_threshold` | int | 0 | Min likes for filtering |
| `query_type` | string | "Latest" | "Latest" or "Top" |

## CLI Usage

```bash
# Basic search
python scripts/scrape_twitter_ai_trends.py --query "OpenAI"

# With engagement filter
python scripts/scrape_twitter_ai_trends.py --query "ChatGPT" --max-tweets 100 --min-likes 10
```

## Output Structure

```json
{
  "tweets": [
    {
      "id": "tweet_id",
      "text": "tweet content",
      "author": "username",
      "created_at": "timestamp",
      "likes": 0,
      "retweets": 0,
      "replies": 0,
      "url": "tweet_url"
    }
  ],
  "scraped_at": "timestamp",
  "total_count": 0
}
```

## Cost
~$0.00025 per tweet ($0.10-0.50 per 100 tweets)

## Notes
- Pay-per-result pricing
- Filters: Excludes retweets, excludes replies
- Sorted by engagement (likes + retweets) descending

## Testing Checklist

### Pre-flight
- [ ] `APIFY_API_TOKEN` set in `.env`
- [ ] Dependencies installed (`pip install apify-client python-dotenv`)
- [ ] Network connectivity to `api.apify.com`

### Smoke Test
```bash
# Quick test with a simple query (minimal results)
python scripts/scrape_twitter_ai_trends.py --query "test" --max-tweets 5

# Verify with a known popular term
python scripts/scrape_twitter_ai_trends.py --query "OpenAI" --max-tweets 10
```

### Validation
- [ ] Response contains `tweets` array with expected fields (`id`, `text`, `author`, `likes`)
- [ ] `scraped_at` timestamp is present and valid
- [ ] `total_count` matches actual tweets returned
- [ ] No error messages in output
- [ ] Tweets are sorted by engagement (descending)
- [ ] No retweets or replies in results (filter working)
- [ ] Cost estimate: ~$0.0025 for 10 tweets

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid or expired Apify API token | Verify `APIFY_API_TOKEN` in .env, regenerate token in Apify console |
| `402 Payment Required` | Insufficient Apify credits | Add credits to Apify account |
| `Actor timeout` | Search took too long (>300s default) | Reduce `max_tweets`, use simpler query |
| `Run failed` | Actor crashed or hit rate limit | Retry after 60 seconds, check Twitter's API status |
| `Proxy error` | IP blocked by Twitter | Actor handles automatically with proxy rotation |
| `No results found` | Query too specific or typo | Broaden search terms, verify spelling |
| `Invalid query` | Unsupported search operators | Use standard keywords, avoid advanced operators |

### Recovery Strategies

1. **Automatic retry**: Implement exponential backoff (30s, 60s, 120s) for transient failures
2. **Graceful degradation**: If actor fails, fall back to reduced `max_tweets` (25 instead of 100)
3. **Cost protection**: Set `maxCostPerRun` in actor options to prevent runaway costs
4. **Alerting**: Log failures with query details for investigation

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
