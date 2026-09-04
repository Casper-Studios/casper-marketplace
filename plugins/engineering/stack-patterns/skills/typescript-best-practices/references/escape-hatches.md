# Type Escape Hatches

Do not use `any` or broad `object` as placeholders. They erase type information that callers need. Accept `unknown` only at a genuinely untrusted boundary or for a caught error, then narrow or validate it in that boundary-handling code.

```typescript
// BAD: disables checking.
function parseResponse(value: any) {}

// BAD: does not describe readable properties.
function logPayload(value: object) {}

// GOOD: untrusted input is narrowed immediately.
function parseResponse(value: unknown) {
	return v.parse(ResponseSchema, value);
}

// GOOD: caught values are narrowed before use.
if (error instanceof Error) logger.error(error.message);
```

Contain `any` and `unknown` inside the boundary that receives them. Return only narrowed or validated values; never let an escape hatch propagate to callers or into domain state and parameters.
