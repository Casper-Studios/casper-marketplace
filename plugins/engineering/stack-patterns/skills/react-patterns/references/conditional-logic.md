# Conditional Logic Patterns

## Affirmative Logic

Avoid double negatives:

```tsx
// Bad - double negative
if (!isInvalid) {
	reject();
} else {
	resolve();
}

// Good - affirmative
if (isValid) {
	resolve();
} else {
	reject();
}

// Bad ternary
const result = !condition ? valueB : valueA;

// Good ternary
const result = condition ? valueA : valueB;
```

## Explicit Conditionals

Avoid implicit coercion:

```tsx
let input: number | null;

// Bad - 0 is falsy, might not be intentional
if (input) { ... }

// Good - explicit null check
if (input !== null) { ... }

// Good - explicit zero check if needed
if (input !== null && input !== 0) { ... }
```

## Conditional Rendering

Use ternaries, not `&&`:

```tsx
// Bad - && can render 0 or empty string
{
	count && <Badge count={count} />;
}

// Good - explicit ternary
{
	count > 0 ? <Badge count={count} /> : null;
}

// Good - explicit null check
{
	condition === null ? null : <Inner value={condition} />;
}
```

## Type Narrowing with Conditionals

```tsx
// Bad - prop drilling nullable values
function Parent({ value }: { value: string | null }) {
	return value ? <Inner value={value} /> : null;
}

// Good - Inner receives caller-narrowed type as prop
function Inner({ value }: { value: string }) {
	// value is guaranteed string
	return <span>{value.toUpperCase()}</span>;
}
```

## Early Returns

```tsx
function Component({ data, isLoading, error }: Props) {
	// Guard clauses first
	if (isLoading) return <Spinner />;
	if (error) return <ErrorMessage error={error} />;
	if (!data) return <Empty />;

	// Happy path last
	return <DataDisplay data={data} />;
}
```
