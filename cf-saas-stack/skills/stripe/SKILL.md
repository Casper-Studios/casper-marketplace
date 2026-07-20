---
name: stripe
description: Stripe integration guidelines for payment processing via context-based client
user-invocable: false
---

# Stripe Integration Guidelines

## Stripe Client Usage

**NEVER create the Stripe client inside repositories or service functions.**

The Stripe client is created once in the tRPC context (`app/trpc/index.ts`) and is available as `ctx.stripe`. Always pass the Stripe client from context to repository functions.

### Correct Pattern
```typescript
// In tRPC route
.mutation(async ({ ctx, input }) => {
  if (!ctx.stripe) {
    throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Payment system is not configured." });
  }
  return await someRepository.doStripeOperation(ctx.db, input.someId, ctx.stripe);
});

// In repository
export async function doStripeOperation(db: Database, someId: string, stripe: StripeClient) {
  const customer = await stripe.customers.retrieve(customerId);
}
```

### Incorrect Pattern (NEVER do this)
```typescript
// DON'T create client in repositories
import { createStripeClient } from "@/lib/stripe";
export async function doStripeOperation(db: Database, someId: string, stripeSecretKey: string) {
  const stripe = createStripeClient(stripeSecretKey); // DON'T
}
```

## Type Definitions
```typescript
import type Stripe from "stripe";
type StripeClient = Stripe;
export async function someFunction(db: Database, stripe: StripeClient) { ... }
```

## Context Setup
The Stripe client is initialized in `app/trpc/index.ts`:
```typescript
const stripe = opts.cfContext.STRIPE_SECRET_KEY ? createStripeClient(opts.cfContext.STRIPE_SECRET_KEY) : null;
```
Always check for null before using: `if (!ctx.stripe) { throw new TRPCError({ ... }); }`

## File Locations
- **Stripe utilities**: `app/lib/stripe.ts` - Low-level Stripe helpers
- **Payment service**: `app/services/payment-trigger.ts` - Payment triggering logic
- **Organization repository**: `app/repositories/organization.ts` - Organization + Stripe customer operations
- **Payment repository**: `app/repositories/payment.ts` - Payment record operations

## Stripe Webhook Handling
For webhook handlers that don't have tRPC context, use `createStripeClient` directly since there's no context available. This is the **only exception** to the context-based client rule.
