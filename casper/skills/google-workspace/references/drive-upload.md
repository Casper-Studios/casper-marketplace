# Google Drive Upload

## Overview
Upload files to Google Drive with auto-folder creation and sharing.

## Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `files` | list | required | Files to upload |
| `folder` | string | required | Destination folder path |
| `share` | string | - | "anyone" for public link |
| `auto_create` | bool | true | Create folders if missing |

## CLI Usage

```bash
# Upload single file
python scripts/google_drive_upload.py --file report.pdf --folder "Clients/Acme"

# Upload multiple files
python scripts/google_drive_upload.py --files *.png --folder "Clients/Acme/Assets"

# Upload with sharing
python scripts/google_drive_upload.py --file doc.pdf --folder "Reports" --share anyone

# Create folders only
python scripts/google_drive_upload.py --create-folders "Clients/NewClient/Assets"
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

### Upload a Single File
```python
# Create file in folder
folder_id = "1abc123xyz"
file = drive.CreateFile({
    'title': 'thumbnail.png',
    'parents': [{'id': folder_id}]
})
file.SetContentFile('local_file.png')
file.Upload()

print(f"Uploaded: {file['title']} - {file['id']}")
print(f"View: {file['alternateLink']}")
```

### Upload with Auto-Detected MIME Type
```python
import mimetypes

def upload_file(drive, local_path, folder_id, title=None):
    """Upload file with automatic MIME type detection."""
    mime_type, _ = mimetypes.guess_type(local_path)

    file = drive.CreateFile({
        'title': title or local_path.split('/')[-1],
        'parents': [{'id': folder_id}],
        'mimeType': mime_type
    })
    file.SetContentFile(local_path)
    file.Upload()
    return file

# Usage
uploaded = upload_file(drive, 'report.pdf', folder_id)
```

### Upload Multiple Files
```python
from pathlib import Path

def upload_multiple(drive, file_paths, folder_id):
    """Upload multiple files to a folder."""
    uploaded_files = []
    for path in file_paths:
        file = drive.CreateFile({
            'title': Path(path).name,
            'parents': [{'id': folder_id}]
        })
        file.SetContentFile(str(path))
        file.Upload()
        uploaded_files.append({
            'title': file['title'],
            'id': file['id'],
            'link': file['alternateLink']
        })
    return uploaded_files

# Usage
files = ['image1.png', 'image2.png', 'doc.pdf']
results = upload_multiple(drive, files, folder_id)
```

### Share File Publicly
```python
# Share file with anyone (view only)
file.InsertPermission({
    'type': 'anyone',
    'value': 'anyone',
    'role': 'reader'
})
public_link = file['alternateLink']

# Share with edit access
file.InsertPermission({
    'type': 'anyone',
    'value': 'anyone',
    'role': 'writer'
})
```

### Share with Specific Users
```python
# Share with a specific email
file.InsertPermission({
    'type': 'user',
    'value': 'colleague@example.com',
    'role': 'writer'  # or 'reader', 'commenter'
})

# Share with a domain
file.InsertPermission({
    'type': 'domain',
    'value': 'company.com',
    'role': 'reader'
})
```

### Upload and Convert to Google Format
```python
# Upload Word doc and convert to Google Doc
file = drive.CreateFile({
    'title': 'Document',
    'parents': [{'id': folder_id}],
    'mimeType': 'application/vnd.google-apps.document'  # Target format
})
file.SetContentFile('document.docx')
file.Upload({'convert': True})

# Conversion MIME types:
# Word -> Google Doc: application/vnd.google-apps.document
# Excel -> Google Sheet: application/vnd.google-apps.spreadsheet
# PowerPoint -> Google Slides: application/vnd.google-apps.presentation
```

### Update Existing File
```python
# Update content of existing file
existing_file = drive.CreateFile({'id': 'existing_file_id'})
existing_file.SetContentFile('updated_content.pdf')
existing_file.Upload()
```

### Resumable Upload for Large Files
```python
# For files > 5MB, PyDrive2 automatically uses resumable upload
# To explicitly control chunk size:
from pydrive2.files import GoogleDriveFile

