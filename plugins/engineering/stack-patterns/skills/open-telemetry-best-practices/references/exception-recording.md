# Exception Recording

Record an observed exception as a meaningful occurrence while preserving the failed operation's independently determined span outcome. Keep exception ownership, terminal fallback coverage, and duplicate avoidance separate from error classification.

This policy is language-agnostic. JavaScript examples illustrate how another language can map the same decisions to its official OpenTelemetry APIs; they are neither normative nor canonical.

OpenTelemetry defines exception fields and operation-outcome semantics. It does not define how an application proves that a causal failure was already recorded. Treat the ownership topology below as house policy. Describe its required outcomes without prescribing branding, mutable error state, process-local registries, or another implementation mechanism.

## Own Each Exception Record

- Prefer the lowest useful instrumented operation boundary that owns the failure. The resulting record remains correlated with the most specific span and its bounded local context.
- When that boundary recovers, retries, skips, or otherwise consumes the exception, record it there because no caller will receive it.
- When the exception propagates, preserve it unchanged or through native cause chaining so a caller retains the available causal history.
- At the terminal request, job, command, consumer, or process boundary, record an escaping exception when application policy cannot establish that the same causal failure already has an application-owned exception record.

Pass the outermost exception instance available at the owning boundary to the OpenTelemetry Logger API when the language SDK supports it. Otherwise, set the standard `exception.type`, `exception.message`, and `exception.stacktrace` attributes. Do not emit one exception record per cause.

Use the operation-specific event name defined by the active semantic convention. For a custom operation, use a low-cardinality name with an `.exception` suffix. Use `exception` only for a global handler that is not operation-specific.

## Prefer Exception Logs over Span Events

OpenTelemetry is moving exception events from span events to log-based events. For new instrumentation, emit a correlated exception log and set the span outcome separately. Do not also call the trace API's exception-recording method for the same failure.

Existing frameworks and instrumentations can still emit exception span events during the migration. Treat that cross-signal duplication as compatibility behavior; do not reproduce it in application instrumentation.

## Apply One Propagation Rule

When an exception escapes an operation:

1. Record that operation's failed outcome independently.
2. If the exception is unexpected by that boundary, rethrow the original instance unchanged.
3. If the boundary translates an expected failure into caller-relevant meaning, wrap it with the language's native cause mechanism.
4. Emit an exception record only when this operation owns the record under the application's exception-ownership convention.
5. Emit a stack-free contextual event only when the boundary performs an independently meaningful translation or transition that needs its own timestamp or occurrence-specific metadata.
6. Throw the propagated exception.

Do not catch a mere pass-through only to log or wrap it. Do not emit a translation event for every wrapper. Do not use `WARN` merely because a boundary wraps or rethrows an exception. Select severity from expected impact or an operation-specific semantic convention.

## Record Every Recovery

When a boundary swallows an exception and recovers:

1. Emit the exception record with the recovery action and relevant bounded context.
2. Use the exception severity defined by the active semantic convention. Otherwise, select severity from expected impact.
3. Perform the fallback, retry, skip, or other recovery action.

Logging alone is not recovery. A failed attempt span remains failed, while an enclosing operation span remains successful when the recovery fulfills that operation.

## Preserve Retry Failures

Treat each retry attempt as a distinct operation when attempt-level diagnostics matter:

- A failed attempt span ends with `Error` status and its own `error.type` when a failure classification is available.
- When no lower operation already owns the exception record, record an earlier failed attempt before another attempt replaces its exception. Use the severity defined by the operation-specific convention. `WARN` is appropriate when the exception is expected to be handled by application code.
- Let the final exception propagate to the next owning boundary instead of recording that same attempt again at both the retry layer and the caller.
- Keep the enclosing logical operation successful when a later attempt fulfills it. Mark it failed only when the retry strategy is exhausted and the operation fails.

Do not suppress distinct attempt failures merely because retrying is a recovery strategy. Do not derive severity solely from the attempt number.

## Preserve One Complete Exception Chain

Prefer the language's native exception chaining. Record the outermost exception available at the owning boundary, including every caller-relevant cause already added there.

A complete chain contains every cause reachable when the owning boundary records it. It cannot contain wrappers that a later caller has not created yet. Preserve later translation context through the ancestor span's outcome. Emit a stack-free contextual event only when the translation is an independently meaningful occurrence that needs its own timestamp or occurrence-specific metadata.

OpenTelemetry standardizes `exception.type`, `exception.message`, and `exception.stacktrace`; it does not define a portable record for each cause. Verify that the language SDK, logging bridge, exporter, and backend preserve the complete native chain in one exception record.

When an adapter does not serialize native causes, format the complete chain into the single `exception.stacktrace` value in a shared telemetry adapter. Preserve cause order, bound depth and output size, detect cycles, and keep the outer exception as the primary `exception.type` unless an active semantic convention requires another value.

Do not emit multiple exception logs merely to walk the cause tree. Multiple exception records are justified only when distinct instrumented operations own distinct failures, not because one exception wraps another.

## Make Custom Errors Independently Analyzable

