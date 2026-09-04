# Query Function Inputs

Capturing request variables in a query closure is forbidden, even when the key contains the same values. Put application request arguments in the typed `queryKey` and destructure them from `queryFn`'s context. Receive cancellation through `context.signal` and an infinite-query cursor through `context.pageParam`.

Declare every `queryFn` as `async` and `await` its request.

```typescript
import { useQuery } from '@tanstack/react-query';

// BAD: the key contains the ID, but the query function still captures it.
function useCapturedReport(reportId: string) {
	return useQuery({
		queryKey: ['report', reportId] as const,
		queryFn: async ({ signal }) => {
			const response = await fetch('/api/reports/' + encodeURIComponent(reportId), { signal });
			if (!response.ok) throw new Error('Report request failed');
			return await response.text();
		},
	});
}

// GOOD: the request reads the ID from context, not the hook's closure.
function useReport(reportId: string) {
	return useQuery({
		queryKey: ['report', reportId] as const,
		queryFn: async ({ queryKey: [, keyReportId], signal }) => {
			const response = await fetch('/api/reports/' + encodeURIComponent(keyReportId), { signal });
			if (!response.ok) throw new Error('Report request failed');
			return await response.text();
		},
	});
}
```

This makes request identity visible at the I/O boundary. Do not mutate key values or React state from `queryFn`. Never put secrets, functions, clients, or `AbortSignal` instances in a key; use a non-secret actor or session partition when visibility changes the response.

Do not hide response-changing arguments in `meta`, mutable module state, ambient configuration, or an imported helper's closure. Keep presentation-only values outside the query function and key.
