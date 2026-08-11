# Request Ownership

Let TanStack Query own server-state requests. It owns cache identity, request cancellation, retries, deduplication, and pending/error state. Components must not recreate that lifecycle with `useEffect` and local state.

```tsx
// BAD: local state and an effect duplicate the query lifecycle.
function JobList() {
	const [jobs, setJobs] = useState<Job[]>([]);

	useEffect(() => {
		void fetchJobs().then(setJobs);
	}, []);

	return <JobRows jobs={jobs} />;
}

// GOOD: the query key identifies the request and the query function forwards cancellation.
function JobList({ teamId }: { teamId: string }) {
	const { data, isPending, isError, error } = useQuery({
		queryKey: ['jobs', teamId],
		queryFn: async ({ signal }) => await fetchJobs({ teamId, signal }),
	});

	if (isPending) return <Skeleton />;
	if (isError) return <ErrorBanner error={error} />;
	if (typeof data === 'undefined') return <EmptyState />;
	return <JobRows jobs={data} />;
}
```

Put every response-changing request input in the query key. Keep browser events, local form state, and resolved presentation outside the request lifecycle.
