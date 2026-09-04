# Inference Over Annotation

Let TypeScript infer a type when that inference already proves the intended contract. Add an annotation when inference cannot express the required contract or when the function deliberately owns a stable output contract. Do not duplicate an inferred type merely for documentation.

```typescript
// BAD: `void` and `async` results are derivable from the implementation.

function registerUser({ token, user }: Registration): void {
	users.set(token, user);
}

async function listen(port = 4001): Promise<number> {
	return port;
}
```

```typescript
// GOOD: retain parameter contracts and infer derivable returns.

function registerUser({ token, user }: Registration) {
	users.set(token, user);
}

async function listen(port = 4001) {
	return port;
}
```

Annotate declared parameters unless an initializer or contextual type supplies the intended type. Return inference applies equally to valued, valueless, synchronous, and asynchronous functions and methods.

Use an explicit return annotation when inference would not express the required contract. A function declaration that only throws can infer `void`; annotate `never` to state that it cannot return. Assertion signatures likewise require explicit annotations.

```typescript
// GOOD: inference alone cannot communicate the required control-flow contract.
function fail(message: string): never {
	throw new Error(message);
}

// GOOD: runtime evidence establishes the asserted contract.
function assertUser(value: unknown): asserts value is User {
	if (!isUser(value)) throw new Error('Invalid user');
}
```

Use an explicit return annotation when a function owns a stable output contract that must constrain every returned value.

```typescript
interface Loading {
	status: 'loading';
}

interface Loaded {
	status: 'loaded';
	value: string;
}

type LoadState = Loading | Loaded;

// GOOD: the function boundary owns and enforces LoadState.
function createLoadState(value?: string): LoadState {
	return value === undefined ? { status: 'loading' } : { status: 'loaded', value };
}
```

Use `satisfies` on an ad-hoc returned value when it must conform to a contract while retaining narrower inferred literals for callers.

```typescript
// GOOD: prove conformance without widening the inferred result to LoadState.
function createLoadedState(value: string) {
	return { status: 'loaded', value } satisfies LoadState;
}
```

An annotation is justified only when it adds information or enforces an intentional contract. Supply missing inference at the narrowest site.

```typescript
// GOOD: an empty array has no elements from which to infer User.
const users: User[] = [];

// GOOD: the constructor needs its key and value contracts.
const usersById = new Map<string, User>();
```

Prefer a generic argument to a variable annotation when a constructor or function accepts the missing information directly. Never use a return annotation to claim that unvalidated input is trusted.
