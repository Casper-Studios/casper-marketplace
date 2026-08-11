# Optional Value Narrowing

Narrow an optional value before passing it to an operation that requires a present value.

```typescript
if (typeof value === 'undefined') throw new Error('Expected value to be defined');
useValue(value);
```

If absence is expected, preserve it in the operation's return or state contract instead of throwing.
