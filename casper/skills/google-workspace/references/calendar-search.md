# Google Calendar Search

## Overview
Search Google Calendar for meetings with clients. Read-only operations.

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | No | Text search in title/description |
| `attendee_domain` | string | No | Filter by attendee domain |
| `days_back` | int | No | Days in past (default: 14) |
| `days_forward` | int | No | Days in future (default: 14) |
| `calendar_id` | string | No | Calendar ID (default: primary) |
| `max_results` | int | No | Max events (default: 50) |

## CLI Usage

```bash
# Search by client name
python scripts/google_calendar_search.py "Microsoft" --days-back 30

# Search by attendee domain
python scripts/google_calendar_search.py --domain "microsoft.com" --days-back 14

# Show only upcoming meetings
python scripts/google_calendar_search.py "Client" --upcoming --days-forward 30

# Output as JSON
python scripts/google_calendar_search.py "Kit" --json
```

## Output Structure

```json
{
  "past_meetings": [
    {
      "id": "event123",
      "summary": "Kit Weekly Sync",
      "description": "Regular check-in",
      "start": "2025-12-20T10:00:00-05:00",
      "end": "2025-12-20T11:00:00-05:00",
      "is_past": true,
      "location": "Google Meet",
      "attendees": [
        {"email": "john@kit.com", "name": "John", "response": "accepted"}
      ],
      "html_link": "https://calendar.google.com/event?eid=..."
    }
  ],
  "upcoming_meetings": [...],
  "total_past": 5,
  "total_upcoming": 2
}
```

## First-Time Setup
1. Enable Calendar API in Google Cloud Console
2. Run script - browser opens for OAuth consent
3. Credentials saved to `calendar_token.pickle`

## Python Usage

### Basic Setup
```python
import os
import pickle
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_service():
    """Initialize Calendar API service with OAuth."""
    creds = None

    # Load saved credentials
    if os.path.exists('calendar_token.pickle'):
        with open('calendar_token.pickle', 'rb') as token:
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
        with open('calendar_token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)

service = get_calendar_service()
```

### Search Events by Query
```python
def search_events(service, query, days_back=14, days_forward=14, calendar_id='primary'):
    """Search calendar events by text query."""
    now = datetime.utcnow()
    time_min = (now - timedelta(days=days_back)).isoformat() + 'Z'
    time_max = (now + timedelta(days=days_forward)).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        q=query,
        singleEvents=True,
        orderBy='startTime',
        maxResults=100
    ).execute()

    events = events_result.get('items', [])
    return events

# Usage
events = search_events(service, "Microsoft", days_back=30)
for event in events:
    print(f"{event['start'].get('dateTime', event['start'].get('date'))}: {event['summary']}")
```

### Get Event Details
```python
def format_event(event):
    """Format event into standardized structure."""
    start = event['start'].get('dateTime', event['start'].get('date'))
    end = event['end'].get('dateTime', event['end'].get('date'))

    attendees = []
    for attendee in event.get('attendees', []):
        attendees.append({
            'email': attendee.get('email', ''),
            'name': attendee.get('displayName', ''),
            'response': attendee.get('responseStatus', 'needsAction')
        })

    return {
        'id': event['id'],
        'summary': event.get('summary', 'No title'),
        'description': event.get('description', ''),
        'start': start,
        'end': end,
        'location': event.get('location', ''),
        'attendees': attendees,
        'html_link': event.get('htmlLink', ''),
        'is_past': datetime.fromisoformat(start.replace('Z', '+00:00')) < datetime.now().astimezone()
    }

# Usage
for event in events:
    details = format_event(event)
    print(f"{'[PAST]' if details['is_past'] else '[UPCOMING]'} {details['summary']}")
```

### Search by Attendee Domain
```python
def search_by_attendee_domain(service, domain, days_back=14, days_forward=14):
    """Find meetings with attendees from a specific domain."""
    now = datetime.utcnow()
    time_min = (now - timedelta(days=days_back)).isoformat() + 'Z'
    time_max = (now + timedelta(days=days_forward)).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime',
        maxResults=250
    ).execute()

    matching_events = []
    for event in events_result.get('items', []):
        attendees = event.get('attendees', [])
        for attendee in attendees:
            if domain in attendee.get('email', ''):
                matching_events.append(format_event(event))
                break

    return matching_events

# Usage
microsoft_meetings = search_by_attendee_domain(service, "microsoft.com", days_back=30)
```

### Separate Past and Upcoming
```python
def search_client_meetings(service, client_name, days_back=14, days_forward=14):
    """Search meetings and separate by past/upcoming."""
    events = search_events(service, client_name, days_back, days_forward)

    now = datetime.now().astimezone()
    past_meetings = []
    upcoming_meetings = []

    for event in events:
        details = format_event(event)

        if details['is_past']:
            past_meetings.append(details)
        else:
            upcoming_meetings.append(details)

    return {
        'past_meetings': past_meetings,
        'upcoming_meetings': upcoming_meetings,
        'total_past': len(past_meetings),
        'total_upcoming': len(upcoming_meetings)
    }

# Usage
results = search_client_meetings(service, "Kit", days_back=30, days_forward=30)
print(f"Past: {results['total_past']}, Upcoming: {results['total_upcoming']}")
```

