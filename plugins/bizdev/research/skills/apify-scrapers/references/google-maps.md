# Google Maps/Places Scraping

## Overview

Scrape Google Maps for business listings, place details, reviews, and contact information. Ideal for lead generation, competitor analysis, and market research.

## Actors

| Mode | Actor ID | Purpose |
|------|----------|---------|
| `search` | `compass/crawler-google-places` | Search businesses by query + location |
| `place` | `compass/google-maps-extractor` | Extract details from specific place URLs |
| `reviews` | `compass/google-maps-reviews-scraper` | Scrape reviews for a specific place |

## Inputs

### Search Mode

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | Business type or name (e.g., "coffee shops") |
| `location` | string | required | City, address, or region (e.g., "San Francisco, CA") |
| `max_results` | int | 20 | Maximum places to return |
| `min_rating` | float | 0 | Minimum star rating filter (0-5) |
| `zoom` | int | 14 | Map zoom level (10=city, 14=neighborhood, 17=street) |
| `language` | string | "en" | Language code for results |

### Place Mode

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string/list | required | Single URL or list of Google Maps place URLs |

### Reviews Mode

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | required | Google Maps place URL |
| `max_reviews` | int | 50 | Maximum reviews to scrape |
| `sort_by` | string | "relevant" | Sort order: newest, highest, lowest, relevant |

## CLI Usage

```bash
# Search for businesses in a location
python scripts/scrape_google_maps.py search "coffee shops" --location "San Francisco" --max-results 50

# Search with rating filter
python scripts/scrape_google_maps.py search "restaurants" --location "NYC" --min-rating 4.0 --max-results 100

# Search with zoom level for larger area
python scripts/scrape_google_maps.py search "gyms" --location "Los Angeles" --zoom 12 --max-results 200

# Extract details from a specific place
python scripts/scrape_google_maps.py place "https://maps.google.com/maps/place/..."

# Batch extract multiple places
python scripts/scrape_google_maps.py place "url1" "url2" "url3"

# Scrape reviews for a place
python scripts/scrape_google_maps.py reviews "https://maps.google.com/maps/place/..." --max-reviews 100 --sort-by newest

# Get highest rated reviews
python scripts/scrape_google_maps.py reviews "https://maps.google.com/..." --max-reviews 50 --sort-by highest
```

## Output Structure

### Search/Place Output

```json
{
  "places": [
    {
      "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
      "name": "Business Name",
      "address": "123 Main St, City, State 12345",
      "phone": "+1-555-123-4567",
      "website": "https://example.com",
      "rating": 4.5,
      "reviews_count": 234,
      "price_level": "$$",
      "categories": ["Coffee Shop", "Cafe"],
      "coordinates": {
        "lat": 37.7749,
        "lng": -122.4194
      },
      "hours": {
        "monday": "7:00 AM - 8:00 PM",
        "tuesday": "7:00 AM - 8:00 PM"
      },
      "url": "https://maps.google.com/maps/place/..."
    }
  ],
  "scraped_at": "2024-01-15T10:30:00Z",
  "total_count": 50,
  "query": "coffee shops",
  "location": "San Francisco"
}
```

### Reviews Output

```json
{
  "place": {
    "name": "Business Name",
    "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4"
  },
  "reviews": [
    {
      "author": "John D.",
      "rating": 5,
      "text": "Great coffee and friendly staff!",
      "date": "2024-01-10",
      "likes": 12,
      "owner_response": "Thank you for visiting!"
    }
  ],
  "scraped_at": "2024-01-15T10:30:00Z",
  "total_count": 100
}
```

## Cost Estimates

| Operation | Approximate Cost |
|-----------|------------------|
| Search (per place) | ~$0.01-0.02 |
| Place details (per URL) | ~$0.01-0.03 |
| Reviews (per review) | ~$0.005-0.01 |

**Examples:**
- 50 places search: ~$0.50-1.00
- 100 reviews: ~$0.50-1.00
- Batch 20 place URLs: ~$0.20-0.60

## Testing Checklist

### Pre-flight
- [ ] `APIFY_API_TOKEN` set in `.env`
- [ ] Dependencies installed (`pip install apify-client python-dotenv`)
- [ ] Network connectivity to `api.apify.com`

