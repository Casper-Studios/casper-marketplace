---
description: Creates and manages feature flags in PostHog with proper naming conventions and rollout patterns
argument-hint: <feature flag name and description>
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Create Feature Flag in PostHog

Create and manage feature flags in PostHog. Use when creating a feature flag, adding a flag, setting up A/B testing, enabling a feature for a percentage of users, or managing rollouts.

Feature flag details: $ARGUMENTS

## Workflow

When creating a feature flag:

1. **Create the flag in PostHog** using the PostHog API or dashboard
2. **Add the flag constant** to `app/posthog/feature-flags.ts`
3. **Implement usage** in the appropriate loader/component

## Step 1: Create Flag in PostHog

Create the feature flag in PostHog dashboard or via API:

- **key**: `feature-my-feature-name` (lowercase, hyphens)
- **name**: "My Feature Name" (human-readable)
- **filters**: rollout configuration (see examples below)

### Common Rollout Patterns

**100% rollout (feature on for everyone):**
```json
{
  "groups": [{ "rollout_percentage": 100 }]
}
```

**Percentage rollout (e.g., 20%):**
```json
{
  "groups": [{ "rollout_percentage": 20 }]
}
```

**Specific users only:**
```json
{
  "groups": [{
    "properties": [{ "key": "email", "value": ["user@example.com"], "operator": "exact", "type": "person" }],
    "rollout_percentage": 100
  }]
}
```

## Step 2: Add to feature-flags.ts

Add the flag constant to `app/posthog/feature-flags.ts`:

```typescript
export const FEATURE_FLAGS = {
  // Existing flags...
  MY_NEW_FEATURE: "feature-my-feature-name",
} as const;

export interface FeatureFlags {
  // Existing properties...
  myNewFeatureEnabled: boolean;
}

export const DEFAULT_FEATURE_FLAGS: FeatureFlags = {
  // Existing defaults...
  myNewFeatureEnabled: false,
};

export const FLAG_KEY_TO_DEFAULT: Record<string, boolean> = {
  // Existing mappings...
  [FEATURE_FLAGS.MY_NEW_FEATURE]: false,
};
```

## Step 3: Use the Flag

**In a loader:**
```typescript
import { getFeatureFlag } from "@/posthog/server";
import { FEATURE_FLAGS } from "@/posthog/feature-flags";

export async function loader({ request, context }: Route.LoaderArgs) {
  const session = await context.auth.api.getSession({ headers: request.headers });

  const myFeatureEnabled = await getFeatureFlag(
    context.posthog,
    session?.user?.id ?? "",
    FEATURE_FLAGS.MY_NEW_FEATURE,
    false
  );

  return { myFeatureEnabled };
}
```

**In a component:**
```typescript
const { myFeatureEnabled } = useLoaderData<typeof loader>();

return myFeatureEnabled ? <NewFeature /> : <OldFeature />;
```

## Naming Conventions

| Location | Format | Example |
|----------|--------|---------|
| PostHog key | `feature-kebab-case` | `feature-new-checkout` |
| TypeScript constant | `SCREAMING_SNAKE` | `NEW_CHECKOUT` |
| Interface property | `camelCaseEnabled` | `newCheckoutEnabled` |

## PostHog Management Reference

| Action | How |
|------|---------|
| Create a flag | PostHog dashboard or API |
| Update rollout percentage | PostHog dashboard |
| Check flag configuration | PostHog dashboard |
| List all flags | PostHog dashboard |
| Delete a flag | PostHog dashboard |
