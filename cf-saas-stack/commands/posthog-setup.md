---
description: Sets up PostHog analytics and feature flags in Cloudflare Workers + React Router projects
argument-hint: <setup request, e.g. "initial setup" or "add tracking">
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# PostHog Setup for Cloudflare Workers + React Router

Set up PostHog analytics and feature flags in Cloudflare Workers + React Router projects.

Setup request: $ARGUMENTS

## Quick Start

Install dependencies:

```bash
bun add posthog-node posthog-js @posthog/react
```

| Package | Purpose |
|---------|---------|
| `posthog-node` | Server-side SDK (feature flags, server events) |
| `posthog-js` | Client-side SDK for browser analytics |
| `@posthog/react` | React hooks and context provider |

## File Structure

Create files in `app/posthog/`:

```
app/posthog/
├── index.ts          # Re-exports
├── server.ts         # Server-side client
├── provider.tsx      # Client-side provider
└── feature-flags.ts  # Flag constants and types
```

## Implementation Checklist

```
- [ ] Install dependencies
- [ ] Create app/posthog/feature-flags.ts
- [ ] Create app/posthog/server.ts
- [ ] Create app/posthog/provider.tsx
- [ ] Create app/posthog/index.ts
- [ ] Update workers/app.ts (create client, add to context, shutdown)
- [ ] Update app/root.tsx (add loader, wrap with PHProvider)
- [ ] Add POSTHOG_CLIENT_KEY to wrangler.jsonc and .env
- [ ] Run bun run cf-typegen
```

## Key Implementation Details

### Server-Side Client (Cloudflare Workers)

Critical settings for Workers:
- `flushAt: 1` - Send events immediately (Workers can terminate before batches)
- `flushInterval: 0` - Don't wait for interval
- Always call `shutdownPostHog()` in `ctx.waitUntil()`

### Worker Integration Pattern

```typescript
// workers/app.ts
const posthog = createPostHogClient(env.POSTHOG_CLIENT_KEY);

const response = await requestHandler(request, {
  // ... other context
  posthog,
});

// IMPORTANT: Flush before worker terminates
ctx.waitUntil(shutdownPostHog(posthog));

return response;
```

### Root Layout Pattern

```typescript
// app/root.tsx
export async function loader({ request, context }: Route.LoaderArgs) {
  const session = await context.auth.api.getSession({
    headers: request.headers,
  });

  return {
    posthogApiKey: context.cloudflare.env.POSTHOG_CLIENT_KEY,
    user: session?.user ? {
      id: session.user.id,
      email: session.user.email,
      name: session.user.name,
    } : null,
  };
}

export default function App({ loaderData }: Route.ComponentProps) {
  return (
    <PHProvider apiKey={loaderData.posthogApiKey} user={loaderData.user}>
      <TRPCProvider>
        <Outlet />
      </TRPCProvider>
    </PHProvider>
  );
}
```

## Usage Examples

### Track Events (Client-Side)

```typescript
import { useAnalytics } from "@/posthog";

function MyComponent() {
  const { trackEvent } = useAnalytics();

  const handleClick = () => {
    trackEvent("button_clicked", { buttonName: "signup" });
  };

  return <button onClick={handleClick}>Sign Up</button>;
}
```

### Evaluate Feature Flags (Server-Side)

```typescript
import { getFeatureFlag } from "@/posthog/server";
import { FEATURE_FLAGS } from "@/posthog/feature-flags";

export async function loader({ request, context }: Route.LoaderArgs) {
  const session = await context.auth.api.getSession({
    headers: request.headers,
  });

  const featureEnabled = await getFeatureFlag(
    context.posthog,
    session?.user?.id ?? "",
    FEATURE_FLAGS.MY_FEATURE,
    false
  );

  return { featureEnabled };
}
```

### Add New Feature Flags

1. Add to `FEATURE_FLAGS` constant in `app/posthog/feature-flags.ts`
2. Add to `FeatureFlags` interface
3. Add default value to `DEFAULT_FEATURE_FLAGS`
4. Add mapping to `FLAG_KEY_TO_DEFAULT`

## Additional Resources

- See existing implementation in `app/posthog/` directory
- For detailed patterns, see `.cursor/skills/posthog-setup/reference.md`
- PostHog dashboard is available for AI-assisted analytics queries
