# Discriminated Unions

Use `z.discriminatedUnion` for objects with a literal discriminant. It dispatches on the tag and reports the failing branch. Reserve `z.union` for genuinely un-tagged alternatives as a last resort.

```typescript
const enum ResponseStatus {
	Success = 'success',
	Failed = 'failed',
}

// BAD: tries every tagged branch sequentially.
const Response = z.union([
	z.object({ status: z.literal(ResponseStatus.Success), data: z.string() }),
	z.object({ status: z.literal(ResponseStatus.Failed), error: z.string() }),
]);

// GOOD: dispatches by the status tag.
const Response = z.discriminatedUnion('status', [
	z.object({ status: z.literal(ResponseStatus.Success), data: z.string() }),
	z.object({ status: z.literal(ResponseStatus.Failed), error: z.string() }),
]);
```

Use `z.union([z.string(), z.number()])` for alternatives without a shared literal tag.
