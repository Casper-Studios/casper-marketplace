# Manual Memoization

Use `useMemo` for every pure render-time computation worse than O(1): O(log n) search, O(n) scan or reduction, O(n log n) sorting, and more expensive work. Result shape is irrelevant: a count is scalar, and a single result from `some`, `find`, or `includes` can still require a scan. Keep O(1) derivations inline.

Apply this rule with or without React Compiler. Profiling is not a prerequisite.

```tsx
// Component excerpt.
// BAD: filtering repeats O(n) work during every render.
function BadItemList({ items }: ItemListProps) {
	const visibleItems = items.filter(item => item.isVisible);
	return <Rows items={visibleItems} />;
}
```

```tsx
// Component excerpt.
// GOOD: cache the O(n) derivation until items changes.
function ItemList({ items }: ItemListProps) {
	const visibleItems = useMemo(() => items.filter(item => item.isVisible), [items]);
	return <Rows items={visibleItems} />;
}

// GOOD: keep O(1) work inline.
const isEmpty = count === 0;
```

Move derived work behind the conditional subtree that needs it before memoizing it. Call hooks unconditionally in that subtree's component; do not put `useMemo` in a branch, event handler, or query callback.

Keep the callback pure. Do not use `useMemo` for I/O, mutation, subscriptions, or an effect replacement; rendering must remain correct if React discards a cached value.
