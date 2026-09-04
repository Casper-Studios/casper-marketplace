---
name: vertically-sliced-feature-modules
description: Feature-first module architecture for cohesive ownership, composition, and promotion boundaries. Use when designing, moving, or reviewing feature and package structure.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# Vertically Sliced Feature Modules

This skill organizes systems around capabilities that own their implementation end to end. Feature roots, nested subsystems, compositional entry points, and deliberately promoted shared boundaries keep cohesion high and dependency direction visible.

Reconstruct the current ownership graph and build/runtime boundaries before proposing folders. Treat the example trees as adaptable ownership shapes, not prescribed filenames.

## Feature Ownership

A feature owns one user-visible or business capability end to end. Keep its complete private implementation closure under that owner, recursively, instead of scattering technical roles across global layers.

An entry implements or composes the operation its consumer needs. Keep setup options private when a caller only uses them to finish that operation. Do not introduce a forwarding wrapper or re-export barrel to manufacture an entry point.

Keep a readable private helper in its consumer. Extract a utility file when meaningful sans-I/O behavior needs a focused colocated test, even with one production consumer; this does not make the utility shared. Do not invent tests for trivial glue.

Features are isolated siblings and do not import one another. Callers and orchestrators compose feature entries. When multiple features need the same stable logic, promote it to a focused shared owner instead of making either feature the dependency of the other.

## References

Read the reference that matches the ownership or boundary being changed.

1. Keep each capability's technical roles together under its owning feature.
   - [Use a feature-first directory structure instead of scattering a capability by layer.](./references/directory-structure.md)
   - [Give a single owner's private capability a deeper nested subsystem instead of a broad prefixed namespace.](./references/nested-subsystems.md)
   - [Collocate unit tests with their narrowest leaf and hoist cross-cutting scenarios to an integration owner.](./references/test-placement.md)
2. Compose features through deliberate entries and one-way public boundaries.
   - [Keep routes and registries as composition surfaces; entry points must not absorb reusable business behavior.](./references/entry-points-and-composition.md)
   - [Prevent feature-to-feature coupling through public contracts with downward import direction.](./references/public-contracts-and-import-direction.md)
3. Promote shared ownership and package boundaries only when the system requires them.
   - [Require multiple owners to share one stable responsibility before promoting code to a shared-code owner.](./references/shared-code-promotion.md)
   - [Admit an independently buildable package only for a real dependency, runtime, build, or deployment closure.](./references/package-admission.md)
4. Preserve the existing ownership graph, contracts, and behavior during structural changes.
   - [Refactor and review module moves without redesigning logic under the cover of a move.](./references/refactor-and-review.md)
