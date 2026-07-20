---
name: feature-flags
description: PostHog feature flag evaluation patterns with server-side loading
user-invocable: false
---

# Feature Flags with PostHog

## Overview
- This project uses **PostHog** for feature flag management
- Feature flags are evaluated **server-side** in loaders for performance and security
- Flag values are passed to components via loader data

## File Structure
- `app/posthog/feature-flags.ts` - Flag key constants and TypeScript types
- `app/posthog/server.ts` - Server-side PostHog client and flag evaluation
- `app/posthog/provider.tsx` - Client-side PostHog provider and hooks
- `app/posthog/index.ts` - Re-exports

## Defining Feature Flags

### Step 1: Add Flag Key to Constants
```typescript
// app/posthog/feature-flags.ts
export const FEATURE_FLAGS = {
  MY_NEW_FLAG: "feature-my-new-flag",
} as const;
```

### Step 2: Add to FeatureFlags Interface
```typescript
export interface FeatureFlags {
  myNewFlagEnabled: boolean;
}
```

### Step 3: Set Default Value
```typescript
export const DEFAULT_FEATURE_FLAGS: FeatureFlags = {
  myNewFlagEnabled: false,
};
```

## Server-Side Flag Evaluation
**ALWAYS** evaluate feature flags server-side in route loaders using `context.posthog`:
```typescript
import { getFeatureFlag } from "@/posthog/server";
import { FEATURE_FLAGS } from "@/posthog/feature-flags";

export async function loader({ request, context }: Route.LoaderArgs) {
  const session = await context.auth.api.getSession({ headers: request.headers });
  const myFeatureEnabled = session?.user
    ? await getFeatureFlag(context.posthog, session.user.id, FEATURE_FLAGS.MY_NEW_FLAG, false)
    : false;
  return { myFeatureEnabled };
}
```

### Key Points
- **ALWAYS** use `context.posthog` - it's already initialized in `workers/app.ts`
- **NEVER** call `createPostHogClient()` in loaders
- **ALWAYS** pass `session.user.id` as the `distinctId`
- **ALWAYS** provide a default value (typically `false`)
- **NEVER** evaluate flags client-side for security-sensitive features

## Using Flags in Components
```typescript
export default function MyPage() {
  const { myFeatureEnabled } = useLoaderData<typeof loader>();
  return (
    <div>
      {myFeatureEnabled && <NewFeatureComponent />}
    </div>
  );
}
```

## Client-Side Analytics
```typescript
import { useAnalytics } from "@/posthog";
function MyComponent() {
  const { trackEvent } = useAnalytics();
  const handleClick = () => { trackEvent('button_clicked', { buttonName: 'signup' }); };
}
```

## Naming Conventions
- Flag keys in PostHog: `feature-{feature-name}` or `{TICKET-ID}-{Feature-Name}`
- TypeScript constants: `SCREAMING_SNAKE_CASE`
- Interface properties: `camelCaseEnabled`

## Cleanup
- Remove flag checks after feature is fully rolled out
- Update `FEATURE_FLAGS`, `FeatureFlags` interface, and `DEFAULT_FEATURE_FLAGS`
- Search codebase for all usages before removing
