# Mutation Invalidation

Invalidate the cache entry identified by successful mutation variables using the callback context's QueryClient.

```typescript
import { queryOptions, useMutation } from '@tanstack/react-query';

interface Job {
	id: string;
	title: string;
}

declare function getJob(id: string): Promise<Job>;
declare function updateJob(job: Job): Promise<Job>;

const jobQueryKeys = {
	all: ['jobs'] as const,
	job(id: string) {
		return ['jobs', id] as const;
	},
};

function jobOptions(id: string) {
	return queryOptions({
		queryKey: jobQueryKeys.job(id),
		queryFn: async ({ queryKey: [, jobId] }) => await getJob(jobId),
	});
}

// BAD: every successful edit invalidates unrelated records.
function useBroadUpdateJob() {
	return useMutation({
		mutationFn: updateJob,
		async onSuccess(_data, _variables, _onMutateResult, context) {
			await context.client.invalidateQueries({ queryKey: jobQueryKeys.all });
		},
	});
}

// GOOD: mutation variables identify the stale cache entry.
export function useUpdateJob() {
	return useMutation({
		mutationFn: updateJob,
		async onSuccess(_data, variables, _onMutateResult, context) {
			await context.client.invalidateQueries({ queryKey: jobQueryKeys.job(variables.id) });
		},
	});
}
```

Use `context.client` from TanStack Query mutation callbacks. Do not call `useQueryClient()` inside a callback.

Invalidate the narrowest query family that has become stale. Invalidate a list as well only when the mutation changes list membership, ordering, or displayed summary data.

Keep optimistic updates and other application-specific sequencing with the application feature that owns their policy.
