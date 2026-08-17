# Narrow Error Boundaries

Catch only an expected failure from the smallest operation that can produce it. Preserve unexpected failures and their original causes. Exclude cancellation, interruption, and other platform-defined control-flow signals from ordinary error handling.

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

// GOOD: translate the expected failure and preserve its cause.
async function load() {
	const request = buildRequest(input);
	try {
		return await send(request);
	} catch (error) {
		if (!(error instanceof NetworkUnavailable)) throw error;
		throw new RetryableRequestError('Request could not be sent', { cause: error });
	}
}
```

Make one of these explicit decisions:

- **Recover:** record the recovery, perform the explicit fallback, retry, skip, or other recovery action, then swallow the exception. Logging alone is not recovery.
- **Propagate:** preserve the exception unchanged or wrap it with the language's native cause mechanism when caller-relevant context is added, then throw it. Do not catch a mere pass-through unless required to complete operation-owned cleanup or telemetry.
- **Terminate an owned operation:** convert the exception into the boundary's terminal failure contract or rethrow it after completing boundary-owned cleanup and telemetry.

```typescript
// GOOD: recover from the expected failure.
try {
	result = await loadProfile(userId);
} catch (error) {
	if (!(error instanceof ProfileUnavailableError)) throw error;
	recordRecovery(error, { userId, recoveryType: 'anonymous_profile' });
	result = anonymousProfile;
}

// GOOD: propagation can add caller-relevant context.
try {
	await saveProfile(profile);
} catch (error) {
	if (!(error instanceof StorageWriteError)) throw error;
	throw new ProfilePersistenceError('Could not persist profile', { cause: error });
}
```

Prefer native exception chaining such as Python `raise ... from error`, JavaScript `new Error(message, { cause: error })`, or the language's equivalent. Pass the outermost exception instance to the designated exception-recording boundary.

Do not add `try` blocks preemptively. Let pass-through layers propagate failures without noise.
