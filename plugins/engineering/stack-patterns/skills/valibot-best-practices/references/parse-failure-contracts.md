# Parse Failure Contracts

Choose Valibot's parsing API from the failure contract at the boundary.

- Use `v.parse` when invalid input violates a contract and the operation must stop.
- Use `v.safeParse` when invalid input is an expected branch that the caller must render, return, or otherwise handle.

```typescript
import * as v from 'valibot';

const User = v.object({ id: v.pipe(v.string(), v.uuid()), name: v.string() });
const CreateKpiInput = v.object({ name: v.string(), amount: v.number() });

// A malformed provider response aborts this operation.
const acceptProviderUser = v.parser(User);

// Invalid submitted data is an expected branch with explicit issues.
function acceptKpiInput(submitted: unknown) {
	const result = v.safeParse(CreateKpiInput, submitted);
	if (result.success === false) return { issues: result.issues };
	return { input: result.output };
}
```

Do not choose `safeParse` only to avoid defining the failure behavior.

Reuse immutable schemas at their owning lifetime. When a callback needs a parser function, construct `v.parser` or `v.safeParser` once according to that same failure contract, then reuse it. Keep direct `v.parse(Schema, input)` for a one-off parse; do not add a parser wrapper for symmetry.

```typescript
// BAD: rebuilds the same immutable schema and parser for every row.
function parseCountsRepeatedly(rows: readonly string[]) {
	return rows.map(row =>
		v.parser(v.pipe(v.string(), v.toNumber(), v.integer(), v.minValue(0)))(row),
	);
}
```

```typescript
// GOOD: invalid provider rows abort; construction belongs to the schema owner.
const Count = v.pipe(v.string(), v.toNumber(), v.integer(), v.minValue(0));
const parseCount = v.parser(Count);
function parseCounts(rows: readonly string[]) {
	return rows.map(row => parseCount(row));
}
```

Keep request-specific configuration within its actual lifetime; hoist only definitions that are invariant across those requests. Reuse a parser definition, not a previous input's validation result.
