# Loader and Inner

Use a Loader component for TanStack Query state and an Inner component for resolved presentation.

```tsx
// BAD: presentation receives unresolved query state.
function BadJobDetail({ data, isPending }: { data: JobData | undefined; isPending: boolean }) {
	return <JobDetailInner data={data} isPending={isPending} />;
}

// GOOD: the Loader resolves every query state before rendering presentation.
function JobDetailLoader({ jobId }: { jobId: string }) {
	const { data, isPending, isError, error } = useGetJob(jobId);
	if (isPending === true) return <Skeleton />;
	if (isError === true) return <ErrorBanner error={error} />;
	if (typeof data === 'undefined') return <NotFound />;
	return <JobDetailInner data={data} />;
}

function JobDetailInner({ data }: { data: JobData }) {
	return <DataDisplay items={data.items} />;
}
```

The Loader owns query execution and state boundaries. The Inner receives resolved non-null data and stays focused on presentation.

Keep mutations in a narrow form driver nested below the resolved boundary. Only query loading belongs in the Loader.

Keep presentation and owned business decisions sans-I/O when they deserve direct unit tests. A component that owns a mutation hook is an I/O driver and does not become unit-testable merely because it sits below the Loader.

The Loader alone handles pending, error, missing, and success states. Do not pass optional data or query-state booleans into the Inner.

Gate missing data with `typeof data === 'undefined'`, not truthiness. `null` can be a valid resolved value.

Load server state through the query layer, not a mount effect. The query layer owns cache identity, pending state, retries, cancellation, and deduplication.

For conditionally visible UI, mount the Loader only while the UI is visible. Mount the stateful Inner only after resolved data exists.
