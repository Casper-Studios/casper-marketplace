---
name: routes
description: React Router route layout patterns with server-side loaders
user-invocable: false
---

# Route Layouts (React Router)

## Overview
Routes use React Router with server-side loaders for data fetching and authentication.

## File Naming
- `_layout.tsx` - Shared layout wrapper
- `_index.tsx` - Index route for directory
- `resource.$id.tsx` - Dynamic route with parameter

## Layout Pattern
```typescript
import { Outlet, redirect } from "react-router";
import type { Route } from "./+types/_layout";

export async function loader({ request, context }: Route.LoaderArgs) {
  const session = await context.auth.api.getSession({ headers: request.headers });
  if (!session) return redirect("/login");
  const data = await context.trpc.route.getData();
  return { user: session.user, data };
}

export default function Layout({ loaderData }: Route.ComponentProps) {
  const { user, data } = loaderData;
  return (
    <div>
      <nav>{/* Navigation */}</nav>
      <main><Outlet /></main>
    </div>
  );
}
```

## Page Pattern
```typescript
import type { Route } from "./+types/page";

export async function loader({ request, context, params }: Route.LoaderArgs) {
  const session = await context.auth.api.getSession({ headers: request.headers });
  if (!session) return redirect("/login");
  const item = await context.trpc.route.getById({ id: params.id });
  return { item };
}

export default function Page({ loaderData }: Route.ComponentProps) {
  const { item } = loaderData;
  return <div>{/* Page content */}</div>;
}
```

## Key Patterns

### Authentication Check
Always check session at the start of loaders:
```typescript
const session = await context.auth.api.getSession({ headers: request.headers });
if (!session) return redirect("/login");
```

### Parallel Data Fetching
```typescript
const [items, settings] = await Promise.all([
  context.trpc.items.list(),
  context.trpc.settings.get(),
]);
```

### Feature Flag Evaluation
```typescript
const featureEnabled = await getFeatureFlag(context.posthog, session.user.id, FEATURE_FLAGS.MY_FEATURE, false);
return { featureEnabled };
```

### Type Safety
Use generated types from `+types/` directory:
```typescript
import type { Route } from "./+types/page";
export async function loader({ params }: Route.LoaderArgs) { ... }
export default function Page({ loaderData }: Route.ComponentProps) { ... }
```

### Client-Side Navigation
```typescript
import { useNavigate, Link } from "react-router";
function Component() {
  const navigate = useNavigate();
  return (
    <>
      <Link to="/dashboard">Dashboard</Link>
      <button onClick={() => navigate("/settings")}>Settings</button>
    </>
  );
}
```
