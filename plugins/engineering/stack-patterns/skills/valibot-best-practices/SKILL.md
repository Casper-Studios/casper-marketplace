---
name: valibot-best-practices
description: Valibot conventions for owned wire contracts and explicit validation outcomes. Use when defining or reviewing Valibot schemas or parsing untrusted data with Valibot.
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

## Effective Strategies for Valibot

Read the references that apply to the current task before defining or reviewing Valibot schemas and parsing code.

1. Make schemas the owned, trusted contract for wire data.
   - [Make a schema that proves a domain shape the single source of truth](./references/schema-ownership.md) and infer the exported type instead of maintaining a duplicate declaration.
   - [Validate serialized data at its trust boundary](./references/serialized-trust-boundaries.md), including authenticated external payloads, before it becomes a domain value.
   - [Keep constructors under the `v` namespace](./references/namespace-imports.md) so library ownership stays clear and import forms remain consistent.
2. Encode exact wire semantics inside the schema.
   - [Encode missing and `null` wire semantics](./references/wire-nullability.md) with the matching wrapper rather than whichever wrapper compiles.
   - [Dispatch literal-tagged alternatives with `v.variant`](./references/discriminated-variants.md) so Valibot selects and reports the failing tagged branch.
   - [Define defaults with exact domain meaning in the schema](./references/schema-defaults.md); do not use a default to reinterpret malformed input.
   - [Transform normalized wire input inside the schema](./references/schema-transformations.md) so consumers receive trusted domain values rather than raw serialized forms.
3. Make validation failure match the boundary contract.
   - [Choose the parse API from the failure contract](./references/parse-failure-contracts.md): abort a violated invariant or return an expected validation branch.
   - [Preserve expected validation issues](./references/validation-failure-preservation.md) instead of substituting an invented `null` or empty value.
