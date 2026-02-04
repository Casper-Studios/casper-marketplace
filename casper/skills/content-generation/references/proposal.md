# Proposal Generator

## Overview
AI agent that creates client proposals from meeting transcripts, with web research for context enrichment.

## Template Structure

1. **Header** - Logo + title
2. **Context** - Partnership opportunity
3. **Problem Statement & Objectives** - Challenges + goals
4. **Proposed Approach** - Work streams with workflow mapping
5. **Estimated Cost** - Price + scope
6. **Staffing** - Team table (optional)
7. **Expected Outcomes** - Benefits list
8. **About Casper Studios** - Boilerplate
9. **Next Steps** - Action items

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `transcript` | string | Yes | Meeting notes |
| `client_name` | string | Yes | Company name |
| `project_name` | string | No | Default: "AI Automation" |
| `folder_id` | string | No | Drive destination |

## CLI Usage

```bash
# From transcript file
python scripts/generate_proposal.py \
    --transcript-file meeting.txt \
    --client "Acme Corp" \
    --project "Lead Scoring"

# Direct transcript
python scripts/generate_proposal.py \
    --transcript "Meeting notes..." \
    --client "Acme Corp"
```

## AI Agent Tools

The agent autonomously uses:
- `research_client` - Company background
- `search_tool_url` - Hyperlink software mentions
- `research_industry_trends` - Industry context
- `get_current_date` - Date references

## Python Usage

### OpenRouter Setup for AI Generation
```python
import os
import openai

client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"]
)
```

### Generate Proposal Content from Transcript
```python
def generate_proposal_content(transcript: str, client_name: str) -> dict:
    system_prompt = """You are a proposal writer for Casper Studios, an AI automation agency.
    Generate a structured proposal with these sections:
    1. Context - Partnership opportunity
    2. Problem Statement & Objectives
    3. Proposed Approach - Work streams
    4. Estimated Cost
    5. Expected Outcomes
    6. Next Steps

    Return as JSON with keys: context, problem_statement, objectives, approach, cost, outcomes, next_steps"""

    response = client.chat.completions.create(
        model="anthropic/claude-3.5-sonnet",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Client: {client_name}\n\nTranscript:\n{transcript}"}
        ],
        response_format={"type": "json_object"}
    )

    import json
    return json.loads(response.choices[0].message.content)

# Usage
transcript = "Met with Acme Corp about automating their lead qualification process..."
content = generate_proposal_content(transcript, "Acme Corp")
```

### Research Client with Parallel AI
```python
import requests
import os

def research_client(company_name: str) -> str:
    response = requests.post(
        "https://api.parallel.ai/v1/chat",
        headers={"Authorization": f"Bearer {os.environ['PARALLEL_API_KEY']}"},
        json={
            "model": "research",
            "messages": [{"role": "user", "content": f"Research {company_name}: industry, size, recent news"}]
        }
    )
    return response.json()["choices"][0]["message"]["content"]

# Usage
company_info = research_client("Acme Corp")
```

### Create Proposal in Google Docs
```python
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def create_proposal_doc(title: str, content: dict, client_name: str) -> dict:
    creds = Credentials.from_authorized_user_file('mycreds.txt')
    docs_service = build('docs', 'v1', credentials=creds)

    # Create document
    doc = docs_service.documents().create(body={'title': title}).execute()
    doc_id = doc['documentId']

    # Build document structure
    requests = []
    index = 1

    # Title
    title_text = f"Proposal: {client_name}\n\n"
    requests.append({'insertText': {'location': {'index': index}, 'text': title_text}})
    index += len(title_text)

    # Sections
    sections = [
        ("Context", content.get('context', '')),
        ("Problem Statement & Objectives", content.get('problem_statement', '')),
        ("Proposed Approach", content.get('approach', '')),
        ("Estimated Cost", content.get('cost', '')),
        ("Expected Outcomes", content.get('outcomes', '')),
        ("Next Steps", content.get('next_steps', ''))
    ]

    for header, body in sections:
        header_text = f"\n{header}\n"
        requests.append({'insertText': {'location': {'index': index}, 'text': header_text}})
        index += len(header_text)

        body_text = f"{body}\n"
        requests.append({'insertText': {'location': {'index': index}, 'text': body_text}})
        index += len(body_text)

    docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

    return {
        'document_id': doc_id,
        'document_url': f"https://docs.google.com/document/d/{doc_id}/edit"
    }
```

### Complete Proposal Generation Workflow
```python
def generate_proposal(transcript: str, client_name: str, project_name: str = "AI Automation") -> dict:
    # Step 1: Research client
    print("Researching client...")
    client_info = research_client(client_name)

    # Step 2: Generate proposal content
    print("Generating proposal content...")
    enriched_transcript = f"{transcript}\n\nClient Research:\n{client_info}"
    content = generate_proposal_content(enriched_transcript, client_name)

    # Step 3: Create Google Doc
    print("Creating document...")
    title = f"{client_name} - {project_name} Proposal"
    result = create_proposal_doc(title, content, client_name)

    print(f"Proposal created: {result['document_url']}")
    return result

# Usage
result = generate_proposal(
    transcript="Meeting with Acme Corp about automating email workflows...",
    client_name="Acme Corp",
    project_name="Email Automation"
)
```

