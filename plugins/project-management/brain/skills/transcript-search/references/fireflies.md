# Fireflies Transcript Search

## API
GraphQL API at `https://api.fireflies.ai/graphql`

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `keyword` | string | No* | Search term (company, topic) |
| `transcript_id` | string | No* | Specific transcript ID |
| `from_date` | string | No | Start date (YYYY-MM-DD) |
| `to_date` | string | No | End date |
| `days_back` | int | No | Search last N days |
| `limit` | int | No | Max results (default: 10, max: 50) |
| `include_content` | bool | No | Include full sentences |

*Either `keyword` or `transcript_id` required.

## CLI Usage

```bash
# Search by company/keyword (searches title)
python scripts/fireflies_transcript_search.py "Microsoft"

# Get specific transcript
python scripts/fireflies_transcript_search.py --id 01KCM2G0YX1GMPWYQ8GPAABBCK

# Include full transcript
python scripts/fireflies_transcript_search.py --id abc123 --content

# Save to file
python scripts/fireflies_transcript_search.py --id abc123 --content --save meeting.md

# Search date range
python scripts/fireflies_transcript_search.py "Client" --days-back 30

# Verbose output (shows summary)
python scripts/fireflies_transcript_search.py "Client" -v

# JSON output
python scripts/fireflies_transcript_search.py "Company" --json
```

## Python Usage

```python
from fireflies_transcript_search import (
    fireflies_transcript_search,
    search_by_company,
    get_transcript,
    get_transcript_text
)

# Search by keyword
result = fireflies_transcript_search(keyword="Microsoft", days_back=90, limit=10)
for t in result["transcripts"]:
    print(f"{t['title']} - {t['date']}")

# Convenience function
transcripts = search_by_company("Acme Corp", days_back=60)

# Get full transcript
transcript = get_transcript("abc123", include_sentences=True)
print(transcript["summary"]["overview"])

# Get formatted text with speaker labels
text = get_transcript_text("abc123")
print(text)
```

## Output Structure

### Search Results
```json
{
  "transcripts": [
    {
      "id": "01KCM2G0YX1GMPWYQ8GPAABBCK",
      "title": "Discovery Call - Microsoft",
      "date": 1765917000000,
      "duration": 1800,
      "host_email": "host@company.com",
      "transcript_url": "https://app.fireflies.ai/view/...",
      "speakers": [{"id": 0, "name": "Giorgio Barilla"}],
      "summary": {
        "overview": "Discussion about AI automation...",
        "keywords": ["automation", "AI", "workflow"],
        "action_items": ["Send proposal", "Schedule follow-up"]
      }
    }
  ]
}
```

### Full Transcript
```json
{
  "sentences": [
    {
      "index": 0,
      "speaker_name": "Todd Sparks",
      "speaker_id": 0,
      "text": "Thanks for joining today.",
      "start_time": 0.08,
      "end_time": 1.92
    }
  ]
}
```

### Formatted Text
```markdown
**Todd Sparks:**
Thanks for joining today.
This meeting is being recorded.

**Giorgio Barilla:**
Thanks for having me.
```

## Available Fields

### Summary Fields
- `id`, `title`, `date`, `duration`
- `host_email`, `organizer_email`
- `transcript_url`, `audio_url`, `video_url`
- `participants`, `speakers`

### Content Fields (with --content)
- `sentences` - Full transcript with speaker attribution
  - `speaker_name`, `text`, `start_time`, `end_time`

### AI Summary
- `summary.overview` - Meeting summary
- `summary.keywords` - Key topics
- `summary.action_items` - Extracted actions

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `FIREFLIES_API_KEY not found` | Missing env variable | Add `FIREFLIES_API_KEY` to .env |
| `401 Unauthorized` | Invalid API key | Verify key in Fireflies settings |
| `404 Transcript not found` | Invalid transcript ID | Verify ID exists, may have been deleted |
| `429 Rate Limited` | Too many requests | Wait and retry with exponential backoff |
| `No transcripts found` | Search returned no results | Broaden search terms, extend date range |
| `GraphQL error` | Malformed query | Check query syntax, update to latest API |
| `Timeout` | Request took too long | Retry, reduce date range or limit |
| `AI summary unavailable` | Transcript not yet processed | Wait for Fireflies to complete processing |
| `Sentences not available` | Content not included in query | Use `include_content=True` flag |

### Recovery Strategies

1. **Automatic retry**: Implement exponential backoff (1s, 2s, 4s) for rate limits
2. **Graceful degradation**: If AI summary unavailable, return transcript without summary
3. **Search fallback**: If specific search fails, try broader search terms
4. **Pagination**: For many results, implement pagination to avoid timeouts
5. **Caching**: Cache transcript data to avoid repeated API calls
6. **Date range chunking**: For large date ranges, search in chunks (30 days at a time)

## Testing Checklist

### Pre-flight
- [ ] `FIREFLIES_API_KEY` set in `.env`
- [ ] Dependencies installed (`pip install requests python-dotenv`)
- [ ] Network connectivity to `api.fireflies.ai`
- [ ] At least one transcript exists in Fireflies account

### Smoke Test
```bash
# Search by keyword (any recent meeting)
python scripts/fireflies_transcript_search.py "meeting" --days-back 30

# Search for specific company
python scripts/fireflies_transcript_search.py "Microsoft"

# Get specific transcript by ID (use ID from search results)
python scripts/fireflies_transcript_search.py --id "YOUR_TRANSCRIPT_ID"

# Get full transcript content
python scripts/fireflies_transcript_search.py --id "YOUR_TRANSCRIPT_ID" --content

# Verbose output with summary
python scripts/fireflies_transcript_search.py "Client" -v

# JSON output for parsing
python scripts/fireflies_transcript_search.py "Company" --json

# Save transcript to file
python scripts/fireflies_transcript_search.py --id "YOUR_TRANSCRIPT_ID" --content --save meeting.md
```

### Validation
- [ ] Search returns `transcripts` array with results
- [ ] Each transcript has `id`, `title`, `date`, `duration`, `transcript_url`
- [ ] `speakers` array lists meeting participants
- [ ] `summary.overview` provides meeting summary (if AI enabled)
- [ ] `summary.action_items` extracts action items
- [ ] `--content` flag includes `sentences` array
- [ ] Each sentence has `speaker_name`, `text`, `start_time`, `end_time`
- [ ] Formatted text output includes speaker labels
- [ ] `--days-back` filter works correctly
- [ ] `--save` creates markdown file at specified path
- [ ] `--json` output is valid JSON
- [ ] 401 error returned for invalid API key
- [ ] Transcript not found error for invalid ID
