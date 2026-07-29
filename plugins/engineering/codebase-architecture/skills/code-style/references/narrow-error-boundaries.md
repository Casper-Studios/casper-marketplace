# Narrow Error Boundaries

Catch only an expected failure from the smallest operation that can produce it. Preserve unexpected failures and their original causes.

```typescript
// BAD: a broad catch hides request-building and persistence defects.
async function loadBroadly() {
	try {
		const request = buildRequest(input);
		const response = await send(request);
		await save(response);
	} catch {
		return emptyResult;
	}
}

// GOOD: only the expected network failure is translated.
async function load() {
	const request = buildRequest(input);
	let response: Response;
	try {
		response = await send(request);
	} catch (error) {
		if (error instanceof NetworkUnavailable) return retryableFailure(error);
		throw error;
	}
	await save(response);
}
```

Do not add `try` blocks preemptively. Do not catch an error only to log and continue. If the operation cannot recover, propagate or rethrow with the original cause.
