---
name: extract-my-action-items
description: Extract action items from a Fireflies call transcript. Default extracts for ALL attendees; specify a target person to extract only theirs. Use when the user wants to find commitments, assignments, and follow-ups from a recorded meeting.
user-invocable: true
---

# Extract Action Items

Extract action items from a Fireflies transcript using parallel subagents. Catches items automated summaries miss.

**Two modes:**
- **All attendees (default):** No target specified — extract action items for every participant
- **Single person:** Target specified — extract action items for that person only

## Phase 1: Find and Fetch

1. Search with `mcp__fireflies__fireflies_get_transcripts` (date, or keyword)
2. Determine mode:
   - If a target person is specified in the invocation → **single-person mode**
   - Otherwise → **all-attendees mode**
3. Fetch `mcp__fireflies__fireflies_get_summary` and `mcp__fireflies__fireflies_get_transcript` in parallel

## Phase 2: Preprocess Transcript

The transcript API returns a JSON array. Extract to plain text before chunking:

```bash
jq -r '.[].text' < raw_transcript.json > .claude/scratchpad/transcript.txt
```

If `jq` is unavailable, use Python: `json.load` then join `[e["text"] for e in data]` with newlines.

Count lines: `wc -l < .claude/scratchpad/transcript.txt`

**All-attendees mode:** Also extract the distinct speaker list from the transcript JSON:

```python
speakers = sorted(set(e["speaker_name"] for e in data if e.get("speaker_name")))
```

## Phase 3: Parallel Subagent Extraction

**Chunk sizing:** `ceil(total_lines / 5)` lines per chunk, minimum 200. Adjust chunk count so no chunk is under 200 lines.

Launch one `general-purpose` subagent per chunk.

### Single-Person Prompt

```
Read lines [START] to [END] of [FILE_PATH].

Find ALL action items for [TARGET_PERSON]. Return each as:
- **Item**: what they committed to
- **Quote**: exact words from transcript
- **Context**: who else involved, any deadline

Beyond obvious commitments ("I'll do X"), catch these non-obvious patterns:
- Self-notes: "I'll make a note to...", "let me jot down..."
- Admissions implying catch-up: "I dropped the ball on X", "I still haven't read X"
- Conditional offers that became commitments: "If we have time, I'm happy to..."
- Volunteering: "I guess I'll volunteer to..."
- Exploration tasks: "Let me spend a few hours with it"
- Questions/topics for external parties: "I need to ask [person/firm] about X", "thing to discuss with [party]"
```

### All-Attendees Prompt

```
Read lines [START] to [END] of [FILE_PATH].

The meeting attendees are: [SPEAKER_LIST]

Find ALL action items for EVERY attendee. Group by person. For each item return:
- **Person**: who owns the action item
- **Item**: what they committed to
- **Quote**: exact words from transcript
- **Context**: who else involved, any deadline

Beyond obvious commitments ("I'll do X"), catch these non-obvious patterns:
- Self-notes: "I'll make a note to...", "let me jot down..."
- Admissions implying catch-up: "I dropped the ball on X", "I still haven't read X"
- Conditional offers that became commitments: "If we have time, I'm happy to..."
- Volunteering: "I guess I'll volunteer to..."
- Exploration tasks: "Let me spend a few hours with it"
- Questions/topics for external parties: "I need to ask [person/firm] about X", "thing to discuss with [party]"
- Delegations: "[Person], can you handle X?", "I'll leave that to [person]"
```

## Phase 4: Consolidate

Merge subagent results, deduplicate, and categorize. **Only include categories that have items.**

### Categories

1. **High Priority / Technical** — Code changes, bug fixes, PR reviews, investigations
2. **Pairing / Collaboration** — Scheduled syncs, joint work sessions
3. **Content / Research** — Reading, writing, experiments, documentation
4. **Questions for External Parties** — Topics to raise with specific people/firms outside the immediate team
5. **Exploration / Tooling** — Tool evaluations, setup, environment tasks
6. **Catch-up** — Things explicitly acknowledged as dropped or missed

### Output

**Single-person mode** — Write to `.claude/scratchpad/[name]-action-items-YYYY-MM-DD.md`:

```markdown
# [Name] Action Items — [Meeting Title]

**Date:** [Date]
**Fireflies Link:** https://app.fireflies.ai/view/[TRANSCRIPT_ID]

## [Category Name]

- [ ] **Item title**
  - Context and details
  - > "Exact quote"

## Quick Reference — Time-Sensitive

1. [Item with deadline or scheduled time]
```

**All-attendees mode** — Write to `.claude/scratchpad/action-items-YYYY-MM-DD.md`:

```markdown
# Action Items — [Meeting Title]

**Date:** [Date]
**Fireflies Link:** https://app.fireflies.ai/view/[TRANSCRIPT_ID]

## [Person Name]

### [Category Name]

- [ ] **Item title**
  - Context and details
  - > "Exact quote"

## Quick Reference — Time-Sensitive

1. [Person] — [Item with deadline or scheduled time]
```

## Phase 5: Review & Post to Slack

1. Use `AskUserQuestion`: **"Post action items to Slack?"** — options: "Post to Slack", "Skip — just keep the file"
2. If approved, run the bundled script with the output file path:

```bash
node [SKILL_DIR]/scripts/slack-post.mjs [OUTPUT_FILE_PATH]
```

The script handles markdown-to-mrkdwn conversion, chunking by person section (max 3900 chars), and posting via `curl` + Slack API. Requires env vars `SLACK_BOT_TOKEN` and `SLACK_CHANNEL_ID`.

3. After posting (or skipping), delete all artifacts created during the run: `transcript.txt`, the action items markdown file, and any other temp files written to `.claude/scratchpad/` during this workflow.

## Example Invocations

- `/extract-my-action-items` — all attendees, most recent meeting
- `/extract-my-action-items standup` — all attendees, search for "standup"
- `/extract-my-action-items for Basti from yesterday` — single person
- `/extract-my-action-items 01KFY1RSEVVQW7MB1TKG4N2D20` — all attendees, specific transcript
