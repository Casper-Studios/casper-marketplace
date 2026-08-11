# Parse Failure Contracts

Choose Zod's parsing API from the failure contract at the boundary.

- Use `.parse` when invalid input violates a contract and the operation must stop.
- Use `.safeParse` when invalid input is an expected branch that the caller must render, return, or otherwise handle.

```typescript
// A malformed provider response aborts this operation.
const user = User.parse(responseBody);

// Invalid user input is an expected branch with explicit issues.
const result = CreateKpiInput.safeParse(formData);
if (!result.success) return { issues: result.error.issues };
const input = result.data;
```

Do not choose `safeParse` only to avoid defining the failure behavior.
