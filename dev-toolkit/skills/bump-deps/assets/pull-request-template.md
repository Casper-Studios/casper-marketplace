# Pull Request Template

Write the PR summary to `.claude/scratchpad/PR.md` using this template:

```markdown
# Dependency Upgrade Summary

## Intended Changes

| Package | Current | Target | Migration Effort |
| ------- | ------- | ------ | ---------------- |
| pkg-a   | 1.0.0   | 2.0.0  | Medium           |
| pkg-b   | 3.1.0   | 3.2.0  | Low              |

## Resolved Breaking Changes

<details>
<summary><strong>pkg-a</strong>: 1.0.0 → 2.0.0 (Medium effort)</summary>

### Breaking Change 1: [Title]

- **Change**: [Description]
- **Resolution**: [How we addressed it]
- **Source**: [Link to GitHub Release or CHANGELOG entry]

### Breaking Change 2: [Title]

- **Change**: [Description]
- **Resolution**: [How we addressed it]
- **Source**: [Link to GitHub Release or CHANGELOG entry]

</details>

<details>
<summary><strong>pkg-b</strong>: 3.1.0 → 3.2.0 (Low effort)</summary>

No breaking changes. Minor version bump with backwards-compatible additions.

</details>

## Confidence Assessment

| Category         | Score | Notes                          |
| ---------------- | ----- | ------------------------------ |
| Breaking Changes | X/10  | All identified changes handled |
| Test Coverage    | X/10  | Relevant tests exist           |
| Documentation    | X/10  | Sources were authoritative     |
| **Overall**      | X/10  |                                |

## Deferred Work (Major Versions)

These major version upgrades require separate, dedicated migration efforts:

- **pkg-c**: v2.x → v3.x (blocked by: reason)
- **pkg-d**: v1.x → v2.x (requires: prerequisite)

## Source References

All breaking changes and migrations are backed by authoritative sources:

| Package | Source Type    | URL                                                        |
| ------- | -------------- | ---------------------------------------------------------- |
| pkg-a   | GitHub Release | https://github.com/owner/pkg-a/releases/tag/v2.0.0         |
| pkg-b   | CHANGELOG.md   | https://github.com/owner/pkg-b/blob/main/CHANGELOG.md#v320 |
```

## Requirements

- Every breaking change MUST reference a specific changelog entry from the sub-agent analysis
- Confidence score reflects how well-documented the upgrade path is
- Deferred work section captures major versions that should NOT be upgraded in this PR
- Each package's breaking changes should be in a collapsible `<details>` section
