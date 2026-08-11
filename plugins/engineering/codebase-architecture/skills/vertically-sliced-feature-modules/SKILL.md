---
name: vertically-sliced-feature-modules
description: Opinionated feature-first architecture conventions for cohesive modules, owned subtrees, entry points, shared-code promotion, and package boundaries. Use when designing or reviewing directory structure, placing UI or workflow code, splitting nested capabilities, extracting shared modules, enforcing feature import boundaries, deciding whether a feature deserves a package, or refactoring horizontal technical layers.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# Vertically Sliced Feature Modules

This skill organizes systems around capabilities that own their implementation end to end. Feature roots, nested subsystems, compositional entry points, and deliberately promoted shared boundaries keep cohesion high and dependency direction visible.

Reconstruct the current ownership graph and build/runtime boundaries before proposing folders. Treat the example trees as adaptable ownership shapes, not prescribed filenames.

## Feature Ownership

A feature owns one user-visible or business capability end to end. Keep its technical roles inside that owner instead of scattering them across global layers.

Features are isolated siblings and do not import one another. Callers and orchestrators compose feature entries. When multiple features need the same stable logic, promote it to a focused shared owner instead of making either feature the dependency of the other.

## References

Read as many linked references as are relevant to the current task before planning, moving, or reviewing modules.

- Keep each capability's technical roles together with a feature-first [directory structure](./references/directory-structure.md) instead of scattering them by layer.
- Keep routes and registries as composition surfaces; [entry points](./references/entry-points-and-composition.md) must not absorb reusable business behavior.
- Give a single owner's private capability a deeper [nested subsystem](./references/nested-subsystems.md) instead of a broad prefixed namespace.
- Prevent feature-to-feature coupling by routing cross-boundary access through [public contracts with downward import direction](./references/public-contracts-and-import-direction.md).
- Before promoting code, require multiple owners to share one stable responsibility under the [shared-code owner](./references/shared-code-promotion.md).
- Admit an [independently buildable package](./references/package-admission.md) only for a real dependency, runtime, build, or deployment closure.
- Collocate unit tests with their narrowest leaf and [hoist cross-cutting scenarios to an integration owner](./references/test-placement.md).
- During structural changes, [preserve ownership, contracts, and behavior](./references/refactor-and-review.md) instead of redesigning logic under the cover of a move.
