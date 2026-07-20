# Google Drive Search

## Overview
Search Google Drive for client folders and documents. Read-only operations.

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_name` | string | Yes | Client name to search |
| `query` | string | No | File name search query |
| `folder_id` | string | No | Specific folder to search in |
| `file_types` | list | No | Filter by type (doc, sheet, slide, pdf) |
| `modified_days` | int | No | Files modified in last N days |

## CLI Usage

```bash
# Find client folder
python scripts/gdrive_search.py folder "Microsoft"

# Search for files
python scripts/gdrive_search.py files "proposal" --modified-days 30

# Search in specific folder
python scripts/gdrive_search.py files "transcript" --in-folder "1abc123"

# Filter by file type
python scripts/gdrive_search.py files "report" --type doc sheet

# List folder contents
python scripts/gdrive_search.py list "1abc123" --recursive

# Full client document search
python scripts/gdrive_search.py client "Kit" --days 30
```

## Output Structure

### Client Folder Search
```json
{
  "id": "1YNgzp4W17samDTCXcWWccDwOmloh4Fk-",
  "title": "[26] Kit",
  "number": 26,
  "webViewLink": "https://drive.google.com/drive/folders/..."
}
```

### File Search
```json
[
  {
    "id": "1abc123",
    "title": "Casper Studios - Partner Agreement - Kit",
    "mimeType": "application/vnd.google-apps.document",
    "webViewLink": "https://docs.google.com/document/d/...",
    "modifiedDate": "2025-12-20",
    "fileSize": ""
  }
]
```

## Client Folder Pattern

Numbered client folders: `[XX] Client Name`
```
[XX] Client Name
├── [1] Admin
└── [2] Discovery
    ├── [1] Reference/Data
    ├── [2] Interviews
    ├── [3] Meeting Transcripts
    └── [4] Functional Read Out
```

## Python Usage

### Basic Setup
```python
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# Initialize with saved credentials
gauth = GoogleAuth()
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
gauth.SaveCredentialsFile("mycreds.txt")

drive = GoogleDrive(gauth)
```

### Search for Files by Name
```python
# Search for files containing 'Report' in title
file_list = drive.ListFile({
    'q': "title contains 'Report' and trashed=false"
}).GetList()

for file in file_list:
    print(f"{file['title']} - {file['id']}")
```

### Search with Multiple Conditions
```python
# Search for Google Docs modified in last 30 days
from datetime import datetime, timedelta

cutoff = (datetime.now() - timedelta(days=30)).isoformat() + "Z"
file_list = drive.ListFile({
    'q': f"mimeType='application/vnd.google-apps.document' and modifiedDate > '{cutoff}' and trashed=false"
}).GetList()
```

### Search Within a Folder
```python
# List files in a specific folder
folder_id = "1YNgzp4W17samDTCXcWWccDwOmloh4Fk-"
file_list = drive.ListFile({
    'q': f"'{folder_id}' in parents and trashed=false"
}).GetList()

for file in file_list:
    print(f"{file['title']} ({file['mimeType']})")
```

### Search for Client Folders by Pattern
```python
# Find numbered client folders like [XX] Client Name
import re

all_folders = drive.ListFile({
    'q': "mimeType='application/vnd.google-apps.folder' and trashed=false"
}).GetList()

client_pattern = re.compile(r'^\[(\d+)\]\s+(.+)$')
for folder in all_folders:
    match = client_pattern.match(folder['title'])
    if match:
        number, name = match.groups()
        print(f"Client #{number}: {name} - {folder['id']}")
```

### Recursive Folder Navigation
```python
def list_folder_recursive(drive, folder_id, indent=0):
    """Recursively list folder contents."""
    files = drive.ListFile({
        'q': f"'{folder_id}' in parents and trashed=false"
    }).GetList()

    for file in files:
        prefix = "  " * indent
        print(f"{prefix}{file['title']}")

        if file['mimeType'] == 'application/vnd.google-apps.folder':
            list_folder_recursive(drive, file['id'], indent + 1)

