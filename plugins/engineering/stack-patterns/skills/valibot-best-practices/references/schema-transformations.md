# Schema Transformations

Parse and normalize in the schema so consumers receive the final shape, not raw wire values:

```typescript
const Timestamp = v.pipe(
	v.number(),
	v.transform(n => new Date(n)),
);
```
