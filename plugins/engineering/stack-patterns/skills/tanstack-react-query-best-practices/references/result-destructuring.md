# Result Destructuring

At call sites, destructure the stable query-result fields that the component uses.

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

Do not place the complete query result object in an effect dependency, memo dependency, context value, or prop contract merely for convenience. Its object identity is not the component's semantic dependency.

Keep the complete result only when a library API explicitly requires it. Otherwise, name the fields that drive rendering or behavior.

This rule improves dependency precision; it does not require destructuring inside reusable query hooks.

Destructure close to the consumer so each component declares its own query-state needs.

Do not pass unused status fields through intermediate components merely because the query result exposes them.
