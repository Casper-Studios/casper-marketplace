# Request Ownership

Let TanStack Query own cache identity, cancellation, retries, deduplication, and pending/error state. An effect plus local state duplicates that lifecycle and makes the view responsible for request coordination.

```tsx
import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';

async function fetchTeamReport(teamId: string, signal?: AbortSignal) {
	const response = await fetch('/api/team-report/' + encodeURIComponent(teamId), { signal });
	if (!response.ok) throw new Error('Team report request failed');
	return await response.text();
}

// BAD: the component recreates the query lifecycle.
function BadTeamReport({ teamId }: { teamId: string }) {
	const [report, setReport] = useState<string>();
	useEffect(() => {
		void fetchTeamReport(teamId).then(setReport);
	}, [teamId]);
	return <p>{report ?? 'Loading report'}</p>;
}

// GOOD: the feature hook owns the complete operation.
function useTeamReport(teamId: string) {
	return useQuery({
		queryKey: ['team-report', teamId] as const,
		queryFn: async ({ queryKey: [, keyTeamId], signal }) => {
			return await fetchTeamReport(keyTeamId, signal);
		},
	});
}

function TeamReport({ teamId }: { teamId: string }) {
	const { data, isPending, isError, error } = useTeamReport(teamId);
	if (isPending) return <p>Loading report</p>;
	if (isError) return <p role="alert">{error.message}</p>;
	if (typeof data === 'undefined') return <p>No report available</p>;
	return <p>{data}</p>;
}
```

The hook owns request normalization, memoization, key, query function, options, and invocation. Do not export an options factory whose only consumer passes it straight to `useQuery` or `useInfiniteQuery`. Retain one for an actual prefetch, loader, or other independent consumer.

For an infinite query, the hook owns page acquisition and continuation. Do not fetch every page to imitate server filtering or sorting. A later-page failure leaves resolved pages visible and is retried at the page-loading boundary.
