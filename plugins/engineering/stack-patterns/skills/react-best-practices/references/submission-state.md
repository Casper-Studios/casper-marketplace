# Submission State

Model pending work as form-wide state. Disable every submit control while submission is active.

```tsx
// BAD: one button cannot represent keyboard or form-wide submission state.
function BadForm() {
	function onSubmit(event: React.FormEvent<HTMLFormElement>) {
		event.preventDefault();
		const submitter = event.nativeEvent.submitter;
		if (submitter instanceof HTMLButtonElement) submitter.disabled = true;
	}

	return (
		<form onSubmit={onSubmit}>
			<button type="submit">Create</button>
		</form>
	);
}

// GOOD: every submit action reflects the shared operation lifetime.
function Form() {
	const [isSubmitting, setIsSubmitting] = useState(false);
	return (
		<form>
			<button type="submit" disabled={isSubmitting}>
				Create
			</button>
			<button type="submit" disabled={isSubmitting}>
				Save Draft
			</button>
		</form>
	);
}
```

Do not mutate one submit button through `SubmitEvent.submitter`. The submitter is validly `null` for keyboard and programmatic submission, and one element does not represent the whole form lifecycle.

Clear pending state when the submission settles. Keep validation errors distinct from pending state so a failed submission leaves controls usable.

Keep cancellation, network failure, and validation messages explicit. Do not use a disabled control as the only indication that the form is submitting.

When a form has multiple submit buttons, use the same form-wide pending state for every action.

Announce pending work with accessible status text when the operation takes noticeable time. Keep the message independent of button identity so keyboard submission follows the same experience.
