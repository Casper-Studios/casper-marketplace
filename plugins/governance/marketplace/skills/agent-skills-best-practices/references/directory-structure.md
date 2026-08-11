# Directory Structure

Keep skill packages as flat as the resource ownership permits. A skill entry point must be able to name each conditional resource directly without navigating a documentation tree.

```text
# BAD: taxonomy adds navigation without adding ownership.
agent-skill/
├── references/
│   └── sections/
│       └── routing/
│           └── narrative-links.md
└── assets/
    └── fonts/
        └── brand.woff2

# GOOD: resources stay directly discoverable.
agent-skill/
├── references/
│   └── narrative-links.md
└── fonts/
    └── brand.woff2
```

Use a deeper directory only when it is a real owned artifact, such as a complete template copied as one unit. Do not reproduce a document outline in the filesystem.

Prefer another small skill over a deep reference hierarchy when a subtree has an independent trigger and reusable purpose.
