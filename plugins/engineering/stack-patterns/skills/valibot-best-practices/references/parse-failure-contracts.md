# Parse Failure Contracts

Choose Valibot's parsing API from the failure contract at the boundary.

- Use `v.parse` when invalid input violates a contract and the operation must stop.
- Use `v.safeParse` when invalid input is an expected branch that the caller must render, return, or otherwise handle.

```typescript
// A malformed provider response aborts this operation.
const user = v.parse(User, responseBody);

// Invalid user input is an expected branch with explicit issues.
const result = v.safeParse(CreateKpiInput, formData);
if (!result.success) return { issues: result.issues };
const input = result.output;
```

Do not choose `safeParse` only to avoid defining the failure behavior.
