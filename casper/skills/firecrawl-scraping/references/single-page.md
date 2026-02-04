# Single Page Scraping

## API Endpoint
`POST https://api.firecrawl.dev/v2/scrape`

## Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | required | URL to scrape |
| `formats` | array | ["markdown"] | Output formats |
| `only_main_content` | bool | true | Extract only main content |
| `timeout` | int | 30000 | Timeout in ms |
| `wait_for` | int | 0 | Wait before scraping (JS load) |
| `mobile` | bool | false | Emulate mobile device |
| `proxy` | string | "auto" | "basic", "stealth", "auto" |
| `headers` | dict | {} | Custom HTTP headers |
| `actions` | array | [] | Browser actions |

## CLI Usage

```bash
# Basic scrape
python scripts/firecrawl_scrape.py "https://example.com"

# Premium content with stealth
python scripts/firecrawl_scrape.py "https://wsj.com/article" --proxy stealth

# Multiple formats
python scripts/firecrawl_scrape.py "https://example.com" --format markdown summary

# Wait for JS
python scripts/firecrawl_scrape.py "https://spa-site.com" --wait-for 3000
```

## Python SDK

```python
from firecrawl import Firecrawl

firecrawl = Firecrawl(api_key="fc-YOUR-API-KEY")

# Simple scrape
result = firecrawl.scrape("https://example.com", formats=["markdown"])

# With options
result = firecrawl.scrape(
    "https://wsj.com/article",
    formats=["markdown", "summary"],
    only_main_content=True,
    timeout=60000,
    proxy="stealth"
)
```

## Browser Actions

For dynamic content, login flows, or cookie banners:

```python
result = firecrawl.scrape(
    url="https://example.com",
    formats=["markdown"],
    actions=[
        {"type": "click", "selector": "#accept-cookies"},
        {"type": "wait", "milliseconds": 2000},
        {"type": "scroll", "direction": "down", "amount": 500},
        {"type": "screenshot", "fullPage": True}
    ]
)
```

## Output Structure

```json
{
  "success": true,
  "url": "https://example.com/article",
  "title": "Article Title",
  "markdown": "# Article Title\n\nClean markdown content...",
  "summary": "Brief summary of the page",
  "metadata": {
    "title": "Article Title",
    "description": "Meta description",
    "language": "en",
    "statusCode": 200
  },
  "links": ["https://example.com/link1"],
  "scraped_at": "2025-12-09T12:00:00Z"
}
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid or missing API key | Verify `FIRECRAWL_API_KEY` in .env starts with `fc-` |
| `402 Payment Required` | Firecrawl credits exhausted | Add credits at firecrawl.dev/billing |
| `403 Forbidden` | Site blocks scraping | Try `--proxy stealth`, add custom headers |
| `429 Rate Limited` | Too many requests | Wait 60s, implement exponential backoff |
| `Timeout` | Page took too long to load | Increase `timeout`, reduce `wait_for` |
| `JS rendering failed` | Dynamic content didn't load | Increase `wait_for`, add browser actions |
| `Empty content` | Main content extraction failed | Set `only_main_content: false` |
| `Invalid selector` | Browser action selector not found | Verify CSS selector on target page |
| `Redirect loop` | Page redirects infinitely | Check URL, may be geo-blocked |

### Recovery Strategies

1. **Automatic retry**: Implement exponential backoff (1s, 2s, 4s, 8s) for 429 errors
2. **Proxy escalation**: Start with `auto`, escalate to `stealth` on 403
3. **Graceful degradation**: If `summary` format fails, fall back to `markdown` only
4. **Credit monitoring**: Check credit balance before batch jobs, alert at 10% remaining
5. **Timeout tuning**: Start with 30s, increase to 60s for JS-heavy sites
6. **Caching**: Cache successful scrapes to avoid redundant credit usage

## Testing Checklist

### Pre-flight
- [ ] `FIRECRAWL_API_KEY` set in `.env` (format: `fc-...`)
- [ ] Dependencies installed (`pip install firecrawl-py python-dotenv`)
- [ ] Network connectivity to `api.firecrawl.dev`
- [ ] Sufficient Firecrawl credits available

### Smoke Test
```bash
# Quick test with a simple public page
python scripts/firecrawl_scrape.py "https://example.com"

# Test with markdown format explicitly
python scripts/firecrawl_scrape.py "https://httpbin.org/html" --format markdown

# Test with JS-heavy page (wait for load)
python scripts/firecrawl_scrape.py "https://news.ycombinator.com" --wait-for 2000
```

### Validation
- [ ] Response contains `success: true`
- [ ] `markdown` field contains clean, readable content
- [ ] `title` matches the page title
- [ ] `metadata` contains `statusCode: 200`
- [ ] No HTML tags in markdown output (clean conversion)
- [ ] `only_main_content` removes headers/footers/navbars
- [ ] `--proxy stealth` works for paywalled content (test carefully)
- [ ] Error responses include meaningful error codes (401, 402, 403, 429)
- [ ] Cost: ~1 credit per page scraped
