# Fail Impossible States

Treat an impossible-state claim as a commitment. Enforce the invariant at the boundary and terminate the operation when it fails.

```typescript
// BAD: silent recovery contradicts the invariant.
let selected = items.find(item => item.id === selectedId);
if (typeof selected === 'undefined') [selected] = items;

// GOOD: fail at the violated assumption.
const selectedItem = items.find(item => item.id === selectedId);
if (typeof selectedItem === 'undefined') throw new Error(`Selected item must exist: ${selectedId}`);
```

Do not weaken a type, introduce an arbitrary default, skip the operation, or continue with partial state after an invariant violation. Those actions state that the condition was expected after all.

Handle invalid external input as an expected result at the trust boundary. Use an always-active failure mechanism after validation or when internal construction guarantees the invariant. Terminate the current operation; a reusable library does not need to terminate the host process. Do not use a debug-only assertion facility when optimized builds can remove it.
