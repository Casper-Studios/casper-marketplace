---
name: tanstack-react-table-best-practices
description: TanStack Table v9 conventions for stable React table schemas and instance behavior. Use when creating or reviewing React tables, columns, metadata, or rendering.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# TanStack React Table Best Practices

Treat a table as stable schema plus instance-specific behavior: explicitly register only the features it needs, stabilize schemas and options, place callbacks in local metadata, and render through table primitives.

## Library Sources

- GitHub repository ID: `TanStack/table`
- Context7 library ID: `/tanstack/table`
- DeepWiki repository ID: `TanStack/table`

Use Context7 for current documentation and DeepWiki for implementation details.

## References

Read the references that apply to the current task before writing or reviewing TanStack Table code.

1. Configure a table deliberately.
   - [Register explicit capabilities and compose shared infrastructure](./references/explicit-capabilities.md) with only the row models and named functions in use. Do not start tables with `stockFeatures` or whole built-in function registries.
2. Stabilize schema and option identities.
   - [Keep the table contract stable and its capabilities feature-local](./references/table-contract.md). Hoist immutable schema, memoize render-local values whether or not the React Compiler is enabled, and reserve declaration merging for a genuinely global contract.
3. Render and subscribe at the narrowest correct boundary.
   - [Render headers, cells, and footers through table primitives](./references/cell-rendering.md).
   - [Preserve instance ownership through receiver-bound methods and narrow subscriptions](./references/instance-ownership.md), especially for nested components that receive stable table objects.
4. Keep table controls consistent as pages load.
   - [Handle selection, sort clearing, filters, and pinning](./references/interaction-semantics.md) without treating loaded rows as the full dataset.
