# Diagnose Derived-State Effects

Identify effects whose only external consequence is calling a state setter from current props or state.

```tsx
function ItemList({ items, filters }: Props) {
	// BAD: this stores a value that the current props already determine.
	const [visibleItems, setVisibleItems] = useState<Item[]>([]);

	useEffect(() => {
		setVisibleItems(applyFilters(items, filters));
	}, [items, filters]);

	return <Rows items={visibleItems} />;
}
```

```tsx
function ItemList({ items, filters }: Props) {
	// GOOD: render from the values that own the result.
	const visibleItems = applyFilters(items, filters);

	return <Rows items={visibleItems} />;
}
```

This shape creates a second source of truth and an intermediate render containing stale state. It is not external-system synchronization.

Use this diagnostic sequence:

1. List every value read by the effect.
2. Confirm that the effect performs no I/O, subscription, DOM synchronization, or imperative integration.
3. Confirm that no user action edits the stored result independently.
4. Remove the effect-driven copy and compute the value at the render boundary.

If users edit the stored result independently, identify the real state owner instead of classifying it as derived. If the effect synchronizes an external system, retain the effect and give it focused setup and cleanup.

Sharing the result across descendants does not justify effect synchronization. Pass the owned value through props or a coherent context boundary.
