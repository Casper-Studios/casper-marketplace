# Prompting Guidelines

Prompts should err on the side of deduplication and minimalism.

## Claude Prompting Best Practices

All prompts must follow the [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices.md). Before creating/editing/reviewing any prompts, make sure to read the guidelines first.

After creating/editing any prompts, review the `git diff` to ensure no regressions, prompt fidelity losses, or unexpected behavior changes. New features and bug fixes will obviously alter behavior, but only within the blast radius of the request — cascading implications and stale references are not allowed without prior clarification.

## Skills Best Practices

- Skill names must start with a verb (e.g. `generate-`, `create-`, `review-`)
- Skill names should be as specific as possible (e.g `generate-client-proposal` is better than `generate-doc`) 
- Use hyphens instead of underscores in skill names and file paths 
- Set `user-invocable: false` for internal skills. Skills that are only called by other skills, not directly by the user, should be marked as internal so they don't pollute the user-facing skill list.