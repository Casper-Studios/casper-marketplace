# Raw Query Results

Prefer Drizzle builders and helpers. Use raw execution only when they cannot represent the database operation.

Ban generic result assertions such as `db.execute<T>(...)`. They do not validate driver output. Define a complete runtime schema for every returned row and parse the full collection before domain code consumes it.

```typescript
import * as v from 'valibot'; // or alternatively `zod`
import { sql } from 'drizzle-orm';

const IsolationRowSchema = v.object({ transaction_isolation: v.string() });
const parseIsolationRows = v.parser(v.array(IsolationRowSchema));

// node-postgres: SHOW is not represented by a Drizzle query builder.
const result = await db.execute(sql`SHOW transaction_isolation`);
const rows = parseIsolationRows(result.rows);
```

Keep the statement static. Interpolate values only through Drizzle's SQL template so the driver receives parameters instead of concatenated SQL.

Document the missing builder or helper beside the boundary. Keep driver-specific result handling there because raw execution result shapes differ across drivers.