Include every dynamic, public, immutable, telemetry-safe scalar property of a custom error in its human-readable message and as a named structured attribute when the owning boundary records it.

Telemetry-safe scalar properties are bounded, non-sensitive strings, numbers, booleans, integer-like values, and enumeration-like values. Exclude secrets, personal data, unbounded text, objects, and collections. Write the message as natural prose that gives each value clear meaning; reserve key/value syntax for structured attributes.

The message-and-attribute outcome is required; a constructor shape, static factory, base class, reflection mechanism, or logging API is not. A construct-record-throw helper is valid only at an exception-recording boundary.

## Illustrative OpenTelemetry JavaScript Mapping

The JavaScript Logs API's `exception` input is experimental. The current SDK derives the outer error's code or name, message, and stack; it does not recursively traverse `Error.cause` or discover arbitrary public properties. It resolves the active context automatically for immediate emission. Pass an explicitly captured context when emission is deferred or occurs outside the original execution context. Verify all signatures against the installed package version.

The JavaScript trace API's `recordException` method creates an exception span event. Do not call it when emitting the same failure as an exception log.

```typescript
import { logs, SeverityNumber } from '@opentelemetry/api-logs';
import {
	ATTR_EXCEPTION_STACKTRACE,
	ATTR_HTTP_RESPONSE_STATUS_CODE,
} from '@opentelemetry/semantic-conventions';

const logger = logs.getLogger('com.acme.orders');
```

### Illustrative Construct-Record-Throw Helper

This optional JavaScript pattern is valid only when every call site owns immediate exception recording.

```typescript
class ApiResponseError extends Error {
	name = 'ApiResponseError';

	constructor(public readonly code: number) {
		super(`API response returned status ${code}`);
		this.name = 'ApiResponseError';
	}

	static throwNew(code: number): never {
		const error = new ApiResponseError(code);
		logger.emit({
			eventName: 'api.request.exception',
			severityNumber: SeverityNumber.WARN,
			body: 'API request failed',
			exception: error,
			attributes: {
				[ATTR_HTTP_RESPONSE_STATUS_CODE]: error.code,
			},
		});
		throw error;
	}
}
```

This example uses `WARN` for an external client failure that application code is expected to handle. When a later boundary owns recording, construct and throw the error without emitting here.

### Record an Exception at Its Owning Boundary

This minimal fragment assumes `error` is an `Error` caught by the owning boundary. The operation's span outcome is recorded separately.

```typescript
logger.emit({
	eventName: 'profile.load.exception',
	severityNumber: SeverityNumber.WARN,
	body: 'Profile loading failed',
	exception: error,
	attributes: {
		[ATTR_EXCEPTION_STACKTRACE]: formatCompleteExceptionChain(error),
		'com.acme.operation.phase': 'profile_load',
	},
});

throw error;
```

### Record a Recovered Exception

This recovery boundary supplies the exception because no outer boundary will receive it:

```typescript
logger.emit({
	eventName: 'cache.lookup.exception',
	severityNumber: SeverityNumber.WARN,
	body: 'Cache lookup recovered with defaults',
	exception: error,
	attributes: {
		'com.acme.recovery.action': 'use_defaults',
	},
});

return defaultPreferences;
```

### Propagate an Unexpected Exception Unchanged

```typescript
try {
	return await loadProfile();
} catch (error) {
	if (!(error instanceof ProfileUnavailableError)) throw error;

	throw new OrderProfileError('Order profile is unavailable', {
		cause: error,
	});
}
```

Do not wrap the fallback branch merely to convert an unexpected exception into an application-specific type.

### Record a Meaningful Translation Event

A routine wrapper only updates its operation span and propagates the cause without a log. Emit a stack-free event only when the translation is independently meaningful:

```typescript
const propagatedError = new OrderCreationError(
	'Order creation failed while loading the customer profile',
	{ cause: error },
);

logger.emit({
	eventName: 'order.create.failure_translated',
	severityNumber: SeverityNumber.DEBUG,
	body: 'Failure translated for the order domain',
	attributes: {
		'com.acme.error.from_type': error.name,
		'com.acme.error.to_type': propagatedError.name,
	},
});

throw propagatedError;
```

### Keep a Terminal Fallback

`exceptionNeedsRecording` represents the application's policy decision; it is not an OpenTelemetry API, and this guidance intentionally does not prescribe its implementation.

```typescript
if (exceptionNeedsRecording(error)) {
	logger.emit({
		eventName: 'order.request.exception',
		severityNumber: SeverityNumber.ERROR,
		body: 'Order request failed',
		exception: error,
		attributes: {
			[ATTR_EXCEPTION_STACKTRACE]: formatCompleteExceptionChain(error),
		},
	});
}
```

The terminal handler still records its operation outcome and fulfills its control-flow contract by returning an error response, rejecting the job, negatively acknowledging the message, terminating the command, or rethrowing. Telemetry emission does not determine whether the exception is swallowed.

### Preserve the Complete Cause Chain

`formatCompleteExceptionChain` is an application adapter, not an OpenTelemetry API. Use it only when the configured integration does not preserve native causes. Preserve the complete chain in one stacktrace value without creating additional records.
