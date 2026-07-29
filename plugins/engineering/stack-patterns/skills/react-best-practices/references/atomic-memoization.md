# Atomic Memoization

When manual memoization is justified, memoize each independent computation separately.

```tsx
// BAD: unrelated dependencies invalidate one cache.
const { client, total } = useMemo(
	() => ({ client: createClient(url), total: sum(items) }),
	[url, items],
);

// GOOD: each cache has its own dependency surface.
const client = useMemo(() => createClient(url), [url]);
const total = useMemo(() => sum(items), [items]);
```

Derive a stable boolean or scalar before passing it to a memo when several inputs only matter through that derived value.

```tsx
const isPending = isSaving || isPublishing;
const nodes = useMemo(() => render(isPending), [isPending]);
```

Do not combine values only to reduce the number of hooks. Minimize invalidation scope instead.
