# Schema as Single Source of Truth

Define the schema once and infer its type when a type name is needed. Never hand-write a type that the schema already proves. When both belong to the intended public API, export the schema and inferred type under the same name. Keep internal schemas, parsers, and inferred aliases local; do not create an unused alias or export for symmetry.

```typescript
import { z } from 'zod';

// BAD: a handwritten type can drift from the schema.
const UserSchema = z.object({ id: z.string(), name: z.string() });
interface UserInput {
	id: string;
	name: string;
}
```

```typescript
// GOOD: consumers need both the runtime schema and its parsed type.
export const User = z.object({ id: z.uuid(), name: z.string() });
export type User = z.infer<typeof User>;
```

```typescript
// GOOD: an internal boundary needs only its local schema and inferred result.
const User = z.object({ id: z.uuid(), name: z.string() });

function acceptUser(responseBody: unknown) {
	return User.parse(responseBody);
}
```
