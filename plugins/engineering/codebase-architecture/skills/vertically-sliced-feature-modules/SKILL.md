---
name: vertically-sliced-feature-modules
description: Feature-first module architecture for cohesive ownership, composition, and promotion boundaries. Use when designing, moving, or reviewing feature and package structure.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# Vertically Sliced Feature Modules

Organize systems around capabilities that own their implementation end to end. Reconstruct the production import graph and the build + runtime boundaries before proposing folders. Treat example names as adaptable ownership shapes, not prescribed filenames.

## Recursive Ownership

A feature or subsystem owns the complete private import closure required to provide its operation. Apply this rule recursively:

1. Place each private dependency beneath its narrowest production consumer.
2. Place a dependency used by several children at their lowest common owning ancestor.
3. Let external consumers import only an operational entry.
4. Do not import ancestor-private or sibling-private implementation files.
5. Repeat the placement analysis inside every child until no dependency can move closer to its consumer.

An entry implements or composes the operation its consumer needs. A file that only re-exports private leaves is a barrel, not an entry. Familiar entry filenames such as `index.ts`, `mod.rs`, `__init__.py`, `page.tsx`, and `+page.svelte` can make a boundary visible, but the filename does not create the boundary.

Name operation-owning subsystems with verbs such as `filter`, `edit`, `review`, or `publish`. Use nouns for owned domain concepts, records, and infrastructure such as `policy`, `repository`, or `schema`. Follow an established repository convention when it communicates the same ownership clearly.

Features are isolated siblings and do not import one another. Callers and orchestrators compose feature entries. Promote stable behavior only when its real consumer set requires a broader owner.

## References

Read the reference that matches the ownership decision being changed.

1. Derive the directory tree from the production import graph.
   - [Recursively place every private dependency beneath its narrowest owning consumer.](./references/recursive-ownership.md)
   - [Give each public boundary an operational entry and keep private imports inside that boundary.](./references/entries-and-import-boundaries.md)
2. Broaden ownership only when the consumer set proves it is necessary.
   - [Place shared behavior at its lowest common owner before promoting it across features.](./references/ownership-promotion.md)
   - [Admit an independently buildable package only for a real dependency, runtime, build, or deployment closure.](./references/package-admission.md)
3. Preserve behavior and evidence while changing structure.
   - [Apply the ownership analysis to a fixed point and audit the resulting import graph.](./references/refactor-and-review.md)
   - [Collocate unit tests with their narrowest leaf and hoist cross-boundary scenarios to their composing owner.](./references/test-placement.md)
