# Ticket Template

Use this template when drafting tickets to the scratchpad and when formatting the `description` field for `mcp__linear__create_issue`.

## Scratchpad File Format

```markdown
# Linear Tickets — YYYY-MM-DD

Source: [description of input source, with link if available]

## Config
- Team: {from config}
- Project: {from config}
- Assignee: {from config}
- Cycle: {from config}

## Ideas / Needs More Thought

### Idea title
Brief description of the exploratory concept.

---

## Tickets

### 1. Ticket Title
- **Priority:** High | Medium | Low
- **Labels:** [matched from config labels]

{ticket body — same format as Linear description below}
```

## Linear Ticket Description Format

```markdown
## User Story
Why this is needed and how it should work. Include concrete examples with exact quotes, specific companies/tickers, KPIs, and scenarios discussed in the source material.

## Requirements
- [ ] Technical/operational requirement 1
- [ ] Technical/operational requirement 2

## User Story Examples

### Example 1: [Scenario] (timestamp if available)
> Exact quote from source
- Explain the desired behavior, how it should work, and why it matters.

### Example 2: [Scenario] (timestamp if available)
> Another quote...


## Limitations / Boundaries
- Do NOT do X
- Out of scope: Y

## Acceptance Criteria
- [ ] Testable condition 1
- [ ] Testable condition 2
```

## Rules

- Every ticket with a real-world example from the source MUST include that example verbatim — do not summarize away specifics.
- Use `>` blockquotes for exact quotes from participants.
- Include timestamps when available (call transcripts, Slack messages).
- Sections with no content should be omitted, not left empty.
