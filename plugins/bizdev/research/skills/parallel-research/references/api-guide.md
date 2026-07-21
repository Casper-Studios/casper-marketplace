# Parallel AI API Guide

## Authentication

**Headers:**
- `x-api-key: $PARALLEL_API_KEY` (Task/FindAll APIs)
- `Authorization: Bearer $PARALLEL_API_KEY` (Chat API)
- `Content-Type: application/json`

---

## 1. Chat with Web (Fast Q&A)

**Endpoint:** `POST https://api.parallel.ai/chat/completions`

**Use Cases:** Quick fact-checking, real-time data, competitive snapshots

**Input:**
```json
{
  "model": "speed",
  "messages": [
    {"role": "system", "content": "You are a research assistant."},
    {"role": "user", "content": "What is the latest funding round for Anthropic?"}
  ],
  "stream": false
}
```

**Output:** OpenAI-compatible chat completion with web citations

**Cost:** $0.005 per request

---

## 2. Deep Research (Reports)

**Endpoint:** `POST https://api.parallel.ai/v1/tasks/runs`

**Use Cases:** Market research, competitive analysis, due diligence

**Input:**
```json
{
  "processor": "ultra",
  "input": "Research the competitive landscape of AI code editors in 2025."
}
```

**Processor Selection:**
```
Simple question → lite/base
Cross-referenced facts → core
Exploratory research → pro
Comprehensive report → ultra
Impossible research → ultra4x/ultra8x
```

**Output:**
```json
{
  "run_id": "task_abc123",
  "status": "completed",
  "result": {
    "content": "# Competitive Landscape Report\n\n...",
    "basis": [
      {"title": "Source", "url": "https://...", "confidence": 0.95}
    ]
  }
}
```

**Result Retrieval:**
- Blocking: `GET /v1/tasks/runs/{run_id}/result`
- Streaming: `GET /v1beta/tasks/runs/{run_id}/events`

---

## 3. FindAll (Entity Discovery)

**Endpoint:** `POST https://api.parallel.ai/v1beta/findall/runs`

**Use Cases:** Find competitors, build lead lists, market sizing

### Step 1: Ingest Query
```json
POST /v1beta/findall/ingest
{
  "objective": "FindAll AI code editor companies that raised funding in 2024-2025"
}
```

### Step 2: Create Run
```json
POST /v1beta/findall/runs
{
  "entity_type": "AI code editor companies",
  "match_conditions": [...],
  "enrichments": [...],
  "generator": "core",
  "match_limit": 100
}
```

### Step 3: Retrieve Results
```json
GET /v1beta/findall/runs/{findall_id}/result
```

**Output:**
```json
{
  "matches": [
    {
      "name": "Cursor",
      "url": "https://cursor.sh",
      "match_status": "matched",
      "enrichments": {"funding_amount": "$8M Series A"}
    }
  ]
}
```

---

## 4. Enrich with Web Data

**Endpoint:** `POST https://api.parallel.ai/v1/tasks/runs`

**Use Cases:** Enrich CRM, update records, add web data to lists

**Input:**
```json
{
  "processor": "core",
  "input": "Company: Anthropic. Founded: 2021",
  "task_spec": {
    "output_schema": {
      "type": "object",
      "properties": {
        "latest_funding_round": {"type": "string"},
        "total_funding": {"type": "string"},
        "employee_count": {"type": "number"}
      }
    }
  }
}
```

---

## Processor Comparison

### Parallel AI Processors

| Processor | Speed | Depth | Cost | Best For |
|-----------|-------|-------|------|----------|
| `lite` | 5-10s | Basic | $0.01 | Quick facts |
| `base` | 10-20s | Good | $0.03 | Simple research |
| `core` | 15-30s | Good | $0.05 | Standard research |
| `pro` | 30-60s | Deep | $0.10 | Thorough analysis |
| `ultra` | 60-120s | Deepest | $0.25 | Comprehensive |
| `ultra4x` | 2-5min | Maximum | $1.00 | Impossible research |
| `ultra8x` | 5-10min | Maximum | $2.00 | Critical reports |

