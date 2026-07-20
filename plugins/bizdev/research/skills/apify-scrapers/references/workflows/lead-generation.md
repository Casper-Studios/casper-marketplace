# Lead Generation Workflow

## Overview
Multi-step workflow to discover businesses, extract contact info, and prepare leads for CRM.

## Workflow Steps

```
Step 1: Discover Businesses
├── Google Maps search for target industry
└── Output: List of businesses with basic info

Step 2: Extract Contact Info
├── Run contact enrichment on business websites
└── Output: Emails, phones, social links

Step 3: Enrich with Research (Optional)
├── Use parallel-research to get company info
└── Output: Company size, funding, news

Step 4: Save to CRM or Sheets
├── Use attio-crm or google-workspace
└── Output: Leads in your system
```

## Example Commands

```bash
# Step 1: Find coffee shops in SF
python scripts/scrape_google_maps.py search "coffee shops" --location "San Francisco" --max-results 100 --output leads_raw.json

# Step 2: Extract contact info from websites
cat leads_raw.json | jq -r '.data[].website' > websites.txt
python scripts/enrich_contacts.py --from-file websites.txt --output leads_enriched.json

# Step 3: (Optional) Research each company
# Use parallel-research skill

# Step 4: Save to CRM
# Use attio-crm or google-workspace skill
```

## Cost Estimate

| Step | Actor | Items | Cost |
|------|-------|-------|------|
| Discovery | Google Maps | 100 places | ~$1-5 |
| Enrichment | Contact Info | 100 sites | ~$1-2 |
| **Total** | | | ~$2-7 |

## Tips
- Start with specific location + industry queries
- Filter by rating to focus on established businesses
- Use contact enrichment only on sites that have websites
- Dedupe emails before importing to CRM

## Related Skills
- `google-workspace` - Save leads to Google Sheets
- `attio-crm` - Add companies and contacts
- `parallel-research` - Enrich with company intel
