# ElevenLabs Voice Agent API

## API Endpoint
`POST https://api.elevenlabs.io/v1/convai/agents/create`

## Authentication
Header: `xi-api-key: $ELEVENLABS_API_KEY`

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `company_name` | string | Yes | Client company name |
| `scope` | string | Yes | Agent purpose |
| `notes` | string | Yes | Additional context |

## CLI Usage

```bash
# Create discovery agent
python scripts/create_voice_agent.py "Microsoft" --scope discovery --notes "CRM migration project"

# Create feedback agent
python scripts/create_voice_agent.py "Acme Corp" --scope feedback --notes "Post-project review"

# Dry run (preview config, don't create)
python scripts/create_voice_agent.py "Test Company" --scope discovery --notes "Testing" --dry-run

# Output as JSON
python scripts/create_voice_agent.py "Company" --scope discovery --notes "Notes" --json
```

## Python Usage

### Install SDK
```bash
pip install elevenlabs
```

### Create Conversational Agent
```python
import os
import requests

ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]

# Create agent via API
response = requests.post(
    "https://api.elevenlabs.io/v1/convai/agents/create",
    headers={
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    },
    json={
        "name": "[Microsoft] Discovery Agent v1",
        "conversation_config": {
            "agent": {
                "prompt": {
                    "prompt": "You are a discovery call agent...",
                },
                "first_message": "Hi there! This is an AI assistant...",
                "language": "en"
            }
        }
    }
)

agent = response.json()
print(f"Agent ID: {agent['agent_id']}")
print(f"URL: https://elevenlabs.io/app/conversational-ai/agents/{agent['agent_id']}")
```

### Using elevenlabs Package
```python
from elevenlabs import ElevenLabs

client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

# Text-to-speech (for reference)
audio = client.generate(
    text="Hello, this is a test.",
    voice="Rachel",
    model="eleven_monolingual_v1"
)
```

## Scope Descriptions

### Discovery
Interview client team to understand:
- Current operations and workflows
- Pain points and bottlenecks
- Technology stack
- Team structure
- Goals and success criteria

### Feedback
Gather feedback on completed work:
- Project satisfaction
- What worked well
- Areas for improvement
- Future needs
- Referral potential

### Check-in
Relationship maintenance:
- Current status update
- New challenges
- Upcoming needs
- General satisfaction

### Qualification
Lead qualification:
- Company background
- Current needs
- Budget range
- Timeline
- Decision process

### Onboarding
New contact information gathering:
- Role and responsibilities
- Key stakeholders
- Project background
- Communication preferences

## Agent Generation Flow

```
1. Find client folder in Google Drive (optional)
   └── Fetch "Research" document
   └── Find intro meeting transcript

2. Generate agent config using AI:
   └── Agent name: "[Company] Scope Agent v1"
   └── First message: Voice-optimized greeting
   └── Prompt: Comprehensive conversation guide

3. Create ElevenLabs agent via API

4. Return agent details with URL
```

## Generated Prompt Structure

The AI generates a system prompt with:

1. **Identity** - Who the agent represents
2. **Context** - Client background and project
3. **Tone** - Professional, conversational, empathetic
4. **Flow** - 5-7 conversation stages
5. **Techniques** - Open questions, active listening
6. **Guardrails** - Topics to avoid, boundaries
7. **Behavior** - Response length, follow-ups

## Graceful Degradation

The script continues even if optional data is missing:
- No research document → Uses basic context
- No transcript → Generates without history
- Client folder not found → Uses provided notes only

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid ElevenLabs API key | Verify `ELEVENLABS_API_KEY` in .env |
| `402 Payment Required` | ElevenLabs quota exhausted | Upgrade plan or wait for quota reset |
| `429 Rate Limited` | Too many requests | Wait and retry with exponential backoff |
| `Agent creation failed` | Invalid agent config | Check prompt length, first message format |
| `Invalid scope` | Unknown scope type | Use: discovery, feedback, check-in, qualification, onboarding |
| `OpenRouter API error` | AI model unavailable | Check `OPENROUTER_API_KEY`, retry with fallback model |
| `Client folder not found` | No matching Drive folder | Uses provided notes only (graceful degradation) |
| `Research document not found` | No research doc in folder | Generates without research context |
| `Transcript not found` | No meeting transcript available | Generates without conversation history |
| `Prompt generation failed` | AI failed to generate valid prompt | Retry, or use default prompt template |
| `Missing required field` | Company, scope, or notes empty | All three required fields must be provided |
| `Voice configuration error` | Invalid voice settings | Use default ElevenLabs voice |

