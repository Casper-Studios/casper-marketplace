---
name: zod-best-practices
description: Opinionated Zod v4 conventions for schema ownership, format validation, nullability, tagged unions, object-key contracts, transformations, and explicit validation-failure behavior. Use when defining or reviewing Zod schemas, validating forms or HTTP payloads, parsing JSON or persisted data, rendering validation errors, or deciding whether invalid input aborts or becomes an expected branch.
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

## References

Read as many linked references as are relevant to the current task before defining or reviewing Zod schemas and parsing code.

- When a schema or its standard string formats already prove the contract, [keep that schema as the single source of truth](./references/schema-ownership-and-formats.md) instead of duplicating types or custom format logic.
- When serialized data enters the application, [validate it at that trust boundary](./references/serialized-trust-boundaries.md), including authenticated external payloads, before it becomes a domain value.
- When defining Zod schemas, [keep constructors and format validators under one `z` import](./references/zod-imports.md) rather than mixing import forms.
- When a transform or default changes a schema's accepted input from its parsed output, [infer the correct side of the schema](./references/schema-input-output.md) with `z.input` or `z.infer` instead of hand-writing either type.
- When a protocol uses a standard string format, [select Zod's top-level validator](./references/top-level-formats.md) instead of recreating the format with a custom regular expression.
- When a wire field can be missing, `null`, or both, [encode those exact semantics](./references/wire-nullability.md) with the matching wrapper rather than whichever wrapper compiles.
- When absence has an exact domain meaning, [define that default in the schema](./references/schema-defaults.md); do not use defaults to turn unknown or invalid input into arbitrary fallbacks.
- When object alternatives share a literal tag, [dispatch with `z.discriminatedUnion`](./references/discriminated-unions.md) rather than trying each tagged branch with `z.union`.
- When unknown object keys have contract meaning, [select the matching object constructor](./references/object-strictness.md): strip for leniency, reject for closed contracts, or preserve only opaque pass-through data.
- When invalid input reaches a boundary, [choose the parse API from the failure contract](./references/parse-failure-contracts.md): abort a violated invariant or return an expected validation branch.
- When an expected validation branch must reach UI or logs, [derive the presentation from Zod's error](./references/validation-error-rendering.md) instead of discarding its field information.
- When one value violates one boolean rule, [use `.refine()`](./references/predicate-validation.md); move multi-field or multi-issue validation to `.check()`.
- When relationships among several fields need separate actionable issues, [use `.check()`](./references/cross-field-validation.md) instead of collapsing them into one `.refine()` error.
