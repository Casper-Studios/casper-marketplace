# Trigger Descriptions

Treat the frontmatter description as the discovery contract. First state the skill's distinctive capability or governing opinion. Then name only the smallest set of discriminating user intents, artifacts, or decisions that make it relevant.

```yaml
# BAD: the description does not give the agent a usable trigger.
description: Helps with agent skills.
```

```yaml
# GOOD: the description states a distinctive capability and discriminating decisions.
description: PostgreSQL query and schema-design conventions. Use when designing tables, reviewing indexes, or diagnosing query plans.
```

Leave detailed topic and API indexes to `SKILL.md` and routed references. General and specialized skills can apply together. Add exclusions only for genuinely competing workflows.

Do not repeat trigger lists in a `When to Apply` section. The body loads only after discovery has already happened. Use the opening body prose to explain the governing model instead.
