---
name: react-best-practices
description: React component conventions for explicit state ownership and data flow. Use when creating or reviewing React components, hooks, effects, or forms.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# React Best Practices

Treat React as a declarative projection of owned state: derive what can be calculated, render every state explicitly, and isolate effects to synchronization with external systems so components remain predictable and easy to change.

## Library Sources

- GitHub repository ID: `react/react`
- Context7 library ID: `/facebook/react`
- DeepWiki repository ID: `react/react`

Use Context7 for current documentation and DeepWiki for implementation details.

## References

Read the references that apply to the current task before writing or reviewing React component, state, rendering, effect, data-loading, or form code.

1. Own mutable state narrowly and derive every value that its inputs already prove.
   - [Keep computable values out of state](./references/derive-values.md) so they cannot drift from their inputs.
   - [Place mutable state at the smallest shared owner](./references/scope-state.md), lifting it only for sibling consumers.
   - [Represent exclusive UI modes as one valid-state set](./references/state-machines.md), not contradictory flags.
   - [Use a functional state update for transitions derived from the same state](./references/functional-state-updates.md) so queued transitions compose and callbacks do not capture a render snapshot.
   - [Let changed domain identity create a new state lifetime through remounting](./references/reset-state-by-remounting.md), not field-by-field reset effects.
   - [Remove hidden UI through conditional mounting](./references/conditional-mounting.md) when it must discard local state, focus, or other child lifetime state.
2. Render explicit states and compose components around their owned contracts.
   - [Make JSX absence and branch conditions explicit](./references/explicit-rendering.md) rather than relying on truthiness.
   - [Establish context ownership](./references/context-ownership.md) only when one subsystem owns state or behavior consumed across multiple depths.
   - [Preserve the complete platform contract in native element props](./references/native-element-props.md) instead of maintaining an incomplete handwritten prop surface.
   - [Express passive layout content through children composition](./references/children-composition.md); reserve render callbacks for owner-provided behavior.
3. Restrict effects and memoization to their actual ownership boundaries.
   - [Reserve effects for reactive external-system synchronization](./references/external-system-effects.md).
   - [Memoize every pure render-time computation worse than O(1)](./references/manual-memoization.md), including scalar and O(log n) work; keep O(1) derivations inline.
   - [Split independent caches with atomic memoization](./references/atomic-memoization.md) so unrelated inputs do not invalidate each other.
   - [Compute synchronized values during render instead of using derived-state effects](./references/avoid-derived-state-effects.md), preventing stale intermediate UI and a second writable source of truth.
   - [Keep event work in the handler that receives the action](./references/event-work.md) instead of routing it through state and an effect.
   - [Keep ordered work in one event, query, or server-operation owner](./references/avoid-effect-chains.md) to avoid effect chains that obscure sequencing and failures.
4. Treat form input and submission state as form-wide contracts.
   - [Decode then validate at the form boundary](./references/form-validation.md) so mutations never receive raw transport input.
   - [Model pending, success, and failure as a form-wide operation](./references/submission-state.md), not as one button's state.
   - [Treat missing submitter identity as valid](./references/submitter-identity.md) unless distinct buttons select the operation; then validate it as form input instead of throwing or inventing a default.
