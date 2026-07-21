# Google Drive Folder Structure

## Overview
Auto-generate nested folder structures in Google Drive.

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `structure` | dict/JSON | Yes | Folder hierarchy |
| `parent_id` | string | No | Parent folder ID |
| `parent_path` | string | No | Parent folder path |

## CLI Usage

```bash
# Using JSON structure
python scripts/gdrive_folder_structure.py --structure '{
  "Project": {
    "Assets": {},
    "Deliverables": {}
  }
}'

# Using structure file
python scripts/gdrive_folder_structure.py --file structure.json

# Create in specific parent
python scripts/gdrive_folder_structure.py --structure '{"Project": {}}' --parent-path "Clients/Acme"
```

## Structure Format

```json
{
  "Project Alpha": {
    "Assets": {
      "Images": {},
      "Videos": {}
    },
    "Deliverables": {
      "Draft": {},
      "Final": {}
    }
  }
}
```

## Common Templates

### Client Folder
```json
{
  "Client Name": {
    "Assets": {},
    "Deliverables": {},
    "Reports": {},
    "Communications": {}
  }
}
```

### Project Folder
```json
{
  "Project Name": {
    "01_Research": {},
    "02_Design": {},
    "03_Development": {},
    "04_Testing": {},
    "05_Delivery": {}
  }
}
```

## Output Structure

```json
{
  "root_folder_id": "1abc123xyz",
  "root_folder_url": "https://drive.google.com/drive/folders/1abc123xyz",
  "created_folders": [
    {"path": "Project", "id": "1abc123"},
    {"path": "Project/Assets", "id": "2def456"}
  ]
}
```

## Behavior
- Idempotent: skips folders that already exist
- Recursive: creates full hierarchy

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

### List Folder Contents Recursively
```python
def get_folder_tree(drive, folder_id, indent=0):
    """Get folder tree as nested structure."""
    files = drive.ListFile({
        'q': f"'{folder_id}' in parents and trashed=false"
    }).GetList()

    tree = []
    for file in files:
        item = {
            'title': file['title'],
            'id': file['id'],
            'mimeType': file['mimeType'],
            'isFolder': file['mimeType'] == 'application/vnd.google-apps.folder'
        }

        if item['isFolder']:
            item['children'] = get_folder_tree(drive, file['id'], indent + 1)

        tree.append(item)

    return tree

# Usage
tree = get_folder_tree(drive, "root_folder_id")
```

### Print Folder Tree as Text
```python
def print_folder_tree(drive, folder_id, prefix="", is_last=True):
    """Print folder tree with visual structure."""
    files = drive.ListFile({
        'q': f"'{folder_id}' in parents and trashed=false",
        'orderBy': 'folder,title'
    }).GetList()

    for i, file in enumerate(files):
        is_final = (i == len(files) - 1)
        connector = "└── " if is_final else "├── "
        print(f"{prefix}{connector}{file['title']}")

        if file['mimeType'] == 'application/vnd.google-apps.folder':
            extension = "    " if is_final else "│   "
            print_folder_tree(drive, file['id'], prefix + extension, is_final)

# Usage
print("Root/")
print_folder_tree(drive, "folder_id")
```

### Build Path-to-ID Mapping
```python
def build_folder_map(drive, root_id, base_path=""):
    """Create mapping of folder paths to IDs."""
    folder_map = {}

    files = drive.ListFile({
        'q': f"'{root_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    }).GetList()

    for folder in files:
        path = f"{base_path}/{folder['title']}" if base_path else folder['title']
        folder_map[path] = folder['id']

        # Recurse into subfolders
        subfolder_map = build_folder_map(drive, folder['id'], path)
        folder_map.update(subfolder_map)

    return folder_map

# Usage
folder_map = build_folder_map(drive, "root_folder_id")
# Result: {"Assets": "id1", "Assets/Images": "id2", "Assets/Videos": "id3"}
```

### Create Folder Structure from Dict
```python
def create_folder_structure(drive, structure, parent_id=None):
    """Recursively create folder structure from dict."""
    created = []

    for folder_name, substructure in structure.items():
        # Check if folder exists
        query = f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        existing = drive.ListFile({'q': query}).GetList()

        if existing:
            folder = existing[0]
        else:
            # Create new folder
            folder_metadata = {
                'title': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id:
                folder_metadata['parents'] = [{'id': parent_id}]

            folder = drive.CreateFile(folder_metadata)
            folder.Upload()

        created.append({
            'title': folder_name,
            'id': folder['id'],
            'link': folder.get('alternateLink', '')
        })

        # Recurse into subfolders
        if substructure:
            sub_created = create_folder_structure(drive, substructure, folder['id'])
            created.extend(sub_created)

    return created

# Usage
structure = {
    "Project Alpha": {
        "Assets": {
            "Images": {},
            "Videos": {}
        },
        "Deliverables": {
            "Draft": {},
            "Final": {}
        }
    }
}
created = create_folder_structure(drive, structure, parent_folder_id)
```

