---
name: better-all-best-practices
description: '`better-all` conventions for dependency-aware async task graphs. Use when defining `all` or `allSettled` graphs or converting staged async work with task dependencies.'
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

## Effective Strategies for `better-all`

Read the references that apply to the current task before writing or reviewing `better-all` code.

1. Declare concurrency and data dependencies in the task graph.
   - [Declare direct data dependencies in the task graph](./references/dependency-scheduling.md) so independent tasks run concurrently instead of being serialized by manual stages.
   - [Use method syntax for tasks that read sibling results](./references/task-method-syntax.md) so `this.$` is the bound task context rather than lexical `this`.
2. Let the graph own cancellation and failure semantics.
   - [Pass a child operation's task signal through](./references/sibling-cancellation.md) when it accepts an `AbortSignal`, so a sibling failure can stop that work without a second cancellation system.
   - [Choose the matching graph operation](./references/library-exports.md) when the caller needs either fail-fast behavior or every outcome instead of manually staging the dependency graph.
3. Preserve result information that the task graph already proves.
   - [Retain inferred task results](./references/inferred-task-results.md) when task return types already describe the result object so duplicated result interfaces cannot drift.
