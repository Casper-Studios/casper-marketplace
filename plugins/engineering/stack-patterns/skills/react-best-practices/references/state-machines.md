# State Machines

Represent related mutually exclusive state as one discriminated union rather than correlated booleans and nullable values.

```tsx
const enum RequestStatus {
	Idle = 'idle',
	Loading = 'loading',
	Error = 'error',
	Success = 'success',
}

interface IdleRequest {
	status: RequestStatus.Idle;
}

interface LoadingRequest {
	status: RequestStatus.Loading;
}

interface FailedRequest {
	status: RequestStatus.Error;
	error: Error;
}

interface SuccessfulRequest<T> {
	status: RequestStatus.Success;
	data: T;
}

type RequestState<T> = IdleRequest | LoadingRequest | FailedRequest | SuccessfulRequest<T>;

function BadRequestView() {
	// BAD: invalid combinations are representable.
	const [isLoading] = useState(false);
	const [error] = useState<Error | null>(null);
	const [data] = useState<JobData | null>(null);
	return <RequestContent isLoading={isLoading} error={error} data={data} />;
}

function GoodRequestView() {
	// GOOD: the domain type defines valid states.
	const [request] = useState<RequestState<JobData>>({
		status: RequestStatus.Idle,
	});
	return <RequestStateView request={request} />;
}

function RequestStateView({ request }: { request: RequestState<JobData> }) {
	switch (request.status) {
		case RequestStatus.Idle:
			return <IdleNotice />;
		case RequestStatus.Loading:
			return <Spinner />;
		case RequestStatus.Error:
			return <ErrorBanner error={request.error} />;
		case RequestStatus.Success:
			return <JobDetailInner data={request.data} />;
		default: {
			const unreachable: never = request;
			throw new Error(`Unhandled request state: ${String(unreachable)}`);
		}
	}
}
```

Define an enum-backed discriminant and variants that contain only the fields valid for that state. Render each discriminant exhaustively.

Use a state machine when one state changes the valid fields, actions, or rendering of another. Do not introduce one for independent local values such as an input string and an open flag.

Transition through named events or functions that construct only valid variants. Do not mutate one field of a union-shaped state while leaving fields from the previous variant behind.

Treat an unhandled discriminant as an internal invariant failure rather than rendering a fabricated fallback.
