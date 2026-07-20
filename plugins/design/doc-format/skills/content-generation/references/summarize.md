# Content Summarization

## Overview
Summarize long-form content using AI.

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `content` | string | Yes | Text to summarize |
| `style` | string | No | bullet, paragraph, executive |
| `length` | string | No | short, medium, long |
| `focus` | string | No | Specific aspects to highlight |

## CLI Usage

```bash
# Basic summary
python scripts/summarize_content.py --input document.txt

# Bullet point summary
python scripts/summarize_content.py --input transcript.txt --style bullet

# Executive summary
python scripts/summarize_content.py --input report.md --style executive --length short

# Focus on specific topic
python scripts/summarize_content.py --input meeting.txt --focus "action items"
```

## Output Structure

```json
{
  "summary": "Summary text here...",
  "key_points": ["Point 1", "Point 2"],
  "word_count": {
    "original": 5000,
    "summary": 250
  }
}
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

### Basic Summarization
```python
def summarize(content: str, style: str = "paragraph", length: str = "medium") -> dict:
    length_guide = {
        "short": "2-3 sentences",
        "medium": "1-2 paragraphs",
        "long": "3-4 paragraphs"
    }

    style_guide = {
        "bullet": "Format as a bullet point list of key points",
        "paragraph": "Write as flowing prose",
        "executive": "Write a high-level executive summary for stakeholders"
    }

    response = client.chat.completions.create(
        model="anthropic/claude-3.5-sonnet",
        messages=[
            {
                "role": "system",
                "content": f"You are a professional summarizer. {style_guide.get(style, style_guide['paragraph'])}. Keep the summary to {length_guide.get(length, length_guide['medium'])}."
            },
            {
                "role": "user",
                "content": f"Summarize the following content:\n\n{content}"
            }
        ]
    )

    summary = response.choices[0].message.content

    return {
        "summary": summary,
        "word_count": {
            "original": len(content.split()),
            "summary": len(summary.split())
        }
    }

# Usage
result = summarize("Long article text here...", style="bullet", length="short")
print(result["summary"])
```

### Extract Key Points
```python
def extract_key_points(content: str, num_points: int = 5) -> list:
    response = client.chat.completions.create(
        model="anthropic/claude-3.5-sonnet",
        messages=[
            {
                "role": "system",
                "content": f"Extract exactly {num_points} key points from the content. Return as a JSON array of strings."
            },
            {
                "role": "user",
                "content": content
            }
        ],
        response_format={"type": "json_object"}
    )

    import json
    result = json.loads(response.choices[0].message.content)
    return result.get("key_points", result.get("points", []))

# Usage
points = extract_key_points("Long document text...", num_points=5)
for i, point in enumerate(points, 1):
    print(f"{i}. {point}")
```

### Focused Summarization
```python
def summarize_with_focus(content: str, focus: str) -> dict:
    response = client.chat.completions.create(
        model="anthropic/claude-3.5-sonnet",
        messages=[
            {
                "role": "system",
                "content": f"Summarize the content, focusing specifically on: {focus}. Ignore information not related to this focus area."
            },
            {
                "role": "user",
                "content": content
            }
        ]
    )

    return {
        "summary": response.choices[0].message.content,
        "focus": focus
    }

# Usage
result = summarize_with_focus(meeting_notes, focus="action items and deadlines")
```

### Chunked Summarization for Long Documents
```python
def summarize_long_document(content: str, chunk_size: int = 4000) -> str:
    # Split content into chunks
    words = content.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(' '.join(words[i:i + chunk_size]))

    # Summarize each chunk
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...")
        result = summarize(chunk, style="paragraph", length="short")
        chunk_summaries.append(result["summary"])

    # Combine and summarize the summaries
    combined = "\n\n".join(chunk_summaries)
    final_result = summarize(combined, style="paragraph", length="medium")

    return final_result["summary"]

# Usage
long_doc = open("large_document.txt").read()
summary = summarize_long_document(long_doc)
```

### Complete Summarization with All Outputs
```python
def full_summarize(content: str, style: str = "paragraph", length: str = "medium", focus: str = None) -> dict:
    # Build system prompt
    system_parts = ["You are a professional content summarizer."]

    if style == "bullet":
        system_parts.append("Format the summary as bullet points.")
    elif style == "executive":
        system_parts.append("Write an executive summary suitable for stakeholders.")

    length_map = {"short": "2-3 sentences", "medium": "1-2 paragraphs", "long": "3-4 paragraphs"}
    system_parts.append(f"Keep the summary to approximately {length_map.get(length, length_map['medium'])}.")

    if focus:
        system_parts.append(f"Focus specifically on: {focus}")

    system_parts.append("Also extract 3-5 key points. Return JSON with 'summary' and 'key_points' fields.")

    response = client.chat.completions.create(
        model="anthropic/claude-3.5-sonnet",
        messages=[
            {"role": "system", "content": " ".join(system_parts)},
            {"role": "user", "content": content}
        ],
        response_format={"type": "json_object"}
    )

    import json
    result = json.loads(response.choices[0].message.content)

    return {
        "summary": result.get("summary", ""),
        "key_points": result.get("key_points", []),
        "word_count": {
            "original": len(content.split()),
            "summary": len(result.get("summary", "").split())
        }
    }

