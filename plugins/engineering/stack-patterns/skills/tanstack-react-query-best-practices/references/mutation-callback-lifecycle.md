# Mutation Callback Lifecycle

Put every-invocation policy in the mutation definition and mounted UI consequences at the call site. Choose callbacks for an event invocation or `mutateAsync` when the caller composes the promise into an action or larger operation.

```tsx
import { useEffect, type ReactNode } from 'react';
import { useMutation } from '@tanstack/react-query';

interface UpdateJobRequest {
	id: string;
	title: string;
}

declare function updateJob(input: UpdateJobRequest): Promise<void>;
declare function closePanel(): void;

interface JobEditorProps {
	onSubmit: (input: UpdateJobRequest) => void;
	disabled: boolean;
	error: Error | null;
}

declare function JobEditor(props: JobEditorProps): ReactNode;

function useUpdateJob() {
	return useMutation({ mutationFn: updateJob });
}

// BAD: aggregate status loses the identity of the invocation that succeeded.
function BadJobForm() {
	const mutation = useUpdateJob();
	useEffect(() => {
		if (mutation.isSuccess) closePanel();
	}, [mutation.isSuccess]);
	return null;
}

// GOOD: the mutation owns status; its call site owns the mounted consequence.
function JobForm() {
	const { mutate, isPending, error } = useUpdateJob();

	function submit(input: UpdateJobRequest) {
		mutate(input, { onSuccess: closePanel });
	}

	return <JobEditor onSubmit={submit} disabled={isPending} error={error} />;
}
```

Use `onSuccess` for success consequences and `onError` for expected failure presentation. Per-call callbacks stop when their observer unmounts and consecutive calls retain only the latest observer's callbacks. Put required persistence, cache policy, and operation-owned cleanup in the mutation definition, where each invocation receives them.

Read pending and errors from their existing owner instead of clearing duplicate local flags in `onSettled`. Use `onSettled` only for real operation-owned cleanup required after either result; a promise-owning caller awaits its work without recreating the mutation lifecycle.
