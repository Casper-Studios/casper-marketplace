# Mutation Variables

Pass changing operation input through `mutate(...)` variables. Keep only stable mutation configuration in the hook closure.

```typescript
// BAD: the hook hides changing input in its construction closure.
function useUpdateJob(id: string) {
	return useMutation({ mutationFn: data => updateJob(id, data) });
}

// GOOD: each invocation carries its own operation input.
interface UpdateJobVariables {
	id: string;
	data: UpdateJobRequest;
}

export function useUpdateJob() {
	return useMutation({
		async mutationFn({ id, data }: UpdateJobVariables) {
			return await updateJob(id, data);
		},
	});
}
```

This makes each mutation request explicit and lets callbacks identify the affected record through their `variables` parameter.

Do not create one hook instance per changing identifier. Do not hide a mutation identifier in component state merely so the mutation function can read it later.
