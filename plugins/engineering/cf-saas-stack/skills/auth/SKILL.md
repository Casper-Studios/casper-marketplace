---
name: auth
description: Better Auth authentication patterns and conventions for this Cloudflare Workers project
user-invocable: false
---

# Better Auth Rules for This Project

## Better Auth Overview
- This project uses **Better Auth** (`better-auth` v1.3.34+) for authentication
- Better Auth is configured with Drizzle ORM adapter for SQLite (Cloudflare D1)
- Uses email/password authentication with admin plugin enabled
- Supports Google OAuth social authentication
- Base path for auth API: `/api/auth`

## Server-Side Auth Setup

### Creating Auth Instance
- **ALWAYS** use `createAuth()` from `@/auth/server` to create auth instances
- Auth instances must be created per-request (not cached globally)
- Required parameters:
  - `database`: D1Database instance from Cloudflare context
  - `options`: Object containing:
    - `secret`: BETTER_AUTH_SECRET from environment variables
    - `googleClientId`: GOOGLE_CLIENT_ID from environment variables
    - `googleClientSecret`: GOOGLE_CLIENT_SECRET from environment variables
- Example pattern:
```typescript
import { createAuth } from "@/auth/server";

const auth = await createAuth(context.cloudflare.env.DATABASE, {
  secret: context.cloudflare.env.BETTER_AUTH_SECRET,
  googleClientId: context.cloudflare.env.GOOGLE_CLIENT_ID,
  googleClientSecret: context.cloudflare.env.GOOGLE_CLIENT_SECRET,
});
```

### Auth Route Handler
- Auth routes are handled at `/api/auth` via `app/routes/api/auth.$.ts`
- Both `loader` and `action` should call `auth.handler(request)`

### Session Retrieval
- Use `auth.api.getSession({ headers })` to get current session
- Returns `{ session, user }` or `null` if not authenticated
- Always pass request headers for proper session resolution

## Client-Side Auth
- **ALWAYS** use `authClient` from `@/auth/client` for client-side operations
- Client is pre-configured with base path `/api/auth` and admin plugin enabled
- Use `authClient.signIn.email()` for login, `authClient.signUp.email()` for signup
- Use `authClient.signOut()` for logout
- Use `authClient.useSession()` hook for React components

## tRPC Integration
- Auth is integrated into tRPC context via `createTRPCContext`
- Context includes `authApi` (Better Auth API) and `auth` (session data)
- Use `protectedProcedure` for authenticated-only endpoints (guarantees `ctx.auth.user` and `ctx.auth.session`)
- Use `adminProcedure` for admin-only endpoints (checks `user.role === "admin"`)

## Database Schema
- Better Auth uses Drizzle adapter with SQLite provider
- Schema imported from `@/db/schema`, database connection via `getDb()` from `@/db`

## Security Best Practices
- **NEVER** expose `BETTER_AUTH_SECRET` in client-side code
- **ALWAYS** validate authentication server-side
- **NEVER** trust client-side auth state alone
- Use `protectedProcedure` or `adminProcedure` for sensitive operations
- Create auth instances per-request (not globally cached)
- Handle `UNAUTHORIZED` (401) and `FORBIDDEN` (403) errors
- Use tRPC error codes: `UNAUTHORIZED` and `FORBIDDEN`

## Common Patterns

### Checking Auth in Loaders/Actions
```typescript
const auth = await createAuth(env.DATABASE, env.BETTER_AUTH_SECRET);
const session = await auth.api.getSession({ headers: request.headers });
if (!session) {
  throw redirect("/login");
}
```

### Client-Side Auth State
```typescript
import { authClient } from "@/auth/client";
const { data: session } = authClient.useSession();
```
