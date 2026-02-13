# Memoization Patterns

## When to useMemo

**Required:** Any operation beyond O(1) time complexity.

```tsx
// Required - O(n) operation
const total = useMemo(
  () => items.reduce((sum, item) => sum + item.value, 0),
  [items]
);

// Not needed - O(1) operation
const isActive = status === "active";
```

## Atomic Memoization

Minimize dependency arrays by memoizing atomically:

```tsx
// Bad - coupled dependencies
const { client, total } = useMemo(
  () => ({
    client: createClient(url),
    total: items.reduce((s, i) => s + i, 0),
  }),
  [url, items] // Any change recomputes both
);

// Good - atomic memoization
const client = useMemo(() => createClient(url), [url]);
const total = useMemo(() => items.reduce((s, i) => s + i, 0), [items]);
```

## Derived Values as Dependencies

```tsx
// Bad - recomputes when either changes
const nodes = useMemo(
  () => render(query.isPending || mutation.isPending),
  [query.isPending, mutation.isPending]
);

// Good - single derived dependency
const isPending = query.isPending || mutation.isPending;
const nodes = useMemo(() => render(isPending), [isPending]);
```

## useCallback for Handlers

Required when passing to children or dependencies:

```tsx
const handleClick = useCallback(() => {
  doSomething(id);
}, [id]);

return <Button onClick={handleClick} />;
```

## Event Handler Alternative

Use `data-*` attributes to avoid closures:

```tsx
// Bad - closure with dependency
const handleClick = useCallback(() => {
  onSelect(item.id);
}, [item.id, onSelect]);

// Good - data attribute, no dependencies
function handleClick(e: React.MouseEvent<HTMLButtonElement>) {
  const id = e.currentTarget.dataset.id;
  if (id) onSelect(id);
}

<button onClick={handleClick} data-id={item.id}>Select</button>
```

## Loader/Inner Pattern for Type Narrowing

Use Inner components to get narrowed types for useMemo:

```tsx
// Bad - useMemo with optional data runs every render
function Component({ id }: Props) {
	const { data } = useQuery(id);

	// Runs even when data is null!
	const items = useMemo(() => data?.items.filter(i => i.active) ?? [], [data]);
}

// Good - Inner receives non-null types, useMemo works cleanly
function ComponentInner({ data }: { data: Data }) {
	// O(n) with useMemo - no optional chaining needed
	const processed = useMemo(() => data.items.map(i => transform(i)), [data]);
	return <Display items={processed} />;
}

// Loader handles async states
function Component({ id }: Props) {
	const { data, isLoading } = useQuery(id);

	if (isLoading) return <Spinner />;
	if (!data) return <Empty />;

	// Inner only mounts when data exists
	return <ComponentInner data={data} />;
}
```

**Why this matters:**

- useMemo hooks in Inner only run when data is available
- Narrowed types eliminate optional chaining in computations
- Clean separation: Loader handles states, Inner handles logic
