# Mutation Callback Lifecycle

Use synchronous event handlers and per-call mutation callbacks for operation outcomes.

```tsx
// BAD: an effect loses the identity of the invocation that succeeded.
function BadJobForm() {
	const mutation = useUpdateJob();
	useEffect(() => {
		if (mutation.isSuccess === true) closePanel();
	}, [mutation.isSuccess]);
	return null;
}

// GOOD: mounted UI consequences belong to the call site.
function JobForm() {
	const mutation = useUpdateJob();
	const [formError, setFormError] = useState<string>();
	const [isSubmitting, setIsSubmitting] = useState(false);

	function submit(input: UpdateJobRequest) {
		mutation.mutate(input, {
			onSuccess() {
				closePanel();
			},
			onError(error) {
				setFormError(toExpectedMessage(error));
			},
			onSettled() {
				setIsSubmitting(false);
			},
		});
	}

	return <SubmitButton disabled={isSubmitting} error={formError} onSubmit={submit} />;
}
```

Use `onSuccess` for success-only consequences. Use `onError` for expected failure presentation. Use `onSettled` for cleanup required after either outcome.

Do not use an effect to react to `mutation.isSuccess`. Keep the consequence attached to the mutation invocation that caused it.

Do not use `mutateAsync` with ceremonial `try`/`finally` merely to clear pending state. Use `mutateAsync` only when the caller genuinely composes the returned promise into a larger async operation.

Keep mutation-specific UI callbacks at the call site when different submissions need different outcomes. Per-call callbacks do not run after their observer unmounts, and consecutive `mutate` calls guarantee them only for the latest observer. Put consequences that must run for every invocation in the mutation definition instead.
