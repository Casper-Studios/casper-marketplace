---
name: agent-skills-best-practices
description: Agent-skill design conventions for focused scope, precise discovery, and progressive disclosure. Use when creating, restructuring, or reviewing `SKILL.md`-based skills.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# Agent Skills Best Practices

Use skills for decisions, procedures, and knowledge that change how the agent works. Do not repeat documentation it can look up.

Keep essential guidance in `SKILL.md`. Put conditional detail in references and explain when to read each.

Show, don't tell: pair contrasting examples with a short explanation.

## References

1. Make the skill easy to find and invoke.
   - [Name the procedure or subject the skill covers.](./references/skill-naming.md)
   - [Describe what the skill does and when to invoke it.](./references/trigger-descriptions.md)
2. Keep each skill focused.
   - [Split unrelated triggers or decisions into separate skills.](./references/skill-scope.md)
   - [Separate essential guidance from conditional detail.](./references/context-and-disclosure.md)
   - [Explain when each reference applies.](./references/reference-routing.md)
   - [Contrast approaches and explain why the difference matters.](./references/examples.md)
   - [Keep prose direct and formatting consistent.](./references/prose-and-formatting.md)
3. Use scripts for deterministic work and models for judgment. Prefer existing tools and standard libraries. Declare required third-party Python dependencies with [PEP 723](https://peps.python.org/pep-0723/) and lock them with `uv`.
   - [Make scripts reproducible and usable from read-only installations.](./references/executable-scripts.md)
4. Make guidance usable outside its source project.
   - [Write portable guidance with framework-appropriate examples.](./references/agnostic-references.md)
5. Keep resources portable and in the skill that owns them.
   - [Keep resource paths flat and one hop from the entry point.](./references/directory-structure.md)
   - [Identify external libraries without copying their documentation.](./references/library-sources.md)
   - [Check distribution and licensing rules before bundling assets.](./references/asset-distribution.md)
