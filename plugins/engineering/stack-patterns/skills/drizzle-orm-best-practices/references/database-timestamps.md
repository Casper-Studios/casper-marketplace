# Database-Generated Timestamps

Use the database as the source of persisted current time. Do not compute a persisted creation, update, deletion, or audit timestamp with `new Date()`, `Date.now()`, or another application clock.

Prefer the schema's database-default helper for creation timestamps when the selected column type supports it:

```typescript
import { integer, pgTable, timestamp } from 'drizzle-orm/pg-core';

const users = pgTable('users', {
	id: integer('id').primaryKey(),
	createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
});
```

Assign update timestamps with a database expression:

```typescript
// BAD: the application clock decides persisted current time.
import { eq } from 'drizzle-orm';

await db.update(users).set({ updatedAt: new Date() }).where(eq(users.id, userId));
```

```typescript
// GOOD for PostgreSQL and MySQL: the database clock decides persisted current time.
import { eq, sql } from 'drizzle-orm';

await db
	.update(users)
	.set({ updatedAt: sql`now()` })
	.where(eq(users.id, userId));
```

Use the dialect equivalent when `now()` is unavailable. SQLite uses `CURRENT_TIMESTAMP`. A schema callback such as `$onUpdateFn` is compatible with this rule only when it returns a database SQL expression instead of an application timestamp.

Keep the column's timestamp mode and selected driver representation explicit. Database ownership establishes one clock source. It does not make transaction-time evaluation semantics identical across dialects.
