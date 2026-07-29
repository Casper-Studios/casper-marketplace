# Context and Disclosure

Use `SKILL.md` for the minimum context that every invocation needs to understand and apply the skill. Start with a concise orientation that states the governing model and intended outcome.

Inline a rule when the agent must load it on every invocation anyway. A reference creates no progressive disclosure when the entry point always requires the agent to read it.

Move content behind a reference only when it is conditional, detail-oriented, or specific to one branch of the task. Do not require every reference by default. Load as much as the current task needs.

<progressive_disclosure_examples>

```markdown
<!-- BAD: the entry point is only a table of contents. -->

# API Best Practices

## References

- [Errors](./references/errors.md)
- [Pagination](./references/pagination.md)
```

```markdown
<!-- GOOD: the entry point explains the governing opinion first. -->

# API Best Practices

- Design APIs around stable domain contracts rather than transport convenience.
- Keep caller policy visible and preserve information across boundaries.
```

</progressive_disclosure_examples>
