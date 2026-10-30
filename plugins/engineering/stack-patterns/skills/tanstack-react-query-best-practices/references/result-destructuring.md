# Result Destructuring

React query-hook consumers must destructure the named result fields they use. The top-level result object is not referentially stable: it has a new identity on every render. Do not retain it as a component-level alias or use it as a hook dependency, prop, or context value.

Avoid object-rest destructuring: it reads the remaining tracked properties and defeats selective subscriptions.

```tsx
// BAD: the complete result is an imprecise dependency and prop contract.
function BadJobDetail({ jobId }: { jobId: string }) {
	const result = useGetJob(jobId);
	useEffect(() => report(result), [result]);
	return null;
}

// GOOD: name only the fields that drive this component.
function JobDetail({ jobId }: { jobId: string }) {
	const { data, isPending, isError, error } = useGetJob(jobId);

	if (isPending === true) return <Skeleton />;
	if (isError === true) return <ErrorBanner error={error} />;
	if (typeof data === 'undefined') return <NotFound />;
	return <JobDetailInner data={data} />;
}
```

Keep the complete result only when a library API explicitly requires it. Otherwise, name the fields that drive rendering or behavior.

Do not pass unused status fields through intermediate components merely because the query result exposes them.
