# Absent Identifiers

Disable a query when a required identifier is absent. Preserve that absence in the key, then use `skipToken` instead of fabricating a request value.

```typescript
// Query-options excerpt.
// BAD: absence becomes a request for a fabricated record.
const queryKey = ['team-report', teamId ?? ''] as const;
```

```typescript
import { skipToken, useQuery } from '@tanstack/react-query';

// GOOD: preserve absence and do not execute a request.
function useTeamReport(teamId: string | undefined) {
	return useQuery({
		queryKey: ['team-report', teamId] as const,
		queryFn:
			typeof teamId === 'undefined'
				? skipToken
				: async ({ queryKey: [, keyTeamId], signal }) => {
						if (typeof keyTeamId === 'undefined') throw new Error('Expected a team ID');
						const response = await fetch('/api/team-report/' + encodeURIComponent(keyTeamId), {
							signal,
						});
						if (!response.ok) throw new Error('Team report request failed');
						return await response.text();
					},
	});
}
```

The key preserves the optional identifier's type. Selecting `skipToken` does not narrow the context value, so the query function guards its own ID before constructing the request. This avoids a capture, cast, non-null assertion, or fake default while the hook still runs unconditionally.

The disabled state is part of the query contract, not a request for an empty record. `skipToken` does not support manual refetch; model a manually triggered request explicitly instead of bypassing the absent-ID rule.

Model `null` separately when the domain distinguishes it from `undefined`.
