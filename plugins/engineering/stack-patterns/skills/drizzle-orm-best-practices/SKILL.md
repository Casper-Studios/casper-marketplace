---
name: drizzle-orm-best-practices
description: Opinionated, dialect-aware Drizzle ORM conventions for helper-first query construction, scoped projections, mutation cardinality, transaction boundaries, database timestamps, runtime decoding, and raw-query validation. Use when writing or reviewing Drizzle schemas, selects, filters, aggregates, inserts, updates, deletes, transactions, `sql` expressions, driver mutation results, or database-generated timestamps.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# Drizzle ORM Best Practices

Treat Drizzle as a typed SQL builder over SQL dialect and driver contracts. Search its builders, operators, and helpers before writing `sql`. Keep data scope and invariants in SQL, read mutation metadata from the configured driver, let the database own persisted current time, and decode every unavoidable raw result at runtime.

## Library Sources

- GitHub repository ID: `drizzle-team/drizzle-orm`
- Context7 library ID: `/drizzle-team/drizzle-orm-docs`
- DeepWiki repository ID: `drizzle-team/drizzle-orm`

Use Context7 for current documentation and DeepWiki when documentation is insufficient or conflicts with implementation.

## References

Read as many linked references as are relevant to the current task before writing or reviewing Drizzle code.

- Before introducing any raw SQL, exhaust the [built-in query builders and helpers](./references/built-in-query-helpers.md) so Drizzle keeps ownership of SQL generation, parameterization, and result decoding.
- When a read exposes more data than its caller needs or checks access after retrieval, enforce [query scope at the database boundary](./references/query-scope.md).
- When behavior depends on whether a write changed zero, one, or many rows, interpret [mutation cardinality from the driver result](./references/mutation-cardinality.md) without returning row data solely to count it.
- When several statements preserve one invariant, define a [transaction boundary](./references/transaction-boundaries.md) that passes the transaction through every participating helper.
- When persisted timestamps mean the database's current time, use [database-generated timestamps](./references/database-timestamps.md) instead of an application clock.
- When an unavoidable `sql` expression returns a value, apply [runtime expression decoding](./references/sql-expression-decoding.md) and ban compile-time-only result annotations.
- When a builder cannot represent a result-bearing operation, contain it behind [complete raw-result validation](./references/raw-query-results.md) rather than trusting a generic result type.
