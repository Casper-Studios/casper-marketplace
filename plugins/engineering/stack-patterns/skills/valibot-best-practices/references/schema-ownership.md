# Schema as Single Source of Truth

Define the schema once and infer its type when a type name is needed. Never hand-write a type that the schema already proves. When both belong to the intended public API, export the schema and inferred type under the same name. Keep internal schemas, parsers, and inferred aliases local; do not create an unused alias or export for symmetry.

```typescript
import * as v from 'valibot';

// BAD: a handwritten type can drift from the schema.
const UserSchema = v.object({ id: v.string(), name: v.string() });
interface UserInput {
	id: string;
	name: string;
}
```

```typescript
// GOOD: consumers need both the runtime schema and its parsed type.
export const User = v.object({ id: v.pipe(v.string(), v.uuid()), name: v.string() });
export type User = v.InferOutput<typeof User>;
```

```typescript
// GOOD: an internal boundary needs only its local schema and inferred result.
const User = v.object({ id: v.pipe(v.string(), v.uuid()), name: v.string() });
const acceptUser = v.parser(User);
```
