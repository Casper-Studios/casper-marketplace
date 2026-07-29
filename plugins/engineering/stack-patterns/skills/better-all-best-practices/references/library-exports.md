# Library Exports

`better-all` exports `all`, `allSettled`, and the `Task` type.

- Use `all` when one task failure must reject the graph and abort sibling task signals.
- Use `allSettled` when the caller needs every task outcome, including failures.
- Use `Task` only when a public type boundary cannot infer the task shape.

Child operations stop only when they consume the task signal. Import the operation that matches the caller's required failure semantics. Do not substitute manual staging for a graph that needs dependency scheduling.
