# Attio API Guide

## Authentication

| Setting | Value |
|---------|-------|
| API Base URL | `https://api.attio.com/v2` |
| Auth Method | Bearer Token |
| Env Variable | `ATTIO_API_KEY` |

## Operations

### Companies

#### Get Company
```bash
python scripts/attio_api.py get-company <record_id>
```

#### Search Companies
```bash
python scripts/attio_api.py search-companies "Acme Corp" --limit 10
```

#### Create Company
```bash
python scripts/attio_api.py create-company "Microsoft" --domain "microsoft.com" --status "Active Prospect"
```

#### Assert (Upsert) Company
Creates or updates based on domain match:
```python
company = client.assert_company(
    name="Microsoft",
    domain="microsoft.com",
    customer_status="Active Prospect"
)
```

#### Update Company
```bash
python scripts/attio_api.py update-company <record_id> \
  --slack-channel "https://slack.com/..." \
  --drive-folder "https://drive.google.com/..."
```

### People (Contacts)

#### Create Person
```bash
python scripts/attio_api.py create-person "john@acme.com" \
  --first-name "John" \
  --last-name "Smith" \
  --company-id <company_record_id>
```

#### Assert (Upsert) Person
Creates or updates based on email match:
```python
person = client.assert_person(
    email="john@acme.com",
    first_name="John",
    last_name="Smith",
    company_record_id="abc-123"
)
```

### Notes

#### Create Note
```bash
python scripts/attio_api.py create-note <record_id> "Note Title" "Note content..."
```

#### List Notes
```bash
python scripts/attio_api.py list-notes <record_id> --limit 10
```

### URL Parsing

```bash
python scripts/attio_api.py parse-url "https://app.attio.com/yourworkspace/companies/view/abc-123"
```

Output:
```json
{
  "workspace_slug": "yourworkspace",
  "object_type": "companies",
  "record_id": "abc-123"
}
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

### Using AttioClient Wrapper

```python
from attio_api import AttioClient

client = AttioClient()  # Uses ATTIO_API_KEY env var

# Get company
company = client.get_company("record-uuid")
name = client.get_company_name(company)

# Search
companies = client.search_companies(name_query="Acme", limit=10)

# Upsert company
company = client.assert_company(
    name="New Company",
    domain="newcompany.com",
    customer_status="Active Prospect"
)
record_id = company.get("id", {}).get("record_id")

# Update with links
client.update_company(record_id, {
    "google_drive_folder_url": "https://drive.google.com/...",
    "prospect_slack_channel": "https://slack.com/..."
})

# Create contact
person = client.assert_person(
    email="ceo@newcompany.com",
    first_name="Jane",
    last_name="Doe",
    company_record_id=record_id
)

# Add note
note = client.create_note(
    parent_record_id=record_id,
    title="Lead Kickoff Complete",
    content="Created all resources"
)
```

## Custom Attributes

Expected custom attributes on Company object:

| Attribute Slug | Type | Description |
|---------------|------|-------------|
| `google_drive_folder_url` | URL | Client Drive folder |
| `prospect_slack_channel` | URL | Slack channel link |
| `customer_status` | Status | "Active Prospect", "Customer" |

## Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/objects/companies/records/{id}` | GET | Get company |
| `/objects/companies/records/query` | POST | Search companies |
| `/objects/companies/records` | POST | Create company |
| `/objects/companies/records` | PUT | Assert company |
| `/objects/companies/records/{id}` | PATCH | Update company |
| `/objects/people/records` | POST | Create person |
| `/objects/people/records` | PUT | Assert person |
| `/notes` | GET/POST | List/create notes |

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid or expired API key | Verify `ATTIO_API_KEY` in .env |
| `404 Not Found` | Record ID doesn't exist | Verify record ID, may have been deleted |
| `422 Validation Error` | Invalid field value or format | Check field types and allowed values |
| `429 Rate Limited` | Too many requests | Wait `retry-after` seconds, implement backoff |
| `400 Bad Request` | Malformed request body | Validate JSON structure before sending |
| `Invalid field ID` | Custom attribute slug doesn't exist | Create attribute in Attio workspace settings |
| `Domain already exists` | Company with domain exists (on create) | Use `assert_company` for upsert behavior |
| `Email already exists` | Person with email exists (on create) | Use `assert_person` for upsert behavior |
| `Company not found` | Invalid company_record_id for person | Verify company exists before linking person |

### Recovery Strategies

1. **Automatic retry**: Implement exponential backoff (1s, 2s, 4s) for rate limits
2. **Upsert over create**: Use `assert_company` and `assert_person` to avoid duplicates
3. **Validation first**: Validate record IDs exist before update operations
4. **Attribute caching**: Cache custom attribute slugs to avoid repeated lookups
5. **Batch with delays**: Add 100ms delay between batch operations to avoid rate limits
6. **Idempotent operations**: Design workflows to be safely retryable

## Testing Checklist

### Pre-flight
- [ ] `ATTIO_API_KEY` set in `.env`
- [ ] Dependencies installed (`pip install requests python-dotenv`)
- [ ] Network connectivity to `api.attio.com`
- [ ] Custom attributes exist in Attio workspace (see Custom Attributes table)

### Smoke Test

#### Company Operations
```bash
# Search for an existing company
python scripts/attio_api.py search-companies "Microsoft" --limit 5

# Get company by record ID
python scripts/attio_api.py get-company "YOUR_RECORD_ID"

# Create test company (will be upserted if domain exists)
python scripts/attio_api.py create-company "Test Company $(date +%s)" \
  --domain "testcompany$(date +%s).com" \
  --status "Active Prospect"

# Update company with links
python scripts/attio_api.py update-company "RECORD_ID" \
  --slack-channel "https://example.slack.com/test" \
  --drive-folder "https://drive.google.com/test"
```

#### Person Operations
```bash
# Create test person linked to company
python scripts/attio_api.py create-person "test$(date +%s)@example.com" \
  --first-name "Test" \
  --last-name "User" \
  --company-id "COMPANY_RECORD_ID"
```

#### Note Operations
```bash
# Create note on company
python scripts/attio_api.py create-note "RECORD_ID" "Test Note" "Test content"

# List notes
python scripts/attio_api.py list-notes "RECORD_ID" --limit 5
```

#### URL Parsing
```bash
# Parse Attio URL
python scripts/attio_api.py parse-url "https://app.attio.com/yourworkspace/companies/view/abc-123"
```

### Validation
- [ ] Search returns companies with `record_id` and `name`
- [ ] Get company returns full record with custom attributes
- [ ] Create company returns new `record_id`
- [ ] Assert (upsert) updates existing record or creates new one
- [ ] Update company modifies specified attributes only
- [ ] Create person links to company correctly
- [ ] Notes appear on company record in Attio UI
- [ ] URL parsing extracts `workspace_slug`, `object_type`, `record_id`
- [ ] 401 error returned for invalid API key
- [ ] 404 error returned for non-existent record
