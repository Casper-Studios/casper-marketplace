---
name: open-telemetry-best-practices
description: Language-agnostic OpenTelemetry conventions for queryable signals and explicit operational outcomes. Use when adding or reviewing spans, structured logs, attributes, or exception recording.
compatibility: Requires OpenTelemetry-compatible systems using the official SDKs.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# OpenTelemetry Best Practices

Treat spans as operation records and named log records as occurrence records. Put safe, bounded, operationally useful inputs, final outputs, and outcomes on the span that represents the operation. Emit a named log event only for a meaningful point-in-time occurrence. Do not infer one signal from another.

Use an established OpenTelemetry semantic convention before defining an application attribute. Keep custom policy visibly separate from OpenTelemetry requirements, and keep telemetry useful across languages, SDKs, collectors, and backends.

Treat this guidance as language-agnostic. Adapt illustrative JavaScript SDK examples to the target language's official OpenTelemetry APIs, native exception chaining, and resource-management conventions.

## Core Conventions

- Preserve trace and span correlation on every log record emitted during an active span.
- Put safe, bounded operation inputs and final outputs on the span; put meaningful point-in-time occurrences on named log records.
- Strongly prefer a stable `eventName` for structured log records so consumers can select the correct attribute schema without inferring the record type from its body or attribute set.
- Represent a duration-bearing sub-operation with a child span instead of a completion event.
- Represent every loop execution with its own span so its total duration, final bounded results, decisions, and per-iteration records remain correlated.
- Do not emit a successful-completion log merely because a span ended; its end time, final attributes, and status already record completion.
- Explicitly set a successfully completed span to `OK` after all fallible work has finished, and leave that status set.
- Decide a failed operation's span outcome independently from whether and where its exception is recorded.
- Apply semantic conventions before custom policy, and keep custom policy explicit when OpenTelemetry does not define it.
- For a standard name or value, use the target language's official OpenTelemetry semantic-convention library when it provides a stable equivalent. Follow that SDK's stability guidance instead of assuming every language exposes the same constants or APIs.
- Exclude secrets, credentials, personal data, and unbounded payloads from telemetry.

## Library Sources

- Specification GitHub and DeepWiki: `open-telemetry/opentelemetry-specification`
- Semantic Conventions GitHub and DeepWiki: `open-telemetry/semantic-conventions`

## Effective Strategies for OpenTelemetry

Read the linked guidance that governs the current task.

1. Make telemetry fields queryable, interoperable, and bounded.
   - When placing or naming queryable context, applying official semantic-convention libraries, or instrumenting loops, apply [structured attribute conventions](./references/structured-attributes.md) to distinguish operation attributes from occurrence attributes without copying correlated context by default.
   - When a log occurrence needs an impact level, apply the [log severity model](./references/log-severity.md) without deriving severity from control flow or span status.
2. Preserve the operational outcome and exception causal chain independently.
   - When an operation fails, apply [failed-operation outcomes](./references/operation-failure-outcomes.md) so span status and any available `error.type` describe that operation independently from exception emission.
   - When an exception is observed, propagated, recovered, retried, or terminally handled, apply [exception recording](./references/exception-recording.md) to preserve its causal chain without gaps or repeated payloads.
