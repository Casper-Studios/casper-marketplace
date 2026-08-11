# Discriminated Union State

Model a finite state machine with a `const enum` discriminant and one interface for each valid state. Keep the structured state variants as a `type` union. Do not represent mutually exclusive states with parallel flags.

```typescript
// BAD: permits invalid combinations.
interface RequestStateFlags<Data> {
	isLoading: boolean;
	data?: Data;
	error?: Error;
}

// GOOD: each state has one valid shape.
const enum RequestStatus {
	Idle = 'idle',
	Loading = 'loading',
	Success = 'success',
	Error = 'error',
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
interface ErrorState {
	status: RequestStatus.Error;
	error: Error;
}

type RequestState<Data> = IdleState | LoadingState | SuccessState<Data> | ErrorState;
```

Use the discriminant to narrow state before accessing state-specific values.
