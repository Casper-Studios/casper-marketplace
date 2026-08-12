# Built-In Query Helpers

Use Drizzle's public API before `sql`. A builder or helper preserves dialect behavior, parameterization, types, and runtime mapping that handwritten SQL must reconstruct.

Apply this decision order:

1. Use a builder method for selects, joins, set operations, grouping, ordering, pagination, inserts, updates, deletes, and driver-supported transactions.
2. Use a root-exported helper for predicates, ordering, and aggregates.
3. Use a schema or column helper for defaults, generated values, and conflict behavior.
4. Check current Context7 documentation when memory does not establish whether a helper exists.
5. Use DeepWiki to inspect implementation only when the documentation is incomplete.
6. Use `sql` only after the previous checks establish that Drizzle has no suitable API.

Prefer these helpers over equivalent raw fragments:

| Need                          | Drizzle API                                      |
| ----------------------------- | ------------------------------------------------ |
| Count rows or non-null values | `count()`, `count(column)`                       |
| Count distinct values         | `countDistinct(column)`                          |
| Average or distinct average   | `avg(column)`, `avgDistinct(column)`             |
| Sum or distinct sum           | `sum(column)`, `sumDistinct(column)`             |
| Minimum or maximum            | `min(column)`, `max(column)`                     |
| Equality and comparison       | `eq`, `ne`, `gt`, `gte`, `lt`, `lte`             |
| Boolean composition           | `and`, `or`, `not`                               |
| Membership and ranges         | `inArray`, `notInArray`, `between`, `notBetween` |
| Null and existence checks     | `isNull`, `isNotNull`, `exists`, `notExists`     |
| Pattern matching              | `like`, `notLike`                                |
| Ordering                      | `asc`, `desc`                                    |
| Transactions                  | `db.transaction` when the driver supports it     |

Use the dialect-specific API when the selected dialect supports it:

- Use `ilike` and `notIlike` only with PostgreSQL-compatible `ILIKE`.
- Use `arrayContains`, `arrayContained`, and `arrayOverlaps` only with PostgreSQL-compatible array operators.
- Use `.onConflictDoNothing()` and `.onConflictDoUpdate()` with PostgreSQL and SQLite.
- Use `.onDuplicateKeyUpdate()` with MySQL and SingleStore.
- Use `.returning()` only with dialects that support returned mutation rows.
- Use `.$returningId()` for MySQL inserted primary keys.

Drizzle's aggregate helpers already own their runtime mapping. `count()` and `countDistinct()` return `number` and map through `Number`. `avg()`, `avgDistinct()`, `sum()`, and `sumDistinct()` return `string | null` and map non-null database results through `String`. The string is the JavaScript representation of the numeric aggregate; it does not mean that the SQL aggregate is textual. The result is `null` when SQL returns `NULL`, such as when no qualifying non-null value contributes to the aggregate. `min()` and `max()` use the selected column's decoder when a column supplies one. Do not replace these helpers with raw SQL merely to add `.mapWith()`. Validate the selected result afterward only when the domain contract is stricter than the helper's documented output.

```typescript
// BAD: raw SQL reimplements an existing aggregate helper.
import { sql } from 'drizzle-orm';

const rawSummary = await db.select({ total: sql`count(*)`.mapWith(Number) }).from(users);
```

```typescript
// GOOD: count owns SQL generation and runtime conversion.
import { count } from 'drizzle-orm';

const summary = await db.select({ total: count() }).from(users);
```

Raw SQL remains appropriate for an unsupported database function, a window expression, `case` expressions, a dialect-specific ordering modifier such as `nulls last`, or arithmetic that Drizzle does not model with a helper. A raw fragment used only in a predicate, ordering clause, join condition, or write expression does not return a value to application code and therefore does not need a result decoder.

Confirm transaction support in the configured driver before using `db.transaction`. An adapter can expose the method without implementing transactions; MySQL Proxy, for example, throws when it is called.
