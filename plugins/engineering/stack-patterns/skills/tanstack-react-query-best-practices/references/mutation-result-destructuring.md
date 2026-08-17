# Mutation Result Destructuring

Destructure every consumed field from `useMutation`. The complete mutation result object is not referentially stable and must not become a hook dependency, prop, context value, or component-level alias.

```tsx
import { useCallback } from 'react';
import { useMutation } from '@tanstack/react-query';

async function saveJob(name: string) {
	await fetch('/jobs', { method: 'POST', body: name });
}

function SaveJobButton({ name }: { name: string }) {
	// BAD: the aggregate result changes identity and invalidates the dependency.
	const mutation = useMutation({ mutationFn: saveJob });
	const save = useCallback(() => mutation.mutate(name), [mutation, name]);

	return <button onClick={save}>Save</button>;
}
```

```tsx
import { useCallback } from 'react';
import { useMutation } from '@tanstack/react-query';

async function saveJob(name: string) {
	await fetch('/jobs', { method: 'POST', body: name });
}

function SaveJobButton({ name }: { name: string }) {
	// GOOD: the callback depends only on the named function it consumes.
	const { mutate, isPending } = useMutation({ mutationFn: saveJob });
	const save = useCallback(() => mutate(name), [mutate, name]);

	return (
		<button disabled={isPending} onClick={save}>
			Save
		</button>
	);
}
```

Destructure at the `useMutation` call site. Do not retain the complete result merely to access named fields later.
