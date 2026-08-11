# Explicit Rendering

Use a ternary when a JSX branch can render a value.

```tsx
// BAD: && can render 0 or an empty string.
function BadBadgeSlot({ count }: { count: number }) {
	return count && <Badge count={count} />;
}

// GOOD: the absent branch is explicit.
function BadgeSlot({ count }: { count: number }) {
	return count > 0 ? <Badge count={count} /> : null;
}
```

Use early returns for full component states such as loading, error, empty, and success. Use a ternary for local optional fragments.

Do not hide semantic conditions inside coercion, truthiness, or string interpolation.

Prefer affirmative predicates that state what renders. Name a non-trivial predicate before JSX when that makes the condition readable.

Render an explicit empty branch with `null`; do not rely on an omitted expression to communicate absence.

Use `null` for intentionally empty UI. Use a dedicated empty-state component when absence needs explanation, recovery, or an action.
