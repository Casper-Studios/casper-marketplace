# Attio CRM Integration Patterns

## Lead Kickoff Workflow

When a new lead is qualified, create all associated resources:

```python
from attio_api import AttioClient

client = AttioClient()

# 1. Create/update company in Attio
company = client.assert_company(
    name="Acme Corp",
    domain="acme.com",
    customer_status="Active Prospect"
)
record_id = company["id"]["record_id"]

# 2. Create Slack channel
# (using slack-automation skill)
channel = create_slack_channel(f"internal-acme")

# 3. Create Drive folder
# (using google-workspace skill)
folder = create_client_folder("Acme Corp")

# 4. Link resources to Attio
client.update_company(record_id, {
    "prospect_slack_channel": channel["url"],
    "google_drive_folder_url": folder["folder_url"]
})

# 5. Add kickoff note
client.create_note(
    parent_record_id=record_id,
    title="Lead Kickoff Complete",
    content=f"""
    - Slack: {channel['url']}
    - Drive: {folder['folder_url']}
    - Status: Active Prospect
    """
)
```

## Contact Import Pattern

Import contacts from a list and link to company:

```python
contacts = [
    {"email": "john@acme.com", "first": "John", "last": "Smith"},
    {"email": "jane@acme.com", "first": "Jane", "last": "Doe"}
]

for contact in contacts:
    client.assert_person(
        email=contact["email"],
        first_name=contact["first"],
        last_name=contact["last"],
        company_record_id=company_record_id
    )
```

## Meeting Note Pattern

After a meeting, add notes with context:

```python
client.create_note(
    parent_record_id=company_record_id,
    title=f"Discovery Call - {date}",
    content="""
    ## Attendees
    - John Smith (VP Engineering)
    - Jane Doe (PM)

    ## Key Points
    - Budget: $50-100k
    - Timeline: Q1 2025
    - Decision maker: CTO

    ## Next Steps
    1. Send proposal by Friday
    2. Schedule technical deep-dive
    """
)
```

## URL Extraction Pattern

When you have an Attio URL, extract the record ID:

```python
url = "https://app.attio.com/casperstudios/companies/view/abc-123-def"
parsed = client.parse_attio_url(url)
# {'workspace_slug': 'casperstudios', 'object_type': 'companies', 'record_id': 'abc-123-def'}

company = client.get_company(parsed["record_id"])
```

## Python Usage

### Basic Client Setup
```python
import os
import requests

ATTIO_API_KEY = os.environ["ATTIO_API_KEY"]
BASE_URL = "https://api.attio.com/v2"

headers = {
    "Authorization": f"Bearer {ATTIO_API_KEY}",
    "Content-Type": "application/json"
}
```

### Search Companies
```python
def search_companies(query: str, limit: int = 10):
    response = requests.post(
        f"{BASE_URL}/objects/companies/records/query",
        headers=headers,
        json={
            "filter": {
                "name": {"$contains": query}
            },
            "limit": limit
        }
    )
    return response.json()["data"]

companies = search_companies("Microsoft")
for company in companies:
    print(f"{company['values']['name'][0]['value']} - {company['id']['record_id']}")
```

### Create Contact
```python
def create_contact(email: str, name: str, company_id: str = None):
    data = {
        "data": {
            "values": {
                "email_addresses": [{"email_address": email}],
                "name": [{"first_name": name.split()[0], "last_name": " ".join(name.split()[1:])}]
            }
        }
    }
    if company_id:
        data["data"]["values"]["company"] = [{"target_record_id": company_id}]

    response = requests.post(
        f"{BASE_URL}/objects/people/records",
        headers=headers,
        json=data
    )
    return response.json()
```

### Add Note to Company
```python
def add_note(parent_object: str, parent_record_id: str, content: str, title: str = "Note"):
    response = requests.post(
        f"{BASE_URL}/notes",
        headers=headers,
        json={
            "data": {
                "parent_object": parent_object,
                "parent_record_id": parent_record_id,
                "title": title,
                "content_plaintext": content
            }
        }
    )
    return response.json()

# Add note to a company
add_note("companies", "abc-123", "Discussed Q1 expansion plans")
```

## Batch Operations

For multiple records, use pagination:

```python
all_companies = []
offset = 0
limit = 25

while True:
    batch = client.search_companies(
        name_query="",  # All companies
        limit=limit,
        offset=offset
    )
    if not batch:
        break
    all_companies.extend(batch)
    offset += limit
```

## Testing Checklist

### Pre-flight
- [ ] `ATTIO_API_KEY` set in `.env`
- [ ] `SLACK_BOT_TOKEN` set (for lead kickoff)
- [ ] Google Drive OAuth credentials available (for lead kickoff)
- [ ] Test company exists in Attio for integration tests

### Smoke Test

#### Lead Kickoff Pattern
```bash
# Full lead kickoff (creates company, Slack channel, Drive folder, links all)
python scripts/lead_kickoff.py "Test Company $(date +%s)" \
  --domain "testcompany$(date +%s).com" \
  --dry-run

# Without dry-run (creates actual resources)
python scripts/lead_kickoff.py "New Client Inc" \
  --domain "newclient.com"
```

#### Contact Import Pattern
```bash
# Import contacts from CSV to existing company
python scripts/import_contacts.py "COMPANY_RECORD_ID" contacts.csv

# Test with single contact
python scripts/attio_api.py create-person "test@example.com" \
  --first-name "Test" \
  --last-name "Contact" \
  --company-id "COMPANY_RECORD_ID"
```

#### Meeting Note Pattern
```bash
# Add meeting note to company
python scripts/add_meeting_note.py "COMPANY_RECORD_ID" \
  --title "Discovery Call" \
  --attendees "John Smith, Jane Doe" \
  --content "Key points from meeting..."
```

### Validation
- [ ] Lead kickoff creates company in Attio
- [ ] Slack channel created with correct naming pattern (`internal-{company}`)
- [ ] Drive folder created with correct structure
- [ ] Attio company record has `prospect_slack_channel` and `google_drive_folder_url` populated
- [ ] Kickoff note created with links to all resources
- [ ] Contact import links people to company correctly
- [ ] Duplicate contacts are upserted (not duplicated)
- [ ] Meeting notes appear in Attio UI with markdown formatting
- [ ] Batch operations handle pagination correctly
- [ ] URL extraction works for all Attio URL formats

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `Attio API error` | API key invalid or rate limited | Check key, implement backoff |
| `Slack channel creation failed` | Bot lacks permissions | Add `channels:manage` scope |
| `Drive folder creation failed` | OAuth expired or no access | Re-authenticate Google Drive |
| `Company not found` | Invalid record ID or deleted | Re-search company by name/domain |
| `Contact link failed` | Invalid company_record_id | Verify company exists before linking |
| `Note creation failed` | Invalid parent_record_id | Verify record exists |
| `Batch operation partial failure` | Some records failed | Log failures, continue with successful ones |
| `URL parse error` | Malformed Attio URL | Validate URL format before parsing |

### Recovery Strategies

1. **Atomic operations**: If Slack or Drive fails, still create Attio record with partial data
2. **Rollback support**: Track created resources to enable cleanup on critical failure
3. **Partial success handling**: For batch imports, continue with valid records, log failures
4. **Retry with backoff**: Retry failed API calls up to 3 times before giving up
5. **Link verification**: Before updating links, verify URLs are accessible
6. **Idempotent kickoffs**: Design kickoff to be safely re-run (upsert, check existing resources)
