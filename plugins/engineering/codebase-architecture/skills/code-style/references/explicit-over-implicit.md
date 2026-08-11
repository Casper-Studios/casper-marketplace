# Explicit over Implicit

Make behavior visible where it occurs. Prefer code that names the decision over truthiness, coercion, hidden mutation, ambient state, order dependence, or a fallback that silently changes meaning.

```typescript
// BAD: truthiness hides the decision and rejects a valid zero timeout.
configuration.timeout && applyTimeout(configuration.timeout);

// GOOD: presence controls the branch explicitly.
if (typeof configuration.timeout !== 'undefined') applyTimeout(configuration.timeout);
```

Use implicit behavior only when the target language's construct has one obvious meaning and cannot conceal a valid value or failure. Never treat brevity as evidence of clarity.

During review, ask what a reader must know but cannot see at the call site. Put that decision into the code.
