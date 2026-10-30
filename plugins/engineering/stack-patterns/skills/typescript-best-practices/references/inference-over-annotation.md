# Inference Over Annotation

Infer locals and returns whenever TypeScript proves the intended contract. Add type information where inference cannot establish a required contract, or to establish an empty collection's contract at construction.

```typescript
// BAD: the valued async return is already inferred.
async function annotatedPort(port: number): Promise<number> {
	return port;
}

// GOOD: infer valued, valueless, sync, and async returns.
// Keep parameter contracts when context or an initializer cannot supply them.
async function portValue(port: number) {
	return port;
}

// GOOD: continuing branches establish the local's type before use.
// A missing initializer alone does not justify an annotation.
function roleLabel(isOwner: boolean) {
	let label;
	if (isOwner) label = 'Owner';
	else label = 'Member';
	return label.toUpperCase();
}
```

```typescript
interface User {
	name: string;
}

// GOOD: a throwing declaration can infer `void`; `never` states that it cannot return.
function fail(message: string): never {
	throw new Error(message);
}

// GOOD: assertion signatures need annotations and actual validation.
// Never annotate unvalidated input as trusted.
function assertUser(value: unknown): asserts value is User {
	if (
		typeof value !== 'object' ||
		value === null ||
		!('name' in value) ||
		typeof value.name !== 'string'
	) {
		throw new Error('Invalid user');
	}
}

const enum LoadStatus {
	Loading = 'loading',
	Loaded = 'loaded',
}

interface Loading {
	status: LoadStatus.Loading;
}

interface Loaded {
	status: LoadStatus.Loaded;
	value: string;
}

type LoadState = Loading | Loaded;

// GOOD: the owner's intentional return contract constrains every branch.
function createLoadState(value?: string): LoadState {
	return typeof value === 'undefined'
		? { status: LoadStatus.Loading }
		: { status: LoadStatus.Loaded, value };
}

// GOOD: `satisfies` checks this value while retaining its narrower inferred type.
function createLoadedState(value: string) {
	return { status: LoadStatus.Loaded, value } satisfies LoadState;
}
```

Give empty collections explicit element, key, and value contracts. Use an element annotation with an array literal and constructor generics for `Map` and `Set`. Do not rely on later insertions to evolve their types. Infer populated collections when their initial values establish the intended contract.

```typescript
// GOOD: the empty array's element contract constrains every later insertion.
const users: User[] = [];

// GOOD: constructor generics establish both key and value contracts.
const usersById = new Map<string, User>();
```

## Inferred Filter Predicates

In TypeScript 5.5 and later, let supported filter callbacks infer their predicates from the boolean expression.

```typescript
const values = ['Ada', 0, '', 42];

// BAD: the explicit predicate repeats inference and can assert an incorrect result.
const assertedNames = values.filter((value): value is string => typeof value === 'string');

// GOOD: the callback infers `string[]`; retain `filter` instead of substituting `flatMap`.
const names = values.filter(value => typeof value === 'string');

const candidates = [
	{ active: true, visible: false },
	{ active: true, visible: true },
];

// GOOD: pure conditions share one pass when behavior and narrowing are preserved.
// Keep stages separate if combining them changes effects or callback index/array inputs.
const visibleUsers = candidates.filter(user => user.active && user.visible);
```

Check the resulting type: compound or truthiness expressions do not always narrow. Preserve valid zero and empty values.

## Defining-Module Result Contracts

The defining module owns its named result contract. Do not derive `ReturnType` or `Awaited<ReturnType<...>>` from an imported function in a consumer.

```typescript
// reports.ts

// Ordinary call results stay inferred in the defining module.
export function summarize(rows: readonly number[]) {
	return { count: rows.length, total: rows.reduce((sum, value) => sum + value, 0) };
}

// Export a contract only when consumers need it; reuse an existing domain/schema
// type or an owner-local alias. No return annotation or forwarding wrapper is needed.
export type Summary = ReturnType<typeof summarize>;
```

```typescript
// BAD: the consumer derives a contract owned by `reports.ts`.
import { summarize } from './reports';
type Summary = ReturnType<typeof summarize>;
```

```typescript
// GOOD: the consumer imports the owner's named contract.
import type { Summary } from './reports';

function renderSummary(summary: Summary) {
	return summary.total.toFixed(2);
}
```