## Pricing Reference

| Project Type | Price Range | Timeline |
|--------------|-------------|----------|
| Simple automation | $10,000-20,000 | 2-4 weeks |
| Multi-workflow | $20,000-40,000 | 4-8 weeks |
| Internal tool | $40,000-80,000 | 2-3 months |
| MVP product | $80,000-150,000 | 3-4 months |

## Prompting Best Practices

### Proposal Tone
- Professional but approachable
- Confident without being arrogant
- Specific to client's industry

### Key Elements to Include
1. Client's pain points (from discovery)
2. Proposed solution with specifics
3. Expected outcomes with metrics
4. Timeline and milestones
5. Investment (not "cost")

### Customization Prompts
```
"Write for [industry], emphasizing [their priority],
addressing their concern about [specific worry]"
```

### Industry-Specific Language
| Industry | Emphasize | Avoid |
|----------|-----------|-------|
| Healthcare | Compliance, patient outcomes | "Disruption" |
| Finance | Risk mitigation, ROI | Overpromising |
| Tech | Innovation, scalability | Jargon overload |
| Manufacturing | Efficiency, cost savings | Abstract benefits |

### Section-Specific Prompts
```
# Problem Statement
"Frame the problem in client's own words from the transcript"

# Proposed Approach
"Include specific deliverables, not vague 'solutions'"

# Expected Outcomes
"Quantify benefits: time saved, cost reduced, revenue impact"

# Next Steps
"Include concrete actions with clear ownership"
```

### Transcript Analysis
Before generating, extract:
- Client's stated challenges
- Budget signals or constraints
- Timeline expectations
- Decision makers mentioned
- Competitive alternatives considered

### Common Mistakes
1. Generic proposals: No client-specific details
2. Feature dumping: Listing capabilities vs. solving problems
3. Vague outcomes: "Improved efficiency" vs. "30% time reduction"
4. Missing urgency: No reason to act now
5. Cost focus: "Cost" vs. "Investment" framing

## Cost
~$0.07-0.15 per proposal (AI + research)

## Testing Checklist

### Pre-flight
- [ ] `OPENROUTER_API_KEY` set in `.env` (for AI agent)
- [ ] `PARALLEL_API_KEY` set in `.env` (for research)
- [ ] Google Docs API enabled and OAuth credentials available
- [ ] Dependencies installed (`pip install openai google-api-python-client python-dotenv`)

### Smoke Test
```bash
# Test with minimal transcript
python scripts/generate_proposal.py \
    --transcript "Met with client about automating their email workflow. They have 5 team members." \
    --client "Test Company"

# Test with transcript file
python scripts/generate_proposal.py \
    --transcript-file .tmp/test_transcript.txt \
    --client "Acme Corp" \
    --project "Email Automation"

# Test with specific folder destination
python scripts/generate_proposal.py \
    --transcript "Brief meeting notes" \
    --client "TestClient" \
    --folder-id "1abc123xyz"
```

### Validation
- [ ] Proposal created in Google Docs
- [ ] Document URL returned and accessible
- [ ] Header section includes Casper Studios branding
- [ ] Context section mentions client name
- [ ] Problem Statement derived from transcript
- [ ] Proposed Approach includes relevant work streams
- [ ] Estimated Cost falls within pricing reference ranges
- [ ] About Casper Studios boilerplate included
- [ ] Next Steps section has actionable items
- [ ] AI tools used: `research_client` fetches company info
- [ ] External software mentions are hyperlinked
- [ ] Total cost ~$0.07-0.15 (check OpenRouter dashboard)

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `OpenRouter API error` | AI model unavailable | Check API key, try different model |
| `Parallel AI error` | Research API failed | Continue without enriched research |
| `Invalid credentials` | Google OAuth expired | Re-authenticate for Docs access |
| `Transcript too short` | Not enough content to generate | Provide more detailed meeting notes |
| `Client not found` | Company research returned no results | Continue with provided client name only |
| `Folder not found` | Invalid Drive folder_id | Verify folder ID, create in root instead |
| `Document creation failed` | Google Docs API error | Retry, check API quota |
| `Tool execution failed` | AI agent tool returned error | Log error, continue with available data |

### Recovery Strategies

1. **Graceful degradation**: If research fails, generate proposal with available data
2. **Tool fallbacks**: If one AI tool fails, skip and continue with others
3. **Retry with backoff**: Retry API calls up to 3 times with exponential backoff
4. **Partial proposals**: Return partial proposal if some sections fail
5. **Cost protection**: Set maximum AI cost per proposal and abort if exceeded
6. **Transcript validation**: Check transcript length/content before starting