### When to Use Each
- **Quick lookups**: lite - simple facts, definitions
- **Standard research**: core - most use cases
- **Deep dives**: pro - competitive analysis, market research
- **Maximum depth**: ultra - investment decisions, critical reports
- **Impossible research**: ultra4x/ultra8x - when no other tier works

### FindAll vs Deep Research

| Feature | FindAll | Deep Research |
|---------|---------|---------------|
| Purpose | Discover entities | Analyze topics |
| Output | List of companies/people | Research report |
| Best for | Lead generation | Strategy |
| Endpoint | `/v1beta/findall/runs` | `/v1/tasks/runs` |

### Enrich vs Chat

| Feature | Enrich | Chat |
|---------|--------|------|
| Purpose | Add data to records | Answer questions |
| Input | Entity list + schema | Natural language |
| Output | Structured JSON | Conversational text |
| Best for | CRM enhancement | Ad-hoc queries |

## Rate Limits

- Chat: 300 req/min
- Task/FindAll: 2000 req/min

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid or missing API key | Verify `PARALLEL_API_KEY` in .env |
| `402 Payment Required` | Insufficient credits | Add credits at parallel.ai/billing |
| `429 Rate Limited` | Exceeded request limits | Wait `retry-after` seconds, implement backoff |
| `408 Request Timeout` | Research taking too long | Use lower processor tier or simpler query |
| `500 Internal Server Error` | Service temporarily unavailable | Retry after 30 seconds |
| `Task failed` | Research task could not complete | Check `result.error` for details |
| `Invalid processor` | Unknown processor tier specified | Use lite/base/core/pro/ultra/ultra4x/ultra8x |
| `FindAll exhausted` | No more matches found | Broaden search criteria or reduce `match_limit` |
| `Schema validation failed` | Output schema doesn't match result | Fix schema definition, use flexible types |

### Recovery Strategies

1. **Automatic retry**: Implement exponential backoff (5s, 10s, 20s) for rate limits and 500 errors
2. **Processor fallback**: If ultra times out, retry with pro; if pro fails, try core
3. **Polling with timeout**: For long research tasks, poll status with max 2hr timeout
4. **Cost protection**: Set budget limits and track credit usage per request
5. **Result caching**: Cache research results to avoid duplicate expensive queries
6. **Graceful degradation**: If FindAll fails, fall back to Chat API for entity discovery

## Testing Checklist

### Pre-flight
- [ ] `PARALLEL_API_KEY` set in `.env`
- [ ] Dependencies installed (`pip install requests python-dotenv`)
- [ ] Network connectivity to `api.parallel.ai`
- [ ] API key has sufficient credits

### Smoke Test

#### Chat API (Fast Q&A)
```bash
# Quick test with simple question
python scripts/parallel_research.py chat "What year was OpenAI founded?"
```

#### Deep Research (Task API)
```bash
# Test with lite processor (fastest/cheapest)
python scripts/parallel_research.py research "Summarize Anthropic's products" --processor lite

# Test with core processor
python scripts/parallel_research.py research "Competitive landscape of AI assistants" --processor core
```

#### FindAll (Entity Discovery)
```bash
# Test finding companies
python scripts/parallel_research.py findall "AI code editors" --limit 5
```

### Validation

#### Chat API
- [ ] Response contains `choices[0].message.content`
- [ ] Web citations included in response
- [ ] Response time under 5 seconds
- [ ] Cost: ~$0.005 per request

#### Task/Research API
- [ ] `run_id` returned from POST request
- [ ] Status polling shows `completed` eventually
- [ ] `result.content` contains markdown report
- [ ] `result.basis` contains source URLs with confidence scores
- [ ] Processor tier affects response time and depth

#### FindAll API
- [ ] `matches` array returned with entities
- [ ] Each match has `name`, `url`, `match_status`
- [ ] `enrichments` contain requested data fields
- [ ] `match_limit` is respected

#### Error Cases
- [ ] 401 returns meaningful auth error
- [ ] 429 returns rate limit info (retry-after)
- [ ] Timeouts handled gracefully for long research tasks
