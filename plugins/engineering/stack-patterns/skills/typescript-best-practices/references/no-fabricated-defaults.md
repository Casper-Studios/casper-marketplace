# No Fabricated Defaults

Do not add a default parameter merely to absorb an omitted value. Require callers to resolve required information before calling the operation.

```typescript
// BAD: omission silently fabricates a label.
function publish(label = '') {}

// GOOD: the operation requires a real label.
function publish(label: string) {}
```

Use a default parameter only when the domain contract defines that exact value for an omitted argument.
