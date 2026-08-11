# Submitter Identity

Use submitter identity only when a form has multiple operations. A missing submitter is valid browser behavior.

```tsx
// BAD: keyboard and programmatic submissions have no required button identity.
const action = requireSubmitter(event).value;

// GOOD: reject a missing identity only when it selects a distinct operation.
const nativeEvent = event.nativeEvent;
if (!(nativeEvent instanceof SubmitEvent)) {
	setFormError('Choose an action.');
	return;
}
if (!(nativeEvent.submitter instanceof HTMLButtonElement)) {
	setFormError('Choose an action.');
	return;
}

const action = v.safeParse(Action, nativeEvent.submitter.value);
if (!action.success) {
	setFormError('Choose an action.');
	return;
}
```

Proceed normally when button identity does not affect the operation. When it selects an action, reject an absent or invalid submitter as an expected form error.

Never throw an invariant error or invent a default action for a missing submitter.
