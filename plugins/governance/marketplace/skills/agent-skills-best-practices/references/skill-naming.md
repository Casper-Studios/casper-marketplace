# Skill Naming

Name a skill after the capability it gives the agent. The name must reveal whether the skill performs a procedure or supplies documentary guidance.

Use a verb-noun pair for an entirely procedural workflow:

```yaml
# BAD: the name does not say what action the workflow performs.
name: pull-request

# GOOD: the workflow writes a pull request.
name: write-pull-request
```

Use a descriptive adjective-noun pair for peripheral knowledge or conventions:

```yaml
# BAD: an imperative name misrepresents documentary guidance as a workflow.
name: optimize-nextjs

# GOOD: the skill supplies an opinionated body of guidance.
name: nextjs-best-practices
```

Do not name a skill after its implementation mechanism, resource type, or internal stage unless that mechanism is the capability users actually seek.
