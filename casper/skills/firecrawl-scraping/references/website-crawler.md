# Website Crawler (Multi-Page)

Deep crawl entire websites to extract clean content from multiple pages. Ideal for documentation sites, knowledge bases, and building RAG datasets.

## API Endpoint

`POST https://api.firecrawl.dev/v1/crawl`

**Note:** This is an asynchronous endpoint. It returns a job ID that you poll for results.

## Authentication

```bash
Authorization: Bearer fc-YOUR-API-KEY
Content-Type: application/json
```

The API key must start with `fc-`. Set it in your environment:

```bash
export FIRECRAWL_API_KEY="fc-your-api-key-here"
```

## Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | required | Starting URL for the crawl |
| `limit` | int | 10 | Maximum pages to crawl |
| `maxDepth` | int | 10 | Maximum link depth from start URL |
| `allowBackwardLinks` | bool | false | Follow links to parent directories |
| `allowExternalLinks` | bool | false | Follow links to other domains |
| `includePaths` | array | [] | URL patterns to include (glob patterns) |
| `excludePaths` | array | [] | URL patterns to exclude (glob patterns) |
| `ignoreSitemap` | bool | true | Ignore sitemap.xml for discovery |
| `scrapeOptions` | object | {} | Options applied to each page (see below) |
| `webhook` | string | null | URL to POST results when complete |

### Scrape Options (Applied to Each Page)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `formats` | array | ["markdown"] | Output formats per page |
| `onlyMainContent` | bool | true | Extract only main content |
| `includeTags` | array | [] | HTML tags to include |
| `excludeTags` | array | [] | HTML tags to exclude |
| `waitFor` | int | 0 | Wait time (ms) for JS to load |
| `timeout` | int | 30000 | Timeout per page (ms) |

## Output Structure

### Job Creation Response

```json
{
  "success": true,
  "id": "crawl_abc123def456",
  "url": "https://api.firecrawl.dev/v1/crawl/crawl_abc123def456"
}
```

### Poll Status Response (In Progress)

```json
{
  "status": "scraping",
  "total": 50,
  "completed": 23,
  "creditsUsed": 23,
  "expiresAt": "2025-12-09T13:00:00Z"
}
```

### Final Results Response

```json
{
  "status": "completed",
  "total": 50,
  "completed": 50,
  "creditsUsed": 50,
  "expiresAt": "2025-12-09T13:00:00Z",
  "data": [
    {
      "markdown": "# Page Title\n\nClean markdown content...",
      "html": "<html>...</html>",
      "metadata": {
        "title": "Page Title",
        "description": "Meta description",
        "sourceURL": "https://docs.example.com/page1",
        "statusCode": 200,
        "language": "en"
      },
      "links": ["https://docs.example.com/link1", "https://docs.example.com/link2"]
    }
  ]
}
```

## CLI Usage

```bash
# Basic crawl (10 pages default)
python scripts/firecrawl_crawl.py "https://docs.example.com"

# Crawl with page limit
python scripts/firecrawl_crawl.py "https://docs.example.com" --limit 100

# Crawl specific sections only
python scripts/firecrawl_crawl.py "https://docs.example.com" \
  --include-paths "/api/*,/guides/*" \
  --exclude-paths "/blog/*,/changelog/*"

# Deep crawl with increased depth
python scripts/firecrawl_crawl.py "https://docs.example.com" \
  --limit 500 --max-depth 5

# Crawl with backward links (parent directories)
python scripts/firecrawl_crawl.py "https://example.com/docs/v2/" \
  --allow-backward-links

# Output to file
python scripts/firecrawl_crawl.py "https://docs.example.com" \
  --output .tmp/crawl_results.json

# Wait for JS-heavy pages
python scripts/firecrawl_crawl.py "https://react-docs.example.com" \
  --wait-for 3000 --limit 50

# Dry run (estimate without crawling)
python scripts/firecrawl_crawl.py "https://docs.example.com" \
  --limit 100 --dry-run
```

