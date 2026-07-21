# Facebook Scraping

## Overview

Facebook scraping provides access to public pages, posts, reviews, groups, and marketplace listings. Each data type uses a specialized Apify actor optimized for that content category.

**Capabilities:**
- Scrape public Facebook page information and metadata
- Extract posts from pages, profiles, and groups
- Collect reviews from business pages
- Monitor group discussions and activity
- Search marketplace listings by location and category

**Limitations:**
- Private profiles and closed groups are not accessible
- Login-protected content requires authentication (not recommended)
- Rate limits apply per actor run

## Actors Used

| Mode | Actor ID | Description | Pay Model |
|------|----------|-------------|-----------|
| `page` | `apify/facebook-pages-scraper` | Page metadata, about info, contact details | Per page |
| `posts` | `apify/facebook-posts-scraper` | Posts from pages/profiles with engagement metrics | Per post |
| `reviews` | `apify/facebook-reviews-scraper` | Reviews from business pages with ratings | Per review |
| `groups` | `apify/facebook-groups-scraper` | Group posts, comments, member activity | Per post |
| `marketplace` | `apify/facebook-marketplace-scraper` | Product listings with prices and locations | Per listing |

## Inputs

### Page Scraper

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `startUrls` | array | required | List of Facebook page URLs |
| `proxyConfiguration` | object | auto | Proxy settings for request rotation |

### Posts Scraper

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `startUrls` | array | required | Page/profile URLs to scrape posts from |
| `maxPosts` | int | 50 | Maximum posts per page |
| `maxPostDate` | string | null | Oldest post date (YYYY-MM-DD) |
| `maxComments` | int | 0 | Comments to include per post |

### Reviews Scraper

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `startUrls` | array | required | Business page URLs |
| `maxReviews` | int | 100 | Maximum reviews to collect |
| `sortBy` | string | "most_recent" | Sort order: "most_recent" or "most_helpful" |

### Groups Scraper

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `startUrls` | array | required | Group URLs (must be public) |
| `maxPosts` | int | 50 | Maximum posts from group |
| `maxComments` | int | 10 | Comments per post |
| `includeNestedComments` | bool | false | Include reply threads |

### Marketplace Scraper

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `searchQuery` | string | required | Product search term |
| `location` | string | null | City/region for local listings |
| `maxItems` | int | 50 | Maximum listings to return |
| `minPrice` | int | null | Minimum price filter |
| `maxPrice` | int | null | Maximum price filter |
| `categoryId` | string | null | Category filter (vehicles, electronics, etc.) |

## CLI Usage

```bash
# Scrape page metadata
python scripts/scrape_facebook.py page "https://facebook.com/pagename"

# Get recent posts from a page
python scripts/scrape_facebook.py posts "https://facebook.com/pagename" --max-posts 50

# Collect business reviews
python scripts/scrape_facebook.py reviews "https://facebook.com/pagename" --max-reviews 100

# Monitor group activity
python scripts/scrape_facebook.py groups "https://facebook.com/groups/groupname" --max-posts 50

# Search marketplace listings
python scripts/scrape_facebook.py marketplace "laptops" --location "New York" --max-items 50

# Marketplace with price filters
python scripts/scrape_facebook.py marketplace "iphone" --location "Los Angeles" --min-price 200 --max-price 800 --max-items 25
```

## Output Structure

### Page Output

```json
{
  "page": {
    "id": "page_id",
    "name": "Page Name",
    "url": "https://facebook.com/pagename",
    "category": "Technology Company",
    "about": "Company description...",
    "followers": 150000,
    "likes": 145000,
    "website": "https://example.com",
    "phone": "+1-555-0100",
    "email": "contact@example.com",
    "address": "123 Main St, City, State",
    "hours": {
      "monday": "9:00 AM - 5:00 PM",
      "tuesday": "9:00 AM - 5:00 PM"
    },
    "founded": "2015",
    "verified": true
  },
  "scraped_at": "2024-01-15T10:30:00Z"
}
```

### Posts Output

