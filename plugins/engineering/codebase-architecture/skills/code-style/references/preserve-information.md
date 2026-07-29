# Preserve Information

A lower layer must preserve information that a caller can use to make policy decisions. Normalize representation, but do not collapse distinct provider states into one convenient result.

```typescript
// BAD: the transport discards continuation state.
async function fetchItems() {
	const page = await provider.fetchPage();
	return page.items;
}

// GOOD: the transport returns the complete validated page.
async function fetchPage(cursor?: string) {
	const response = await provider.fetchPage(cursor);
	return validatePage({
		items: response.items,
		nextCursor: response.nextCursor,
	});
}
```

Keep caller-owned choices outside the lower layer: continuation, selection, flattening, fallback, retry, persistence, caching, and domain filtering.

Translate vendor-specific shapes into package-owned values when that creates insulation. Preserve every distinction required for correct caller policy.
