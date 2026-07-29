# Conditional Mounting

Mount a stateful child only while the UI needs its state.

```tsx
// BAD: keeping the form mounted requires a reset effect to simulate a new lifetime.
function BadEditorPanel({ isOpen }: { isOpen: boolean }) {
	return <EditForm isOpen={isOpen} />;
}

// GOOD: mounting defines the form state lifetime directly.
function EditorPanel({ isOpen }: { isOpen: boolean }) {
	return isOpen === true ? <EditForm /> : null;
}
```

The shell owns visibility. The mounted child owns its form state. Hiding the panel unmounts the child and discards that state; showing it again creates a fresh state lifetime.

Use this for dialogs, sheets, tabs, accordions, and wizard steps when state must not survive hiding. Do not add a reset effect for a state lifetime that unmounting already defines.

Use a persistent mounted child only when hiding must preserve unsaved input, focus, an expensive resource, or another explicit state-lifetime requirement. State survival must be a deliberate product decision.

Keep the conditional boundary immediately above the stateful subtree so unrelated shell state survives visibility changes.