### Find or Create Folder Path
```python
def ensure_folder_path(drive, path, root_id=None):
    """Ensure folder path exists, creating if needed. Returns final folder ID."""
    parts = path.strip('/').split('/')
    current_parent = root_id or 'root'

    for part in parts:
        # Search for existing folder
        query = f"title='{part}' and mimeType='application/vnd.google-apps.folder' and trashed=false and '{current_parent}' in parents"
        results = drive.ListFile({'q': query}).GetList()

        if results:
            current_parent = results[0]['id']
        else:
            # Create folder
            folder = drive.CreateFile({
                'title': part,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [{'id': current_parent}]
            })
            folder.Upload()
            current_parent = folder['id']

    return current_parent

# Usage
folder_id = ensure_folder_path(drive, "Clients/Acme/Assets/Images")
```

### Get Folder Statistics
```python
def get_folder_stats(drive, folder_id):
    """Get statistics for a folder and its contents."""
    stats = {
        'total_files': 0,
        'total_folders': 0,
        'by_type': {},
        'total_size': 0
    }

    def count_recursive(fid):
        files = drive.ListFile({
            'q': f"'{fid}' in parents and trashed=false"
        }).GetList()

        for file in files:
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                stats['total_folders'] += 1
                count_recursive(file['id'])
            else:
                stats['total_files'] += 1
                mime = file['mimeType']
                stats['by_type'][mime] = stats['by_type'].get(mime, 0) + 1
                if 'fileSize' in file:
                    stats['total_size'] += int(file['fileSize'])

    count_recursive(folder_id)
    return stats

# Usage
stats = get_folder_stats(drive, "folder_id")
print(f"Files: {stats['total_files']}, Folders: {stats['total_folders']}")
```

### OAuth Troubleshooting

1. **Token refresh fails**: Delete `mycreds.txt` and re-authenticate
2. **settings.yaml missing**: Create from template with OAuth settings
3. **Quota exceeded**: Wait 24h or use different project
4. **Folder creation fails**: Check parent folder permissions
5. **Duplicate folders**: Use idempotent creation (check before create)

## Testing Checklist

### Pre-flight
- [ ] OAuth credentials file exists (`mycreds.txt` or `credentials.json`)
- [ ] Google Drive API enabled in Google Cloud Console
- [ ] Dependencies installed (`pip install pydrive2 python-dotenv`)
- [ ] First-time OAuth flow completed (browser auth)

### Smoke Test
```bash
# Create a simple test structure
python scripts/gdrive_folder_structure.py --structure '{"Test-$(date +%s)": {"SubA": {}, "SubB": {}}}'

# Create from JSON file
python scripts/gdrive_folder_structure.py --file test_structure.json

# Create in a specific parent folder
python scripts/gdrive_folder_structure.py --structure '{"NewProject": {}}' --parent-path "Clients/TestClient"
```

### Validation
- [ ] Response contains `root_folder_id` and `root_folder_url`
- [ ] `created_folders` array lists all created folders with paths and IDs
- [ ] Nested folders are created correctly
- [ ] `root_folder_url` is accessible in browser
- [ ] Idempotent: re-running skips existing folders
- [ ] `--parent-path` correctly finds and uses parent folder
- [ ] Empty `{}` creates folder without subfolders
- [ ] Invalid JSON structure returns meaningful error

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `Invalid credentials` | OAuth token expired or invalid | Delete `mycreds.txt`, re-authenticate |
| `Parent folder not found` | Parent path doesn't exist | Verify parent path or create parent first |
| `403 Forbidden` | No write access to location | Request edit access from folder owner |
| `Invalid JSON` | Malformed structure definition | Validate JSON syntax before running |
| `Quota exceeded` | API rate limit reached | Wait 1 minute, reduce batch size |
| `Folder name too long` | Name exceeds 255 characters | Shorten folder names |
| `Invalid characters` | Folder name contains forbidden chars | Remove `/`, `\`, or other special characters |
| `Duplicate folder` | Folder already exists (not idempotent) | Script should skip - verify idempotent behavior |

### Recovery Strategies

1. **Idempotent design**: Check for existing folders before creating to support retry
2. **Atomic operations**: Create folders in order so partial failures can resume
3. **Validation first**: Validate JSON structure and folder names before API calls
4. **Progress logging**: Log each folder creation to enable recovery from partial failure
5. **Rollback support**: Track created folders to enable cleanup on critical failure

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
