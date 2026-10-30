# Mutation Variables

Pass changing operation input through `mutate(...)` variables. Keep only stable mutation configuration in the hook closure.

```typescript
import { useMutation } from '@tanstack/react-query';

interface UpdateJobRequest {
	title: string;
}

declare function updateJob(id: string, data: UpdateJobRequest): Promise<void>;

// BAD: the hook hides changing input in its construction closure.
function useCapturedUpdateJob(id: string) {
	return useMutation({ mutationFn: (data: UpdateJobRequest) => updateJob(id, data) });
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

Use callback variables for submitted identity and intent, returned data for the confirmed outcome, and callback context for the QueryClient. Do not guess a returned outcome by inverting a captured pre-request boolean.

```tsx
interface BookmarkInput {
	id: string;
}

interface BookmarkResult {
	isBookmarked: boolean;
}

interface BookmarkButtonProps extends BookmarkInput, BookmarkResult {}

declare function toggleBookmark(input: BookmarkInput): Promise<BookmarkResult>;
declare function showBookmark(id: string, isBookmarked: boolean): void;

function BookmarkButton({ id, isBookmarked }: BookmarkButtonProps) {
	const { mutate } = useMutation({ mutationFn: toggleBookmark });
	const input = { id };

	// BAD: the pre-request render snapshot guesses the server result.
	function saveGuessed() {
		mutate(input, { onSuccess: () => showBookmark(input.id, !isBookmarked) });
	}

	// GOOD: submitted identity and confirmed state come from the callback.
	function save() {
		mutate(input, {
			onSuccess({ isBookmarked }, { id }) {
				showBookmark(id, isBookmarked);
			},
		});
	}

	return (
		<button type="button" onClick={save}>
			Toggle Bookmark
		</button>
	);
}
```

Capture stable configuration and UI capabilities when the callback does not supply them. Do not create one hook instance per changing identifier or hide mutation input in component state merely so the function can read it later.
