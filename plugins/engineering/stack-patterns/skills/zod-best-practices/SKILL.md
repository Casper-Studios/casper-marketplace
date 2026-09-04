---
name: zod-best-practices
description: Zod v4 conventions for owned wire contracts and explicit validation outcomes. Use when defining or reviewing Zod schemas or parsing untrusted data with Zod.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# Zod Best Practices

Treat a Zod schema as the owned contract at an untrusted data boundary: it defines accepted wire values, produces trusted domain values, and makes invalid input an explicit, intentional outcome.

## Library Sources

- GitHub repository ID: `colinhacks/zod`
- Context7 library ID: `/colinhacks/zod`
- DeepWiki repository ID: `colinhacks/zod`

Use Context7 for current documentation and DeepWiki for implementation details.

## Effective Strategies for Zod

Read the references that apply to the current task before defining or reviewing Zod schemas and parsing code.

1. Make schemas the owned, trusted contract for wire data.
   - [Keep a schema and its standard string formats as the single source of truth](./references/schema-ownership-and-formats.md) instead of duplicating types or custom format logic.
   - [Validate serialized data at its trust boundary](./references/serialized-trust-boundaries.md), including authenticated external payloads, before it becomes a domain value.
   - [Keep constructors and format validators under one `z` import](./references/zod-imports.md) rather than mixing import forms.
   - [Infer the correct side of a schema](./references/schema-input-output.md) with `z.input` or `z.infer` when a transform or default changes accepted input from parsed output instead of hand-writing either type.
2. Express the complete protocol contract in the schema.
   - [Select Zod's top-level validator for a standard string format](./references/top-level-formats.md) instead of recreating the format with a custom regular expression.
   - [Encode missing and `null` wire semantics](./references/wire-nullability.md) with the matching wrapper rather than whichever wrapper compiles.
   - [Define defaults with exact domain meaning in the schema](./references/schema-defaults.md); do not use defaults to turn unknown or invalid input into arbitrary fallbacks.
   - [Dispatch literal-tagged alternatives with `z.discriminatedUnion`](./references/discriminated-unions.md) rather than trying each tagged branch with `z.union`.
   - [Select the matching object constructor when unknown keys have contract meaning](./references/object-strictness.md): strip for leniency, reject for closed contracts, or preserve only opaque pass-through data.
3. Make validation failure match the boundary and presentation contracts.
   - [Choose the parse API from the failure contract](./references/parse-failure-contracts.md): abort a violated invariant or return an expected validation branch.
   - [Derive expected validation presentation from Zod's error](./references/validation-error-rendering.md) instead of discarding its field information.
   - [Use `.refine()` for one value and one boolean rule](./references/predicate-validation.md); move multi-field or multi-issue validation to `.check()`.
   - [Use `.check()` for multi-field relationships with separate actionable issues](./references/cross-field-validation.md) instead of collapsing them into one `.refine()` error.