## Python SDK Usage

### Basic Crawl (Synchronous)

```python
from firecrawl import Firecrawl
import os

firecrawl = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))

# Crawl and wait for results (blocks until complete)
result = firecrawl.crawl(
    url="https://docs.example.com",
    limit=100
)

# Access results
for page in result.data:
    print(f"URL: {page.metadata.sourceURL}")
    print(f"Title: {page.metadata.title}")
    print(f"Content: {page.markdown[:200]}...")
```

### Async Crawl with Polling

```python
from firecrawl import Firecrawl
import os
import time

firecrawl = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))

# Start crawl (returns immediately)
job = firecrawl.async_crawl_url(
    url="https://docs.example.com",
    params={
        "limit": 100,
        "maxDepth": 3,
        "scrapeOptions": {
            "formats": ["markdown"],
            "onlyMainContent": True
        }
    }
)

print(f"Crawl started: {job['id']}")

# Poll for completion
while True:
    status = firecrawl.check_crawl_status(job['id'])

    if status['status'] == 'completed':
        print(f"Crawl complete! {status['completed']} pages")
        break
    elif status['status'] == 'failed':
        raise Exception(f"Crawl failed: {status.get('error')}")

    print(f"Progress: {status['completed']}/{status['total']} pages")
    time.sleep(5)

# Get results
results = firecrawl.get_crawl_status(job['id'])
pages = results['data']
```

### Advanced Crawl with Filters

```python
from firecrawl import Firecrawl
import os

firecrawl = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))

# Crawl documentation only, exclude blog and changelog
result = firecrawl.crawl(
    url="https://docs.example.com",
    params={
        "limit": 200,
        "maxDepth": 4,
        "includePaths": ["/docs/*", "/api/*", "/guides/*"],
        "excludePaths": ["/blog/*", "/changelog/*", "/internal/*"],
        "allowBackwardLinks": False,
        "ignoreSitemap": False,  # Use sitemap for discovery
        "scrapeOptions": {
            "formats": ["markdown"],
            "onlyMainContent": True,
            "excludeTags": ["nav", "footer", "aside", ".sidebar"]
        }
    }
)

print(f"Crawled {len(result.data)} pages")
```

### Direct API (No SDK)

