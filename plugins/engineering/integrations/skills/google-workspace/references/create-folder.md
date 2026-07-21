# Create Client Folder

## Overview
Create standardized client folder structure in shared drive.

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_name` | string | Yes | Client/company name |
| `template` | string | No | Template type (default, minimal) |

## CLI Usage

```bash
# Create with default template
python scripts/create_client_folder.py "Acme Corporation"

# Minimal structure
python scripts/create_client_folder.py "NewClient" --template minimal
```

## Default Folder Structure

```
[XX] Client Name
├── [1] Admin
│   ├── Contracts
│   └── Invoices
└── [2] Discovery
    ├── [1] Reference/Data
    ├── [2] Interviews
    │   ├── [1] Leads
    │   └── [2] Team
    ├── [3] Meeting Transcripts
    └── [4] Functional Read Out
```

## Output Structure

```json
{
  "client_folder_id": "1abc123",
  "client_folder_url": "https://drive.google.com/drive/folders/...",
  "folder_number": 27,
  "created_subfolders": [
    {"path": "[1] Admin", "id": "..."},
    {"path": "[2] Discovery", "id": "..."}
  ]
}
```

## Folder Numbering
Auto-increments based on highest existing client number.

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

### Create a Single Folder
```python
# Create folder with folder MIME type
folder = drive.CreateFile({
    'title': 'New Folder',
    'mimeType': 'application/vnd.google-apps.folder'
})
folder.Upload()

print(f"Created folder: {folder['title']} - {folder['id']}")
print(f"Link: {folder['alternateLink']}")
```

### Create Folder in Specific Parent
```python
# Create folder inside another folder
parent_folder_id = "1abc123xyz"

folder = drive.CreateFile({
    'title': 'Subfolder',
    'mimeType': 'application/vnd.google-apps.folder',
    'parents': [{'id': parent_folder_id}]
})
folder.Upload()
```

### Create Numbered Client Folder
```python
import re

