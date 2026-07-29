# Non-null Assertions

Do not use the `!` operator to claim that a possibly absent value exists. Guard the value and fail with context when absence violates the operation contract.

```typescript
// BAD: hides absence from the compiler and runtime.
const user = users.find(user => user.id === id)!;

// GOOD: make the required invariant explicit.
const user = users.find(user => user.id === id);
if (typeof user === 'undefined') {
	throw new Error(`User not found: ${id}`);
}
```

If absence is an expected result, model it in the return contract instead of forcing a non-null value.
