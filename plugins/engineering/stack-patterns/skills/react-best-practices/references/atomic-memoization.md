# Atomic Memoization

Memoize each independent pure render-time computation worse than O(1) separately. Otherwise, an unrelated input invalidates work whose result did not depend on it.

```tsx
// Render-body excerpt.
// BAD: changing selectedIds recomputes total unnecessarily.
const { selected, total } = useMemo(() => {
	const selectedIdSet = new Set(selectedIds);
	return {
		selected: items.filter(item => selectedIdSet.has(item.id)),
		total: items.reduce((sum, item) => sum + item.price, 0),
	};
}, [items, selectedIds]);
```

```tsx
// Render-body excerpt.
// GOOD: each cache has its complete, independent dependency surface.
const selectedIdSet = useMemo(() => new Set(selectedIds), [selectedIds]);
const selected = useMemo(
	() => items.filter(item => selectedIdSet.has(item.id)),
	[items, selectedIdSet],
);
const total = useMemo(() => items.reduce((sum, item) => sum + item.price, 0), [items]);
```

When several inputs matter only through one O(1) value, derive that value inline and depend on it.

```tsx
// Component excerpt.
function PendingRows({ items, isSaving, isPublishing }: PendingRowsProps) {
	const isPending = isSaving || isPublishing;
	const pendingItems = useMemo(
		() => items.filter(item => item.isPending === isPending),
		[items, isPending],
	);
	return <Rows items={pendingItems} />;
}
```

Do not combine values only to reduce the number of hooks. Keep each memo callback pure: `useMemo` does not run effects, and rendering must stay correct if React discards a cache.