### Smoke Test
```bash
# Quick search test (minimal results)
python scripts/scrape_google_maps.py search "coffee" --location "San Francisco" --max-results 5

# Single place extraction
python scripts/scrape_google_maps.py place "https://maps.google.com/maps/place/Starbucks/..."

# Reviews test (small batch)
python scripts/scrape_google_maps.py reviews "https://maps.google.com/..." --max-reviews 10
```

### Validation
- [ ] Response contains `places` array with expected fields
- [ ] `place_id` is present for each result
- [ ] `coordinates` contains valid lat/lng
- [ ] `phone` and `website` populated when available
- [ ] `rating` is between 0-5
- [ ] `reviews_count` is a positive integer
- [ ] `scraped_at` timestamp is present and valid
- [ ] No error messages in output

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid Apify API token | Verify `APIFY_API_TOKEN` in .env |
| `402 Payment Required` | Insufficient Apify credits | Add credits to Apify account |
| `Invalid URL` | Malformed Google Maps URL | Use full URL from browser address bar |
| `No results found` | Query too specific or location invalid | Broaden search, verify location spelling |
| `Actor timeout` | Too many results requested | Reduce `max_results`, use smaller zoom |
| `Rate limited` | Too many requests | Wait 60 seconds, implement backoff |
| `Place not found` | URL outdated or place removed | Verify place still exists on Google Maps |

### Recovery Strategies

1. **Automatic retry**: Implement exponential backoff (30s, 60s, 120s) for transient failures
2. **Graceful degradation**: Reduce `max_results` if actor times out
3. **URL validation**: Pre-validate Google Maps URLs before submitting
4. **Cost protection**: Set `maxCostPerRun` to prevent runaway costs
5. **Batch chunking**: Split large place URL lists into batches of 20-50

## Performance Tips

### Search Optimization
- Use specific `zoom` levels: 10 for city-wide, 14 for neighborhoods, 17 for specific streets
- Lower zoom = larger area = more results but slower
- Add `min_rating` filter to reduce low-quality results

### Batch Processing
- Combine multiple place URLs in single actor run (up to 100)
- Use `max_results` to limit during testing
- Process results incrementally for large datasets

### Cost Optimization
- Start with `max_results: 10` for testing queries
- Use `min_rating` to filter out irrelevant results early
- Cache place_ids to avoid re-scraping known places
- Batch place detail requests instead of individual calls

### Memory Usage
- Stream large result sets to file for >500 places
- Process reviews in batches of 100
- Use pagination for very large datasets

## Use Cases

### Lead Generation
```bash
# Find potential clients in target area
python scripts/scrape_google_maps.py search "dental clinics" --location "Austin, TX" --max-results 200 --min-rating 3.5
```

### Competitor Analysis
```bash
# Analyze competitor reviews
python scripts/scrape_google_maps.py reviews "https://maps.google.com/competitor-url" --max-reviews 500 --sort-by newest
```

### Market Research
```bash
# Map business density in area
python scripts/scrape_google_maps.py search "restaurants" --location "Downtown Seattle" --zoom 15 --max-results 500
```

### Contact Enrichment
```bash
# Get phone/website for known businesses
python scripts/scrape_google_maps.py place "url1" "url2" "url3" "url4" "url5"
```

## Related Skills

| Skill | Integration |
|-------|-------------|
| `attio-crm` | Save scraped leads directly to Attio CRM |
| `parallel-research` | Enrich place data with company research |
| `google-workspace` | Export results to Google Sheets |
| `slack-automation` | Send lead alerts to Slack channels |

### Example Pipeline

```bash
# 1. Scrape leads from Google Maps
python scripts/scrape_google_maps.py search "marketing agencies" --location "Chicago" --max-results 100

# 2. Enrich with company research
python ~/.claude/skills/parallel-research/scripts/research.py company "Company Name"

# 3. Save to CRM
python ~/.claude/skills/attio-crm/scripts/create_company.py --name "Company" --website "url" --phone "phone"

# 4. Notify team
python ~/.claude/skills/slack-automation/scripts/send_message.py "#leads" "New leads added from Chicago search"
```

## Notes

- Google Maps data updates frequently; re-scrape periodically for accuracy
- Some businesses may have incomplete data (missing phone/website)
- Review scraping respects Google's display limits
- Place IDs are stable and can be used for tracking/deduplication
- Coordinates are WGS84 format (standard GPS)
