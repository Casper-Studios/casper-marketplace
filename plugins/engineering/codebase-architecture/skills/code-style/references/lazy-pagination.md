# Lazy Pagination

Produce pages incrementally. Validate each page before yielding it. Let the consumer decide whether to continue, stop, flatten, filter, persist, or retry.

```typescript
// BAD: the producer eagerly consumes every page.
async function listAllItems() {
	const results: Item[] = [];
	for await (const page of pages()) results.push(...page.items);
	return results;
}

// GOOD: expose one validated page at a time.
async function* pages() {
	let cursor: string | undefined;
	do {
		const page = validatePage(await fetchPage(cursor));
		yield page;
		cursor = page.nextCursor;
	} while (typeof cursor !== 'undefined');
}
```

Yield the complete page when pagination metadata can affect caller policy. Expose a caller-controlled safety limit or enough information to report that more data exists.

Detect invalid continuation behavior required by the provider contract, such as a repeated token. Keep policy retries under caller control. A transport owns protocol retries only when repetition is safe and explicit.
