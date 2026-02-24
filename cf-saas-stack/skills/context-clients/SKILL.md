---
name: context-clients
description: Context-based client pattern for passing external service clients through request context
user-invocable: false
---

# Context-Based Client Pattern

## Overview
External service clients (Stripe, AI, analytics, etc.) are created once at the request level and passed through context. Repositories and services receive clients as parameters rather than creating them.

## Why This Pattern?
1. **Single initialization** - Clients are created once per request, not per function call
2. **Testability** - Easy to mock clients in tests
3. **Configuration** - Environment variables are accessed in one place
4. **Resource management** - Proper cleanup/shutdown of clients

## Worker Entry Point
Create clients in the Cloudflare Worker and pass to React Router context:
```typescript
// workers/app.ts
export default {
  async fetch(request, env, ctx) {
    const auth = await createAuth(env.DATABASE, { secret: env.AUTH_SECRET });
    const stripe = env.STRIPE_SECRET_KEY ? createStripeClient(env.STRIPE_SECRET_KEY) : null;
    const ai = createAIClient(env.AI_API_KEY);
    return requestHandler(request, { cloudflare: { env, ctx }, auth, stripe, ai });
  },
} satisfies ExportedHandler<Env>;
```
Run `bun typegen` to generate the `AppLoadContext` types automatically.

## tRPC Context
Pass clients from Cloudflare context to tRPC context:
```typescript
// app/trpc/index.ts
export const createTRPCContext = async (opts) => {
  const db = await getDb(opts.cfContext.DATABASE);
  const stripe = opts.cfContext.STRIPE_SECRET_KEY ? createStripeClient(opts.cfContext.STRIPE_SECRET_KEY) : null;
  const ai = createAIClient(opts.cfContext.AI_API_KEY);
  return { db, stripe, ai, cfContext: opts.cfContext };
};
```

## Using Clients in tRPC Routes
Access clients from context, pass to repositories:
```typescript
export const paymentRouter = createTRPCRouter({
  createPayment: protectedProcedure
    .input(z.object({ amount: z.number() }))
    .mutation(async ({ ctx, input }) => {
      if (!ctx.stripe) {
        throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Payment system not configured" });
      }
      return await paymentRepository.createPayment(ctx.db, ctx.stripe, input);
    }),
});
```

## Repository Functions
Repositories receive clients as parameters:
```typescript
// CORRECT: Receive client as parameter
export async function createPayment(db: Database, stripe: StripeClient, input: CreatePaymentInput) {
  const paymentIntent = await stripe.paymentIntents.create({ amount: input.amount, currency: "usd" });
}

// WRONG: Creating client inside repository
export async function createPaymentBad(db: Database, stripeSecretKey: string, input: CreatePaymentInput) {
  const stripe = new Stripe(stripeSecretKey); // Don't create here
}
```

## Client Factory Functions
Create simple factory functions in `app/lib/`:
```typescript
// app/lib/stripe.ts
export function createStripeClient(secretKey: string): Stripe {
  return new Stripe(secretKey, { apiVersion: "2024-06-20" });
}
```

## Null Checking Pattern
Always check for optional clients before use:
```typescript
if (!ctx.stripe) {
  throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Payment system is not configured" });
}
await ctx.stripe.customers.create({ ... });
```

## Layer Responsibilities
| Layer | Responsibility |
|-------|---------------|
| `workers/app.ts` | Create clients from env vars |
| `app/trpc/index.ts` | Include clients in tRPC context |
| `app/trpc/routes/*.ts` | Access clients from `ctx`, pass to repos |
| `app/repositories/*.ts` | Receive clients as parameters |
| `app/lib/*.ts` | Factory functions for client creation |
