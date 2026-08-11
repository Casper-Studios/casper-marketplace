# Serialized Trust Boundaries

Validate serialized data when it enters the application: network responses, request bodies, `FormData`, JSON, JSONB, webhooks, environment-provided strings, and persisted opaque payloads.

Authenticated network payloads remain external input. Authentication identifies the sender; it does not prove payload shape.

Do not re-parse values that the application has already constructed and retained within its typed domain.

```typescript
// A provider response remains external even after authentication.
const user = User.parse(responseBody);
```

Treat a serialization boundary as the place where untrusted values become domain values.