```python
import requests
import os
import time

API_KEY = os.getenv("FIRECRAWL_API_KEY")
BASE_URL = "https://api.firecrawl.dev/v1"

def crawl_website(url: str, limit: int = 100) -> list:
    """Crawl a website and return all pages."""

    # Start crawl
    response = requests.post(
        f"{BASE_URL}/crawl",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "url": url,
            "limit": limit,
            "scrapeOptions": {
                "formats": ["markdown"],
                "onlyMainContent": True
            }
        }
    )
    response.raise_for_status()
    job = response.json()
    job_id = job["id"]

    # Poll for completion
    while True:
        status_response = requests.get(
            f"{BASE_URL}/crawl/{job_id}",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        status_response.raise_for_status()
        status = status_response.json()

        if status["status"] == "completed":
            return status["data"]
        elif status["status"] == "failed":
            raise Exception(f"Crawl failed: {status.get('error')}")

        print(f"Progress: {status['completed']}/{status['total']}")
        time.sleep(5)

# Usage
pages = crawl_website("https://docs.example.com", limit=50)
for page in pages:
    print(f"- {page['metadata']['sourceURL']}")
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid or missing API key | Verify `FIRECRAWL_API_KEY` starts with `fc-` |
| `402 Payment Required` | Credits exhausted | Add credits at firecrawl.dev/billing |
| `403 Forbidden` | Domain blocks crawling | Check robots.txt, try different start URL |
| `429 Rate Limited` | Too many concurrent crawls | Wait 60s, reduce concurrent jobs |
| `Crawl timeout` | Pages too slow or limit too high | Reduce `limit`, increase `timeout` |
| `Partial results` | Some pages failed | Check individual page errors in results |
| `Empty data array` | No pages matched filters | Verify `includePaths`/`excludePaths` patterns |
| `Status: failed` | Crawl job failed entirely | Check error message, verify URL accessible |

### Recovery Strategies

1. **Credit monitoring**: Check balance before large crawls, alert at 20% remaining
2. **Chunked crawling**: For very large sites, crawl sections separately with `includePaths`
3. **Exponential backoff**: For 429 errors, wait 5s, 10s, 20s, 40s between retries
4. **Partial result handling**: Save successful pages even if crawl partially fails
5. **Resume capability**: Track crawled URLs, exclude them on retry with `excludePaths`
6. **Timeout tuning**: Start with 30s per page, increase to 60s for JS-heavy sites

```python
def crawl_with_retry(url: str, limit: int, max_retries: int = 3):
    """Crawl with automatic retry and exponential backoff."""
    for attempt in range(max_retries):
        try:
            return firecrawl.crawl(url=url, limit=limit)
        except Exception as e:
            if "429" in str(e):
                wait_time = (2 ** attempt) * 5
                print(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
            elif attempt == max_retries - 1:
                raise
            else:
                time.sleep(5)
```

## Cost Estimates

| Crawl Size | Credits Used | Est. Cost (Standard) |
|------------|--------------|----------------------|
| 10 pages | 10 credits | ~$0.10 |
| 50 pages | 50 credits | ~$0.50 |
| 100 pages | 100 credits | ~$1.00 |
| 500 pages | 500 credits | ~$5.00 |
| 1000 pages | 1000 credits | ~$10.00 |

**Notes:**
- 1 credit = 1 page crawled
- Failed pages may still consume credits
- Stealth proxy costs 5x more per page
- Check current pricing at firecrawl.dev/pricing

### Cost Optimization

```python
# Estimate before crawling
def estimate_crawl_cost(url: str, limit: int) -> dict:
    """Estimate crawl cost before execution."""
    # Use sitemap or discovery to estimate page count
    # Most doc sites have 50-500 pages
    estimated_pages = min(limit, 100)  # Conservative estimate

    return {
        "estimated_pages": estimated_pages,
        "estimated_credits": estimated_pages,
        "estimated_cost_usd": estimated_pages * 0.01,
        "max_credits": limit,
        "max_cost_usd": limit * 0.01
    }
```

## Rate Limits

| Plan | Concurrent Crawls | Pages/Minute | Max Pages/Crawl |
|------|-------------------|--------------|-----------------|
| Free | 1 | 10 | 100 |
| Standard | 3 | 50 | 1,000 |
| Growth | 5 | 100 | 10,000 |
| Enterprise | 10+ | 500+ | Unlimited |

**Best Practices:**
- Don't start multiple large crawls simultaneously
- Use webhooks instead of polling for large crawls
- Batch small crawls during off-peak hours

## Testing Checklist

### Pre-flight
- [ ] `FIRECRAWL_API_KEY` set in `.env` (format: `fc-...`)
- [ ] Dependencies installed (`pip install firecrawl-py python-dotenv requests`)
- [ ] Network connectivity to `api.firecrawl.dev`
- [ ] Sufficient Firecrawl credits (check at firecrawl.dev/dashboard)
- [ ] Target site is accessible (not geo-blocked, login-required)

### Smoke Test

```bash
# Quick test with small limit
python scripts/firecrawl_crawl.py "https://example.com" --limit 5

# Test documentation site
python scripts/firecrawl_crawl.py "https://docs.python.org/3/" --limit 10

# Test with path filters
python scripts/firecrawl_crawl.py "https://docs.example.com" \
  --include-paths "/api/*" --limit 20
```

### Validation
- [ ] Job ID returned from initial request
- [ ] Status polling shows progress (completed/total)
- [ ] Final status is `completed` (not `failed`)
- [ ] `data` array contains page objects
- [ ] Each page has `markdown` and `metadata.sourceURL`
- [ ] `creditsUsed` matches number of pages
- [ ] No HTML tags in markdown output (clean conversion)
- [ ] `includePaths` filter works correctly
- [ ] `excludePaths` filter excludes specified paths

## Security Notes

### robots.txt Compliance
- Firecrawl respects `robots.txt` by default
- Some sites may block crawler user agents
- For legitimate use cases, contact site owners for permission

### Data Handling
- Crawled content may contain sensitive information
- Store results securely (encrypted at rest)
- Delete crawl results after processing
- Don't crawl login-protected pages without authorization

### API Key Security
- Never commit API keys to version control
- Use environment variables or secrets management
- Rotate keys if exposed
- Set up billing alerts to detect unauthorized usage

## Advanced Features

### Webhook Notifications

```python
# Get notified when crawl completes
result = firecrawl.crawl(
    url="https://docs.example.com",
    params={
        "limit": 100,
        "webhook": "https://your-server.com/webhook/firecrawl"
    }
)

# Webhook payload:
# {
#   "type": "crawl.completed",
#   "id": "crawl_abc123",
#   "status": "completed",
#   "total": 100,
#   "data": [...]
# }
```

### Sitemap-Based Discovery

```python
# Use sitemap for comprehensive discovery
result = firecrawl.crawl(
    url="https://docs.example.com",
    params={
        "limit": 500,
        "ignoreSitemap": False,  # Enable sitemap discovery
        "maxDepth": 10
    }
)
```

### Depth Control

```python
# Shallow crawl (homepage + direct links only)
shallow = firecrawl.crawl(
    url="https://example.com",
    params={"limit": 50, "maxDepth": 1}
)

# Deep crawl (follow links deeply)
deep = firecrawl.crawl(
    url="https://example.com",
    params={"limit": 500, "maxDepth": 5}
)
```

### Backward Links

```python
# Include parent directories (useful for versioned docs)
result = firecrawl.crawl(
    url="https://docs.example.com/v2/api/",
    params={
        "limit": 100,
        "allowBackwardLinks": True  # Also crawl /v2/ and /docs/
    }
)
```

## Integration Patterns

### RAG Pipeline Integration

```python
from firecrawl import Firecrawl
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb

# 1. Crawl documentation
firecrawl = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))
result = firecrawl.crawl(url="https://docs.example.com", limit=200)

