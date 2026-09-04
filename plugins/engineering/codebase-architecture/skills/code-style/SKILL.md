---
name: code-style
description: Language-agnostic code-design rules for explicit state, failure, ownership, and I/O boundaries. Use when implementing, refactoring, or reviewing code.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# Code Style

This skill keeps code explicit, linear, and honest about state, failure, ownership, and side effects. Its directives favor enforceable invariants, narrow boundaries, simple abstractions, and sans-I/O decision logic.

Treat each directive as a language-agnostic semantic requirement. Adapt its TypeScript example to the target language's native syntax, type system, resource-management mechanisms, and compiler checks.

## Effective Strategies for Clear, Correct Code

Follow the guidelines below. Read each linked reference that applies before writing or reviewing code.

1. Express control flow so that the permitted state and successful path are easy to read.
   - [Use affirmative conditions when a condition needs mental negation to understand.](./references/affirmative-conditions.md)
   - [Reject invalid or exceptional cases early with guard clauses.](./references/guard-clauses.md)
   - [Make decisions visible at their point of effect instead of concealing valid values or control flow through implicit behavior.](./references/explicit-over-implicit.md)
   - [Reserve conditional expressions for selecting one of two simple values, not for hidden effects.](./references/conditional-expressions.md)
2. Make valid state explicit and enforce it throughout the system.
   - [Make contradictory field combinations unrepresentable by enforcing invariants.](./references/enforce-invariants.md)
   - [Fail impossible states when an internal guarantee is broken instead of continuing with invented state.](./references/fail-impossible-states.md)
   - [Prevent new finite-state members from silently inheriting a fallback through exhaustive decisions.](./references/exhaustive-decisions.md)
3. Keep failure, ownership, and information at their decision-owning boundaries.
   - [Handle and record each failure once at a narrow error boundary, preserving unrelated errors and their original causes.](./references/narrow-error-boundaries.md)
   - [Bind resource ownership to lifetime so a resource never escapes uninitialized or unreleased.](./references/resources-own-lifetimes.md)
   - [Preserve caller-relevant information when normalizing external data so continuation, retry, filtering, fallback, and other policy choices remain with the caller.](./references/preserve-information.md)
   - [Let consumers control continuation and stopping through lazy pagination.](./references/lazy-pagination.md)
4. Keep abstractions and public contracts intentional.
   - [Keep one-off or cosmetic indirection out of the design with simple abstractions.](./references/simple-abstractions.md)
   - [Convert untrusted external payloads into trusted values at the first controlled boundary.](./references/validate-at-boundaries.md)
   - [Keep required absence explicit and reject fabricated defaults unless the domain defines the exact value.](./references/no-fabricated-defaults.md)
   - [Keep consumer APIs intentional and side-effect-free with narrow public surfaces.](./references/narrow-public-surfaces.md)
   - [Put decisions in a pure core and keep I/O in the imperative shell.](./references/pure-core-imperative-shell.md)
