# Optional Arguments

Omit an optional argument when omission expresses the intent. Pass `void 0` only when an API requires an explicit undefined argument.

```typescript
// BAD: explicit undefined when omission is supported.
reset(undefined);

// GOOD: omit the optional argument.
reset();

// GOOD: the API requires an argument at this position.
resetAt(index, void 0);
```
