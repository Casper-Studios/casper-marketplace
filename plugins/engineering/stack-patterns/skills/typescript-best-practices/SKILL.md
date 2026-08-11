---
name: typescript-best-practices
description: Opinionated TypeScript conventions for inference-first typing, precise contracts, finite-state modelling, exhaustive decisions, and strict handling of optional or untrusted values. Use when writing or reviewing TypeScript types, state transitions, API signatures, schema-adjacent parsing, array or regular-expression access, or strict compiler errors.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# TypeScript Best Practices

Treat types as precise, compiler-checked models of valid program states and boundaries; preserve inference where it carries information, then narrow uncertainty explicitly so invalid states and unhandled cases cannot silently reach runtime.

## References

Read as many linked references as are relevant to the current task before writing or reviewing TypeScript.

- When TypeScript can derive the correct type, [keep the annotation inferred](./references/inference-over-annotation.md) because repeated annotations drift and can hide errors.
- At an untrusted-input or caught-error boundary, [contain type escape hatches](./references/escape-hatches.md) by narrowing or validating `unknown` immediately instead of propagating it into domain code.
- When an API infers a closed state from one initial literal, [declare the intended state set at that inference boundary](./references/literal-union-inference.md) so later valid members remain assignable.
- When a durable domain concept has a named closed set of serialized primitive values, [model it as a `const enum`](./references/const-enums.md) rather than a string-literal union.
- When writing an object contract, [choose `interface` by default and compose it with `extends`](./references/interfaces-and-types.md); reserve `type` for contracts that interfaces cannot express naturally.
- When a value is untrusted or insufficiently typed, [replace unchecked assertions with runtime proof](./references/unchecked-assertions.md) at its serialization boundary.
- When consumers require readonly tuple or literal-union inference from a literal constant, [preserve it with `as const`](./references/literal-const-assertions.md) rather than treating the assertion as a default.
- When a value must satisfy a shape without losing its precise inferred literals, [use structural conformance](./references/structural-conformance.md) instead of widening it with an annotation.
- When parallel flags permit impossible state combinations, [model the state as discriminated variants](./references/discriminated-union-state.md) so each status has one valid shape.
- When each member of a closed enum or union needs distinct behavior, [make the decision exhaustive](./references/exhaustive-decisions.md) so new members cannot silently reach a fallback.
- When an operation requires a value that might be absent, [establish that invariant explicitly](./references/non-null-assertions.md) rather than asserting it with `!`.
- When an optional argument can be omitted, [express omission by leaving it out](./references/optional-arguments.md); pass `void 0` only when the API requires a positional value.
- When an operation requires a present optional value, [narrow it before the call](./references/optional-value-narrowing.md), or preserve absence in its return or state contract when it is expected.
- When a required input is missing, [do not fabricate a default](./references/no-fabricated-defaults.md) unless the domain contract assigns that exact omitted-value meaning.
- When bracket access or destructuring can produce no array element, [guard the indexed value](./references/array-index-guards.md) before treating it as present.
- When a `.split()` component can be absent, [preserve that absence until domain or display policy resolves it](./references/split-results.md) instead of supplying an arbitrary empty string.
- When a regular-expression capture supplies a required domain field, [validate the capture first](./references/regex-capture-groups.md) because named and positional groups can be absent.
