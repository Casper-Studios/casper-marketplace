# Exhaustive Decisions

Use a `switch` when every member of a closed enum or structured union has distinct behavior. Do not add synthetic `default` branches, `never` annotations, `satisfies never`, or assertion helpers to prove a closed switch exhaustive.

```typescript
// BAD: Hide Missing Enum Members Behind a Default
const enum Status {
	Success = 'success',
	Failed = 'failed',
	Pending = 'pending',
}

function getStatusColor(status: Status) {
	switch (status) {
		case Status.Success:
			return 'green';
		case Status.Failed:
			return 'red';
		default:
			return 'gray';
	}
}
```

The fallback silently accepts `Status.Pending` and any future member.

```typescript
// GOOD: Handle Each Member Explicitly
const enum Status {
	Success = 'success',
	Failed = 'failed',
	Pending = 'pending',
}

function getStatusColor(status: Status) {
	switch (status) {
		case Status.Success:
			return 'green';
		case Status.Failed:
			return 'red';
		case Status.Pending:
			return 'yellow';
	}
}
```

An exhaustive `switch` needs no `default`. TypeScript already treats the end of the `switch` as unreachable, so a `default` that returns, throws, or logs is dead code.

Add a `default` only when the switched type is open, such as `string` or `number`, and the remaining values share one defined behavior.

Use `satisfies Record<Enum, Value>` only for static data that has one value for every member of a closed enum.

```typescript
const statusColors = {
	[Status.Success]: 'green',
	[Status.Failed]: 'red',
	[Status.Pending]: 'yellow',
} satisfies Record<Status, string>;
```
