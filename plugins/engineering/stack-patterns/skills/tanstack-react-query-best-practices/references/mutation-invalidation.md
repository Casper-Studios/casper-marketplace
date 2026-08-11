# Mutation Invalidation

Invalidate the cache entry identified by successful mutation variables. Use the callback context's QueryClient.

```typescript
// BAD: every successful edit invalidates unrelated records.
queryClient.invalidateQueries({ queryKey: jobQueryKeys.all });

// GOOD: mutation variables identify the stale cache entry.
export function useUpdateJob() {
	return useMutation({
		mutationFn: updateJob,
		onSuccess(_data, variables, _onMutateResult, context) {
			context.client.invalidateQueries({ queryKey: jobQueryKeys.job(variables.id) });
		},
	});
}
```

Use `context.client` from TanStack Query mutation callbacks. Do not call `useQueryClient()` inside a callback.

Invalidate the narrowest query family that has become stale. Invalidate a list as well only when the mutation changes list membership, ordering, or displayed summary data.

Keep optimistic updates and other application-specific sequencing with the application feature that owns their policy.
