# Absent Identifiers

Disable a query when a required identifier is absent. Preserve that absence in the key.

```typescript
// BAD: absence becomes a request for a fabricated record.
const queryKey = jobQueryKeys.job(jobId ?? '');

// GOOD: preserve absence and do not execute a request.
import { skipToken, useQuery } from '@tanstack/react-query';

export function useGetJob(jobId: string | undefined) {
	return useQuery({
		queryKey: jobQueryKeys.job(jobId),
		queryFn: typeof jobId === 'undefined' ? skipToken : async () => await fetchJob(jobId),
	});
}
```

Do not replace an absent identifier with `''`, `0`, a sentinel UUID, or another fabricated request value.

Use `skipToken` when the installed TanStack Query version supports it. The disabled state is part of the query contract, not a request for an empty record.

Model `null` separately when the domain distinguishes it from `undefined`.
