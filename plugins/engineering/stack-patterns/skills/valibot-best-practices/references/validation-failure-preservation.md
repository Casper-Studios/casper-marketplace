# Validation Failure Preservation

Preserve validation failure information. Do not replace invalid input with an arbitrary `null`, empty collection, or invented value.

```typescript
// BAD: converts malformed input into an invented domain value.
const result = v.safeParse(User, input);
const user = result.success ? result.output : null;

// GOOD: surface the expected validation branch.
if (!result.success) return { issues: result.issues };
const user = result.output;
```

Let the caller render, return, log, or otherwise handle the actual validation failure.
