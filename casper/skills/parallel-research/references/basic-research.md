# Basic Company Research

## Overview
Simplified company research using Parallel AI's Chat API.

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `company` | string | Yes | Company name |
| `focus` | string | No | Research focus area |

## CLI Usage

```bash
# Basic company research
python scripts/basic_research.py "Anthropic"

# With focus area
python scripts/basic_research.py "Microsoft" --focus "AI strategy"

# Output as JSON
python scripts/basic_research.py "OpenAI" --json
```

## Output Structure

```json
{
  "company": "Anthropic",
  "summary": "AI safety company founded in 2021...",
  "key_facts": {
    "founded": "2021",
    "headquarters": "San Francisco",
    "funding": "$8B+ total",
    "employees": "~400"
  },
  "recent_news": [...],
  "products": ["Claude", "Claude API"],
  "competitors": ["OpenAI", "Google DeepMind"],
  "sources": [...]
}
```

## Cost
~$0.005 per company (uses Chat API)

## When to Use

| Scenario | Use This |
|----------|----------|
| Quick company overview | basic_research.py |
| Comprehensive report | parallel_research.py research |
| Find similar companies | parallel_research.py findall |

## Testing Checklist

### Pre-flight
- [ ] `PARALLEL_API_KEY` set in `.env`
- [ ] Dependencies installed (`pip install requests python-dotenv`)
- [ ] Network connectivity to `api.parallel.ai`

### Smoke Test
```bash
# Basic company research
python scripts/basic_research.py "Google"

# With specific focus area
python scripts/basic_research.py "Microsoft" --focus "Azure cloud services"

# Output as JSON (for parsing)
python scripts/basic_research.py "Anthropic" --json
```

### Validation
- [ ] Response contains `company` name matching input
- [ ] `summary` provides coherent company overview
- [ ] `key_facts` includes `founded`, `headquarters`, `funding`, `employees`
- [ ] `recent_news` array contains relevant articles (if available)
- [ ] `products` list is accurate
- [ ] `competitors` list is reasonable
- [ ] `sources` array contains valid URLs
- [ ] `--focus` parameter narrows research scope appropriately
- [ ] Response time under 10 seconds (Chat API)
- [ ] Cost: ~$0.005 per company

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid or missing API key | Verify `PARALLEL_API_KEY` in .env |
| `402 Payment Required` | Insufficient credits | Add credits at parallel.ai/billing |
| `429 Rate Limited` | Exceeded 300 req/min limit | Wait and retry with exponential backoff |
| `Company not found` | No data available for company | Try alternative company name or domain |
| `Timeout` | Request took too long | Retry, network may be slow |
| `Invalid response` | API returned unexpected format | Log response, may need schema update |
| `Empty sources` | No web sources found | Company may be too new or private |

### Recovery Strategies

1. **Automatic retry**: Implement exponential backoff (1s, 2s, 4s) for transient failures
2. **Alternative queries**: If company name fails, try domain name or stock ticker
3. **Graceful degradation**: If sources empty, return available data without sources
4. **Response validation**: Validate response structure before parsing
5. **Caching**: Cache successful research results to avoid redundant API calls

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
