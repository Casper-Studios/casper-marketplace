# Exhaustive Decisions

Use a `switch` when every member of a closed enum or structured union has distinct behavior. Make the compiler prove that the fallback is unreachable.

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
// GOOD: Make the Compiler Prove the Fallback Is Unreachable
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
		default:
			throw new Error('unhandled status');
	}
}
```

Use `satisfies Record<Enum, Value>` only for static data that has one value for every member of a closed enum.

```typescript
const statusColors = {
	[Status.Success]: 'green',
	[Status.Failed]: 'red',
	[Status.Pending]: 'yellow',
} satisfies Record<Status, string>;
```
