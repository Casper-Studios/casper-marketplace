# Flowchart Generator

## Overview
Generate Mermaid diagrams from natural language descriptions.

## Diagram Types

| Type | Use Case |
|------|----------|
| `flowchart` | Process flows, decision trees |
| `sequence` | API calls, system interactions |
| `state` | Status transitions |
| `journey` | User experience maps |
| `gantt` | Project timelines |
| `mindmap` | Concept hierarchies |

## Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `description` | string | required | Natural language process |
| `diagram_type` | string | flowchart | Type of diagram |
| `direction` | string | TB | TB, BT, LR, RL |
| `theme` | string | default | default, dark, forest, neutral |
| `output_formats` | list | [svg] | svg, png, pdf, md |

## CLI Usage

```bash
# Simple flowchart
python scripts/generate_flowchart.py "login: enter email, validate, check password, if correct dashboard, if wrong error"

# Sequence diagram
python scripts/generate_flowchart.py "API: frontend calls backend, backend calls Stripe, returns confirmation" --type sequence

# Left-to-right, dark theme
python scripts/generate_flowchart.py "approval: submit, review, approve or reject" --direction LR --theme dark
```

## Python Usage

### OpenRouter Client Setup
```python
import os
import openai

client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"]
)
```

### Generate Mermaid from Description
```python
def generate_mermaid(description: str, diagram_type: str = "flowchart") -> str:
    response = client.chat.completions.create(
        model="anthropic/claude-3.5-sonnet",
        messages=[
            {
                "role": "system",
                "content": f"You are a Mermaid diagram expert. Generate valid {diagram_type} syntax."
            },
            {
                "role": "user",
                "content": f"Create a Mermaid {diagram_type} for: {description}"
            }
        ]
    )
    return response.choices[0].message.content

# Example usage
mermaid_code = generate_mermaid(
    "login flow: user enters email, validate format, check password, if correct go to dashboard, if wrong show error",
    "flowchart"
)
print(mermaid_code)
```

### Render Mermaid to SVG (using subprocess)
```python
import subprocess
from pathlib import Path

def render_mermaid(mermaid_code: str, output_path: str = "diagram.svg") -> str:
    # Save Mermaid code to temp file
    mmd_path = Path(output_path).with_suffix(".mmd")
    mmd_path.write_text(mermaid_code)

    # Render using Mermaid CLI (requires: npm install -g @mermaid-js/mermaid-cli)
    subprocess.run([
        "mmdc",
        "-i", str(mmd_path),
        "-o", output_path,
        "-t", "default"
    ], check=True)

    return output_path

# Example
svg_path = render_mermaid(mermaid_code, ".tmp/flowchart.svg")
```

### Complete Workflow
```python
import os
import openai
import subprocess
from pathlib import Path
from datetime import datetime

def create_flowchart(description: str, diagram_type: str = "flowchart", theme: str = "default"):
    # Setup client
    client = openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"]
    )

    # Generate Mermaid code
    response = client.chat.completions.create(
        model="anthropic/claude-3.5-sonnet",
        messages=[
            {"role": "system", "content": f"Generate only valid Mermaid {diagram_type} code. No explanations."},
            {"role": "user", "content": description}
        ]
    )
    mermaid_code = response.choices[0].message.content

    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f".tmp/flowcharts/{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save Mermaid source
    mmd_path = output_dir / "diagram.mmd"
    mmd_path.write_text(mermaid_code)

    # Render to SVG
    svg_path = output_dir / "diagram.svg"
    subprocess.run(["mmdc", "-i", str(mmd_path), "-o", str(svg_path), "-t", theme], check=True)

    return {"mermaid": mermaid_code, "svg_path": str(svg_path)}

# Usage
result = create_flowchart("user registration: enter details, validate, create account, send confirmation email")
print(result["svg_path"])
```

## Model Comparison

### OpenRouter Models for Text Generation

| Model | Speed | Quality | Cost/1K tokens | Best For |
|-------|-------|---------|----------------|----------|
| `anthropic/claude-3.5-sonnet` | Fast | Highest | $0.003/$0.015 | Complex analysis |
| `anthropic/claude-3-haiku` | Fastest | Good | $0.00025/$0.00125 | Simple tasks |
| `openai/gpt-4o` | Fast | High | $0.005/$0.015 | General purpose |
| `openai/gpt-4o-mini` | Fast | Good | $0.00015/$0.0006 | Budget tasks |
| `google/gemini-pro-1.5` | Medium | High | $0.00125/$0.005 | Long context |
| `meta-llama/llama-3.1-70b` | Medium | Good | $0.0008/$0.0008 | Open source |

### When to Use Each
- **High quality, complex**: Claude 3.5 Sonnet - best reasoning
- **Fast and cheap**: GPT-4o-mini or Haiku - quick tasks
- **Long documents**: Gemini Pro 1.5 - 1M token context
- **Open source**: Llama 3.1 70B - self-hostable

