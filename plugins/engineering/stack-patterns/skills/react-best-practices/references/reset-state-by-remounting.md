# Reset State by Remounting

Reset local state by changing component identity instead of synchronizing a reset effect.

```tsx
// BAD: each new field can be missed by the reset effect.
function BadCategoryItems({ categoryId, items }: Props) {
	const [selection, setSelection] = useState<string | null>(null);
	useEffect(() => {
		setSelection(null);
	}, [categoryId]);
	return <ItemList items={items} selection={selection} />;
}

// GOOD: a new identity mounts fresh state.
function CategoryItems({ categoryId, items }: Props) {
	return <ItemList key={categoryId} items={items} />;
}
```

Use a `key` when a changed identity means the component must start a new local-state lifetime.

Do not use a key as an incidental force-refresh. If state must survive the identity change, preserve it in the actual owner instead.

Choose a key that represents the domain identity, not an arbitrary counter. A changing random key destroys state on every render and obscures the intended lifecycle.

Keep the remounted boundary narrow so unrelated sibling state does not reset with it.
