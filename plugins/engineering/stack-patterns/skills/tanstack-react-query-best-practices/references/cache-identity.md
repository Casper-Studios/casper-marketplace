# Cache Identity

Every input that can change a query response belongs in its query key. Centralize keys in one factory per entity.

```typescript
// BAD: distinct filters reuse one cache entry.
const queryKey = ['jobs', 'list'] as const;

// GOOD: every response-changing input participates in identity.
export const jobQueryKeys = {
	all: ['jobs'] as const,
	list: (filters: JobFilters | undefined) =>
		typeof filters === 'undefined'
			? (['jobs', 'list'] as const)
			: (['jobs', 'list', filters] as const),
	job: (id: string | undefined) => ['jobs', 'detail', id] as const,
};
```

The key defines when results can be reused. Include filters, pagination state, locale, tenant, and other response-changing inputs.

Do not include values that affect only rendering after the response arrives. Do not create separate key shapes for fetching and invalidation.

Use readonly literal tuples so key factories preserve their exact structure. `as const` is appropriate here because these are literal cache-key constants, not a cast over uncertain data.

Use one hierarchy so broad invalidation can target an entity prefix while detailed invalidation can target one record.

Review cache identity whenever a request gains a new argument that can change the returned data.
