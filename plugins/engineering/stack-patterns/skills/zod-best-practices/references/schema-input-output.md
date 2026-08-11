# Schema Input and Output

Infer a schema's output with `z.infer<typeof Schema>`. Use `z.input<typeof Schema>` only when a transform or default makes the accepted input differ from the parsed output.

```typescript
const Timestamp = z.string().transform(value => new Date(value));

type TimestampInput = z.input<typeof Timestamp>; // string
type TimestampOutput = z.infer<typeof Timestamp>; // Date
```

Do not hand-write either type when the schema already proves it.