file = drive.CreateFile({
    'title': 'large_video.mp4',
    'parents': [{'id': folder_id}]
})
file.SetContentFile('large_video.mp4')
file.Upload(param={'uploadType': 'resumable'})
```

### OAuth Troubleshooting

1. **Token refresh fails**: Delete `mycreds.txt` and re-authenticate
2. **settings.yaml missing**: Create from template with OAuth settings
3. **Quota exceeded**: Wait 24h or use different project
4. **Upload fails mid-way**: Use resumable upload for automatic retry
5. **Permission denied on folder**: Verify you have edit access to target folder

```python
# Robust upload with error handling
def safe_upload(drive, local_path, folder_id, max_retries=3):
    """Upload with retry logic."""
    import time

    for attempt in range(max_retries):
        try:
            file = drive.CreateFile({
                'title': Path(local_path).name,
                'parents': [{'id': folder_id}]
            })
            file.SetContentFile(str(local_path))
            file.Upload()
            return file
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise e
```

## Output Structure

```json
{
  "file_id": "1abc123",
  "web_view_link": "https://drive.google.com/file/d/...",
  "folder_ids": ["parent_id", "child_id"]
}
```

## Rate Limits
- 1000 requests per 100 seconds per user
- Resumable uploads for files > 5MB

## Testing Checklist

### Pre-flight
- [ ] OAuth credentials file exists (`mycreds.txt` or `credentials.json`)
- [ ] Google Drive API enabled in Google Cloud Console
- [ ] Dependencies installed (`pip install pydrive2 python-dotenv`)
- [ ] First-time OAuth flow completed (browser auth)
- [ ] Test file exists locally for upload

### Smoke Test
```bash
# Upload a test file
python scripts/google_drive_upload.py --file test.txt --folder "Test"

# Upload with sharing
python scripts/google_drive_upload.py --file test.pdf --folder "Test/Public" --share anyone

# Create folders only (no file upload)
python scripts/google_drive_upload.py --create-folders "Test/NewFolder/SubFolder"
```

### Validation
- [ ] Response contains `file_id` and `web_view_link`
- [ ] File appears in correct Drive folder
- [ ] `web_view_link` is accessible
- [ ] `--share anyone` creates public link
- [ ] `--auto-create` creates missing parent folders
- [ ] Multiple file upload works (`--files *.png`)
- [ ] Large files (>5MB) use resumable upload
- [ ] File permissions match requested sharing settings
- [ ] Duplicate uploads update existing files (or create new versions)

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `Invalid credentials` | OAuth token expired or invalid | Delete `mycreds.txt`, re-authenticate |
| `File not found` (local) | Source file doesn't exist | Verify file path before upload |
| `Folder not found` | Target folder doesn't exist | Use `--auto-create` or create folder first |
| `403 Forbidden` | No write access to folder | Request edit access from folder owner |
| `413 Request Entity Too Large` | File exceeds 5TB limit | Split file or use alternative storage |
| `Quota exceeded` | Storage quota full or API rate limited | Free up space or wait for rate limit reset |
| `Upload interrupted` | Network failure during upload | Resumable upload auto-retries, or restart |
| `Invalid MIME type` | Unsupported file format | Check file extension, convert if needed |
| `Sharing failed` | Cannot share to specified users | Verify email addresses and domain policies |

### Recovery Strategies

1. **Resumable uploads**: Use resumable upload for files >5MB to handle network interruptions
2. **Retry with backoff**: Implement exponential backoff (1s, 2s, 4s) for transient failures
3. **Pre-flight validation**: Verify local file exists and folder access before upload
4. **Batch uploads**: Process multiple files in chunks to avoid timeouts
5. **Progress tracking**: Log upload progress for large files to enable recovery

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
