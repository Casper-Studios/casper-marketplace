---
name: code-style
description: Opinionated language-agnostic design rules for implementation, refactoring, and code review. Use when shaping conditional control flow, finite states, invariants, error boundaries, resource lifetimes, abstractions, public APIs, validation boundaries, pagination, missing values, or the separation of sans-I/O decisions from imperative drivers.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# Code Style

This skill keeps code explicit, linear, and honest about state, failure, ownership, and side effects. Its directives favor enforceable invariants, narrow boundaries, simple abstractions, and sans-I/O decision logic.

Treat each directive as a language-agnostic semantic requirement. Adapt its TypeScript example to the target language's native syntax, type system, resource-management mechanisms, and compiler checks.

## References

Read as many linked references as are relevant to the current task before writing or reviewing code.

- When a condition needs mental negation to understand, express the permitted state through [affirmative conditions](./references/affirmative-conditions.md).
- Keep the successful path readable by rejecting invalid or exceptional cases early with [guard clauses](./references/guard-clauses.md).
- Make decisions visible at their point of effect; avoid [implicit behavior](./references/explicit-over-implicit.md) that conceals valid values or control flow.
- Reserve [conditional expressions](./references/conditional-expressions.md) for selecting one of two simple values, not for hidden effects.
- Make contradictory field combinations unrepresentable by [enforcing invariants](./references/enforce-invariants.md).
- When an internal guarantee is broken, [fail impossible states](./references/fail-impossible-states.md) instead of continuing with invented state.
- Prevent new finite-state members from silently inheriting a fallback through [exhaustive decisions](./references/exhaustive-decisions.md).
- Translate only the expected failure at its source with [narrow error boundaries](./references/narrow-error-boundaries.md), preserving unrelated errors.
- Keep one-off or cosmetic indirection out of the design with [simple abstractions](./references/simple-abstractions.md).
- Ensure a resource never escapes uninitialized or unreleased by binding [ownership to lifetime](./references/resources-own-lifetimes.md).
- When a lower layer normalizes external data, [preserve caller-relevant information](./references/preserve-information.md) so continuation, retry, filtering, fallback, and other policy choices remain with the caller.
- Let consumers control continuation and stopping by exposing [lazy pagination](./references/lazy-pagination.md).
- Convert untrusted external payloads into trusted values at the first controlled [boundary](./references/validate-at-boundaries.md).
- Keep required absence explicit; reject [fabricated defaults](./references/no-fabricated-defaults.md) unless the domain defines the exact value.
- Keep consumer APIs intentional and side-effect-free with [narrow public surfaces](./references/narrow-public-surfaces.md).
- Put decisions in a [pure core](./references/pure-core-imperative-shell.md) and keep I/O in the imperative shell.
