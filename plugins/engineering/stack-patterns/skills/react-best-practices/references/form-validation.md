# Form Validation

Use a semantic form with named fields. Keep inputs uncontrolled unless their live values drive rendered UI, such as validation feedback. Controlled state serves that live presentation; it is not the submission payload.

In both cases, intercept `onSubmit`, prevent the browser's default navigation, and take a fresh `FormData` snapshot from `event.currentTarget`. Decode its transport representation and validate it before calling the domain operation. Submission reads the named form controls rather than capturing the input state that changes on every keystroke.

```tsx
import { useState, type FormEvent } from 'react';
import { decode } from 'decode-formdata';
import * as v from 'valibot';

const minimumNameLength = 3;
const CreateItem = v.object({ name: v.pipe(v.string(), v.minLength(minimumNameLength)) });
type CreateItem = v.InferOutput<typeof CreateItem>;

declare function createItem(input: CreateItem): Promise<void>;

// BAD: representation conversion alone does not establish trust.
async function saveUnvalidated(formData: FormData) {
	const input = decode(formData);
	await createItem(input);
}

// Both forms share submission logic that captures no live input state.
async function submit(event: FormEvent<HTMLFormElement>) {
	event.preventDefault();
	const formData = new FormData(event.currentTarget);
	const input = v.parse(CreateItem, decode(formData));
	await createItem(input);
}

// No live value is rendered, so named uncontrolled fields suffice.
function ItemForm() {
	return (
		<form onSubmit={submit}>
			<label>
				Name
				<input name="name" required minLength={minimumNameLength} />
			</label>
			<button type="submit">Create</button>
		</form>
	);
}

// Controlled state is justified by the live validation feedback.
function ItemFormWithFeedback() {
	const [name, setName] = useState('');
	const isTooShort = name.length > 0 && name.length < minimumNameLength;

	return (
		<form onSubmit={submit}>
			<label>
				Name
				<input
					name="name"
					value={name}
					onChange={event => setName(event.currentTarget.value)}
					required
					minLength={minimumNameLength}
					aria-invalid={isTooShort}
				/>
			</label>
			<p role="status">{isTooShort ? 'Enter at least three characters.' : null}</p>
			<button type="submit">Create</button>
		</form>
	);
}
```

Live validation feedback does not replace parsing at submission. Server-callable boundaries must also enforce their own input and authorization contracts regardless of a typed caller. Keep pending, failure, and reset behavior with the operation owner, and preserve `textarea` newline behavior and explicit shortcuts.
