# Exhaustive Decisions

Handle every member of a finite state space. Make new or unknown members fail visibly instead of falling through to an unrelated default.

```typescript
const enum Status {
	Active = 'active',
	Paused = 'paused',
	Stopped = 'stopped',
}

// BAD: every non-active state inherits gray.
function statusColorWithFallback(status: Status) {
	if (status === Status.Active) return 'green';
	return 'gray';
}

// GOOD: the compiler proves every state is handled.
function statusColor(status: Status) {
	switch (status) {
		case Status.Active:
			return 'green';
		case Status.Paused:
			return 'yellow';
		case Status.Stopped:
			return 'gray';
		default:
			throw new Error('unhandled status');
	}
}
```

Use the target language's compiler-supported exhaustiveness mechanism when one exists. This directive owns the language-agnostic requirement.
