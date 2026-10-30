# Exhaustive Decisions

Handle every member of a finite state space. Make a new member a type-checking failure instead of letting it fall through to an unrelated default.

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

// GOOD: each state has an explicit case.
function statusColor(status: Status) {
	switch (status) {
		case Status.Active:
			return 'green';
		case Status.Paused:
			return 'yellow';
		case Status.Stopped:
			return 'gray';
	}
}
```

Enforce completeness with the target language's exhaustive type checker or linter. Keep closed decisions limited to real cases instead of adding synthetic unreachable branches or assertion helpers. Validate external values at their input boundary.

Reserve a default branch for an open domain, such as an arbitrary string or number, where the remaining values share one defined behavior.
