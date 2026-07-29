# Split Results

With `noUncheckedIndexedAccess: true`, a `.split()` result can be absent at every indexed position. Preserve that absence until the owning display or domain policy resolves it.

```typescript
// BAD: split('@')[0] is string | undefined.
const localPart = email.split('@')[0];

// GOOD: choose display fallbacks deliberately.
const [localPart] = email.split('@');
const displayName = fullName ?? localPart ?? email;
```

Do not use an arbitrary empty-string fallback merely to satisfy a type.
