# Library Sources

A skill dedicated to one external library keeps its lookup identifiers in `SKILL.md`, where they remain visible whenever the skill is active:

```markdown
## Library Sources

- GitHub: `owner/repository`
- Context7: `/owner/repository`
- DeepWiki: `owner/repository`
```

Do not move these identifiers into some `documentation.md` reference. Lookup procedure is part of operating the skill, not conditional domain guidance.

Use Context7 for current library documentation and DeepWiki when documentation is insufficient or conflicts with implementation. Verify identifiers before publishing them; never invent a missing ID.

The skill must still encode conventions rather than copied documentation. Source identifiers make current documentation fetchable and remove the excuse for embedding a tutorial in the skill.
