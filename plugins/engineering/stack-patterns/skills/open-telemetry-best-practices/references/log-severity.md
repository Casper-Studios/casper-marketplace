# Log Severity

Use OpenTelemetry's normalized severity ranges. Preserve the source logger's original level in `SeverityText`, and map its meaning to `SeverityNumber`.

This policy is language-agnostic. Select severity from the occurrence's expected impact after deciding that the occurrence warrants a log record. The exception severity rules below align with the [OpenTelemetry exception-log guidance](https://opentelemetry.io/docs/specs/semconv/exceptions/exceptions-logs/). The checkpoint rules for `INFO`, `DEBUG`, and `TRACE` are house policy; OpenTelemetry does not prescribe them.

| Severity Number | Range   | Default House Policy                                                                                                            |
| --------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------- |
| 1–4             | `TRACE` | Record exhaustive internal detail, including every loop iteration.                                                              |
| 5–8             | `DEBUG` | Record verbose internal checkpoints, especially meaningful decisions and selected branches.                                     |
| 9–12            | `INFO`  | Record notable checkpoints involving external systems, especially meaningful results after an asynchronous operation completes. |
| 13–16           | `WARN`  | Record a recoverable failure. It remains observable even when normal control flow continues.                                    |
| 17–20           | `ERROR` | Record an unhandled failure that does not cause process-wide shutdown.                                                          |
| 21–24           | `FATAL` | Record a critical failure that causes process-wide shutdown.                                                                    |

Use the default house policy only when the active semantic convention does not define a severity. Severity communicates expected impact; it does not communicate the surrounding code's control flow.

- Use the severity defined by an operation-specific semantic convention.
- Do not infer severity from a syntactic control-flow construct. Select it from the failure's impact and recoverability.
- Do not infer span status from log severity, or severity from span status.
- Do not make a record `FATAL` only because an exception was thrown. Reserve `FATAL` for process-wide shutdown.
- A span can end with `Error` status without requiring a `FATAL` log.

For exception events when no operation-specific convention applies:

- Use `FATAL` when the exception causes process-wide shutdown, such as application configuration failure during startup.
- Use `ERROR` when application code does not handle the exception and it does not cause process-wide shutdown, such as invalid user input that reaches an HTTP server's terminal error handler and rejects one request while the server continues running.
- Use `WARN` when the exception represents a recoverable failure, such as a failed attempt followed by retry or fallback. Always record such failures for observability.
- Use a lower severity only when the exception is not a failure for the application, such as expected cancellation. Do not relabel a failure as `DEBUG` merely because it was caught.

Always provide `SeverityNumber` for an exception event. Exception attributes are valid at every severity. A `WARN` exception record means that a real exception occurred and application code is expected to handle it; it does not mean the exception lacks a stack trace or causal chain.

For non-exception checkpoints when no operation-specific convention applies:

- Use `INFO` after a notable external-system result, such as a successful external API request. Do not create a duplicate `INFO` record merely because any span ended.
- Use `DEBUG` when an internally meaningful decision or branch is taken, such as an `if` branch.
- Use `TRACE` for exhaustive diagnostic detail, including each execution of a loop body, rather than only decisions within the loop.

Severity applies only after an occurrence warrants a log record. Represent duration-bearing work with a span, and do not create a log merely to report that the span completed.
