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

`const enum` is the convention for these named primitive sets; do not replace one with a string-literal union. With TypeScript's normal enum erasure, member references inline their primitive values. Emission depends on the toolchain and options such as `preserveConstEnums`; do not promise erasure from every emitter.

Check the package declaration and consumer compilation contract before exposing a `const enum` publicly. Ambient const enums in distributed declarations have `isolatedModules` and dependency-version pitfalls. A local convention does not establish that every downstream compiler can consume the same public declarations.

Keep `type` unions for structured discriminated variants, schema-inferred outputs, and ad-hoc local literal inference. Those types describe shapes or one-off inference rather than one reusable primitive vocabulary.