# 2. Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = []
for page in result.data:
    page_chunks = splitter.split_text(page.markdown)
    for chunk in page_chunks:
        chunks.append({
            "text": chunk,
            "source": page.metadata.sourceURL,
            "title": page.metadata.title
        })

# 3. Store in vector database
client = chromadb.Client()
collection = client.create_collection("docs")
collection.add(
    documents=[c["text"] for c in chunks],
    metadatas=[{"source": c["source"], "title": c["title"]} for c in chunks],
    ids=[f"chunk_{i}" for i in range(len(chunks))]
)
```

### Export to Google Docs

```python
# Crawl and export to Google Doc
pages = firecrawl.crawl(url="https://docs.example.com", limit=50)

# Combine all markdown
combined = ""
for page in pages.data:
    combined += f"# {page.metadata.title}\n\n"
    combined += f"Source: {page.metadata.sourceURL}\n\n"
    combined += page.markdown
    combined += "\n\n---\n\n"

# Save to file, then upload to Google Docs
with open(".tmp/crawl_export.md", "w") as f:
    f.write(combined)
```

### Competitive Analysis

```python
# Crawl competitor documentation
competitors = [
    "https://docs.competitor1.com",
    "https://docs.competitor2.com",
    "https://docs.competitor3.com"
]

all_results = {}
for url in competitors:
    result = firecrawl.crawl(url=url, limit=100)
    all_results[url] = {
        "pages": len(result.data),
        "topics": [p.metadata.title for p in result.data]
    }
