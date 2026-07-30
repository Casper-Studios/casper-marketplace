# Examples

Use examples to demonstrate an opinion that prose alone can leave ambiguous. Do not teach ordinary API syntax or reproduce a tutorial that current documentation can supply.

Add a "BAD"/"GOOD" counterpart when the rejected approach is plausible, compiles, or appears to work. Keep a single example when the reference only establishes one canonical syntax or declarative shape.

Put the labels inside the code fence as comments. The BAD implementation must remain real code; never comment it out. Use the same small scenario for both sides and change only the decision under review.

```tsx
// BAD: the state change hides a click-driven operation behind reactivity.
import { useEffect, useState } from 'react';

function save() {}

function SaveButton() {
	const [requested, setRequested] = useState(false);

	useEffect(() => {
		if (requested) save();
	}, [requested]);

	return <button onClick={() => setRequested(true)}>Save</button>;
}
```

```tsx
// GOOD: the event handler owns work caused by the event.
function save() {}

function SaveButton() {
	return <button onClick={save}>Save</button>;
}
```

Make every snippet self-contained and valid for its claimed language or framework. Do not leave undefined placeholders, invalid imports, conflicting declarations, or deprecated APIs in "GOOD" examples.

Use a fence language that matches the snippet. A `json` fence cannot contain comments; use `jsonc` when comments are part of the example, or keep the explanation outside the fence.

Do not use secondary Markdown headings for "GOOD" and "BAD". Do not preserve a bad example merely to achieve visual symmetry.
