# Validation Error Rendering

When a normal validation branch must surface errors, derive the representation from Zod's error object rather than discarding its information.

```typescript
const result = CreateKpiInput.safeParse(formData);
if (!result.success) {
	const fields = z.treeifyError(result.error);
	const message = z.prettifyError(result.error);
	return { fields, message };
}
```

Use `z.treeifyError` for nested field-level UI and `z.prettifyError` for a human-readable log or summary. Do not replace validation errors with arbitrary empty state.
