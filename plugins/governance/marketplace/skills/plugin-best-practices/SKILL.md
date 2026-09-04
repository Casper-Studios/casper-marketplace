---
name: plugin-best-practices
description: Agent-plugin design conventions for public outcomes, private implementation, and minimal packaging. Use when creating, restructuring, or reviewing agent-skill plugins.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# Plugin Best Practices

Prefer fine-grained plugins that package one coherent installable capability or body of guidance. Consumers install the plugin as a unit instead of assembling cooperating skills or accepting unrelated functionality.

Treat a plugin as an encapsulation boundary. Like a class in object-oriented programming, it exposes a deliberate public interface while hiding implementation details that consumers do not need to understand or invoke.

A plugin can expose one public skill or several independently useful public skills. Those entry points own consumer-facing outcomes while private skills support them without exposing the internal call graph.

## Effective Strategies for Focused Agent-Skill Plugins

Follow the guidelines below. Read each linked reference that applies to the plugin design task.

1. Expose public outcomes while keeping implementation skills private.
   - [Structure the plugin around public outcomes and private implementation skills.](./references/plugin-structure.md)
2. Package only the metadata and files that consumers need.
   - [Keep manifests and packaged files minimal.](./references/plugin-manifests.md)
