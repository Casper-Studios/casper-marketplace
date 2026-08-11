---
name: plugin-best-practices
description: Opinionated conventions for designing focused agent-skill plugins as encapsulated, installable capabilities. Use when defining a plugin boundary, deciding which skills are public entry points, hiding shared implementation skills, splitting broad plugins, designing plugin structure, minimizing client manifests, or removing auxiliary package documentation.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# Plugin Best Practices

Prefer fine-grained plugins that package one coherent installable capability or body of guidance. Consumers install the plugin as a unit instead of assembling cooperating skills or accepting unrelated functionality.

Treat a plugin as an encapsulation boundary. Like a class in object-oriented programming, it exposes a deliberate public interface while hiding implementation details that consumers do not need to understand or invoke.

A plugin can expose one public skill or several independently useful public skills. Those entry points own consumer-facing outcomes while private skills support them without exposing the internal call graph.

## References

Read as many linked references as are relevant to the plugin design task.

- When translating the public boundary into directories and invocation visibility, [structure the plugin around public outcomes and private implementation skills](./references/plugin-structure.md).
- When defining plugin metadata or package contents, keep [manifests and packaged files minimal](./references/plugin-manifests.md).
