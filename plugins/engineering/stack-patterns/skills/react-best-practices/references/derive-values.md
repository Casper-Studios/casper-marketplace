# Derive Values

Keep values that are computable from props or state out of React state.

```tsx
// BAD: two sources of truth require synchronization.
function BadName({ firstName, lastName }: NameProps) {
	const [fullName, setFullName] = useState('');
	useEffect(() => {
		setFullName(`${firstName} ${lastName}`);
	}, [firstName, lastName]);
	return <p>{fullName}</p>;
}

// GOOD: render derives the value from its sources.
function Name({ firstName, lastName }: NameProps) {
	const fullName = `${firstName} ${lastName}`;
	return <p>{fullName}</p>;
}
```

Derived values update with their inputs, cannot become stale, and do not need cleanup.

Keep cheap derivations inline. Move expensive work into the conditional subtree that needs it. Add a cache only when measured repeated work or a stable-identity contract justifies it.

Do not store a filtered list, formatted label, boolean predicate, or computed total merely because it appears in more than one JSX expression. Extract a local variable or a pure function when that improves clarity.