# Usage
result = full_summarize(
    content="Long article text...",
    style="executive",
    length="short",
    focus="financial metrics"
)
print(result)
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

## Summary Styles

| Style | Format |
|-------|--------|
| `bullet` | Key points as bullet list |
| `paragraph` | Flowing prose summary |
| `executive` | High-level overview for stakeholders |

## Prompting Best Practices

### Summarization Styles
| Style | Use Case | Prompt |
|-------|----------|--------|
| Executive | C-suite briefings | "Summarize for executives, focus on business impact" |
| Technical | Engineering docs | "Summarize technical details, include specifics" |
| Action-oriented | Meeting notes | "Extract action items and decisions" |

### Length Control
- **Brief**: "In 2-3 sentences..."
- **Detailed**: "Provide a comprehensive summary covering..."
- **Bullet points**: "Summarize as bullet points..."

### Focus Prompts
```
"Focus specifically on: [topic1], [topic2], ignore [topic3]"
```

### Audience-Specific Prompts
| Audience | Prompt Modifier |
|----------|-----------------|
| Executives | "Focus on strategic implications and ROI" |
| Engineers | "Include technical specifications and dependencies" |
| Sales | "Highlight customer benefits and competitive advantages" |
| Legal | "Focus on risks, compliance, and contractual terms" |

### Extraction Patterns
```
# Action items
"Extract all action items with owners and deadlines"

# Decisions
"List all decisions made and their rationale"

# Key metrics
"Summarize with focus on quantitative data and metrics"

# Risks and issues
"Highlight risks, blockers, and open questions"
```

### Common Mistakes
1. No length guidance: AI produces overly long summaries
2. Missing focus: Summary covers everything equally
3. Wrong audience: Technical summary for executives
4. No structure request: Unorganized output

## Cost
~$0.001-0.01 depending on content length

## Testing Checklist

### Pre-flight
- [ ] `OPENROUTER_API_KEY` set in `.env`
- [ ] Dependencies installed (`pip install openai python-dotenv`)
- [ ] Test content file exists

### Smoke Test
```bash
# Basic summary from file
python scripts/summarize_content.py --input test_document.txt

# Bullet point summary
python scripts/summarize_content.py --input long_article.txt --style bullet

# Executive summary (short)
python scripts/summarize_content.py --input report.md --style executive --length short

# With specific focus
python scripts/summarize_content.py --input meeting_notes.txt --focus "action items and decisions"

# Direct text input
python scripts/summarize_content.py --text "Long text to summarize goes here..."
```

### Validation
- [ ] Response contains `summary`, `key_points`, `word_count`
- [ ] `summary` is coherent and captures main points
- [ ] `key_points` array contains distinct bullet points
- [ ] `word_count.original` matches input length
- [ ] `word_count.summary` is significantly less than original
- [ ] `--style bullet` produces bullet-formatted output
- [ ] `--style executive` produces high-level overview
- [ ] `--length short/medium/long` affects summary length
- [ ] `--focus` parameter narrows summary scope
- [ ] No hallucinated content (facts match original)
- [ ] Cost: ~$0.001 for short docs, ~$0.01 for long docs

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid OpenRouter API key | Verify `OPENROUTER_API_KEY` in .env |
| `429 Rate Limited` | Too many AI requests | Wait and retry with exponential backoff |
| `Input file not found` | Specified file doesn't exist | Verify file path |
| `Content too long` | Exceeds model context window | Chunk content and summarize incrementally |
| `Empty content` | No text to summarize | Provide non-empty input |
| `Invalid style` | Unknown summary style | Use: bullet, paragraph, executive |
| `Invalid length` | Unknown length option | Use: short, medium, long |
| `Model unavailable` | AI model is down | Try alternative model via OpenRouter |

### Recovery Strategies

1. **Automatic retry**: Implement exponential backoff (1s, 2s, 4s) for rate limits
2. **Content chunking**: For long documents, split and summarize chunks, then combine
3. **Model fallback**: If primary model fails, try Claude -> GPT-4 -> GPT-3.5
4. **Length estimation**: Pre-calculate token count to avoid context overflow
5. **Input validation**: Verify file exists and has content before processing
6. **Caching**: Cache summaries to avoid reprocessing same content
