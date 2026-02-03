# Vendor Selection

## Overview
Compare vendors/tools based on specific requirements using Parallel AI research.

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | string | Yes | Software/service category |
| `requirements` | list | Yes | Must-have features |
| `nice_to_have` | list | No | Optional features |
| `budget` | string | No | Budget constraints |
| `limit` | int | No | Max vendors to compare |

## CLI Usage

```bash
# Basic vendor comparison
python scripts/vendor_selection.py "CRM software" --requirements "enterprise,API,automation"

# With budget
python scripts/vendor_selection.py "Project management" \
  --requirements "gantt,collaboration" \
  --budget "under $50/user/month"

# With nice-to-haves
python scripts/vendor_selection.py "Email marketing" \
  --requirements "automation,analytics" \
  --nice-to-have "AI content,SMS" \
  --limit 5
```

## Output Structure

```json
{
  "category": "CRM software",
  "requirements": ["enterprise", "API", "automation"],
  "vendors": [
    {
      "name": "Salesforce",
      "url": "https://salesforce.com",
      "match_score": 95,
      "meets_requirements": true,
      "pricing": "$25-300/user/month",
      "pros": ["Enterprise-grade", "Extensive API"],
      "cons": ["Complex", "Expensive"],
      "requirements_check": {
        "enterprise": true,
        "API": true,
        "automation": true
      }
    }
  ],
  "recommendation": "Salesforce for enterprise needs, HubSpot for mid-market",
  "sources": [...]
}
```

## Workflow

1. FindAll API discovers vendors matching category
2. Task API enriches each with feature analysis
3. Chat API generates comparison and recommendation

## Cost
~$5-15 depending on number of vendors (uses FindAll + Task APIs)

## Testing Checklist

### Pre-flight
- [ ] `PARALLEL_API_KEY` set in `.env`
- [ ] Dependencies installed (`pip install requests python-dotenv`)
- [ ] Network connectivity to `api.parallel.ai`
- [ ] Sufficient API credits for FindAll + Task operations

### Smoke Test
```bash
# Simple vendor comparison (minimal requirements)
python scripts/vendor_selection.py "video conferencing" --requirements "screen sharing,recording" --limit 3

# With budget constraint
python scripts/vendor_selection.py "project management tools" \
  --requirements "kanban,mobile app" \
  --budget "under $20/user/month" \
  --limit 5

# With nice-to-haves
python scripts/vendor_selection.py "email marketing platform" \
  --requirements "automation,analytics" \
  --nice-to-have "AI content,A/B testing" \
  --limit 5
```

### Validation
- [ ] Response contains `category`, `requirements`, `vendors` array
- [ ] Each vendor has `name`, `url`, `match_score`, `pricing`
- [ ] `meets_requirements` boolean is accurate
- [ ] `requirements_check` shows true/false for each requirement
- [ ] `pros` and `cons` are relevant to vendor
- [ ] `recommendation` provides actionable summary
- [ ] `sources` array contains valid research URLs
- [ ] `--limit` parameter caps number of vendors
- [ ] `--budget` filter excludes vendors above price point
- [ ] Cost tracked: FindAll (~$1-5) + Task enrichment (~$0.10-0.50 per vendor)

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid or missing API key | Verify `PARALLEL_API_KEY` in .env |
| `402 Payment Required` | Insufficient credits | Add credits - vendor selection uses multiple APIs |
| `429 Rate Limited` | Exceeded request limits | Wait and retry with exponential backoff |
| `FindAll timeout` | Discovery taking too long | Reduce `match_limit`, narrow category |
| `No vendors found` | Category too specific | Broaden search terms or remove constraints |
| `Enrichment failed` | Task API failed for vendor | Skip vendor, continue with remaining |
| `Budget parse error` | Invalid budget format | Use format like "under $50/user/month" |
| `Empty requirements` | No requirements specified | At least one requirement is needed |

### Recovery Strategies

1. **Automatic retry**: Implement exponential backoff for transient failures
2. **Partial results**: If some vendor enrichments fail, return available data
3. **FindAll fallback**: If FindAll fails, use Chat API to discover vendors (less structured)
4. **Cost protection**: Set hard budget limit, abort if approaching threshold
5. **Incremental processing**: Process vendors one at a time to enable resume on failure
6. **Cache vendor data**: Cache enrichment results to avoid re-processing on retry

## Performance Tips

### Processor Selection
- Start with `core-lite` for simple lookups
- Use `core` for standard research
- Reserve `ultra` for critical decisions

### Polling Optimization
- Start polling after 5 seconds
- Use exponential backoff (5s, 10s, 20s, 40s)
- Set reasonable timeout (5min for ultra)

### Cost Reduction
- Cache research results (valid for hours)
- Combine related queries
- Use `chat` for quick questions, `research` for depth

### Batch Research
- Queue multiple research requests
- Process results as they complete
- Implement concurrent polling