```

## Performance Tips

### Optimize Crawl Speed

1. **Use appropriate limits**: Don't crawl more pages than needed
2. **Filter paths early**: Use `includePaths` to avoid crawling irrelevant sections
3. **Reduce page timeout**: Lower `scrapeOptions.timeout` for fast-loading sites
4. **Skip JS wait**: Set `waitFor: 0` for static HTML sites
5. **Disable HTML output**: Only request `formats: ["markdown"]` if you don't need HTML

### Reduce Credit Usage

1. **Test with small limits first**: Start with `limit: 10` to verify filters
2. **Use path filters**: `excludePaths` for blog, changelog, etc.
3. **Check sitemap first**: Estimate page count before crawling
4. **Cache results**: Don't re-crawl unchanged content

### Handle Large Sites

```python
# For sites with 1000+ pages, crawl in sections
sections = ["/docs/", "/api/", "/guides/", "/tutorials/"]

all_pages = []
for section in sections:
    result = firecrawl.crawl(
        url=f"https://docs.example.com{section}",
        params={
            "limit": 200,
            "maxDepth": 3,
            "allowBackwardLinks": False  # Stay within section
        }
    )
    all_pages.extend(result.data)
    print(f"Crawled {len(result.data)} pages from {section}")
```

## Troubleshooting

### Crawl Returns Empty Data

```python
# Check if URL is accessible
import requests
response = requests.get("https://docs.example.com")
print(f"Status: {response.status_code}")

# Verify path filters aren't too restrictive
# Try without filters first
result = firecrawl.crawl(url="https://docs.example.com", limit=10)
print(f"Pages without filters: {len(result.data)}")
```

### Crawl Stuck on "scraping" Status

- Check if target site is rate limiting
- Reduce `limit` to test with fewer pages
- Increase `scrapeOptions.timeout`
- Try a different start URL

### Missing Pages

- Check `maxDepth` - increase if pages are deeply nested
- Enable `allowBackwardLinks` if pages link to parent directories
- Use sitemap discovery: `ignoreSitemap: False`
- Verify pages aren't excluded by `excludePaths`

### Duplicate Content

- Some sites have multiple URLs for same content
- Use `excludePaths` to filter query strings: `/page?*`
- Post-process results to deduplicate by content hash

### JS-Heavy Sites Not Rendering

```python
# Increase wait time for JS to execute
result = firecrawl.crawl(
    url="https://spa-docs.example.com",
    params={
        "limit": 50,
        "scrapeOptions": {
            "waitFor": 5000,  # Wait 5 seconds for JS
            "timeout": 60000  # Longer timeout
        }
    }
)
```

## Related Skills

- **firecrawl-scraping/single-page** - For scraping individual pages with more control
- **apify-scrapers** - Alternative crawler with different anti-bot capabilities
- **parallel-research** - Use crawled content for AI research
- **google-workspace** - Export crawl results to Google Docs/Sheets

## Comparison: Firecrawl Crawl vs Apify Website Content Crawler

| Feature | Firecrawl Crawl | Apify Crawler |
|---------|-----------------|---------------|
| API | Async polling | Async polling |
| Speed | Fast | Very fast (cheerio mode) |
| JS rendering | Built-in | Playwright mode |
| Anti-bot | Excellent | Good |
| Max pages | Plan-based | Unlimited |
| Cost model | Credits/page | Compute units |
| Path filtering | Include/exclude | Glob patterns |
| Best for | Small-medium crawls | Large crawls, RAG |
| Webhook support | Yes | Yes |
| SDK | Python, Node | Python, Node, many |

**Recommendation:**
- **Firecrawl**: Premium content, stealth needed, <500 pages
- **Apify**: Large documentation sites, 500+ pages, cost-sensitive