### Recovery Strategies

1. **Automatic retry**: Implement exponential backoff (5s, 10s, 20s) for rate limits
2. **Graceful degradation**: Continue with available data if optional fields missing
3. **Prompt fallback**: If AI generation fails, use scope-specific template prompt
4. **Model fallback**: If primary OpenRouter model fails, try Claude -> GPT-4 -> GPT-3.5
5. **Validation first**: Validate all inputs before API calls
6. **Dry run support**: Use `--dry-run` to preview config before creating
7. **Cost protection**: Check ElevenLabs quota before creating agents

## Output

```json
{
  "agent_id": "abc123xyz",
  "agent_name": "[Microsoft] Discovery Agent v1",
  "agent_url": "https://elevenlabs.io/app/conversational-ai/agents/abc123xyz",
  "first_message": "Hi there! This is an AI assistant calling on behalf of Casper Studios. Am I speaking with the right person regarding the CRM migration project?",
  "company_name": "Microsoft",
  "scope": "discovery"
}
```

## Related Skills
- `google-workspace` - Client folder and document access
- `transcript-search` - Meeting transcript retrieval

## Testing Checklist

### Pre-flight
- [ ] `ELEVENLABS_API_KEY` set in `.env`
- [ ] `OPENROUTER_API_KEY` set in `.env` (for prompt generation)
- [ ] Google Drive OAuth credentials available (optional, for client context)
- [ ] Dependencies installed (`pip install requests python-dotenv`)
- [ ] Network connectivity to `api.elevenlabs.io`

### Smoke Test
```bash
# Dry run - preview agent config without creating
python scripts/create_voice_agent.py "Test Company" --scope discovery --notes "Testing agent creation" --dry-run

# Create discovery agent
python scripts/create_voice_agent.py "Test Company $(date +%s)" --scope discovery --notes "Initial discovery call for demo project"

# Create feedback agent
python scripts/create_voice_agent.py "Test Company $(date +%s)" --scope feedback --notes "Post-project feedback collection"

# JSON output for parsing
python scripts/create_voice_agent.py "Test Company" --scope qualification --notes "Lead qualification" --json --dry-run

# Test all scope types
python scripts/create_voice_agent.py "Test" --scope check-in --notes "Quarterly check-in" --dry-run
python scripts/create_voice_agent.py "Test" --scope onboarding --notes "New contact onboarding" --dry-run
```

### Validation
- [ ] Response contains `agent_id`, `agent_name`, `agent_url`
- [ ] `agent_url` is valid ElevenLabs URL (accessible in browser)
- [ ] `agent_name` follows format `[Company] Scope Agent v1`
- [ ] `first_message` is voice-optimized (natural speaking)
- [ ] Generated prompt includes all sections (Identity, Context, Tone, Flow, etc.)
- [ ] `--dry-run` shows config but doesn't create agent
- [ ] `--json` output is valid JSON
- [ ] Each scope type generates appropriate conversation guide:
  - Discovery: operational questions
  - Feedback: satisfaction questions
  - Check-in: status update questions
  - Qualification: budget/timeline questions
  - Onboarding: role/stakeholder questions
- [ ] Missing client folder triggers graceful degradation (uses notes only)
- [ ] 401 error returned for invalid ElevenLabs API key
- [ ] OpenRouter errors handled gracefully

### Agent Quality Checks
```bash
# After creating a test agent:
# 1. Visit agent_url in browser
# 2. Test conversation flow
# 3. Verify first_message sounds natural
# 4. Confirm tone matches scope type
```

### Cleanup
```bash
# Delete test agents from ElevenLabs dashboard
# https://elevenlabs.io/app/conversational-ai/agents
```
