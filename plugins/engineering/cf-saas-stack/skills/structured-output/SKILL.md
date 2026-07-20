---
name: structured-output
description: Structured JSON output patterns for Gemini and Claude AI APIs
user-invocable: false
---

# Structured Output with AI APIs

**ALWAYS use structured JSON output** instead of prompting for JSON and parsing responses manually. This guarantees valid JSON matching your schema.

## Gemini (Google)

### Package
```typescript
// CORRECT - Use the unified SDK
import { GoogleGenAI, Type, type Schema } from "@google/genai";

// WRONG - Deprecated package
import { GoogleGenerativeAI } from "@google/generative-ai";
```

### Current Model
```typescript
const MODEL = "gemini-3-flash-preview";  // Fast, cost-effective
const MODEL = "gemini-3-pro-preview";    // More powerful
```

### Structured Output Pattern
```typescript
import { GoogleGenAI, Type, type Schema } from "@google/genai";

const mySchema: Schema = {
  type: Type.OBJECT,
  properties: {
    title: { type: Type.STRING, description: "The title" },
    count: { type: Type.INTEGER, description: "The count", nullable: true },
    items: {
      type: Type.ARRAY,
      items: {
        type: Type.OBJECT,
        properties: {
          name: { type: Type.STRING },
          value: { type: Type.NUMBER, nullable: true },
        },
        required: ["name"],
      },
    },
  },
  required: ["title", "items"],
};

const response = await client.models.generateContent({
  model: "gemini-3-flash-preview",
  contents: prompt,
  config: {
    responseMimeType: "application/json",
    responseSchema: mySchema,
  },
});
const result = JSON.parse(response.text ?? "");
```

### Type Enum Values
- `Type.STRING`, `Type.INTEGER`, `Type.NUMBER`, `Type.BOOLEAN`, `Type.OBJECT`, `Type.ARRAY`

### Schema Tips
- Use `nullable: true` for optional fields that can be null
- Use `required: [...]` to specify mandatory fields
- Add `description` to help the model understand field purpose

## Claude (Anthropic)

### Structured Output via Tool Use
```typescript
import Anthropic from "@anthropic-ai/sdk";

const extractionTool = {
  name: "extract_data",
  description: "Extract structured data from content",
  input_schema: {
    type: "object" as const,
    properties: {
      title: { type: "string", description: "The title" },
      items: { type: "array", items: { type: "object", properties: { name: { type: "string" }, value: { type: "number" } }, required: ["name"] } },
    },
    required: ["title", "items"],
  },
};

const response = await client.messages.create({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1024,
  tools: [extractionTool],
  tool_choice: { type: "tool", name: "extract_data" },
  messages: [{ role: "user", content: prompt }],
});
const toolUse = response.content.find((block) => block.type === "tool_use");
const result = toolUse?.input;
```

## Best Practices
1. Always use structured output - Don't ask for JSON in prompts and parse manually
2. Define TypeScript interfaces to match your schema for type safety
3. Use descriptive field descriptions
4. Mark nullable fields explicitly
5. Keep schemas focused - one schema per extraction task
