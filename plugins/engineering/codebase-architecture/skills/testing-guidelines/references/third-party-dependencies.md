# Third-Party Dependencies

Do not test that a library parses, validates, serializes, queries, retries, renders, or raises errors according to its documented contract. A transparent wrapper does not transfer ownership of that behavior to the project.

```typescript
// BAD: retesting the Valibot library

const User = v.object({
	name: v.string(),
});

test('parses a valid user', () => {
	expect(v.parse(User, { name: 'Ada' })).toEqual({ name: 'Ada' });
});

test('rejects an invalid user', () => {
	expect(() => v.parse(User, { name: 42 })).toThrow();
});
```

Valibot owns both results. Add no test.

When a schema uses project-owned domain logic, extract that logic into a pure predicate or transition and test it directly. Do not use schema parsing as the test harness for business policy.

The same rule applies to:

- A schema library rejecting a missing field.
- An ORM returning mapped records.
- A context manager calling a dependency's close operation.
- A UI primitive rendering the children passed to it.
- A mock returning the value configured on that mock.
