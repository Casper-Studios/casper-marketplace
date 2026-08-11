# Resources Own Lifetimes

Acquire a resource and establish its cleanup as one indivisible lifecycle. A usable resource must never exist before successful acquisition or remain observable after release.

```typescript
// BAD: callers can forget initialization or cleanup.
const database = new Database();
await database.initialize();
await use(database);
await database.close();

// GOOD: native scoped acquisition guarantees cleanup.
await using databaseConnection = await openDatabase();
await use(databaseConnection);
```

The lifecycle owner must guarantee cleanup on success, failure, and partial startup. Release dependent resources before their dependencies.

Use the target language's native deterministic-lifetime mechanism. If destruction cannot perform required asynchronous cleanup, expose and enforce asynchronous cleanup within the owning scope. The mechanism varies; atomic acquisition, valid lifetime, and guaranteed reverse-order release do not.