# Usage
list_folder_recursive(drive, "root_folder_id")
```

### Query Syntax Reference
```python
# Common query patterns for ListFile
queries = {
    # By title
    "exact_title": "title = 'Exact Name'",
    "contains": "title contains 'keyword'",

    # By type
    "folders_only": "mimeType = 'application/vnd.google-apps.folder'",
    "docs_only": "mimeType = 'application/vnd.google-apps.document'",
    "sheets_only": "mimeType = 'application/vnd.google-apps.spreadsheet'",
    "slides_only": "mimeType = 'application/vnd.google-apps.presentation'",
    "pdfs_only": "mimeType = 'application/pdf'",

    # By location
    "in_folder": "'folder_id' in parents",
    "in_root": "'root' in parents",

    # By date
    "modified_after": "modifiedDate > '2025-01-01T00:00:00'",
    "created_after": "createdDate > '2025-01-01T00:00:00'",

    # Combined
    "recent_docs": "mimeType = 'application/vnd.google-apps.document' and modifiedDate > '2025-01-01'",
    "folder_search": "title contains 'Client' and mimeType = 'application/vnd.google-apps.folder'",
}
```

### OAuth Troubleshooting

1. **Token refresh fails**: Delete `mycreds.txt` and re-authenticate
2. **settings.yaml missing**: Create from template with OAuth settings
3. **Quota exceeded**: Wait 24h or use different project
4. **"Access denied" error**: Ensure Google Drive API is enabled in Cloud Console
5. **Credentials expired during long operation**: Wrap operations in try/except and refresh

```python
# Robust credential handling
def get_drive_client():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("mycreds.txt")

    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        try:
            gauth.Refresh()
        except:
            gauth.LocalWebserverAuth()

    gauth.SaveCredentialsFile("mycreds.txt")
    return GoogleDrive(gauth)
```

## API Used
Google Drive API v2 via PyDrive2

## Testing Checklist

### Pre-flight
- [ ] OAuth credentials file exists (`mycreds.txt` or `credentials.json`)
- [ ] Google Drive API enabled in Google Cloud Console
- [ ] Dependencies installed (`pip install pydrive2 python-dotenv`)
- [ ] First-time OAuth flow completed (browser auth)

### Smoke Test
```bash
# Search for a known client folder
python scripts/gdrive_search.py folder "Microsoft"

# Search for files in root
python scripts/gdrive_search.py files "report" --modified-days 30

# List contents of a known folder
python scripts/gdrive_search.py list "1abc123" --recursive

# Full client document search
python scripts/gdrive_search.py client "Kit" --days 30
```

### Validation
- [ ] Folder search returns valid `id` and `webViewLink`
- [ ] Client folder pattern `[XX] Client Name` detected correctly
- [ ] File search returns `title`, `mimeType`, `modifiedDate`
- [ ] `--type` filter works (doc, sheet, slide, pdf)
- [ ] `--modified-days` correctly filters recent files
- [ ] `--recursive` lists nested folder contents
- [ ] `webViewLink` URLs are accessible
- [ ] OAuth token refreshes automatically when expired

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `Invalid credentials` | OAuth token expired or invalid | Delete `mycreds.txt`, re-authenticate |
| `File not found` | File was deleted or moved | Verify file ID, search by name |
| `Folder not found` | Folder doesn't exist or no access | Check folder ID and sharing permissions |
| `403 Forbidden` | Insufficient permissions | Request access from file owner |
| `404 Not Found` | Invalid file/folder ID | Verify ID format and existence |
| `Quota exceeded` | API rate limit reached | Wait 1 minute, implement exponential backoff |
| `Invalid query` | Malformed search query | Check query syntax, escape special characters |
| `Shared drive access denied` | No access to shared drive | Request membership from drive admin |

### Recovery Strategies

1. **Automatic token refresh**: PyDrive2 handles token refresh automatically if `mycreds.txt` exists
2. **Graceful degradation**: If specific file fails, continue with other search results
3. **Retry with backoff**: Implement exponential backoff (1s, 2s, 4s) for quota errors
4. **Cache folder IDs**: Cache frequently accessed folder IDs to reduce API calls
5. **Pagination**: Use page tokens for large result sets to avoid timeouts

## Performance Tips

### Batch Operations
- Use `batch_update` for multiple file operations
- Group requests to reduce API calls
- Max 100 operations per batch request

### Caching
- Cache folder IDs (they don't change)
- Cache file metadata for repeated access
- Use ETags for conditional requests

### Query Optimization
- Use specific fields in query (not '*')
- Add `trashed=false` to exclude deleted items
- Use `pageSize=100` for listing (max 1000)

### Large File Handling
- Use resumable uploads for files >5MB
- Implement chunk upload with progress
- Handle network interruptions gracefully
