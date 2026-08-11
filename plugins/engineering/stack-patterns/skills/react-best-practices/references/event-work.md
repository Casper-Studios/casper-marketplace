# Event Work

Event handling is event-based, not data-reactive. Perform user-initiated work in the event handler that receives the action. Effects synchronize rendered data with external systems; they do not handle events.

```tsx
// BAD: the event sets a flag and a later effect performs the work.
function BadForm() {
	const [submitted, setSubmitted] = useState(false);
	useEffect(() => {
		if (submitted === true) navigate('/success');
	}, [submitted]);
	return <button onClick={() => setSubmitted(true)}>Submit</button>;
}

// GOOD: the event owns its direct consequences.
function Form() {
	function handleSubmit() {
		sendAnalytics('form_submit');
		navigate('/success');
	}

	return <button onClick={handleSubmit}>Submit</button>;
}
```

Keep event consequences close to their cause. This makes ordering and failure behavior visible instead of requiring a later render to trigger the operation.

Do not use state as an event queue. Use state only when the result must affect rendering after the event finishes.
