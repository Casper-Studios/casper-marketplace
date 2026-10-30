# Narrow Error Boundaries

At a recovery or translation boundary, catch only expected failures from the smallest operation that can produce them. Preserve unexpected failures and their original causes. A terminal boundary may present the failures its callback contract supplies without classifying them all as one known subtype. Preserve the operation's cancellation and interruption policy; platform control-flow signals are not ordinary failures.

```typescript
class NetworkUnavailable extends Error {}

class RetryableRequestError extends Error {
	constructor(options: ErrorOptions) {
		super('Request could not be sent', options);
	}
}

// Application adapters: request construction and persistence can also fail.
declare function buildRequest(input: string): Request;
declare function send(request: Request): Promise<Response>;
declare function save(response: Response): Promise<void>;

// BAD: a broad catch hides request-building and persistence defects.
async function loadBroadly(input: string) {
	try {
		const request = buildRequest(input);
		const response = await send(request);
		await save(response);
		return response;
	} catch {
		return new Response(null, { status: 503 });
	}
}

// GOOD: translate the expected failure and preserve its cause.
async function load(input: string) {
	const request = buildRequest(input);
	let response;
	try {
		response = await send(request);
	} catch (error) {
		if (!(error instanceof NetworkUnavailable)) throw error;
		throw new RetryableRequestError({ cause: error });
	}
	await save(response);
	return response;
}
```

Make one of these explicit decisions:

- **Recover:** record the recovery, perform the explicit fallback, retry, skip, or other recovery action, then swallow the exception. Logging alone is not recovery.
- **Propagate:** preserve the exception unchanged or wrap it with the language's native cause mechanism when caller-relevant context is added, then throw it. Do not catch a mere pass-through unless required to complete operation-owned cleanup or telemetry.
- **Terminate an owned operation:** convert the exception into the boundary's terminal failure contract or rethrow it after completing boundary-owned cleanup and telemetry.

```typescript
interface Profile {
	displayName: string;
}

class ProfileUnavailableError extends Error {}
class StorageWriteError extends Error {}

class ProfilePersistenceError extends Error {
	constructor(options: ErrorOptions) {
		super('Could not persist profile', options);
	}
}

declare function loadProfile(userId: string): Promise<Profile>;
declare function saveProfile(profile: Profile): Promise<void>;
declare function recordRecovery(
	error: ProfileUnavailableError,
	context: { userId: string; recoveryType: 'anonymous_profile' },
): void;

// GOOD: recover from the expected failure with the explicitly chosen guest profile.
async function loadProfileOrGuest(userId: string) {
	try {
		return await loadProfile(userId);
	} catch (error) {
		if (!(error instanceof ProfileUnavailableError)) throw error;
		recordRecovery(error, { userId, recoveryType: 'anonymous_profile' });
		return { displayName: 'Guest' };
	}
}

// GOOD: propagation can add caller-relevant context.
async function persistProfile(profile: Profile) {
	try {
		await saveProfile(profile);
	} catch (error) {
		if (!(error instanceof StorageWriteError)) throw error;
		throw new ProfilePersistenceError({ cause: error });
	}
}
```

Prefer native exception chaining such as Python `raise ... from error`, JavaScript `new Error(message, { cause: error })`, or the language's equivalent. Pass the outermost exception instance to the designated exception-recording boundary.

Follow existing domain-error contracts when translating failures. If an error owns a stable, helpful human-readable meaning, put that message in its constructor so consumers can use it without duplicating an error-to-message table. Keep operation-specific presentation and localization with the presentation owner. Do not introduce a new error class merely to rename a failure.

Here, the upload driver supplies terminal `Error` values after applying the operation's cancellation policy. Its callback contract permits more failures than `UploadConnectionError`:

```typescript
class UploadConnectionError extends Error {
	constructor(options: ErrorOptions) {
		super('Upload connection lost. Check your connection and retry.', options);
	}
}

interface UploadEvents {
	onError(error: Error): void;
}

declare function subscribeToUpload(events: UploadEvents): void;
declare function showUploadError(message: string): void;

// BAD: this terminal UI hides other failures allowed by the callback contract.
subscribeToUpload({
	onError(error) {
		if (error instanceof UploadConnectionError) showUploadError(error.message);
	},
});

// GOOD: present the actual failure supplied by the typed terminal contract.
subscribeToUpload({
	onError(error) {
		showUploadError(error.message);
	},
});
```

The callback needs no redundant error-shape guard. Use the designated error surface for this operation; do not add a second notification when the same failure is already rendered. This terminal presentation does not authorize a transport catch-all to recover from unrelated failures.

Do not add `try` blocks preemptively. Let pass-through layers propagate failures without noise.
