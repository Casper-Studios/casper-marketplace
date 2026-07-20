---
name: errors
description: Custom error class patterns for consistent error handling across repositories
user-invocable: false
---

# Custom Error Classes

## Overview
Custom error classes provide consistent error handling across repositories and services.

## Base Error Class Pattern
```typescript
export class DomainError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 500,
    public readonly context?: Record<string, unknown>
  ) {
    super(message);
    this.name = "DomainError";
    Object.setPrototypeOf(this, DomainError.prototype);
  }
}
```

## Derived Error Pattern
```typescript
export class NotFoundError extends RepositoryError {
  constructor(
    public readonly entity: string,
    public readonly identifier: string | Record<string, unknown>,
    message?: string
  ) {
    const defaultMessage = typeof identifier === "string"
      ? `${entity} not found: ${identifier}`
      : `${entity} not found`;
    super(message || defaultMessage, "NOT_FOUND", 404, { entity, identifier });
    this.name = "NotFoundError";
    Object.setPrototypeOf(this, NotFoundError.prototype);
  }
}
```

## Common Repository Errors
- `RepositoryError` - Base class
- `NotFoundError` - Record not found (404)
- `CreationError` - Insert failed (500)
- `UpdateError` - Update failed (500)
- `DeletionError` - Delete failed (500)
- `QueryError` - Query failed (500)
- `ValidationError` - Business rule violation (400)

## Usage in Repositories
```typescript
import { NotFoundError, UpdateError } from "@/models/errors";

export async function getById(db: Database, id: string) {
  try {
    const result = await db.select().from(table).where(eq(table.id, id));
    if (result.length === 0) {
      throw new NotFoundError("entity", id);
    }
    return result[0];
  } catch (error) {
    if (error instanceof NotFoundError) throw error;
    throw new QueryError("entity", "Failed to retrieve", error);
  }
}
```

## Error Codes Convention
- `NOT_FOUND` - Resource doesn't exist (404)
- `CREATION_FAILED` - Insert failed (500)
- `UPDATE_FAILED` - Update failed (500)
- `DELETION_FAILED` - Delete failed (500)
- `VALIDATION_FAILED` - Business rule violation (400)

## Important Rules
- Always use `Object.setPrototypeOf` for proper `instanceof` checks
- Preserve original errors for debugging
- Re-throw custom errors, wrap unexpected ones
