---
name: better-all-best-practices
description: Opinionated `better-all` conventions for dependency-declared async task graphs, inferred task results, cancellation propagation, and failure semantics. Use when replacing serial `await` chains or manual `Promise.all` stages, parallelizing work with result dependencies, or writing and reviewing `all` and `allSettled` task definitions.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# `better-all` Best Practices

Model concurrent work as a dependency graph whose task names define the data flow, so independent operations run together while dependent operations remain explicit, inferred, cancellable, and predictable when failures occur.

## Library Sources

- GitHub repository ID: `shuding/better-all`
- Context7 library ID: `/shuding/better-all`
- DeepWiki repository ID: `shuding/better-all`

Use Context7 for current documentation and DeepWiki for implementation details.

## References

Read as many linked references as are relevant to the current task before writing or reviewing `better-all` code.

- When work shares only direct data dependencies, [declare them in the task graph](./references/dependency-scheduling.md) so independent tasks run concurrently instead of being serialized by manual stages.
- When a task reads a sibling result, [define it with method syntax](./references/task-method-syntax.md) so `this.$` is the bound task context rather than lexical `this`.
- When a child operation accepts an `AbortSignal`, [pass the task signal through](./references/sibling-cancellation.md) so a sibling failure can stop that work without a second cancellation system.
- When the caller needs either fail-fast behavior or every outcome, [choose the matching graph operation](./references/library-exports.md) instead of manually staging the dependency graph.
- When task return types already describe the result object, [retain inferred task results](./references/inferred-task-results.md) so duplicated result interfaces cannot drift.
