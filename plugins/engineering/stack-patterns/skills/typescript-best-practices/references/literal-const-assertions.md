# Literal Const Assertions

Use `as const` for literals and non-primitive constants when consumers require readonly tuple or literal-union inference. Do not use it as a default assertion mechanism.

```typescript
// GOOD: preserve a readonly literal tuple required by a consumer.
const requestMethods = ['GET', 'POST'] as const;

// GOOD: preserve literal values in a constant lookup.
const statusColors = {
	success: 'green',
	failed: 'red',
} as const;
```
