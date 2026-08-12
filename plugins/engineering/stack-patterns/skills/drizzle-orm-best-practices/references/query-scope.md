# Query Scope

Project only the columns the caller needs. Put ownership, tenancy, authorization, visibility, and other access predicates in the database statement before rows enter application memory.

```typescript
import { and, eq } from 'drizzle-orm';

const rows = await db
	.select({ id: comments.id, body: comments.body })
	.from(comments)
	.where(and(eq(comments.id, commentId), eq(comments.userId, currentUserId)));
```

Validate untrusted identifiers, filters, sort choices, and pagination values before query construction. Use Drizzle helpers to parameterize values and compose predicates. Do not fetch broadly and then filter protected rows in JavaScript.

Keep authorization predicates in the same statement as the requested data. A prior authorization query creates a time-of-check/time-of-use gap unless a transaction and isolation design explicitly closes it.
