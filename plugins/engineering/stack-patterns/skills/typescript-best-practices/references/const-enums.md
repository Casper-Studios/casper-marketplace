# Const Enums

Use a `const enum` for a named, closed set of primitive values that represents a durable domain concept such as a role, action, or status. Give members PascalCase names and assign the serialized value explicitly.

```typescript
export const enum RequestStatus {
	Idle = 'idle',
	Loading = 'loading',
	Success = 'success',
	Failed = 'failed',
}

const status = RequestStatus.Loading;
```

`const enum` provides named members to TypeScript while compiling away to the primitive value. Do not use a string-literal union for that named primitive set.

Keep `type` unions for structured discriminated variants, schema-inferred outputs, and ad-hoc local literal inference. Those types describe shapes or one-off inference rather than one reusable primitive vocabulary.
