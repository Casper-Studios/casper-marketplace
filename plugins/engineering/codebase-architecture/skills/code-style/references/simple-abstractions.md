# Simple Abstractions

Use the most direct code that preserves the domain model and required behavior. An abstraction must remove real duplication, establish a stable boundary, own a dependency closure or resource lifetime, or give a precise name to a domain concept.

```typescript
// BAD: a single-use helper hides trivial work.
function buildDisplayName(user: User) {
	return `${user.firstName} ${user.lastName}`;
}
const displayName = buildDisplayName(user);

// GOOD: keep one obvious operation at its call site.
const directDisplayName = `${user.firstName} ${user.lastName}`;
```

Do not extract a helper used by one call site unless it establishes a real boundary or isolates independently testable complex logic. Do not create shared code before multiple owners need it.

Do not wrap a library only to rename its operations. Do not create a package, manager, provider, model, or exception unless it hides a dependency, enforces a contract, owns a lifecycle, preserves type safety, or gives consumers a smaller stable capability.

Prefer deleting, merging, or simplifying existing code before adding another layer.
