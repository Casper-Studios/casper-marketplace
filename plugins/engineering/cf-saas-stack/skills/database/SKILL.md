---
name: database
description: Drizzle ORM database schema patterns and conventions for SQLite/D1
user-invocable: false
---

# Database Schema (Drizzle ORM)

## Overview
Database schemas use Drizzle ORM with SQLite. All schema definitions are in `app/db/schema.ts`.

## Table Definition Pattern
```typescript
import { sql } from "drizzle-orm";
import { sqliteTable, text, integer } from "drizzle-orm/sqlite-core";

export const myTable = sqliteTable("my_table", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  description: text("description"),
  email: text("email").notNull().unique(),
  isActive: integer("is_active", { mode: "boolean" }).default(false).notNull(),
  status: text("status", { enum: ["pending", "active", "completed"] }).default("pending").notNull(),
  counter: integer("counter").default(0).notNull(),
  metadata: text("metadata", { mode: "json" }).$type<{ key?: string; value?: number; }>(),
  userId: text("user_id").notNull().references(() => user.id, { onDelete: "cascade" }),
  createdAt: integer("created_at", { mode: "timestamp_ms" })
    .default(sql`(cast(unixepoch('subsecond') * 1000 as integer))`)
    .notNull(),
  updatedAt: integer("updated_at", { mode: "timestamp_ms" })
    .default(sql`(cast(unixepoch('subsecond') * 1000 as integer))`)
    .$onUpdate(() => new Date())
    .notNull(),
});

export type MyTable = typeof myTable.$inferSelect;
export type InsertMyTable = typeof myTable.$inferInsert;
```

## Field Patterns

### Timestamps (ALWAYS include)
```typescript
createdAt: integer("created_at", { mode: "timestamp_ms" })
  .default(sql`(cast(unixepoch('subsecond') * 1000 as integer))`)
  .notNull(),
updatedAt: integer("updated_at", { mode: "timestamp_ms" })
  .default(sql`(cast(unixepoch('subsecond') * 1000 as integer))`)
  .$onUpdate(() => new Date())
  .notNull(),
```

### Booleans
Use integer with `mode: "boolean"`:
```typescript
isEnabled: integer("is_enabled", { mode: "boolean" }).default(false).notNull(),
```

### Enums
Use text with enum option:
```typescript
status: text("status", { enum: ["pending", "active", "completed"] }).default("pending").notNull(),
```

### JSON Fields
Use text with `mode: "json"` and `.$type<T>()`:
```typescript
settings: text("settings", { mode: "json" }).$type<{ notifications?: boolean; theme?: "light" | "dark"; }>(),
```

### Foreign Keys
Always specify `onDelete` behavior:
```typescript
userId: text("user_id").references(() => user.id, { onDelete: "cascade" }),
organizationId: text("organization_id").references(() => organization.id, { onDelete: "set null" }),
```

## Naming Conventions
- **Table names:** `snake_case` in SQL
- **Column names:** `snake_case` in SQL
- **TypeScript variables:** `camelCase`

## Generating Migrations
```bash
bun run db:generate
bun run db:migrate:local
```
