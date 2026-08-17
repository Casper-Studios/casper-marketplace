# Mutation Cardinality

Treat zero, one, and many affected rows as distinct outcomes when behavior depends on mutation cardinality. Do not return row data solely to count affected rows.

Drizzle preserves the configured adapter's mutation result when `.returning()` is absent. Read the documented access path for that exact adapter. These representative paths are not interchangeable:

| Adapter                         | Affected-row access path |
| ------------------------------- | ------------------------ |
| `node-postgres`                 | `result.rowCount`        |
| `mysql2` and MySQL Proxy        | `result[0].affectedRows` |
| PlanetScale and TiDB Serverless | `result.rowsAffected`    |
| LibSQL                          | `result.rowsAffected`    |
| `better-sqlite3`                | `result.changes`         |
| Cloudflare D1                   | `result.meta.changes`    |

There is no portable Drizzle affected-row property. Verify the current adapter contract instead of inferring it from the SQL dialect. Keep the adapter-specific read at the database boundary. Normalize it into an application-owned mutation outcome only when several callers or adapters need the same contract.

```typescript
// node-postgres
import { and, eq, sql } from 'drizzle-orm';

const result = await db
	.update(comments)
	.set({ deletedAt: sql`now()` })
	.where(and(eq(comments.id, commentId), eq(comments.userId, currentUserId)));

if (result.rowCount !== 1)
	throw new Error(`Expected to delete one comment, changed ${result.rowCount}`);
```

Use `.returning()` when supported and when the caller needs returned columns. Use `.$returningId()` for MySQL inserted identifiers. Treat either API as data retrieval, not as a portable substitute for affected-row metadata.
