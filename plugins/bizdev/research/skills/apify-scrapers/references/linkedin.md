# LinkedIn Scraping

## Actor
`harvestapi/linkedin-post-search`

## Modes

### Author Mode
Scrape posts from a specific LinkedIn profile.

### Search Mode
Scrape posts matching search keywords.

## Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | string | required | "author" or "search" |
| `author_urls` | list | - | LinkedIn profile URLs (author mode) |
| `search_queries` | list | - | Keywords (search mode) |
| `max_posts` | int | 30 | Max posts to retrieve |
| `scrape_comments` | bool | false | Include comments (costs more) |
| `scrape_reactions` | bool | false | Include reactions (costs more) |

## CLI Usage

```bash
# Scrape from author profile
python scripts/scrape_linkedin_posts.py author "https://linkedin.com/in/username"

# Multiple profiles
python scripts/scrape_linkedin_posts.py author "https://linkedin.com/in/user1" "https://linkedin.com/in/user2"

# Search by keyword
python scripts/scrape_linkedin_posts.py search "AI agents" "automation tools"

# With comments
python scripts/scrape_linkedin_posts.py author "https://linkedin.com/in/username" --scrape-comments
```

## Output Structure

```json
{
  "posts": [
    {
      "id": "post_id",
      "text": "post content",
      "author_name": "Full Name",
      "author_url": "profile_url",
      "posted_at": "timestamp",
      "likes": 0,
      "comments": 0,
      "reposts": 0,
      "post_url": "url_to_post",
      "media_urls": [],
      "hashtags": []
    }
  ],
  "scraped_at": "timestamp",
  "mode": "author|search",
  "query": "input used"
}
```

## Cost
Higher than other platforms. Disable comments/reactions unless needed.

## Testing Checklist

### Pre-flight
- [ ] `APIFY_API_TOKEN` set in `.env`
- [ ] Dependencies installed (`pip install apify-client python-dotenv`)
- [ ] Network connectivity to `api.apify.com`
- [ ] Test LinkedIn profile URL is valid and public

### Smoke Test
```bash
# Test author mode with a known public profile (minimal posts)
python scripts/scrape_linkedin_posts.py author "https://linkedin.com/in/satlovsolutions" --max-posts 5

# Test search mode with a simple keyword
python scripts/scrape_linkedin_posts.py search "AI agents" --max-posts 5
```

### Validation
- [ ] Response contains `posts` array with expected fields (`id`, `text`, `author_name`, `likes`)
- [ ] `scraped_at` timestamp is present and valid
- [ ] `mode` matches requested mode (`author` or `search`)
- [ ] `query` field contains the input used
- [ ] Post URLs are valid LinkedIn URLs
- [ ] Author URLs are valid LinkedIn profile URLs
- [ ] Comments included only when `--scrape-comments` flag used
- [ ] No error messages related to profile access
- [ ] Cost is higher than Twitter/Reddit - monitor usage

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid or expired Apify API token | Verify `APIFY_API_TOKEN` in .env, regenerate token |
| `402 Payment Required` | Insufficient Apify credits | Add credits to Apify account |
| `Actor timeout` | Scraping took too long | Reduce `max_posts`, disable comments/reactions |
| `Profile not found` | Invalid LinkedIn URL or profile removed | Verify URL format and profile existence |
| `403 Forbidden` | Profile is private or restricted | Cannot scrape private profiles - find alternative |
| `Blocked request` | LinkedIn detected scraping activity | Actor uses proxies but may need retry |
| `Rate limited` | Too many profile requests | Wait 5+ minutes between batches |
| `Empty results` | Profile has no public posts | Verify profile has content, check date range |

### Recovery Strategies

1. **Automatic retry**: Wait 2-5 minutes between retries for blocked requests
2. **Graceful degradation**: Disable `scrape_comments` and `scrape_reactions` to reduce detection risk
3. **Batch limits**: Process max 5 profiles per run to avoid rate limits
4. **Cost protection**: Set budget limits as LinkedIn scraping is expensive
5. **Alerting**: Log blocked URLs for manual verification

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
