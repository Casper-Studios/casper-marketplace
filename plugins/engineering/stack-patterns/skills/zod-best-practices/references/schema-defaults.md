# Schema Defaults

`.default(value)` makes input optional and output non-optional. The default must be assignable to the output type and short-circuits without parsing. Use `.prefault(value)` when the fallback must run through validation as raw input.

Use either only when the domain contract defines the exact value for absence. Do not use schema defaults to turn an unknown or invalid value into an arbitrary fallback.

```typescript
const PageSize = z.number().int().positive().default(20);
```

This default is valid only when omitted page size means exactly `20` in the domain contract.
