# Google Document Generator

## Overview
Create professional Google Docs with brand styling from structured content.

## Supported Section Types

| Type | Description |
|------|-------------|
| `title` | Centered bold title |
| `section_header` | Blue (#548ce9) bold header |
| `subsection_header` | Black bold header |
| `paragraph` | Normal body text |
| `bullet_list` | Unordered list |
| `numbered_list` | Ordered list |
| `table` | Real Google Docs table |
| `divider` | Horizontal separator |

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `title` | string | Yes | Document title |
| `sections` | list | Yes | Section objects |
| `doc_name` | string | No | Filename (default: title) |
| `folder_id` | string | No | Drive folder |

## Section Format

```json
{
  "sections": [
    {"type": "section_header", "content": "Executive Summary"},
    {"type": "paragraph", "content": "This document outlines..."},
    {"type": "bullet_list", "items": [
      {"title": "Goal 1", "description": "Description here"}
    ]},
    {"type": "table", "headers": ["Col1", "Col2"], "rows": [["A", "B"]]}
  ]
}
```

## CLI Usage

```bash
# From JSON file
python scripts/generate_document.py --input content.json --title "Q4 Report"

# From JSON string
python scripts/generate_document.py --json '{"sections": [...]}' --title "Notes"

# Quick text (auto-formats)
python scripts/generate_document.py --title "Notes" --content "Paragraph text here..."
```

## Python Usage

### Setup Google Docs API
```python
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Load credentials (after OAuth flow)
creds = Credentials.from_authorized_user_file('mycreds.txt')
docs_service = build('docs', 'v1', credentials=creds)
drive_service = build('drive', 'v3', credentials=creds)
```

### Create a Document
```python
def create_document(title: str) -> dict:
    doc = docs_service.documents().create(body={'title': title}).execute()
    return {
        'document_id': doc['documentId'],
        'document_url': f"https://docs.google.com/document/d/{doc['documentId']}/edit"
    }

# Usage
result = create_document("Q4 Report")
print(result['document_url'])
```

### Insert Text
```python
def insert_text(doc_id: str, text: str, index: int = 1):
    requests = [
        {'insertText': {'location': {'index': index}, 'text': text}}
    ]
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': requests}
    ).execute()

# Usage
insert_text(doc_id, "Hello World\n\nThis is the first paragraph.")
```

### Apply Formatting
```python
def format_text(doc_id: str, start: int, end: int, bold: bool = False,
                font_size: int = None, color: dict = None):
    text_style = {}
    if bold:
        text_style['bold'] = True
    if font_size:
        text_style['fontSize'] = {'magnitude': font_size, 'unit': 'PT'}
    if color:
        text_style['foregroundColor'] = {'color': {'rgbColor': color}}

    requests = [{
        'updateTextStyle': {
            'range': {'startIndex': start, 'endIndex': end},
            'textStyle': text_style,
            'fields': ','.join(text_style.keys())
        }
    }]
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': requests}
    ).execute()

# Make text bold and blue (brand color #548ce9)
format_text(doc_id, 1, 12, bold=True, color={'red': 0.33, 'green': 0.55, 'blue': 0.91})
```

### Insert Bullet List
```python
def insert_bullet_list(doc_id: str, items: list, start_index: int = 1):
    # Insert text for all items
    text = '\n'.join(items) + '\n'
    requests = [
        {'insertText': {'location': {'index': start_index}, 'text': text}},
        {'createParagraphBullets': {
            'range': {'startIndex': start_index, 'endIndex': start_index + len(text)},
            'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
        }}
    ]
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': requests}
    ).execute()

# Usage
insert_bullet_list(doc_id, ["First item", "Second item", "Third item"])
```

### Insert Table
```python
def insert_table(doc_id: str, headers: list, rows: list, index: int = 1):
    num_rows = len(rows) + 1  # +1 for header
    num_cols = len(headers)

    # Create table
    requests = [{
        'insertTable': {
            'rows': num_rows,
            'columns': num_cols,
            'location': {'index': index}
        }
    }]
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': requests}
    ).execute()

    # Get document to find table cell indices
    doc = docs_service.documents().get(documentId=doc_id).execute()
    # ... populate cells with additional batchUpdate calls

# Usage
insert_table(doc_id, ["Name", "Role"], [["Alice", "Engineer"], ["Bob", "Designer"]])
```

### Complete Document Creation
```python
def create_branded_document(title: str, sections: list) -> dict:
    # Create document
    doc = docs_service.documents().create(body={'title': title}).execute()
    doc_id = doc['documentId']

    # Build requests for all sections
    requests = []
    current_index = 1

    for section in sections:
        if section['type'] == 'section_header':
            text = section['content'] + '\n'
            requests.append({'insertText': {'location': {'index': current_index}, 'text': text}})
            # Add formatting for header (bold, blue)
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': current_index, 'endIndex': current_index + len(text) - 1},
                    'textStyle': {
                        'bold': True,
                        'foregroundColor': {'color': {'rgbColor': {'red': 0.33, 'green': 0.55, 'blue': 0.91}}}
                    },
                    'fields': 'bold,foregroundColor'
                }
            })
            current_index += len(text)
        elif section['type'] == 'paragraph':
            text = section['content'] + '\n\n'
            requests.append({'insertText': {'location': {'index': current_index}, 'text': text}})
            current_index += len(text)

    # Execute all requests
    if requests:
        docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

    return {
        'document_id': doc_id,
        'document_url': f"https://docs.google.com/document/d/{doc_id}/edit"
    }

# Usage
sections = [
    {'type': 'section_header', 'content': 'Executive Summary'},
    {'type': 'paragraph', 'content': 'This document outlines our Q4 achievements...'},
    {'type': 'section_header', 'content': 'Key Metrics'},
    {'type': 'paragraph', 'content': 'Revenue increased by 25% compared to Q3.'}
]
result = create_branded_document("Q4 Report", sections)
print(result['document_url'])
```

## Output

```json
{
  "document_id": "1abc123",
  "document_url": "https://docs.google.com/document/d/...",
  "title": "Q4 Report"
}
```

## Testing Checklist

### Pre-flight
- [ ] Google Docs API enabled in Google Cloud Console
- [ ] OAuth credentials file exists (`mycreds.txt` or `credentials.json`)
- [ ] First-time OAuth flow completed (browser auth)
- [ ] Dependencies installed (`pip install pydrive2 google-api-python-client python-dotenv`)

### Smoke Test
```bash
# Create simple document with title only
python scripts/generate_document.py --title "Test Document"

# Create from JSON content
python scripts/generate_document.py --title "Test Report" --json '{"sections": [{"type": "paragraph", "content": "Test content here"}]}'

# Create with all section types
python scripts/generate_document.py --title "Full Test" --input test_content.json

# Create in specific folder
python scripts/generate_document.py --title "Filed Doc" --folder-id "1abc123xyz"
```

### Validation
- [ ] Response contains `document_id` and `document_url`
- [ ] `document_url` opens in Google Docs
- [ ] Title matches requested title
- [ ] `section_header` renders in blue (#548ce9) and bold
- [ ] `subsection_header` renders in black and bold
- [ ] `bullet_list` renders as proper bullet points
- [ ] `numbered_list` renders as numbered items
- [ ] `table` creates real Google Docs table with headers
- [ ] `divider` creates horizontal separator
- [ ] Document appears in correct Drive folder (if specified)
- [ ] OAuth token refreshes automatically

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `Invalid credentials` | OAuth token expired or invalid | Delete credentials file, re-authenticate |
| `403 Forbidden` | No access to Google Docs API | Enable API in Google Cloud Console |
| `404 Folder not found` | Invalid folder_id specified | Verify folder ID exists and is accessible |
| `Quota exceeded` | Google API rate limit | Wait 1 minute, implement backoff |
| `Invalid JSON` | Malformed sections array | Validate JSON structure before API call |
| `Unknown section type` | Unsupported type in sections | Use valid types: title, section_header, paragraph, etc. |
| `Table format error` | Invalid table structure | Ensure headers array matches row column count |
| `Document creation failed` | API error during creation | Retry, check API status |

### Recovery Strategies

1. **Automatic token refresh**: PyDrive2 handles token refresh automatically
2. **Validation first**: Validate JSON structure and section types before API call
3. **Incremental creation**: Create document, then add sections one at a time for resume
4. **Retry with backoff**: Implement exponential backoff (1s, 2s, 4s) for quota errors
5. **Fallback formatting**: If complex formatting fails, use simple text
6. **Document recovery**: Return document ID even if some sections fail
