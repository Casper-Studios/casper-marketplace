# Wire Nullability

Choose the wrapper that matches a field's wire semantics, not whichever one compiles.

```typescript
const Record = v.object({
	// Always present; value can be null.
	created_at: v.nullable(v.string()),
	// Can be absent; when present, has a value.
	source: v.optional(v.string()),
	// Can be absent or null.
	category: v.nullish(v.string()),
});
```

Prefer `nullable` over `optional` for wire protocols when explicit `null` means "known empty" and a missing key means "not supplied."

Do not nest wrappers to express nullish values:

```typescript
// BAD: redundant.
const filename = v.optional(v.nullable(v.string()));

// GOOD: equivalent wire semantics.
const filename = v.nullish(v.string());
```
