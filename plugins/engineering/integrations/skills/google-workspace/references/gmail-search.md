# Gmail Search

## Overview
Search Gmail for emails with/about clients. Read-only operations.

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | No | Free text search |
| `domain` | string | No | Filter by email domain |
| `days` | int | No | Days back (default: 14) |
| `internal_only` | bool | No | Only internal emails |
| `max_results` | int | No | Max messages (default: 50) |
| `thread_id` | string | No | Get specific thread |

## CLI Usage

```bash
# Search by domain
python scripts/gmail_search.py --domain "microsoft.com" --days 14

# Search by keyword
python scripts/gmail_search.py --query "proposal" --days 30

# Internal emails mentioning client
python scripts/gmail_search.py --query "Microsoft" --internal-only --days 14

# Get specific thread
python scripts/gmail_search.py --thread "thread123"

# Output as JSON
python scripts/gmail_search.py --domain "kit.com" --json
```

## Gmail Query Syntax

- `from:@domain.com` - Emails from domain
- `to:@domain.com` - Emails to domain
- `newer_than:14d` - Last 14 days
- `subject:proposal` - Subject contains word
- `has:attachment` - Has attachments

## Output Structure

```json
{
  "total": 15,
  "external_threads": [
    {
      "id": "msg123",
      "thread_id": "thread456",
      "subject": "Re: Proposal Review",
      "from": "John <john@client.com>",
      "to": "user@yourcompany.com",
      "date": "2025-12-25T10:30:00",
      "snippet": "Thanks for sending over..."
    }
  ],
  "internal_mentions": [...],
  "external_count": 10,
  "internal_count": 5
}
```

## First-Time Setup
1. Enable Gmail API in Google Cloud Console
2. Run script - browser opens for OAuth consent
3. Credentials saved to `gmail_token.pickle`

## Python Usage

### Basic Setup
```python
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Initialize Gmail API service with OAuth."""
    creds = None

    # Load saved credentials
    if os.path.exists('gmail_token.pickle'):
        with open('gmail_token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # Refresh or create credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save credentials
        with open('gmail_token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

service = get_gmail_service()
```

### Search Messages by Query
```python
def search_messages(service, query, max_results=50):
    """Search Gmail messages with query string."""
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=max_results
    ).execute()

    messages = results.get('messages', [])
    return messages

# Usage
messages = search_messages(service, "from:@microsoft.com newer_than:14d")
print(f"Found {len(messages)} messages")
```

### Get Full Message Details
```python
def get_message_details(service, message_id):
    """Get full details of a message."""
    message = service.users().messages().get(
        userId='me',
        id=message_id,
        format='full'
    ).execute()

    # Extract headers
    headers = {h['name']: h['value'] for h in message['payload']['headers']}

    return {
        'id': message['id'],
        'thread_id': message['threadId'],
        'subject': headers.get('Subject', ''),
        'from': headers.get('From', ''),
        'to': headers.get('To', ''),
        'date': headers.get('Date', ''),
        'snippet': message.get('snippet', '')
    }

# Usage
for msg in messages[:5]:
    details = get_message_details(service, msg['id'])
    print(f"{details['date']}: {details['subject']}")
```

### Search by Domain
```python
def search_by_domain(service, domain, days=14):
    """Search for emails from/to a specific domain."""
    query = f"(from:@{domain} OR to:@{domain}) newer_than:{days}d"

    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=100
    ).execute()

    messages = results.get('messages', [])

    detailed = []
    for msg in messages:
        details = get_message_details(service, msg['id'])
        detailed.append(details)

    return detailed

# Usage
emails = search_by_domain(service, "microsoft.com", days=30)
```

### Search Internal vs External
```python
def search_client_mentions(service, client_name, internal_domain, days=14):
    """Separate internal and external emails mentioning client."""
    query = f"{client_name} newer_than:{days}d"

    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=100
    ).execute()

    messages = results.get('messages', [])

    external_threads = []
    internal_mentions = []

    for msg in messages:
        details = get_message_details(service, msg['id'])

        # Check if external
        is_external = internal_domain not in details['from']

        if is_external:
            external_threads.append(details)
        else:
            internal_mentions.append(details)

    return {
        'external_threads': external_threads,
        'internal_mentions': internal_mentions,
        'external_count': len(external_threads),
        'internal_count': len(internal_mentions)
    }

# Usage
results = search_client_mentions(service, "Microsoft", "yourcompany.com", days=14)
```

### Get Thread with All Messages
```python
def get_thread(service, thread_id):
    """Get all messages in a thread."""
    thread = service.users().threads().get(
        userId='me',
        id=thread_id,
        format='full'
    ).execute()

    messages = []
    for msg in thread.get('messages', []):
        headers = {h['name']: h['value'] for h in msg['payload']['headers']}
        messages.append({
            'id': msg['id'],
            'from': headers.get('From', ''),
            'date': headers.get('Date', ''),
            'snippet': msg.get('snippet', '')
        })

    return {
        'thread_id': thread_id,
        'messages': messages,
        'message_count': len(messages)
    }

# Usage
thread = get_thread(service, "thread_id_here")
for msg in thread['messages']:
    print(f"  {msg['from']}: {msg['snippet'][:50]}...")
```

