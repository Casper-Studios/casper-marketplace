# Guard Clauses

Reject invalid, unavailable, or exceptional paths at the start of a procedure. Keep the successful path at the lowest nesting level.

```typescript
interface SubmitRequest {
	isAuthenticated: boolean;
	isValid: boolean;
	hasPermission: boolean;
}

// BAD: the main path is nested behind every condition.
function submitNested(request: SubmitRequest) {
	if (request.isAuthenticated)
		if (request.isValid) if (request.hasPermission) return persist(request);
	return reject(request);
}

// GOOD: each exceptional path exits with its own reason.
function submit(request: SubmitRequest) {
	if (!request.isAuthenticated) return rejectUnauthenticated(request);
	if (!request.isValid) return rejectInvalid(request);
	if (!request.hasPermission) return rejectForbidden(request);
	return persist(request);
}
```

Do not force unrelated failures through one generic fallback. Each guard must preserve the reason that stopped execution.
