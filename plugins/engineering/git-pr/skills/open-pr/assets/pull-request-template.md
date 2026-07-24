## Pull Request Type

- feat, fix, refactor, chore, docs, style, test, perf

## Summary

- 2-4 bullets on what changed and why
- Focus on reviewer-relevant outcomes, not commit chronology

## Scope

- Area 1 (`path/or/domain`): what changed
- Area 2 (`path/or/domain`): what changed

## Key Changes

- Highlight behavior changes and non-obvious decisions
- Call out any broad mechanical edits (formatting/lint/codemod) explicitly

## Reviewer Guide

1. Start with config/policy files (if any)
2. Review core logic files next
3. Skim mechanical files last

## Risk / Impact

- Runtime impact:
- Data/migration impact:
- Operational impact:

## Validation

- [ ] `command here` (passed/failed + note)
- [ ] `command here` (passed/failed + note)

## Breaking Changes

- None / describe clearly

## Tickets

- [Ticket here](link.com)

## Notes

- Optional context for reviewers/deployers

## Attachments

- Screenshots / logs / links (optional)

## Self Checklist

<!-- Before submitting a PR, make sure these are all done and checked -->

- [ ] I have added/updated tests where needed
- [ ] I ran relevant local checks and documented results above
- [ ] Documentation was updated if behavior or workflow changed
- [ ] The database migration **DOES NOT _delete any data_** (if applicable)
