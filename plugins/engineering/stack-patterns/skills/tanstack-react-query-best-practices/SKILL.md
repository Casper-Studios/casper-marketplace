---
name: tanstack-react-query-best-practices
description: TanStack Query conventions for cache-backed React server state. Use when creating or reviewing React queries, mutations, query keys, or cache updates.
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

Read the references that apply to the current task before writing or reviewing TanStack Query code.

1. Let TanStack Query own server-request lifecycle and cache identity.
   - [Let TanStack Query own request lifecycle](./references/request-ownership.md) rather than duplicating it with effects and local state.
   - [Put every response-changing request input in cache identity](./references/cache-identity.md) so distinct results never reuse one entry.
   - [Read request inputs exclusively from the query function's context argument](./references/query-function-inputs.md), never from captured request variables.
   - [Preserve absent identifiers and disable the request](./references/absent-identifiers.md) instead of fabricating a record key.
   - [Partition visibility-sensitive cached data by actor identity](./references/actor-identity-and-secrets.md) without exposing credentials in keys.
2. Resolve query status before presentation consumes data.
   - [Resolve query status at a Loader and Inner boundary](./references/loader-and-inner.md), keeping presentation free of optional data and transport state.
   - [Publish query identity through loader prop contracts](./references/loader-prop-contracts.md) while resolved components receive non-null data.
   - [Destructure only consumed query fields](./references/result-destructuring.md) so dependencies and props express semantic needs.
3. Keep mutation data, callbacks, and cache updates scoped to each operation.
   - [Consume named mutation result fields](./references/mutation-result-destructuring.md) because the complete `useMutation` result is not referentially stable.
   - [Pass changing operation input through mutation variables](./references/mutation-variables.md), not a mutation hook's construction closure.
   - [Parse user-controlled values before mutation invocation](./references/mutation-form-integration.md).
   - [Separate mutation callback lifecycles](./references/mutation-callback-lifecycle.md) by putting every-invocation policy in the definition and mounted UI consequences at the call site instead of aggregate-status effects.
   - [Invalidate the narrow stale entry identified by successful variables](./references/mutation-invalidation.md).
