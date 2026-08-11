# Reference Routing

Put the reference-consumption instruction directly under a `References` subheading.

Index every reference exactly once from `SKILL.md`. Use an explicit `./` relative path. Keep references one hop from the entry point, and do not link from one reference to another.

Write each router as one concise sentence that hooks/establishes the triggering situation and governing opinion or failure mode. Hyperlink the phrase that names the relevant decision.

```markdown
<!-- BAD: a filename with no narrative relevance. -->

- [Validation](./references/validation.md)
```

```markdown
<!-- BAD: an artificial command that still does not explain the decision. -->

- For validation, use [validation](./references/validation.md).
```

```markdown
<!-- BAD: a miniature reference defeats selective loading. -->

- When validation is needed, read [validation](./references/validation.md), which
  covers link checking, formatting, schemas, examples, forward tests, and more.
```

```markdown
<!-- GOOD: the situation and expected protection make the link relevant. -->

- When examples can drift from their claimed API, apply the
  [semantic validation gate](./references/validation.md) before release.
```

Do not make a router a topic label. Do not make it a paragraph. The linked reference owns the details.
