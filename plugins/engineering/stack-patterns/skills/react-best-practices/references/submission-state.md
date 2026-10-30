# Submission State

Read pending, result, and error state from the existing submission owner and pass that state to the form when the owner lives above it. Do not mirror the operation lifecycle in local flags or couple it to the controlled state used for live input feedback. Every submit control must reflect the same pending state.

```tsx
import type { FormEvent } from 'react';
import { decode } from 'decode-formdata';
import * as v from 'valibot';

const SaveInput = v.object({ name: v.pipe(v.string(), v.minLength(1)) });
type SaveInput = v.InferOutput<typeof SaveInput>;

interface FormProps {
	onSave: (input: SaveInput) => void;
	isPending: boolean;
	error: Error | null;
}

// BAD: disabling one clicked element misses keyboard and other submit controls.
function disableSubmitter(event: FormEvent<HTMLFormElement>) {
	const nativeEvent = event.nativeEvent;
	if (nativeEvent instanceof SubmitEvent) {
		const { submitter } = nativeEvent;
		if (submitter instanceof HTMLButtonElement) submitter.disabled = true;
	}
}

// GOOD: the operation owner supplies status; submission parses its own snapshot.
function Form({ onSave, isPending, error }: FormProps) {
	function submit(event: FormEvent<HTMLFormElement>) {
		event.preventDefault();
		const formData = new FormData(event.currentTarget);
		onSave(v.parse(SaveInput, decode(formData)));
	}

	let alert;
	if (error !== null) alert = <p role="alert">{error.message}</p>;

	return (
		<form onSubmit={submit}>
			<label>
				Name
				<input name="name" required />
			</label>
			<button type="submit" disabled={isPending}>
				Save
			</button>
			<p role="status">{isPending ? 'Saving...' : null}</p>
			{alert}
		</form>
	);
}
```

Present validation, cancellation, and request failures separately from progress so controls remain usable after a settled failure. Choose draft reset behavior deliberately after the intended outcome; typing and submission status have separate lifetimes.
