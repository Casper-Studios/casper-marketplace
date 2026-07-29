---
name: tanstack-react-query-best-practices
description: 'Opinionated TanStack Query conventions for React server state: resolved-view boundaries, query ownership, cache identity, disabled inputs, actor-scoped data, mutations, form submissions, and invalidation. Use when creating or reviewing `useQuery` or `useMutation` hooks, query keys, fetch functions, mutation callbacks, loading/error views, or cache updates in React.'
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# TanStack React Query Best Practices

Treat server data as cache-backed asynchronous state with an explicit owner, identity, and view boundary; the outcome is reliable loading and error handling plus focused updates after writes.

## Library Sources

- GitHub repository ID: `TanStack/query`
- Context7 library ID: `/tanstack/query`
- DeepWiki repository ID: `TanStack/query`

Use Context7 for current documentation and DeepWiki for implementation details.

## References

Read as many linked references as are relevant to the current task before writing or reviewing TanStack Query code.

- Let TanStack Query own server-request lifecycle through [request ownership](./references/request-ownership.md), rather than duplicating it with effects and local state.
- Put every response-changing request input in [cache identity](./references/cache-identity.md) so distinct results never reuse one entry.
- Resolve query status at a [Loader and Inner](./references/loader-and-inner.md) boundary, keeping presentation free of optional data and transport state.
- Publish query identity through [loader prop contracts](./references/loader-prop-contracts.md) while resolved components receive non-null data.
- Keep request construction and cache keys aligned with [query function inputs](./references/query-function-inputs.md), including every captured response-changing value.
- Preserve missing IDs with [absent identifiers](./references/absent-identifiers.md) and disable the request instead of fabricating a record key.
- Partition visibility-sensitive cached data through [actor identity and secrets](./references/actor-identity-and-secrets.md) without exposing credentials in keys.
- Destructure only consumed query fields with [result destructuring](./references/result-destructuring.md) so dependencies and props express semantic needs.
- Pass changing operation input through [mutation variables](./references/mutation-variables.md), not a mutation hook's construction closure.
- Parse user-controlled values before mutation invocation with [mutation form integration](./references/mutation-form-integration.md).
- When mutation outcomes trigger follow-up work, [separate callback lifecycles](./references/mutation-callback-lifecycle.md) by putting every-invocation policy in the definition and mounted UI consequences at the call site instead of aggregate-status effects.
- Invalidate the narrow stale entry identified by successful variables with [mutation invalidation](./references/mutation-invalidation.md).
