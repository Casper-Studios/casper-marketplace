# Structured Attributes

Treat a span as the record of one operation and a named log record as the record of one meaningful occurrence. Place an attribute according to what it describes, not where its value exists in code.

This policy is language-agnostic. JavaScript examples illustrate how another language can map the same decisions to its official OpenTelemetry APIs; they are neither normative nor canonical.

## Describe the Whole Operation on the Span

Put safe, bounded, operationally useful properties that describe the operation as a whole on its span:

- Add material inputs known at the operation's start when the span is created. Creation-time attributes are available to head samplers; attributes added later are not.
- Add final output classifications and outcome properties before ending the span.
- Keep only values that materially help operators filter, group, aggregate, correlate, or explain the operation.

Do not capture every function parameter, local value, or closure capture. Variable provenance does not create telemetry meaning. Exclude implementation-only state, complete objects, large collections, and values that have no operational query.

Do not put a changing history under one span-attribute key. Setting the same key again overwrites the earlier value. Use distinct initial and final attributes when both characterize the operation, or emit named events when each transition matters.

```jsonc
// GOOD: the span records material inputs and the final operation result.
{
	"name": "order.submit",
	"attributes": {
		"com.acme.order.channel": "web",
		"com.acme.order.item_count": 3,
		"com.acme.order.final_state": "submitted",
	},
}
```

Do not emit a successful-completion log merely because final attributes were set. The span's end timestamp, final attributes, and status already represent completion.

## Describe Occurrences on Named Log Records

Emit a named log event when a meaningful occurrence needs its own timestamp, severity, repetition, or occurrence-specific attributes. Typical events include state transitions, retry attempts, feature decisions, lifecycle changes, and exceptions.

Strongly prefer a stable `eventName` for every structured log record that represents an event. Treat it as the discriminator that selects the schema for the record's attributes. Do not infer that schema from body text or from the presence of individual attributes. Leave an ordinary diagnostic log record unnamed when it does not represent a stable event type.

```jsonc
// GOOD: the event records one transition within the operation.
{
	"eventName": "order.state_changed",
	"body": "Order state changed",
	"attributes": {
		"com.acme.order.from_state": "pending",
		"com.acme.order.to_state": "submitted",
	},
}
```

Do not emit an event for every intermediate value. Emit one only when the occurrence is independently meaningful. Use a regular log record for unstructured diagnostic text that is not intended to be queried as a stable event.

When an activity is a duration-bearing operation with a meaningful boundary, represent it with a child span instead of a completion event. Put that child operation's inputs and final outputs on the child span. A point-in-time outcome within a longer operation remains eligible for a named event.

## Instrument Loop Executions

Wrap every loop execution in its own span so its duration, decisions, and iteration records remain correlated.

- Emit a `TRACE` log record for every loop iteration with safe, bounded iteration context.
- Emit `DEBUG` records at meaningful decisions or selected branches.
- Set final bounded counts and outcomes on the loop span, and end it even when an iteration fails.
- Keep changing iteration history in log records instead of overwriting span attributes.
- Do not create one span per iteration by default. Create an iteration child span only when that iteration itself is a meaningful duration-bearing operation.

## Keep Correlated Records Focused

Keep the span as the canonical home for operation-wide context. Do not copy every span attribute onto each correlated event. Put only occurrence-specific context on the event unless a repeated value is required to understand, route, alert on, or retain the event without its span.

Intentional cross-signal repetition is valid when the same value serves different semantics. For example, a transition event can contain `to_state=completed` while the span contains `final_state=completed`. The event describes what changed at that time; the span describes the operation's final result.

Keep a log body stable and concise across occurrences. Bind occurrence-specific values as attributes so operators can filter and aggregate them.

```jsonc
// BAD: a meaningful occurrence lacks a stable event identity and hides its values in the body.
{
	"body": "Inventory for books fell from 12 to 4 items",
}
```

