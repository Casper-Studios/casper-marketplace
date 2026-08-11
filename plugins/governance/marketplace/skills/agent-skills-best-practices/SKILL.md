---
name: agent-skills-best-practices
description: Opinionated conventions for authoring, restructuring, and reviewing agent skills. Use when deciding whether guidance belongs in `SKILL.md`, a conditional reference, or a smaller skill; writing trigger descriptions and reference routers; naming procedural or documentary skills; creating examples; keeping skill context focused; or bundling static assets and their licenses.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# Agent Skills Best Practices

Treat agent skills as opinionated context engineering, not as mirrors of documentation that an agent can fetch elsewhere. A skill earns its context cost by preserving distinctive judgment, repeatable procedure, or peripheral knowledge that materially changes how an agent works.

Keep the governing model and the minimum explainer needed to understand a skill in `SKILL.md`. Inline content that every invocation needs. Reserve progressive disclosure for conditional or detail-oriented guidance, and route to that guidance with concise prose that explains why it matters.

## References

Read as many linked references as are relevant to the authoring or review task.

- When a capability must read clearly in discovery and invocation surfaces, choose a [procedural or documentary name](./references/skill-naming.md) that communicates what the skill provides.
- When one skill begins collecting unrelated triggers or decisions, restore a [cohesive skill scope](./references/skill-scope.md) instead of growing an umbrella package.
- When discovery is too broad, too narrow, or vague, make the [trigger description](./references/trigger-descriptions.md) name the capability and concrete situations that need it.
- When deciding what enters the always-loaded entry point, use [context and disclosure](./references/context-and-disclosure.md) to separate the governing model from conditional detail.
- When an index must make conditional material discoverable, write [reference routing](./references/reference-routing.md) that primes the agent with the relevant situation and decision.
- When examples can expose or obscure the actual opinion, follow the [example conventions](./references/examples.md) instead of turning the skill into a tutorial.
- When prose or Markdown formatting can distract from the rule, keep [skill writing](./references/prose-and-formatting.md) direct, compact, and mechanically consistent.
- When resources begin forming subtrees, restore a [flat directory structure](./references/directory-structure.md) so every conditional resource stays one hop from its entry point.
- When a skill governs one external library, keep [library source identifiers](./references/library-sources.md) visible without copying documentation into the skill.
- When a skill would bundle images, fonts, documents, templates, or other blobs, apply the [asset distribution](./references/asset-distribution.md) policy before including them.
