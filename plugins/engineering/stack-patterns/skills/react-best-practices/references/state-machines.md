# State Machines

Represent related mutually exclusive state as one discriminated union rather than correlated booleans and nullable values.

```tsx
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
		case RequestStatus.Success:
			return <JobDetailInner data={request.data} />;
		case RequestStatus.Failure:
			return <ErrorBanner error={request.error} />;
	}
}
```

Use a state machine when one state changes the valid fields, actions, or rendering of another. Do not introduce one for independent local values such as an input string and an open flag.

Transition through named events or functions that construct only valid variants. Do not mutate one field of a union-shaped state while leaving fields from the previous variant behind.
