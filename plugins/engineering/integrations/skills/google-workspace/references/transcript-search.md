# Google Drive Transcript Search

## Overview
Search Google Drive for meeting transcript files (uploaded from Fireflies or other sources).

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_name` | string | Yes | Client name to search |
| `days` | int | No | Days back to search (default: 90) |
| `keywords` | list | No | Additional keywords |

## CLI Usage

```bash
# Search client transcripts
python scripts/gdrive_transcript_search.py "Microsoft" --days 30

# With keywords
python scripts/gdrive_transcript_search.py "Acme" --keywords "discovery" "proposal"
```

## Output Structure

```json
{
  "client": "Microsoft",
  "transcripts": [
    {
      "id": "1abc123",
      "title": "Microsoft - Discovery Call - 2025-12-20",
      "webViewLink": "https://docs.google.com/document/d/...",
      "modifiedDate": "2025-12-20",
      "folder": "[2] Discovery/[3] Meeting Transcripts"
    }
  ],
  "count": 3
}
```

## Search Logic

1. Find client folder by name pattern
2. Navigate to Discovery > Meeting Transcripts
3. List all documents in folder
4. Filter by date and keywords
5. Return sorted by date (newest first)

## Related
- `fireflies_transcript_search.md` - Search Fireflies API directly
