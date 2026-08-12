# Operation Failure Outcomes

Describe every operation outcome independently from whether an exception exists or is recorded. Set span status on the span representing that operation, and set `error.type` only when a failure classification is available. Do not use exception emission as a substitute for either field.

This policy is language-agnostic. JavaScript examples illustrate how another language can map the same decisions to its official OpenTelemetry APIs; they are neither normative nor canonical.

## Set Span Status from the Outcome

Set span status to `Ok` after the represented operation completes all fallible work successfully. Leave it set. Do not set `Ok` early: OpenTelemetry treats it as final, so a later attempt to set `Error` or `Unset` has no effect. Set `Error` when the operation fails according to its active semantic convention. Leave the status `Unset` only when the convention classifies the outcome as neither successful nor failed.

Set each span's status independently when its operation ends. Do not recursively mutate ancestor spans:

- When one exception escapes several nested operations and causes each to fail, each operation's span ends with `Error`.
- When a parent recovers from a failed child operation, the child span remains `Error` and the parent span remains successful.
- When retries have attempt spans, failed attempt spans end with `Error`; the parent operation span remains successful when a later attempt succeeds.
- Do not mark a span as failed for an internal exception that the represented operation handles successfully.

Do not set span status from log severity.

When a recognized error escapes the operation, put its message in the span status description. Do not duplicate the status code or `error.type` in the description.

## Classify the Failed Operation

Set `error.type` when the represented operation fails and a predictable, low-cardinality classification is available:

- Use the exception type when an exception identifies the failure.
- Use the protocol or domain error identifier defined by the active semantic convention.
- Do not use an exception message or another unbounded value.
- Use the same `error.type` on correlated spans and metrics for the same failed operation.
- Omit `error.type` when the failure does not provide a classification; do not invent a fallback.
- Omit `error.type` when the represented operation succeeds.

Do not equate an application-specific exception type with proof that exception telemetry was emitted. Error classification and exception-recording state are separate concerns.
