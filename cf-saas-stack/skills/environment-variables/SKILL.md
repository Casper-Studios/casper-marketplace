---
name: environment-variables
description: Environment variable access patterns for Cloudflare Workers (never use process.env)
user-invocable: false
---

# Environment Variables in Cloudflare Workers

**NEVER use `process.env` to access environment variables.** This project runs on Cloudflare Workers where environment variables must be accessed through the Cloudflare `Env` bindings.

## Preferred Pattern: Create Client Instances in Context

For external services (APIs, SDKs), create client instances in the tRPC context and pass them through:

```typescript
// app/trpc/index.ts
export const createTRPCContext = async (opts) => {
  const gemini = opts.cfContext.GEMINI_API_KEY
    ? createGeminiClient(opts.cfContext.GEMINI_API_KEY)
    : null;
  return { db, auth, gemini };
};

// In tRPC routes - use the client instance
export const myRouter = createTRPCRouter({
  myProcedure: protectedProcedure.mutation(async ({ ctx }) => {
    if (!ctx.gemini) {
      throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Gemini not configured" });
    }
    await ctx.gemini.generateContent(prompt);
  }),
});
```

## Adding New External Services
1. Add the API key to `.env` for local development
2. Run `bunx wrangler types` to regenerate `worker-configuration.d.ts`
3. Create a client factory function in `app/lib/` (e.g., `createMyServiceClient`)
4. Initialize the client in `createTRPCContext` and add to context
5. For production, set secrets via `wrangler secret put VARIABLE_NAME`

## Where Clients are Created

### 1. tRPC Context (`app/trpc/index.ts`)
For use in tRPC routes via `ctx`.

### 2. Workers Entry (`workers/app.ts`)
For use in React Router loaders/actions via `context`.

## Current Available Clients

### In tRPC Routes (`ctx.`)
- `ctx.db` - Drizzle database instance
- `ctx.auth` - Better Auth session/user
- `ctx.gemini` - Google Gemini AI client (nullable)

### In React Router Loaders (`context.`)
- `context.trpc` - tRPC caller for server-side API calls
- `context.auth` - Better Auth instance
- `context.gemini` - Google Gemini AI client (nullable)
- `context.cloudflare.env` - Raw env (avoid using directly)
