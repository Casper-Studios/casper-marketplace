# Google Drive Transcript Search

## Overview
Search for meeting transcript files stored in Google Drive (uploaded from Fireflies or other sources).

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_name` | string | Yes | Client name to search |
| `days` | int | No | Days back (default: 90) |
| `keywords` | list | No | Additional keywords |

## CLI Usage

```bash
# Search client transcripts
python scripts/gdrive_transcript_search.py "Microsoft" --days 30

# With keywords
python scripts/gdrive_transcript_search.py "Acme" --keywords "discovery" "proposal"
```

## Search Logic

1. Find client folder by name pattern `[XX] Client Name`
2. Navigate to `Discovery` > `Meeting Transcripts`
3. List all documents in folder
4. Filter by date and keywords
5. Return sorted by date (newest first)

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

## Client Folder Structure

```
[XX] Client Name
├── [1] Admin
└── [2] Discovery
    ├── [1] Reference/Data
    ├── [2] Interviews
    ├── [3] Meeting Transcripts  ← Search here
    └── [4] Functional Read Out
```

## When to Use Each

| Scenario | Use |
|----------|-----|
| Recent meetings (auto-transcribed) | Fireflies API |
| Archived/uploaded transcripts | Drive search |
| Need AI summary | Fireflies API |
| Need raw document | Drive search |

## Related
- `fireflies_transcript_search.md` - Fireflies API search
- `google-workspace` skill - Drive operations

## Testing Checklist

### Pre-flight
- [ ] Google Drive OAuth credentials available (`mycreds.txt`)
- [ ] Dependencies installed (`pip install pydrive2 python-dotenv`)
- [ ] Client folder exists in Drive with proper structure
- [ ] `Meeting Transcripts` subfolder contains at least one document

### Smoke Test
```bash
# Search for transcripts from a known client
python scripts/gdrive_transcript_search.py "Microsoft" --days 90

# Search with keywords
python scripts/gdrive_transcript_search.py "Acme" --keywords "discovery" "proposal"

# Search with shorter date range
python scripts/gdrive_transcript_search.py "Client" --days 30
```

### Validation
- [ ] Response contains `client`, `transcripts`, `count` fields
- [ ] Each transcript has `id`, `title`, `webViewLink`, `modifiedDate`, `folder`
- [ ] `webViewLink` opens document in Google Docs
- [ ] Results sorted by date (newest first)
- [ ] `--days` filter correctly limits results
- [ ] `--keywords` filter matches document titles
- [ ] Client folder pattern `[XX] Client Name` detected correctly
- [ ] Subfolder path `[2] Discovery/[3] Meeting Transcripts` navigated correctly
- [ ] No results returns empty `transcripts` array (not error)
- [ ] Invalid client name returns meaningful message

### Folder Structure Verification
```bash
# Verify client folder exists and has correct structure
python scripts/gdrive_search.py folder "ClientName"
python scripts/gdrive_search.py list "CLIENT_FOLDER_ID" --recursive
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `Invalid credentials` | OAuth token expired or invalid | Delete `mycreds.txt`, re-authenticate |
| `Client folder not found` | No folder matches `[XX] Client Name` pattern | Verify client name spelling, check folder exists |
| `Meeting Transcripts folder not found` | Folder structure incomplete | Create missing subfolder or check path |
| `403 Forbidden` | No access to client folder | Request sharing permissions |
| `Quota exceeded` | Drive API rate limit | Wait 1 minute, implement backoff |
| `No transcripts found` | Folder empty or wrong date range | Extend `--days` parameter or check folder contents |
| `Invalid document` | File is not a Google Doc | Filter for Google Docs mime type only |

### Recovery Strategies

1. **Automatic token refresh**: PyDrive2 handles token refresh automatically
2. **Folder path verification**: Check each folder in path exists before searching
3. **Flexible pattern matching**: Support variations in folder naming (case-insensitive)
4. **Graceful fallback**: If specific subfolder not found, search entire client folder
5. **Retry with backoff**: Implement exponential backoff (1s, 2s, 4s) for quota errors
6. **Alternative search**: If folder navigation fails, use Drive search API with query
