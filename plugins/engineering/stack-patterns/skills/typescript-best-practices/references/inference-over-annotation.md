# Inference Over Annotation

Let TypeScript infer types when inference produces the correct type. Repeated annotations drift from implementation and can mask errors.

```typescript
// BAD: duplicate return annotation.
function getUsers(): User[] {
	return db.select().from(users);
}

// GOOD: infer the query result.
function getUsers() {
	return db.select().from(users);
}

// GOOD: an empty array has no elements from which to infer User.
const users: User[] = [];

// GOOD: give a generic constructor only the information it cannot infer.
const usersById = new Map<string, User>();
```

Add an annotation only when inference lacks information required by the program. Prefer a generic argument to a variable annotation when a constructor or function accepts that information.
