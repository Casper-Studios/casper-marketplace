# Predicate Validation

Use `.refine()` for one boolean predicate that can report one validation issue. Set its message through the unified `error` option.

```typescript
const Password = z.string().refine(value => value.length >= 8, {
	error: 'Too short',
});
```

Keep the predicate focused on one value-level rule. Move cross-field and multi-issue validation to `.check()`.