### List Calendars
```python
def list_calendars(service):
    """List all accessible calendars."""
    calendars_result = service.calendarList().list().execute()
    calendars = calendars_result.get('items', [])

    return [{
        'id': cal['id'],
        'summary': cal.get('summary', 'Unnamed'),
        'primary': cal.get('primary', False)
    } for cal in calendars]

# Usage
calendars = list_calendars(service)
for cal in calendars:
    primary = " (PRIMARY)" if cal['primary'] else ""
    print(f"{cal['summary']}{primary}: {cal['id']}")
```

### Search Multiple Calendars
```python
def search_all_calendars(service, query, days_back=14, days_forward=14):
    """Search events across all accessible calendars."""
    calendars = list_calendars(service)
    all_events = []

    for cal in calendars:
        try:
            events = search_events(
                service,
                query,
                days_back,
                days_forward,
                calendar_id=cal['id']
            )
            for event in events:
                event['calendar'] = cal['summary']
                all_events.append(format_event(event))
        except Exception as e:
            print(f"Could not access {cal['summary']}: {e}")

    # Sort by start time
    all_events.sort(key=lambda x: x['start'])
    return all_events

# Usage
all_meetings = search_all_calendars(service, "standup")
```

### Get Events for Today
```python
def get_today_events(service, calendar_id='primary'):
    """Get all events for today."""
    today = datetime.utcnow().date()
    time_min = datetime.combine(today, datetime.min.time()).isoformat() + 'Z'
    time_max = datetime.combine(today, datetime.max.time()).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    return [format_event(e) for e in events_result.get('items', [])]

# Usage
today = get_today_events(service)
print(f"You have {len(today)} events today")
```

### Pagination for Large Result Sets
```python
def search_all_events(service, query, days_back=90):
    """Search with pagination for all matching events."""
    now = datetime.utcnow()
    time_min = (now - timedelta(days=days_back)).isoformat() + 'Z'
    time_max = now.isoformat() + 'Z'

    all_events = []
    page_token = None

    while True:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            q=query,
            singleEvents=True,
            orderBy='startTime',
            maxResults=250,
            pageToken=page_token
        ).execute()

        events = events_result.get('items', [])
        all_events.extend([format_event(e) for e in events])

        page_token = events_result.get('nextPageToken')
        if not page_token:
            break

    return all_events

# Usage
all_client_meetings = search_all_events(service, "Client Name", days_back=180)
```

### OAuth Troubleshooting

1. **Token refresh fails**: Delete `calendar_token.pickle` and re-authenticate
2. **credentials.json missing**: Download from Google Cloud Console (OAuth 2.0 Client ID)
3. **Quota exceeded**: Calendar API allows 1M queries/day; implement backoff for bursts
4. **"Access denied" error**: Ensure Calendar API is enabled in Cloud Console
5. **Insufficient scopes**: Re-authenticate with correct scopes (`calendar.readonly`)

```python
# Robust error handling
import time

def safe_calendar_call(func, *args, max_retries=3, **kwargs):
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
- [ ] Google Calendar API enabled in Google Cloud Console
- [ ] OAuth credentials file exists (`credentials.json`)
- [ ] `calendar_token.pickle` exists (or will be created on first run)
- [ ] Dependencies installed (`pip install google-auth google-auth-oauthlib google-api-python-client`)

### Smoke Test
```bash
# Search meetings by keyword
python scripts/google_calendar_search.py "meeting" --days-back 7

# Search by attendee domain
python scripts/google_calendar_search.py --domain "google.com" --days-back 14

# Show upcoming meetings only
python scripts/google_calendar_search.py "sync" --upcoming --days-forward 30

# Output as JSON
python scripts/google_calendar_search.py "client" --json
```

### Validation
- [ ] Response contains `past_meetings`, `upcoming_meetings`, counts
- [ ] Event objects have `id`, `summary`, `start`, `end`, `attendees`, `html_link`
- [ ] `--domain` filter matches attendee email domains
- [ ] `--days-back` correctly filters past events
- [ ] `--days-forward` correctly filters future events
- [ ] `--upcoming` flag shows only future events
- [ ] `attendees` array includes `email`, `name`, `response` status
- [ ] `html_link` opens event in Google Calendar
- [ ] OAuth token refreshes automatically when expired
- [ ] All-day events handled correctly

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `Invalid credentials` | OAuth token expired or invalid | Delete `calendar_token.pickle`, re-authenticate |
| `403 Forbidden` | Calendar API not enabled or no access | Enable Calendar API in Google Cloud Console |
| `404 Not Found` | Calendar or event ID doesn't exist | Verify ID, event may have been deleted |
| `Quota exceeded` | API rate limit (1M queries/day) | Implement exponential backoff |
| `Calendar not found` | Invalid calendar ID | Use 'primary' or verify calendar ID |
| `Backend error` | Calendar service temporarily unavailable | Retry after 30 seconds |
| `Invalid time range` | Start date after end date | Verify `days_back` and `days_forward` values |
| `Insufficient scopes` | Missing required OAuth scopes | Re-authenticate with `calendar.readonly` scope |

### Recovery Strategies

1. **Automatic token refresh**: Google client library handles token refresh automatically
2. **Retry with backoff**: Implement exponential backoff (1s, 2s, 4s) for rate limits
3. **Pagination**: Use `pageToken` for calendars with many events
4. **Timezone handling**: Convert all times to UTC for consistent filtering
5. **Attendee caching**: Cache attendee info to reduce redundant lookups
