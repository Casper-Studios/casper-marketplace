# Scope State

Place state in the smallest component subtree that owns it.

```tsx
// BAD: a layout shell owns form details that no sibling uses.
function BadEditorPanel() {
	const [formData, setFormData] = useState({ name: '' });
	return (
		<section>
			<Form data={formData} onChange={setFormData} />
		</section>
	);
}

// GOOD: the form owns its own details.
function EditorPanel() {
	return (
		<section>
			<FormWithState />
		</section>
	);
}
```

Lift state only when multiple sibling consumers need the same source of truth. Do not lift state preemptively to make a parent look "in control."

Local state narrows re-renders, makes ownership explicit, and lets component identity control lifetime. Use context only when one coherent subsystem owns state consumed at multiple depths.
