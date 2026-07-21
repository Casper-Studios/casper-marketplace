# URL Auto-Detection & Scraping

## Script
`scripts/scrape_content_by_url.py`

## Overview
Automatically detects URL type and uses the appropriate scraper.

## Supported URL Types

| Pattern | Type | Actor/API |
|---------|------|-----------|
| `twitter.com/*`, `x.com/*` | Twitter | Apify Twitter actor |
| `youtube.com/*`, `youtu.be/*` | YouTube | Apify YouTube actor |
| `reddit.com/*` | Reddit | Apify Reddit actor |
| Other URLs | Website | Firecrawl API |

## Usage

```bash
# Auto-detect and scrape
python scripts/scrape_content_by_url.py "https://x.com/user/status/123456"

# Force type
python scripts/scrape_content_by_url.py "https://example.com/article" --type website
```

## URL Type Detection Logic

```python
def detect_url_type(url):
    if "twitter.com" in url or "x.com" in url:
        return "twitter"
    elif "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    elif "reddit.com" in url:
        return "reddit"
    else:
        return "website"
```

## Output Structure

```json
{
  "url": "original_url",
  "type": "twitter|youtube|reddit|website",
  "scraped_at": "timestamp",
  "content": {
    // Type-specific content
  }
}
```

## Twitter Output Fields
- `text`, `author`, `likeCount`, `retweetCount`, `createdAt`

## YouTube Output Fields
- `title`, `description`, `channelName`, `viewCount`, `subtitles`

## Reddit Output Fields
- `title`, `body`, `author`, `score`, `comments`

## Website Output Fields (Firecrawl)
- `title`, `text` (markdown), `url`, `description`, `metadata`

## Cost Estimates
- Twitter: ~$0.00025 per tweet
- YouTube: ~$0.01-0.05 per video
- Reddit: ~$0.001-0.005 per post
- Website: ~1 Firecrawl credit per page

## Testing Checklist

### Pre-flight
- [ ] `APIFY_API_TOKEN` set in `.env`
- [ ] `FIRECRAWL_API_KEY` set in `.env` (for website fallback)
- [ ] Dependencies installed (`pip install apify-client firecrawl-py python-dotenv`)
- [ ] Network connectivity to `api.apify.com` and `api.firecrawl.dev`

### Smoke Test
```bash
# Test Twitter/X URL detection
python scripts/scrape_content_by_url.py "https://x.com/OpenAI/status/1234567890"

# Test YouTube URL detection
python scripts/scrape_content_by_url.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Test Reddit URL detection
python scripts/scrape_content_by_url.py "https://www.reddit.com/r/MachineLearning/comments/abc123"

# Test generic website (Firecrawl fallback)
python scripts/scrape_content_by_url.py "https://example.com/article"

# Force website type
python scripts/scrape_content_by_url.py "https://x.com/somepage" --type website
```

### Validation
- [ ] Response contains `url` (original input), `type` (detected), `scraped_at`
- [ ] `type` correctly detected for each URL pattern:
  - `twitter.com/*` or `x.com/*` -> `twitter`
  - `youtube.com/*` or `youtu.be/*` -> `youtube`
  - `reddit.com/*` -> `reddit`
  - Other URLs -> `website`
- [ ] `content` object contains type-specific fields (see Output Fields)
- [ ] `--type` flag overrides auto-detection when specified
- [ ] No errors when URL is unreachable (graceful failure)
- [ ] Cost varies by detected type (see Cost Estimates above)

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid API key for detected platform | Check `APIFY_API_TOKEN` or `FIRECRAWL_API_KEY` in .env |
| `Invalid URL` | Malformed or unreachable URL | Verify URL format and accessibility |
| `Unknown URL type` | URL doesn't match any known pattern | Falls back to website scraper (Firecrawl) |
| `Content deleted` | Tweet/post/video was removed | Return error with deletion notice |
| `Private content` | Content requires authentication | Cannot scrape - inform user content is private |
| `Timeout` | Scraping took too long | Retry with longer timeout or simpler request |
| `Firecrawl credit exhausted` | No Firecrawl credits remaining | Add credits or use alternative scraper |

### Recovery Strategies

1. **Automatic retry**: 3 attempts with exponential backoff for transient failures
2. **Graceful degradation**: If specialized scraper fails, try generic website scraper
3. **URL validation**: Pre-validate URL accessibility before scraping
4. **Type override**: Allow `--type` flag to force specific scraper if auto-detection fails
5. **Caching**: Cache successful scrapes to avoid redundant requests for same URL

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
