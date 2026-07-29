---
name: valibot-best-practices
description: Opinionated Valibot conventions for wire-schema ownership, nullability, tagged variants, transformations, and explicit validation-failure behavior. Use when defining or reviewing Valibot schemas, validating forms or HTTP payloads, parsing JSON or persisted data, or deciding whether invalid input aborts or becomes an expected branch.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# Valibot Best Practices

Treat a Valibot schema as the owned contract at an untrusted data boundary: it defines accepted wire values, produces trusted domain values, and makes invalid input an explicit, intentional outcome.

## Library Sources

- GitHub repository ID: `open-circle/valibot`
- Context7 library ID: `/open-circle/valibot`
- DeepWiki repository ID: `open-circle/valibot`

Use Context7 for current documentation and DeepWiki for implementation details.

## References

Read as many linked references as are relevant to the current task before defining or reviewing Valibot schemas and parsing code.

- When a schema already proves a domain shape, [make it the single source of truth](./references/schema-ownership.md) and infer the exported type instead of maintaining a duplicate declaration.
- When serialized data enters the application, [validate it at that trust boundary](./references/serialized-trust-boundaries.md), including authenticated external payloads, before it becomes a domain value.
- When defining Valibot schemas, [keep constructors under the `v` namespace](./references/namespace-imports.md) so their library ownership stays clear and import forms remain consistent.
- When a wire field can be missing, `null`, or both, [encode those exact semantics](./references/wire-nullability.md) with the matching wrapper rather than whichever wrapper compiles.
- When object alternatives share a literal tag, [dispatch with `v.variant`](./references/discriminated-variants.md) so Valibot selects and reports the failing tagged branch.
- When invalid input reaches a boundary, [choose the parse API from the failure contract](./references/parse-failure-contracts.md): abort a violated invariant or return an expected validation branch.
- When validation failure is an expected branch, [preserve its issues](./references/validation-failure-preservation.md) instead of substituting an invented `null` or empty value.
- When absence has an exact domain meaning, [define that default in the schema](./references/schema-defaults.md); do not use a default to reinterpret malformed input.
- When wire input needs normalization, [transform it inside the schema](./references/schema-transformations.md) so consumers receive trusted domain values rather than raw serialized forms.
