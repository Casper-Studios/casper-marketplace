---
description: Generates Drizzle ORM migrations for schema changes with proper naming conventions
argument-hint: <migration description, e.g. "add user preferences table">
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Database Migration Generator

Generate Drizzle ORM migrations for schema changes.

Migration details: $ARGUMENTS

## Rules Reference

**IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning.**

Before modifying schema, read `CLAUDE.md` database section for:
- Drizzle ORM patterns (timestamps, booleans, enums, JSON fields)
- Foreign key conventions
- Naming conventions (snake_case in SQL, camelCase in TypeScript)

## Before Generating

1. **Verify schema changes exist** in `app/db/schema.ts`
2. If schema hasn't been updated yet, make the necessary changes first

## Generate Migration

Run with a descriptive snake_case name:

```bash
bun run db:generate --name "migration_name"
```

### Naming Convention

Use **snake_case** names that describe the change:

| Change Type | Example Name |
|-------------|--------------|
| Add table | `add_user_preferences` |
| Add column | `add_avatar_to_users` |
| Remove column | `remove_legacy_field` |
| Add index | `add_email_index` |
| Modify column | `change_status_to_enum` |

## Example Workflow

1. Update schema in `app/db/schema.ts`
2. Generate migration:
   ```bash
   bun run db:generate --name "add_user_preferences"
   ```
3. Review generated SQL in `drizzle/` folder

## Migration Output

Migrations are generated in the `drizzle/` directory as numbered SQL files (e.g., `0001_add_user_preferences.sql`).