### Gmail Query Syntax Examples
```python
# Common query patterns
queries = {
    # By sender/recipient
    "from_domain": "from:@example.com",
    "to_domain": "to:@example.com",
    "from_or_to": "(from:@example.com OR to:@example.com)",

    # By date
    "last_7_days": "newer_than:7d",
    "last_month": "newer_than:30d",
    "date_range": "after:2025/01/01 before:2025/02/01",

    # By content
    "subject": "subject:proposal",
    "has_attachment": "has:attachment",
    "has_pdf": "filename:pdf",

    # Combined
    "client_recent": "from:@client.com newer_than:14d has:attachment",
    "internal_mentions": "to:@ourcompany.com subject:ClientName newer_than:7d",
}
```

### Pagination for Large Result Sets
```python
def search_all_messages(service, query):
    """Search with pagination for all matching messages."""
    all_messages = []
    page_token = None

    while True:
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=100,
            pageToken=page_token
        ).execute()

        messages = results.get('messages', [])
        all_messages.extend(messages)

        page_token = results.get('nextPageToken')
        if not page_token:
            break

    return all_messages

# Usage
all_emails = search_all_messages(service, "from:@important.com")
```

### OAuth Troubleshooting

1. **Token refresh fails**: Delete `gmail_token.pickle` and re-authenticate
2. **credentials.json missing**: Download from Google Cloud Console (OAuth 2.0 Client ID)
3. **Quota exceeded**: Gmail API allows 250 quota units/second; implement backoff
4. **"Access denied" error**: Ensure Gmail API is enabled in Cloud Console
5. **Insufficient scopes**: Re-authenticate with correct scopes (`gmail.readonly`)

```python
# Robust error handling
import time

def safe_api_call(func, *args, max_retries=3, **kwargs):
    """Execute API call with retry logic."""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "quota" in str(e).lower() or "rate" in str(e).lower():
                time.sleep(2 ** attempt)
            else:
                raise
    raise Exception("Max retries exceeded")
```

## Testing Checklist

### Pre-flight
- [ ] Gmail API enabled in Google Cloud Console
- [ ] OAuth credentials file exists (`credentials.json`)
- [ ] `gmail_token.pickle` exists (or will be created on first run)
- [ ] Dependencies installed (`pip install google-auth google-auth-oauthlib google-api-python-client`)

### Smoke Test
```bash
# Search by keyword in last 7 days
python scripts/gmail_search.py --query "test" --days 7

# Search by domain
python scripts/gmail_search.py --domain "gmail.com" --days 7

# Internal emails only
python scripts/gmail_search.py --query "project" --internal-only --days 14

# Output as JSON
python scripts/gmail_search.py --domain "example.com" --json
```

### Validation
- [ ] Response contains `total`, `external_threads`, `internal_mentions`
- [ ] Email objects have `id`, `thread_id`, `subject`, `from`, `to`, `date`, `snippet`
- [ ] `--domain` filter correctly matches sender/recipient domains
- [ ] `--internal-only` excludes external emails
- [ ] `--days` correctly filters by date range
- [ ] `--thread` retrieves specific thread with all messages
- [ ] Gmail query syntax works (`from:`, `to:`, `subject:`, `has:attachment`)
- [ ] OAuth token refreshes automatically when expired
- [ ] Rate limits respected (avoid hammering API)

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `Invalid credentials` | OAuth token expired or invalid | Delete `gmail_token.pickle`, re-authenticate |
| `403 Forbidden` | Gmail API not enabled or no access | Enable Gmail API in Google Cloud Console |
| `404 Not Found` | Thread or message ID doesn't exist | Verify ID, message may have been deleted |
| `Quota exceeded` | API rate limit (250 units/second) | Wait 1 second, implement exponential backoff |
| `Invalid query` | Malformed Gmail search query | Check query syntax, escape special characters |
| `User rate limit exceeded` | Too many requests per user | Reduce request frequency, batch requests |
| `Backend error` | Gmail service temporarily unavailable | Retry after 30 seconds |
| `Insufficient scopes` | Missing required OAuth scopes | Re-authenticate with `gmail.readonly` scope |

### Recovery Strategies

1. **Automatic token refresh**: Google client library handles token refresh automatically
2. **Retry with backoff**: Implement exponential backoff (1s, 2s, 4s) for rate limits
3. **Batch requests**: Use Gmail batch API for multiple message fetches
4. **Pagination**: Use `nextPageToken` for large result sets
5. **Query validation**: Validate query syntax before sending to API
