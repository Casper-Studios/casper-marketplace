# Examples

Show, don't tell. Contrast approaches to the same problem, then briefly explain why one is better. Change only the decision being taught. Use a single example when no useful contrast exists.

Label examples with `BAD:` and `GOOD:` comments inside code fences, not Markdown headings. Do not comment out the implementation.

Teach the decision, not basic API syntax or a tutorial.

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

The second version calls `save` directly from the click handler, removing the extra state and effect. Explain that difference instead of narrating each line.

Keep excerpts focused and identify omitted setup. Syntax and APIs must remain correct. Complete or runnable examples must compile on their own; excerpts need not become standalone programs.
