# Structural Conformance

Use `satisfies` when a value must prove a required shape while retaining its own inferred type.

```typescript
// BAD: Widen the Value With Its Conformance Type
const routes: Record<string, `/${string}`> = {
	users: '/users',
	projects: '/projects',
};

const usersRoute: '/users' = routes.users;
// Error: `/${string}` is not assignable to '/users'.
```

```typescript
// GOOD: Check the Shape While Retaining Inference
const routes = {
	users: '/users',
	projects: '/projects',
} satisfies Record<string, `/${string}`>;

const usersRoute: '/users' = routes.users;
```

Use a type annotation when the variable itself must have the declared type. Use `satisfies` when the expression's more specific inferred type must remain available to consumers.
