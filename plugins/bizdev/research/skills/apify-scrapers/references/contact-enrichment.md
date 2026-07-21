# Contact Enrichment

## Overview
Extract emails, phone numbers, and social media links from websites using Apify's contact info scraper.

## Actor Used
`vdrmota/contact-info-scraper`

## Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `urls` | list | required | Website URLs to crawl |
| `--max-pages` | int | 5 | Max pages to crawl per site |
| `--include-social` | bool | true | Extract social media links |
| `--from-file` | str | - | Load URLs from file |
| `--output` | str | auto | Output filename |

## CLI Usage

```bash
# Single website
python scripts/enrich_contacts.py "https://example.com"

# Multiple websites
python scripts/enrich_contacts.py "https://site1.com" "https://site2.com"

# From file (one URL per line)
python scripts/enrich_contacts.py --from-file company_websites.txt

# With options
python scripts/enrich_contacts.py "https://example.com" --max-pages 10 --output contacts.json

# Without social links
python scripts/enrich_contacts.py "https://example.com" --no-social
```

## Output Structure

```json
{
  "scraped_at": "2025-01-30T...",
  "platform": "contact_enrichment",
  "total_sites": 5,
  "total_emails_found": 12,
  "total_phones_found": 8,
  "data": [
    {
      "url": "https://example.com",
      "emails": ["info@example.com", "sales@example.com"],
      "phones": ["+1-555-123-4567"],
      "social": {
        "linkedin": "...",
        "twitter": "...",
        "facebook": "..."
      }
    }
  ]
}
```

## Cost Estimates
- ~$0.01-0.02 per website
- 100 websites ≈ $1-2

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| No contacts found | No email/phone on site | Check site manually |
| Timeout | Large site | Reduce max_pages |
| 403 Forbidden | Site blocks crawlers | May not be scrapable |

## Testing Checklist
- Pre-flight: APIFY_TOKEN set, URLs are valid
- Smoke test: Run on known site with contact page
- Validate: Check emails are valid format

## Use Cases
- Lead generation: Enrich Google Maps results
- Sales prospecting: Get contacts from company websites
- CRM enrichment: Fill in missing contact data

## Related Skills
- `google-maps` - Find businesses, then enrich
- `attio-crm` - Save enriched contacts
- `parallel-research` - Company research
