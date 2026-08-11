---
name: tanstack-react-table-best-practices
description: Opinionated TanStack Table v9 beta conventions for React table schema, per-table behavior, typed metadata, and header/cell/footer rendering. Use when creating or reviewing `useTable` tables, column definitions, row actions, table feature metadata, or `FlexRender` rendering in React.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# TanStack React Table Best Practices

Treat a table as stable schema plus instance-specific behavior: keep columns static, place callbacks in local metadata, and render through the table primitives for reusable, type-safe tables.

## Library Sources

- GitHub repository ID: `TanStack/table`
- Context7 library ID: `/tanstack/table`
- DeepWiki repository ID: `TanStack/table`

Use Context7 for current documentation and DeepWiki for implementation details.

## References

Read as many linked references as are relevant to the current task before writing or reviewing TanStack Table code.

- Hoist static table schema and send per-instance capabilities through [hoisted columns and meta](./references/hoisted-columns-and-meta.md), avoiding structural recomputation from callback capture.
- Declare each schema's local capability contract with [typed table meta](./references/table-meta-types.md), not v8-style global metadata.
- Render headers, cells, and footers through the table-owned [table primitives](./references/cell-rendering.md), because definitions are schema rather than JSX content.
