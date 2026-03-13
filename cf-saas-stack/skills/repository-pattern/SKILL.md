---
name: repository-pattern
description: Repository pattern for data access with layered architecture
user-invocable: false
---

# Repository Pattern

## Overview
Data access follows a layered architecture:
```
Client Components -> tRPC Hooks -> tRPC Routes -> Repositories -> Database
Server Loaders -> tRPC Caller -> tRPC Routes -> Repositories -> Database
```

## Repository Layer
Repositories are pure functions that handle database operations.

### Structure
```typescript
// app/repositories/user.ts
import { eq } from "drizzle-orm";
import { user } from "@/db/schema";
import { NotFoundError, CreationError, UpdateError } from "@/models/errors";
import type { Context } from "@/trpc";

type Database = Context["db"];

interface CreateUserInput { name: string; email: string; }
interface GetUserInput { userId: string; }

export async function createUser(db: Database, input: CreateUserInput) {
  try {
    const id = crypto.randomUUID();
    const result = await db.insert(user).values({ id, ...input }).returning();
    return result[0];
  } catch (error) {
    throw new CreationError("user", "Failed to create user", error);
  }
}

export async function getUser(db: Database, input: GetUserInput) {
  try {
    const result = await db.select().from(user).where(eq(user.id, input.userId)).limit(1);
    if (result.length === 0) throw new NotFoundError("user", input.userId);
    return result[0];
  } catch (error) {
    if (error instanceof NotFoundError) throw error;
    throw new UpdateError("user", "Failed to retrieve user", error);
  }
}
```

### Rules
- **Location:** `app/repositories/{entity}.ts`
- **First parameter:** Always `db: Database`
- **Input:** Use typed interfaces, not raw parameters
- **Errors:** Throw custom error classes from `@/models/errors`
- **No context access:** Pass data explicitly, don't access ctx or session
- **No tRPC imports:** Keep repositories framework-agnostic

## tRPC Router Layer
```typescript
// app/trpc/routes/user.ts
import { z } from "zod/v4";
import { createTRPCRouter, protectedProcedure, adminProcedure } from "..";
import * as userRepository from "@/repositories/user";

export const userRouter = createTRPCRouter({
  getUser: protectedProcedure
    .input(z.object({ userId: z.string() }))
    .query(async ({ ctx, input }) => {
      return await userRepository.getUser(ctx.db, input);
    }),
  createUser: adminProcedure
    .input(z.object({ name: z.string().min(1), email: z.string().email() }))
    .mutation(async ({ ctx, input }) => {
      return await userRepository.createUser(ctx.db, input);
    }),
  updateProfile: protectedProcedure
    .input(z.object({ name: z.string().min(1) }))
    .mutation(async ({ ctx, input }) => {
      return await userRepository.updateUser(ctx.db, { userId: ctx.auth.user.id, ...input });
    }),
});
```

### Register Router
```typescript
// app/trpc/router.ts
import { userRouter } from "./routes/user";
export const appRouter = createTRPCRouter({ user: userRouter });
export type AppRouter = typeof appRouter;
```

### Router Rules
- **Location:** `app/trpc/routes/{entity}.ts`
- **Import pattern:** `import * as userRepository from "@/repositories/user"`
- **Validation:** Use Zod schemas for all inputs
- **Procedures:** Use `publicProcedure`, `protectedProcedure`, or `adminProcedure`
- **Database:** Pass `ctx.db` as first argument to repositories
- **Errors:** Let repository errors bubble up

## Key Principles
1. Separation: Repositories = data, Routes = validation/auth, Components = UI
2. Type safety: Zod for runtime, TypeScript for compile-time
3. Error bubbling: Throw in repos, let tRPC handle formatting
4. No leaky abstractions: Repositories don't know about HTTP or tRPC
