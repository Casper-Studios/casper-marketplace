# Type Escape Hatches

Do not use `any` or broad `object` as placeholders. They erase type information that callers need. Use `unknown` only for genuinely untrusted input or a caught error, then narrow or validate it in the same boundary-handling code.

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

Do not carry `unknown` into domain state, parameters, or return values.
