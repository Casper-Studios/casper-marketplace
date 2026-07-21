---
name: models
description: Zod schema patterns for data models and runtime validation
user-invocable: false
---

# Models and Types (Zod Schemas)

## Overview
Data models use Zod for runtime validation and TypeScript type inference.

## Basic Pattern
```typescript
import { z } from "zod";

// 1. Define schema
export const entitySchema = z.object({
  id: z.string(),
  name: z.string(),
  status: z.enum(["active", "inactive"]),
});

// 2. Export inferred type
export type Entity = z.infer<typeof entitySchema>;
```

## Naming Conventions
- **Schema:** `camelCaseSchema` (e.g., `userStatusSchema`)
- **Type:** `PascalCase` (e.g., `UserStatus`)

## Common Patterns

### Enums
```typescript
export const statusSchema = z.enum(["pending", "active", "completed"]);
export type Status = z.infer<typeof statusSchema>;
```

### Objects
```typescript
export const userSchema = z.object({
  id: z.string(),
  email: z.string().email(),
  age: z.number().int().positive().optional(),
});
export type User = z.infer<typeof userSchema>;
```

### Optional/Nullable
```typescript
export const profileSchema = z.object({
  bio: z.string().optional(),       // string | undefined
  avatar: z.string().nullable(),    // string | null
  website: z.string().nullish(),    // string | null | undefined
});
```

### Defaults
```typescript
export const settingsSchema = z.object({
  theme: z.enum(["light", "dark"]).default("light"),
  pageSize: z.number().default(10),
});
```

## Composing Schemas
```typescript
export const addressSchema = z.object({ street: z.string(), city: z.string() });
export const companySchema = z.object({ name: z.string(), address: addressSchema });
export type Company = z.infer<typeof companySchema>;
```

## Usage with tRPC
```typescript
import { z } from "zod/v4";
import { statusSchema } from "@/models/types";

export const router = createTRPCRouter({
  update: protectedProcedure
    .input(z.object({ id: z.string(), status: statusSchema }))
    .mutation(async ({ input }) => { ... }),
});
```

**Important:** In tRPC routes, import Zod as `import { z } from "zod/v4"`. In models, use `import { z } from "zod"`.

## Runtime Validation
```typescript
function parseData(data: unknown) {
  const result = entitySchema.safeParse(data);
  if (!result.success) {
    console.error(result.error.flatten());
    return null;
  }
  return result.data; // Fully typed
}
```
