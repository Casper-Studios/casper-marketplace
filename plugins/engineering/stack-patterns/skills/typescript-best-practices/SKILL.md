---
name: typescript-best-practices
description: TypeScript conventions for precise contracts and valid program states. Use when writing or reviewing TypeScript types, state models, optional values, or untrusted boundaries.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# TypeScript Best Practices

> [!IMPORTANT]
> Apply the `codebase-architecture:code-style` principles through TypeScript's type system: treat types as precise, compiler-checked models of valid program states and boundaries, preserve inference where it carries information, and narrow uncertainty explicitly so invalid states and unhandled cases cannot silently reach runtime.

## References

Read the references that apply to the current task before writing or reviewing TypeScript.

1. Preserve TypeScript's specific inference whenever it proves the intended contract.
   - [Infer derivable types and impose annotations only where they prove a required contract](./references/inference-over-annotation.md), keeping inferred locals and filter narrowing while the defining module owns named result contracts.
   - [Declare the intended state set at a literal inference boundary](./references/literal-union-inference.md) when an API infers a closed state from one initial literal so later valid members remain assignable.
   - [Model named durable closed sets of serialized primitive values as `const enum`s](./references/const-enums.md) rather than string-literal unions.
   - [Preserve readonly tuple or literal-union inference with `as const`](./references/literal-const-assertions.md) when consumers require it rather than treating the assertion as a default.
   - [Use structural conformance](./references/structural-conformance.md) when a value must satisfy a shape without losing its precise inferred literals instead of widening it with an annotation.
2. Model domain contracts and closed states precisely.
   - [Choose `interface` by default and compose it with `extends`](./references/interfaces-and-types.md) for handwritten object contracts; use a `Pick` alias for an exact subset of an existing contract.
   - [Make decisions over closed enums or unions exhaustive](./references/exhaustive-decisions.md) so new members cannot silently reach a fallback.
3. Narrow uncertainty and absence explicitly at the boundary that owns it.
   - [Contain type escape hatches](./references/escape-hatches.md) by narrowing or validating `any` and `unknown` inside the boundary that receives them so neither can escape to callers or domain state.
   - [Replace unchecked assertions with runtime proof](./references/unchecked-assertions.md) at a serialization boundary when a value is untrusted or insufficiently typed.
   - [Establish an absent-value invariant explicitly](./references/non-null-assertions.md) when an operation requires it rather than asserting it with `!`.
   - [Preserve omission in optional arguments and object fields](./references/optional-arguments.md); omit absent arguments, conditionally insert present fields, and write `void 0` only where an `undefined` value must be present.
   - [Narrow optional values with `typeof` guards before required calls](./references/optional-value-narrowing.md), or preserve absence in the return or state contract when it is expected.
   - [Do not fabricate a default for missing required input](./references/no-fabricated-defaults.md) unless the domain contract assigns that exact omitted-value meaning.
   - [Narrow indexed access and destructured bindings](./references/indexed-access-and-destructuring.md) before required use when `noUncheckedIndexedAccess` preserves possible absence.
   - [Validate a required regular-expression capture first](./references/regex-capture-groups.md) because named and positional groups can be absent.
