# DAG Patterns with better-all

## Multi-Tier Dependencies

```typescript
const results = await all({
  // Tier 1: Independent fetches (run in parallel)
  earnings: () => fetchEarnings(ticker),
  filings: () => fetchFilings(ticker),
  estimates: () => fetchEstimates(ticker),

  // Tier 2: Processing (each waits for its dependency)
  analyzedEarnings: async (ctx) => analyzeEarnings(await ctx.$.earnings),
  analyzedFilings: async (ctx) => analyzeFilings(await ctx.$.filings),
  modeledEstimates: async (ctx) => modelEstimates(await ctx.$.estimates),

  // Tier 3: Synthesis (waits for all tier 2)
  bullCase: async (ctx) =>
    generateBullCase(
      await ctx.$.analyzedEarnings,
      await ctx.$.analyzedFilings,
      await ctx.$.modeledEstimates
    ),
  bearCase: async (ctx) =>
    generateBearCase(
      await ctx.$.analyzedEarnings,
      await ctx.$.analyzedFilings,
      await ctx.$.modeledEstimates
    ),

  // Tier 4: Final output (waits for both cases)
  report: async (ctx) =>
    compileReport(await ctx.$.bullCase, await ctx.$.bearCase),
});
```

## Diamond Dependencies

When multiple tasks depend on the same upstream task:

```typescript
const results = await all({
  // Single upstream
  config: () => loadConfig(),

  // Multiple downstream depending on same upstream
  service1: async (ctx) => initService1(await ctx.$.config),
  service2: async (ctx) => initService2(await ctx.$.config),
  service3: async (ctx) => initService3(await ctx.$.config),

  // Convergence point
  app: async (ctx) => ({
    s1: await ctx.$.service1,
    s2: await ctx.$.service2,
    s3: await ctx.$.service3,
  }),
});
```

## Conditional Execution

```typescript
const results = await all({
  user: () => fetchUser(userId),
  permissions: async (ctx) => {
    const user = await ctx.$.user;
    if (user.role === "admin") {
      return fetchAdminPermissions(user.id);
    }
    return fetchUserPermissions(user.id);
  },
});
```

## Error Handling

Errors propagate to dependent tasks:

```typescript
const results = await all({
  data: () => mightFail(), // If this fails...
  processed: async (ctx) => process(await ctx.$.data), // ...this fails too
}).catch((error) => {
  console.error("Pipeline failed:", error);
  throw error;
});
```

For partial failure tolerance:

```typescript
const results = await all({
  data: async () => {
    try {
      return await mightFail();
    } catch {
      return null; // Return fallback instead of throwing
    }
  },
  processed: async (ctx) => {
    const data = await ctx.$.data;
    return data ? process(data) : defaultValue;
  },
});
```

## Comparison with Promise.all

| Feature | Promise.all | better-all |
|---------|-------------|------------|
| Manual dependency analysis | Required | Automatic |
| Type inference | Limited | Full |
| Named results | No | Yes |
| Execution order | All at once | Optimized by deps |
| Complex DAGs | Verbose | Natural |

```typescript
// Promise.all - manual coordination
const [a, b] = await Promise.all([fetchA(), fetchB()]);
const [c, d] = await Promise.all([processC(a), processD(b)]);
const result = await combine(c, d);

// better-all - declare and forget
const { result } = await all({
  a: () => fetchA(),
  b: () => fetchB(),
  c: async (ctx) => processC(await ctx.$.a),
  d: async (ctx) => processD(await ctx.$.b),
  result: async (ctx) => combine(await ctx.$.c, await ctx.$.d),
});
```
