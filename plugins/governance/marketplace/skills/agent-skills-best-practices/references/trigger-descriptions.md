# Trigger Descriptions

Treat the frontmatter description as the discovery contract. State what the skill contributes and name concrete user intents, artifacts, or decisions that make it relevant.

```yaml
# BAD: the description does not give the agent a usable trigger.
description: Helps with agent skills.
```

```yaml
# GOOD: the description names the capability and concrete authoring decisions.
description: Opinionated PostgreSQL query and schema-design conventions. Use when designing tables, reviewing indexes, diagnosing query plans, changing connection management, or troubleshooting database performance.
```

Do not repeat trigger lists in a `When to Apply` section. The body loads only after discovery has already happened. Use the opening body prose to explain the governing model instead.