### Cost Optimization
```python
# Use cheaper model for simple tasks
model = "openai/gpt-4o-mini"  # Simple summarization

# Use premium model for complex analysis
model = "anthropic/claude-3.5-sonnet"  # Nuanced proposals
```

## Output Files

```
.tmp/flowcharts/{timestamp}/
├── diagram.mmd   # Mermaid source
├── diagram.svg   # Vector graphic
├── diagram.png   # Raster (if requested)
└── metadata.json # Generation details
```

## Writing Good Descriptions

- Be explicit about decisions: "if X then Y, otherwise Z"
- Name your steps: "validate email" not "validation"
- Specify actors: "user clicks", "system processes"
- Include edge cases: "if error, show message"

## Prompting Best Practices

### Describing Flowcharts
Be explicit about:
1. **Flow type**: Process, decision tree, sequence, state machine
2. **Nodes**: What each box represents
3. **Connections**: Direction and conditions
4. **Layout**: Top-down (TD), left-right (LR)

### Effective Descriptions
```
# Good
"Create a flowchart for user login:
1. User enters credentials
2. System validates → if invalid, show error
3. If valid, check 2FA enabled
4. If 2FA, send code and verify
5. Grant access or deny"

# Bad
"Make a login flowchart"
```

### Diagram Type Selection
| Description Pattern | Use Diagram Type |
|---------------------|------------------|
| Sequential steps with decisions | flowchart |
| API calls between services | sequence |
| Object state changes | state |
| User experience flow | journey |
| Project timeline with tasks | gantt |
| Hierarchical concepts | mindmap |

### Direction Guidelines
| Direction | Use Case |
|-----------|----------|
| TB (top-bottom) | Process flows, hierarchies |
| LR (left-right) | Timelines, pipelines |
| BT (bottom-top) | Build-up processes |
| RL (right-left) | Reverse flows |

### Common Mistakes
1. Vague descriptions: "make a flowchart" - no context
2. Missing decision outcomes: "check if valid" - what happens next?
3. Unclear actors: "data is processed" - by whom?
4. No error paths: only happy path described

## Cost
~$0.002-0.01 per diagram (AI inference only)

## Testing Checklist

### Pre-flight
- [ ] `OPENROUTER_API_KEY` set in `.env` (for AI inference)
- [ ] Dependencies installed (`pip install openai python-dotenv`)
- [ ] Mermaid CLI available for rendering (`npm install -g @mermaid-js/mermaid-cli`)

### Smoke Test
```bash
# Simple flowchart
python scripts/generate_flowchart.py "start, process data, end"

# Decision flowchart
python scripts/generate_flowchart.py "login: enter credentials, if valid then dashboard, else error message"

# Sequence diagram
python scripts/generate_flowchart.py "user calls API, API validates token, returns data" --type sequence

# Different direction and theme
python scripts/generate_flowchart.py "step1, step2, step3" --direction LR --theme dark
```

### Validation
- [ ] Output directory created at `.tmp/flowcharts/{timestamp}/`
- [ ] `diagram.mmd` contains valid Mermaid syntax
- [ ] `diagram.svg` renders correctly (open in browser)
- [ ] Diagram type matches `--type` parameter
- [ ] Direction (TB/LR) applied correctly
- [ ] Theme styling applied
- [ ] Decision branches (`if/else`) rendered correctly
- [ ] No syntax errors in Mermaid output
- [ ] `metadata.json` contains generation details

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid OpenRouter API key | Verify `OPENROUTER_API_KEY` in .env |
| `429 Rate Limited` | Too many AI requests | Wait and retry with exponential backoff |
| `Mermaid syntax error` | AI generated invalid Mermaid | Retry generation with clearer description |
| `Mermaid CLI not found` | mmdc not installed | Install: `npm install -g @mermaid-js/mermaid-cli` |
| `Rendering failed` | SVG/PNG generation error | Check Mermaid syntax, simplify diagram |
| `Invalid diagram type` | Unsupported type specified | Use: flowchart, sequence, state, journey, gantt, mindmap |
| `Description too vague` | AI couldn't parse description | Add more specific steps and decision points |
| `Output directory error` | Cannot create output folder | Check disk permissions and space |

### Recovery Strategies

1. **Automatic retry**: Retry AI generation up to 3 times for syntax errors
2. **Syntax validation**: Validate Mermaid syntax before rendering
3. **Fallback to simple**: If complex diagram fails, simplify and retry
4. **Manual fix prompt**: Provide error back to AI to fix specific syntax issues
5. **Template fallback**: Use pre-defined templates for common diagram types
6. **Multiple formats**: If SVG fails, try PNG; if rendering fails, return raw .mmd file
