# Actor Identity and Secrets

Partition the query cache by stable actor or session identity when that identity changes response visibility.

Use a non-secret identifier such as an actor ID, tenant ID, or stable session partition. The key must distinguish data that one actor cannot safely reuse from another actor's cache entry.

Never include bearer tokens, API keys, cookies, authorization codes, or other credentials in a query key. Query keys can appear in developer tools, logs, persistence, and diagnostics.

Let the HTTP client attach credentials to the request. Cache identity represents visibility, not the credential material used to authenticate the request.

```typescript
// BAD: credential material becomes cache metadata.
const queryKey = ['jobs', accessToken] as const;

// GOOD: stable visibility partition without a secret.
const queryKey = ['jobs', actor.id] as const;
```

Remove or invalidate actor-scoped cache data when the authenticated actor changes under the application's security policy.