```jsonc
// GOOD: a meaningful occurrence has a stable identity and structured context.
{
	"eventName": "inventory.capacity_degraded",
	"body": "Inventory capacity degraded",
	"attributes": {
		"com.acme.inventory.category": "books",
		"com.acme.inventory.previous_count": 12,
		"com.acme.inventory.current_count": 4,
	},
}
```

Do not put full objects, large strings, stack traces, or sensitive values in a log body.

## Use Semantic Conventions First

Use the OpenTelemetry attribute registry and the active semantic convention before defining a custom attribute. Reuse the exact standard name, type, meaning, placement, and value constraints.

In implementation code, use the equivalent official semantic-convention library supplied by the target language's OpenTelemetry ecosystem whenever it exposes a stable constant for a standard attribute, event, metric, or enumerated value. Do not hand-write standard semantic-convention strings when such a constant exists. Follow the target SDK's stability and versioning guidance; do not treat an incubating API as stable. When no official stable constant is available, use the exact standard name and document the compatibility choice.

Use official operation namespaces only for their defined semantics:

- Use `http.request.method` for the normalized HTTP method.
- Use `http.response.status_code` for the HTTP response status code.
- Use `error.type` when a failed operation provides a predictable, low-cardinality classification.
- Use resource attributes such as `service.name` for the entity that produced telemetry.

Do not treat `request.*`, `response.*`, `entity.*`, or `result.*` as generic application namespaces. A name that resembles a semantic convention is not a semantic convention.

When no standard attribute applies:

- Prefix organization-wide attributes with the organization's reverse domain name.
- Prefix internal application attributes with a unique application name when an organization-wide namespace is not available.
- Use lowercase dot-delimited namespaces.
- Use snake_case inside a multi-word namespace component.
- Keep names precise and stable.
- Keep values bounded and suitable for aggregation.
- Avoid an existing OpenTelemetry namespace because a future convention can collide with the custom name.

```jsonc
// BAD: the names are ambiguous and can collide with semantic conventions.
{
	"response_status": 200,
	"entity_count": 12,
}
```

```jsonc
// GOOD: serialized telemetry uses the standard HTTP name and the domain value uses an application namespace.
{
	"http.response.status_code": 200,
	"com.acme.catalog.item_count": 12,
}
```

Do not encode secrets, credentials, personal data, complete request or response bodies, or other unbounded data as attributes.

## Illustrative OpenTelemetry JavaScript Mapping

Use span-creation attributes for known inputs, named log records for meaningful occurrences, and late span attributes for final outputs. The JavaScript Logs API and `eventName` input are experimental; verify their signatures against the installed package version.

```typescript
import { SpanStatusCode, trace } from '@opentelemetry/api';
import { logs, SeverityNumber } from '@opentelemetry/api-logs';
import { ATTR_ERROR_TYPE } from '@opentelemetry/semantic-conventions';

const tracer = trace.getTracer('com.acme.orders');
const logger = logs.getLogger('com.acme.orders');

await tracer.startActiveSpan(
	'order.submit',
	{
		attributes: {
			'com.acme.order.channel': 'web',
			'com.acme.order.item_count': 3,
		},
	},
	async span => {
		try {
			logger.emit({
				eventName: 'order.state_changed',
				severityNumber: SeverityNumber.INFO,
				body: 'Order state changed',
				attributes: {
					'com.acme.order.from_state': 'pending',
					'com.acme.order.to_state': 'submitted',
				},
			});

			span.setAttribute('com.acme.order.final_state', 'submitted');
			span.setStatus({ code: SpanStatusCode.OK });
		} catch (error) {
			if (Error.isError(error)) {
				span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
				span.setAttribute(ATTR_ERROR_TYPE, error.name);
			} else {
				span.setStatus({ code: SpanStatusCode.ERROR });
			}
			throw error;
		} finally {
			span.end();
		}
	},
);
```

Do not add an `order.submit.completed` log to this example. The span already records the completed operation and its final state.
