# Schema as Single Source of Truth

Define the schema once and infer the type from it. Export both under the same name so callers import one symbol. Never hand-write a type that a schema already proves.

```typescript
// BAD: hand-written type drifts from the schema
const UserSchema = z.object({ id: z.string(), name: z.string() });
interface UserInput {
	id: string;
	name: string;
}

// GOOD: schema and type share one name, one definition
export const User = z.object({ id: z.uuid(), name: z.string() });
export type User = z.infer<typeof User>;
```
