# Query Function Inputs

Keep request construction visibly aligned with cache identity.

A closure is valid when every captured request-changing value is represented in the query key.

Declare every `queryFn` as `async` and `await` its request. Do not return a bare promise expression.

```typescript
// BAD: locale changes the request but is absent from cache identity.
function useJobs(locale: string) {
	return useQuery({
		queryKey: ['jobs'] as const,
		queryFn: async () => await fetchJobs(locale),
	});
}

// GOOD: the request and key expose the same response-changing input.
function useJob(jobId: string) {
	return useQuery({
		queryKey: jobQueryKeys.job(jobId),
		queryFn: async () => await fetchJob(jobId),
	});
}
```

Derive request inputs from `QueryFunctionContext` when that makes the key-to-request correspondence clearer or lets one query function serve several callers.

Do not claim closures are inherently stale. The defect is hidden request input that does not participate in cache identity.

Keep values used only for client-side presentation outside the query function and key.

Do not capture a mutable module variable, current timestamp, or implicit global that changes the request without changing the key.

If the request intentionally uses ambient configuration that is constant for the cache lifetime, document that ownership at the request boundary.
