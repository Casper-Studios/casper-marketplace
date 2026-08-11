# Manual Memoization

Keep eligible derivations inline by default. Manual memoization is not a complexity threshold.

```tsx
// BAD: memoizing a cheap comparison adds a cache without avoiding meaningful work.
const isActive = useMemo(() => status === 'active', [status]);

// GOOD: keep cheap work inline; cache only measured repeated work.
const isActive = status === 'active';
const total = useMemo(() => items.reduce((sum, item) => sum + item.value, 0), [items]);
```

First determine whether React Compiler is enabled for the code path. With React Compiler, use manual memoization only when profiling shows remaining cost, an API requires stable identity, or compiler documentation requires preservation.

Without React Compiler, add `useMemo` only after profiling demonstrates meaningful repeated work. Do not add it merely because a derivation is O(n).

Move expensive work behind the conditional subtree that needs it before adding a cache.

Keep the memo callback pure. Do not use `useMemo` for I/O, mutation, subscriptions, or an effect replacement.

If stable identity is the only requirement, document the receiving API that requires it.