```json
{
  "posts": [
    {
      "id": "post_id",
      "text": "Post content here...",
      "url": "https://facebook.com/pagename/posts/12345",
      "created_at": "2024-01-14T15:30:00Z",
      "likes": 1250,
      "comments": 45,
      "shares": 120,
      "media": [
        {
          "type": "image",
          "url": "https://..."
        }
      ],
      "author": {
        "name": "Page Name",
        "id": "page_id"
      }
    }
  ],
  "scraped_at": "2024-01-15T10:30:00Z",
  "total_count": 50
}
```

### Reviews Output

```json
{
  "reviews": [
    {
      "id": "review_id",
      "rating": 5,
      "text": "Great service! Highly recommended...",
      "author": {
        "name": "John Doe",
        "id": "user_id",
        "profile_url": "https://facebook.com/johndoe"
      },
      "created_at": "2024-01-10T08:15:00Z",
      "helpful_count": 12,
      "reply": {
        "text": "Thank you for your feedback!",
        "created_at": "2024-01-10T14:00:00Z"
      }
    }
  ],
  "average_rating": 4.5,
  "total_reviews": 523,
  "scraped_at": "2024-01-15T10:30:00Z"
}
```

### Groups Output

```json
{
  "group": {
    "id": "group_id",
    "name": "Group Name",
    "url": "https://facebook.com/groups/groupname",
    "members": 25000,
    "privacy": "public",
    "description": "Group description..."
  },
  "posts": [
    {
      "id": "post_id",
      "text": "Post content...",
      "author": {
        "name": "Member Name",
        "id": "user_id"
      },
      "created_at": "2024-01-14T12:00:00Z",
      "likes": 45,
      "comments": [
        {
          "id": "comment_id",
          "text": "Comment text...",
          "author": "Commenter Name",
          "created_at": "2024-01-14T12:30:00Z"
        }
      ]
    }
  ],
  "scraped_at": "2024-01-15T10:30:00Z",
  "total_count": 50
}
```

### Marketplace Output

```json
{
  "listings": [
    {
      "id": "listing_id",
      "title": "MacBook Pro 2023",
      "price": 1200,
      "currency": "USD",
      "condition": "Used - Like New",
      "description": "Selling my MacBook Pro...",
      "location": {
        "city": "New York",
        "state": "NY",
        "distance": "5 miles away"
      },
      "seller": {
        "name": "Jane Smith",
        "id": "user_id",
        "joined": "2019",
        "response_rate": "Usually responds within an hour"
      },
      "images": [
        "https://..."
      ],
      "url": "https://facebook.com/marketplace/item/12345",
      "posted_at": "2024-01-13T09:00:00Z"
    }
  ],
  "search_query": "laptops",
  "location": "New York",
  "scraped_at": "2024-01-15T10:30:00Z",
  "total_count": 50
}
```

## Cost Estimates

| Mode | Cost per Item | Typical Run (50 items) | Notes |
|------|---------------|------------------------|-------|
| `page` | ~$0.01 | $0.01 | Single page per run |
| `posts` | ~$0.002 | $0.10 | Varies with media/comments |
| `reviews` | ~$0.001 | $0.05 | Lower cost per review |
| `groups` | ~$0.003 | $0.15 | Higher with comments enabled |
| `marketplace` | ~$0.002 | $0.10 | Includes image URLs |

**Cost Protection:**
- Set `maxCostPerRun` in actor options
- Start with small `maxItems` for testing
- Monitor Apify dashboard for usage

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid Apify API token | Verify `APIFY_API_TOKEN` in .env |
| `402 Payment Required` | Insufficient Apify credits | Add credits to Apify account |
| `Page not found` | Invalid URL or page deleted | Verify URL exists and is public |
| `Private page/group` | Content requires login | Cannot scrape; use public alternatives |
| `Rate limited` | Too many requests | Wait 5-10 minutes, reduce frequency |
| `Actor timeout` | Large dataset or slow response | Reduce `maxPosts`/`maxItems`, retry |
| `Blocked by Facebook` | Anti-scraping detection | Actor handles with proxy rotation |
| `Empty results` | No matching content found | Verify URL format, check page has content |
| `Invalid location` | Marketplace location not recognized | Use major city names, check spelling |

