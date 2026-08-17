# SQL Expression Decoding

Ban `sql<T>` everywhere. Its generic argument changes the TypeScript type without inspecting the database value.

Use a Drizzle builder or helper before raw SQL. When no helper represents a result-bearing expression, attach `.mapWith(...)` at the expression boundary. Pass an existing column when its decoder matches the result. Pass a named runtime parser when the result needs validation or transformation.

Use any synchronous runtime parser that accepts untrusted input, returns its validated output, and throws on a contract violation. Valibot's `v.parser` is one compatible primitive.

Create reusable schemas and parsers at module scope:

```typescript
import { sql } from 'drizzle-orm';

// BAD: the generic asserts a type without decoding the PostgreSQL JSON result.
const unsafeRows = await db
	.select({ title: sql<string | null>`${documents.metadata}->>'title'` })
	.from(documents);
```

```typescript
import * as v from 'valibot';
import { sql } from 'drizzle-orm';

const NullableTitleSchema = v.nullable(v.string());
const parseNullableTitle = v.parser(NullableTitleSchema);

// GOOD: the parser validates the raw selected value.
const rows = await db
	.select({ title: sql`${documents.metadata}->>'title'`.mapWith(parseNullableTitle) })
	.from(documents);
```

Do not construct a schema or parser inline in the query. A module-scope decoder gives the boundary one stable name and avoids rebuilding the same parser.

Use a column decoder for an expression with the same driver representation:

```typescript
const rows = await db
	.select({ normalizedEmail: sql`lower(${users.email})`.mapWith(users.email) })
	.from(users);
```

A bare `sql` fragment is valid when it returns no value to application code, such as an unsupported predicate, join condition, ordering modifier, arithmetic write expression, or database-time assignment. Never concatenate untrusted strings into an SQL fragment.
