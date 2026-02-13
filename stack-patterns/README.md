# Stack Patterns - Idiomatic Usage Patterns for Claude Code

Idiomatic usage patterns for React, TanStack, and more. These are non-invocable skills that provide Claude with reference material for writing correct, performant code following established project conventions.

## Features

- **React Patterns**: Minimal state, proper memoization, type-safe conditional logic, and Loader/Inner patterns
- **TanStack Table**: Meta field pattern for cell callbacks, hoisted column definitions, and sortable headers
- **better-all**: DAG-based dependency optimization for parallel async operations with full type inference

## Installation

### Option 1: Marketplace (Recommended)

```bash
# 1. Add the Casper Studios marketplace
/plugin marketplace add Casper-Studios/plugin-marketplace

# 2. Install the plugin
/plugin install stack-patterns
```

### Option 2: Git Clone + Local Plugin Directory

```bash
# Clone the repository
git clone git@github.com:Casper-Studios/plugin-marketplace.git

# Run Claude Code with the plugin directory
claude --plugin-dir ./plugin-marketplace
```

## Skills

> These skills are **not user-invocable**. They serve as reference material that Claude reads automatically when working on relevant code.

### react-patterns

Write React components with minimal state, proper memoization, and type-safe patterns.

| Reference | Description |
|-----------|-------------|
| `references/state-management.md` | Derived values over state, component boundaries, Context API, Zustand, state machines |
| `references/memoization.md` | useMemo for O(n) ops, atomic memoization, useCallback, Loader/Inner pattern |
| `references/conditional-logic.md` | Affirmative logic, explicit conditionals, type narrowing, early return guards |

### tanstack-table

Build TanStack Table components using the meta field pattern for cell callbacks instead of closures.

| Reference | Description |
|-----------|-------------|
| `references/meta-field.md` | Type-safe meta extension, passing meta to tables, accessing meta in cells/headers |
| `references/column-definitions.md` | Column helper setup, accessor columns, sortable headers, display columns |

### better-all

Use the better-all library for `Promise.all` with automatic DAG-based dependency optimization and full type inference.

| Reference | Description |
|-----------|-------------|
| `references/dag-patterns.md` | Multi-tier dependencies, diamond dependencies, conditional execution, error handling |

## Directory Structure

```
stack-patterns/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── skills/
│   ├── better-all/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── dag-patterns.md
│   ├── react-patterns/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── state-management.md
│   │       ├── memoization.md
│   │       └── conditional-logic.md
│   └── tanstack-table/
│       ├── SKILL.md
│       └── references/
│           ├── meta-field.md
│           └── column-definitions.md
└── README.md                    # This file
```

## License

MIT
