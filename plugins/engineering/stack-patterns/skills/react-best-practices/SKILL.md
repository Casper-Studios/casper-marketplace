---
name: react-best-practices
description: Opinionated React conventions for component boundaries, state ownership, derived values, explicit rendering, event work, external-system effects, memoization, context, and native forms. Use when creating or reviewing React components, hooks, conditional UI, form submission flows, state-sharing boundaries, or `useEffect` and `useMemo` usage.
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

Read as many linked references as are relevant to the current task before writing or reviewing React component, state, rendering, effect, data-loading, or form code.

- Keep computable values out of state with [derived values](./references/derive-values.md) so they cannot drift from their inputs.
- Place mutable state at the smallest shared owner with [state ownership](./references/scope-state.md), lifting it only for sibling consumers.
- Reserve [effects](./references/external-system-effects.md) for reactive synchronization with systems React does not control.
- Represent exclusive UI modes as one valid-state set with [state machines](./references/state-machines.md), not contradictory flags.
- Apply [manual memoization](./references/manual-memoization.md) only for measured work or required stable identity, not as a default optimization.
- Split independent caches with [atomic memoization](./references/atomic-memoization.md) so unrelated inputs do not invalidate each other.
- Make JSX absence and branch conditions explicit with [explicit rendering](./references/explicit-rendering.md), rather than relying on truthiness.
- Establish [context ownership](./references/context-ownership.md) only when one subsystem owns state or behavior consumed across multiple depths.
- Preserve the complete platform contract in [native element props](./references/native-element-props.md) instead of maintaining an incomplete handwritten prop surface.
- Express passive layout content through [children composition](./references/children-composition.md); reserve render callbacks for owner-provided behavior.
- Avoid [derived-state effects](./references/avoid-derived-state-effects.md) by computing synchronized values during render, preventing stale intermediate UI and a second writable source of truth.
- Keep [event work](./references/event-work.md) in the handler that receives the action instead of routing it through state and an effect.
- Let changed domain identity create a new state lifetime through [remounting](./references/reset-state-by-remounting.md), not field-by-field reset effects.
- Avoid [effect chains](./references/avoid-effect-chains.md) by keeping ordered work in one event, query, or server-operation owner so sequencing and failures stay explicit.
- When hidden UI must discard local state, focus, or other child lifetime state, [remove it through conditional mounting](./references/conditional-mounting.md).
- Decode then validate at the form boundary with [form validation](./references/form-validation.md), so mutations never receive raw transport input.
- Model pending, success, and failure as a form-wide operation with [submission state](./references/submission-state.md), not as one button's state.
- Treat missing [submitter identity](./references/submitter-identity.md) as valid unless distinct buttons select the operation; then validate it as form input instead of throwing or inventing a default.
