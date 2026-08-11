# Unchecked Assertions

Do not use `as SomeType` to claim that untrusted or insufficiently typed data has a shape. Validate at serialized boundaries and narrow values through runtime evidence.

```typescript
// BAD: an assertion supplies no proof.
const data = response as UserData;

// GOOD: validation creates trusted domain data.
const result = v.safeParse(UserDataSchema, response);
if (!result.success) throw new Error('Invalid response');
const data = result.output;
```

Treat network responses, JSON columns, and form data as untrusted. Use a schema skill for the concrete parser pattern.