def create_client_folder(drive, client_name, parent_id=None):
    """Create a numbered client folder [XX] Client Name."""

    # Find existing client folders to get next number
    query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    folders = drive.ListFile({'q': query}).GetList()

    # Extract existing numbers
    pattern = re.compile(r'^\[(\d+)\]')
    max_number = 0
    for folder in folders:
        match = pattern.match(folder['title'])
        if match:
            max_number = max(max_number, int(match.group(1)))

    # Create new folder with next number
    new_number = max_number + 1
    folder_title = f"[{new_number}] {client_name}"

    folder_metadata = {
        'title': folder_title,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        folder_metadata['parents'] = [{'id': parent_id}]

    folder = drive.CreateFile(folder_metadata)
    folder.Upload()

    return {
        'folder_id': folder['id'],
        'folder_url': folder['alternateLink'],
        'folder_number': new_number,
        'title': folder_title
    }

# Usage
result = create_client_folder(drive, "Acme Corporation", parent_folder_id)
print(f"Created: {result['title']}")
```

### Create Full Client Folder Structure
```python
def create_client_structure(drive, client_name, parent_id=None, template='default'):
    """Create complete client folder with standard subfolders."""

    # Define templates
    templates = {
        'default': {
            '[1] Admin': {
                'Contracts': {},
                'Invoices': {}
            },
            '[2] Discovery': {
                '[1] Reference/Data': {},
                '[2] Interviews': {
                    '[1] Leads': {},
                    '[2] Team': {}
                },
                '[3] Meeting Transcripts': {},
                '[4] Functional Read Out': {}
            }
        },
        'minimal': {
            'Admin': {},
            'Documents': {},
            'Assets': {}
        }
    }

    structure = templates.get(template, templates['default'])

    # Create main client folder
    client_result = create_client_folder(drive, client_name, parent_id)
    client_folder_id = client_result['folder_id']

    # Create subfolders recursively
    created_subfolders = []

    def create_subfolders(struct, parent):
        for name, children in struct.items():
            subfolder = drive.CreateFile({
                'title': name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [{'id': parent}]
            })
            subfolder.Upload()
            created_subfolders.append({
                'path': name,
                'id': subfolder['id']
            })

            if children:
                create_subfolders(children, subfolder['id'])

    create_subfolders(structure, client_folder_id)

    return {
        'client_folder_id': client_folder_id,
        'client_folder_url': client_result['folder_url'],
        'folder_number': client_result['folder_number'],
        'created_subfolders': created_subfolders
    }

# Usage
result = create_client_structure(drive, "New Client Inc", parent_id, template='default')
```

### Check if Folder Exists
```python
def folder_exists(drive, folder_name, parent_id=None):
    """Check if a folder with given name exists."""
    query = f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = drive.ListFile({'q': query}).GetList()
    return results[0] if results else None

# Usage
existing = folder_exists(drive, "[5] Acme", parent_folder_id)
if existing:
    print(f"Folder already exists: {existing['id']}")
```

### Create Folder Idempotently
```python
def ensure_folder(drive, folder_name, parent_id=None):
    """Create folder if it doesn't exist, return existing if it does."""
    existing = folder_exists(drive, folder_name, parent_id)
    if existing:
        return existing

    folder_metadata = {
        'title': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        folder_metadata['parents'] = [{'id': parent_id}]

    folder = drive.CreateFile(folder_metadata)
    folder.Upload()
    return folder

# Usage
folder = ensure_folder(drive, "Assets", parent_folder_id)
```

### Set Folder Color (via API)
```python
# Note: PyDrive2 doesn't directly support folder colors
# Use the Google API client for advanced features
from googleapiclient.discovery import build

def set_folder_color(folder_id, color_rgb):
    """Set folder color using Drive API v3."""
    service = build('drive', 'v3', credentials=gauth.credentials)
    service.files().update(
        fileId=folder_id,
        body={'folderColorRgb': color_rgb}
    ).execute()

# Usage (hex color without #)
# set_folder_color(folder_id, "4986e7")  # Blue
```

### OAuth Troubleshooting

1. **Token refresh fails**: Delete `mycreds.txt` and re-authenticate
2. **settings.yaml missing**: Create from template with OAuth settings
3. **Quota exceeded**: Wait 24h or use different project
4. **"Folder not found" for parent**: Verify parent_id is valid and accessible
5. **Duplicate folders created**: Use idempotent `ensure_folder()` function

## Testing Checklist

### Pre-flight
- [ ] OAuth credentials file exists (`mycreds.txt` or `credentials.json`)
- [ ] Google Drive API enabled in Google Cloud Console
- [ ] Dependencies installed (`pip install pydrive2 python-dotenv`)
- [ ] First-time OAuth flow completed (browser auth)
- [ ] Access to shared drive where client folders are stored

### Smoke Test
```bash
# Create test client folder (use unique name)
python scripts/create_client_folder.py "Test Client $(date +%s)"

# Create with minimal template
python scripts/create_client_folder.py "Minimal Test $(date +%s)" --template minimal
```

### Validation
- [ ] Response contains `client_folder_id` and `client_folder_url`
- [ ] Folder number auto-incremented correctly (`[XX]` prefix)
- [ ] Default subfolders created: `[1] Admin`, `[2] Discovery`
- [ ] Nested subfolders created: `[1] Reference/Data`, `[2] Interviews`, etc.
- [ ] `client_folder_url` opens in browser
- [ ] Minimal template creates fewer subfolders
- [ ] Duplicate client names handled gracefully
- [ ] Folder permissions match shared drive settings

### Cleanup
```bash
# Move test folders to trash manually in Google Drive
# Or: python scripts/gdrive_delete.py "Test Client..."
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `Invalid credentials` | OAuth token expired or invalid | Delete `mycreds.txt`, re-authenticate |
| `403 Forbidden` | No write access to shared drive | Request edit access from drive admin |
| `Quota exceeded` | API rate limit reached | Wait 1 minute, retry with backoff |
| `Client already exists` | Folder with client name exists | Return existing folder or append suffix |
| `Invalid client name` | Name contains forbidden characters | Remove special characters from name |
| `Shared drive not found` | Cannot access target shared drive | Verify drive ID and membership |
| `Number sequence error` | Cannot determine next client number | Manually check existing numbering |
| `Template not found` | Invalid template name | Use 'default' or 'minimal' template |

### Recovery Strategies

1. **Idempotent design**: Check for existing client folder before creating
2. **Number collision handling**: If number exists, find next available number
3. **Atomic subfolder creation**: Create subfolders in order for resume capability
4. **Validation first**: Validate client name and template before API calls
5. **Partial success handling**: Return created folder ID even if subfolders fail
