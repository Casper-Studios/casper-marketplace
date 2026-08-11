# Enforce Invariants

Choose representations that exclude invalid combinations. Do not represent one domain state with independent flags or optional fields that can contradict each other.

```typescript
// BAD: contradictory combinations are representable.
interface RequestFlags<Data> {
	isLoading: boolean;
	data?: Data;
	error?: Error;
}

// GOOD: each state has one valid shape.
const enum RequestStatus {
	Idle = 'idle',
	Loading = 'loading',
	Success = 'success',
	Failure = 'failure',
}

interface IdleState {
	status: RequestStatus.Idle;
}
interface LoadingState {
	status: RequestStatus.Loading;
}
interface SuccessState<Data> {
	status: RequestStatus.Success;
	data: Data;
}
interface FailureState {
	status: RequestStatus.Failure;
	error: Error;
}

type RequestState<Data> = IdleState | LoadingState | SuccessState<Data> | FailureState;
```

If the representation can exclude an invalid state, redesign the representation. Otherwise, validate the invariant at the boundary and fail explicitly when it is violated.

Do not add fallback values to make an invalid combination executable. Validate external values before they enter the representation. After construction, internal code can rely on the invariant.
