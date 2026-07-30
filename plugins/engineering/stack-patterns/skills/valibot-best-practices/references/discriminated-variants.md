# Discriminated Variants

Use `v.variant` for a union of objects with a literal discriminant. It dispatches on the discriminant and reports the failing branch. Reserve `v.union` for genuinely un-discriminated alternatives.

```typescript
const enum ResponseStatus {
	Success = 'success',
	Failed = 'failed',
}

// BAD: tries every tagged branch.
const Response = v.union([
	v.object({ status: v.literal(ResponseStatus.Success), data: v.string() }),
	v.object({ status: v.literal(ResponseStatus.Failed), error: v.string() }),
]);

// GOOD: dispatches by the status tag.
const Response = v.variant('status', [
	v.object({ status: v.literal(ResponseStatus.Success), data: v.string() }),
	v.object({ status: v.literal(ResponseStatus.Failed), error: v.string() }),
]);
```

Use `v.union([v.string(), v.number()])` for a union with no shared literal discriminant.