### Recovery Strategies

1. **Automatic retry**: Exponential backoff (30s, 60s, 120s) for transient failures
2. **Graceful degradation**: Reduce `maxItems` on timeout (50 -> 25 -> 10)
3. **Proxy rotation**: Built into actors; automatic IP switching
4. **Cost limits**: Set `maxCostPerRun` to prevent runaway costs
5. **Alerting**: Log failures with URL and error details

## Testing Checklist

### Pre-flight
- [ ] `APIFY_API_TOKEN` set in `.env`
- [ ] Dependencies installed (`pip install apify-client python-dotenv`)
- [ ] Network connectivity to `api.apify.com`

### Smoke Tests

```bash
# Test page scraping (use a known public page)
python scripts/scrape_facebook.py page "https://facebook.com/meta" --dry-run

# Test posts with minimal results
python scripts/scrape_facebook.py posts "https://facebook.com/meta" --max-posts 5

# Test marketplace with location
python scripts/scrape_facebook.py marketplace "phone" --location "Chicago" --max-items 5
```

### Validation
- [ ] Response contains expected top-level keys
- [ ] `scraped_at` timestamp is present and valid
- [ ] Item counts match requested limits
- [ ] No error messages in output
- [ ] URLs in results are valid Facebook links
- [ ] Engagement metrics are integers (not strings)
- [ ] Dates parse correctly

### Edge Cases
- [ ] Page with no posts returns empty array (not error)
- [ ] Business page without reviews handles gracefully
- [ ] Marketplace with no results returns empty listings
- [ ] Very long post text is preserved (not truncated)

## Performance Tips

### Batch Processing
- Combine multiple page URLs in single actor run for `page` and `posts` modes
- Use parallel runs for different data types (pages + reviews simultaneously)
- Process results as they stream for large datasets

### Rate Limit Handling
- Implement 30-second delays between runs targeting same page
- Distribute requests across time windows
- Use built-in proxy rotation (enabled by default)

### Cost Optimization
- Start with `maxItems: 10` for testing
- Use date filters (`maxPostDate`) to limit historical data
- Cache results locally to avoid re-scraping same content
- Disable comments (`maxComments: 0`) if not needed

### Memory Usage
- Stream large result sets to file instead of memory
- Process marketplace results in chunks of 100
- Clear actor storage after successful extraction

### Data Freshness
- Posts/reviews: Daily scraping for active monitoring
- Page metadata: Weekly updates sufficient
- Marketplace: Real-time or hourly for time-sensitive listings

## Related Skills

| Skill | Use Case | Link |
|-------|----------|------|
| Twitter Scraping | Cross-platform social monitoring | `references/twitter.md` |
| Google Sheets Export | Store results in spreadsheets | `directives/google_sheets.md` |
| Parallel Research | Deep dive on extracted topics | `directives/parallel_research.md` |
| Slack Notifications | Alert on new posts/reviews | `directives/slack_notifications.md` |

## Example Workflows

### Brand Monitoring
```bash
# 1. Get latest posts from brand page
python scripts/scrape_facebook.py posts "https://facebook.com/brandname" --max-posts 20

# 2. Check recent reviews
python scripts/scrape_facebook.py reviews "https://facebook.com/brandname" --max-reviews 50

# 3. Export to Google Sheets for analysis
python execution/export_to_sheets.py .tmp/facebook_results.json "Brand Monitoring"
```

### Competitive Intelligence
```bash
# Scrape competitor pages
for page in "competitor1" "competitor2" "competitor3"; do
  python scripts/scrape_facebook.py posts "https://facebook.com/$page" --max-posts 30
done
```

### Market Research
```bash
# Search marketplace for product category
python scripts/scrape_facebook.py marketplace "electric bikes" \
  --location "San Francisco" \
  --min-price 500 \
  --max-price 3000 \
  --max-items 100
```
