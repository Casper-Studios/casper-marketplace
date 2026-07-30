---
name: open-telemetry-best-practices
description: Opinionated logging and error-handling conventions for OpenTelemetry-compatible systems covering log levels, attribute naming, and error classification. Use when writing log statements, choosing log levels, or handling errors with traces.
compatibility: Requires OpenTelemetry-compatible systems using the official SDKs.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# OpenTelemetry Best Practices

Use structured, queryable telemetry to make operations and failures diagnosable without reconstructing context from prose. These language-agnostic logging and error-handling conventions layer a house level split and attribute vocabulary on top of OpenTelemetry; they are not OpenTelemetry semantic-convention standards.

## Log Levels

From most to least verbose:

| Level   | Use When                                                                     |
| ------- | ---------------------------------------------------------------------------- |
| `trace` | Per-item iteration details, API response internals, granular computed values |
| `debug` | External API request/response summaries, intermediate checkpoints            |
| `info`  | Significant milestones with counts/summaries                                 |
| `warn`  | Recoverable issues that don't fail the operation                             |
| `error` | Handled failures - logs exception but operation continues                    |
| `fatal` | Unrecoverable failures - logs exception AND marks span as failed             |

## Message Formatting

**Always bind** queryable attributes for structured filtering. Minimal dynamic context in messages is acceptable for span readability.

### Python

```python
# Best: bind for filtering + interpolate key identifier for readability
logger.bind(ticker=ticker, kpi_count=len(kpis)).info(f"Ticker extraction for {ticker} completed")

# Also fine: purely static message when context is clear from bindings
logger.bind(ticker=ticker, kpi_count=len(kpis)).info("Extraction completed")

# Avoid: interpolation without binding (loses queryability)
logger.info(f"Ticker extraction for {ticker} completed")
```

### TypeScript

```typescript
// Best: structured attributes + readable message
logger.info('Ticker extraction completed', { ticker, kpiCount: kpis.length });

// Avoid: string interpolation without structured attributes
logger.info(`Ticker extraction for ${ticker} completed`);
```

**Guidelines:**

- **Always bind** attributes you'll want to filter/query on (identifiers, counts, statuses)
- **Optionally interpolate** 1-2 key identifiers into the message for span readability
- Redundancy between bindings and message is acceptable
- Avoid interpolating large strings, full objects, or sensitive data into messages

## Attribute Naming

Use dot-notation prefixes for semantic grouping:

| Prefix       | Use For                          |
| ------------ | -------------------------------- |
| `request.*`  | HTTP request metadata            |
| `response.*` | HTTP response data               |
| `entity.*`   | Domain objects (id, type, count) |
| `result.*`   | Operation outputs/summaries      |

```python
logger.info("fetched items", entity_type="user", entity_count=len(users))
logger.debug("api response", response_status=200, response_time_ms=142)
```

## Error Classification

Classify every failure before choosing a level. The `error` vs `fatal` split is recoverability: `error` means the operation continues with a fallback; `fatal` means it cannot continue and the exception is re-thrown.

| Error Type                         | Action                                             |
| ---------------------------------- | -------------------------------------------------- |
| Unrecoverable (bug, invalid state) | Log `fatal`, capture in error tracker, re-throw    |
| Retryable (network, rate limit)    | Log `warn`, let propagate for retry infrastructure |
| Handled (fallback available)       | Log `error`, use fallback value                    |
| Unknown cause                      | Include full traceback/stack trace in log          |

```typescript
// error - handled failure, operation recovers with fallback
try {
	result = riskyOperation();
} catch (err) {
	logger.error('operation failed, using fallback', { entityId: id, error: err });
	result = fallbackValue;
}

// fatal - unrecoverable failure, operation cannot continue
try {
	result = criticalOperation();
} catch (err) {
	logger.fatal('critical operation failed', { entityId: id, error: err });
	throw err; // re-throw since we can't recover
}
```

## Exception Chaining

Never lose the original exception when rethrowing — chaining is mandatory, not optional. Use `from e` (Python) or `{ cause: err }` (TypeScript):

```python
try:
    await operation()
except SpecificError as e:
    raise DomainError(f"Operation failed: {e}") from e
```

```typescript
try {
	await operation();
} catch (err) {
	throw new DomainError(`Operation failed: ${err}`, { cause: err });
}
```

## Structured Logging

Bind context progressively for hierarchical attribution:

```python
service_logger = logger.bind(service="kpi_operations")
operation_logger = service_logger.bind(operation="calculate")

# Use .exception() for full traceback
operation_logger.exception("Operation failed")
```

```typescript
const serviceLogger = logger.child({ service: 'kpiOperations' });
const operationLogger = serviceLogger.child({ operation: 'calculate' });

operationLogger.error('Operation failed', { error: err });
```
