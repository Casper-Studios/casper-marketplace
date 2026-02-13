# Source Integrations

How to auto-pull source material from Fireflies.ai, Slack, and Google Drive using existing Casper skill scripts. No new scripts — orchestrate the ones that already exist.

## Source Config File

Stored at `~/.config/casper/linkedin-sources.md` (user-local, never committed).

### Format

```markdown
# LinkedIn Source Configuration

## User
user_email: you@yourcompany.com

## Fireflies
enabled: true
days_back: 14
search_terms: ["internal", "strategy", "product"]

## Slack
enabled: true
channels: []
days_back: 7

## Google Drive
enabled: true
search_terms: ["meeting notes", "strategy", "product update"]
days_back: 30

## Settings
auto_refresh: false
```

The `user_email` field is used to filter Fireflies transcripts to only meetings the user attended. Slack channels should be left empty by default — the setup flow will list available channels for the user to choose from.

### Setup Flow (`--setup-sources`)

1. Ask for the user's work email: "What's your work email? This is used to filter transcripts to only meetings you attended."
   - Save as `user_email` in the config
2. Check which integrations are available by verifying env vars:
   - Fireflies: check if `FIREFLIES_API_KEY` is set
   - Slack: check if `SLACK_BOT_TOKEN` is set
   - Google Drive: check if OAuth creds exist — check for `mycreds.txt` in the google-workspace skill scripts directory
3. For **unavailable** integrations, provide setup instructions:
   - **Fireflies**: "Get your API key from https://app.fireflies.ai/api and set `FIREFLIES_API_KEY` in your environment."
   - **Slack**: "Create a Slack app at https://api.slack.com/apps and set `SLACK_BOT_TOKEN` in your environment."
   - **Google Drive**: "Run the google-workspace skill setup first to configure OAuth."
4. For available integrations, ask the user for configuration:
   - **Fireflies**: "Any specific search terms for transcripts, or pull all recent ones?"
   - **Slack**: "Which channels should I pull from?" — run `python ${CLAUDE_PLUGIN_ROOT}/skills/slack-automation/scripts/slack_search.py search "" --limit 20` to list available channels for the user to choose from
   - **Google Drive**: "Any specific search terms or folders?"
5. Ask: "How many days back should I search? (default: 14 for Fireflies, 7 for Slack, 30 for Drive)"
6. Ask: "Want auto-refresh on every run? (If yes, source material refreshes automatically when you generate posts)"
7. Save config to `~/.config/casper/linkedin-sources.md`

---

## Refresh Flow (`--refresh`)

### Step 1: Read Config

Read `~/.config/casper/linkedin-sources.md`. If missing, run `--setup-sources` first.

### Step 2: Pull from Fireflies

**Script:** `${CLAUDE_PLUGIN_ROOT}/skills/transcript-search/scripts/fireflies_transcript_search.py`

**For each search term in config:**

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/transcript-search/scripts/fireflies_transcript_search.py "{search_term}" --days-back {days_back} --content --json --limit 5
```

**Requires:** `FIREFLIES_API_KEY` environment variable

**Participant Filtering:** After fetching results, filter transcripts to only include meetings the user attended. For each transcript in the response, check if `user_email` (from source config) appears in the transcript's `participants` array (a list of attendee email addresses). Discard transcripts where the user's email is not found in the participants list. This ensures the user only generates posts from meetings they were actually part of.

**Convert output to markdown:**

For each transcript in the **filtered** `transcripts` array:

```markdown
# {title}
Date: {date}
Duration: {duration} minutes
Speakers: {comma-separated speaker names}

## Summary
{summary.overview}

## Key Topics
{summary.keywords as bullet list}

## Action Items
{summary.action_items as bullet list}

## Transcript
{for each sentence: "{speaker_name}: {text}"}
```

**Save as:** `source-material/fireflies-{YYYY-MM-DD}-{title-slugified}.md`

### Step 3: Pull from Slack

**Script:** `${CLAUDE_PLUGIN_ROOT}/skills/slack-automation/scripts/slack_search.py`

**For each channel in config:**

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/slack-automation/scripts/slack_search.py read "{channel_name}" --days {days_back} --limit 100
```

**Requires:** `SLACK_BOT_TOKEN` environment variable

**Convert output to markdown:**

```markdown
# Slack: #{channel_name}
Period: last {days_back} days
Messages: {message_count}

## Messages

{for each message:}
### {user} — {date}
{text}

{if thread_replies:}
> **{reply.user}**: {reply.text}
```

**Save as:** `source-material/slack-{channel_name}-{YYYY-MM-DD}.md`

### Step 4: Pull from Google Drive

**Script:** `${CLAUDE_PLUGIN_ROOT}/skills/google-workspace/scripts/gdrive_search.py`

**For each search term in config:**

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/google-workspace/scripts/gdrive_search.py files "{search_term}" --modified-days {days_back} --limit 10 --json
```

**Requires:** OAuth credentials (`client_secrets.json`, `mycreds.txt`) in the google-workspace skill scripts directory

**For each result**, if the file is a Google Doc or text file, read its content. For Google Docs, use the Docs API or download as text.

**Convert output to markdown:**

```markdown
# {title}
Source: Google Drive
Modified: {modifiedDate}
Type: {mimeType}

## Content
{file content if available, otherwise:}
[File found but content not directly readable — open at {webViewLink}]
```

**Save as:** `source-material/gdrive-{title-slugified}-{YYYY-MM-DD}.md`

### Step 5: Clean Up Old Auto-Pulled Files

Before saving new files, remove previous auto-pulled files (files matching `fireflies-*.md`, `slack-*.md`, `gdrive-*.md` patterns in `source-material/`). This prevents stale content from accumulating. Manually added files (no prefix pattern) are left untouched.

### Step 6: Proceed to Generation

After refresh completes, proceed with the normal post generation flow.

---

## Auto-Refresh

If `auto_refresh: true` is set in the source config, every normal run (no flags) should:

1. Check the most recent auto-pulled file in `source-material/` (by filename date)
2. If the most recent file is older than the shortest `days_back` in the config, run the refresh flow
3. If recent files exist, skip refresh and proceed with generation

This avoids pulling on every single run while keeping content reasonably fresh.

---

## Error Handling

| Error | What to Do |
|-------|-----------|
| Missing env var (`FIREFLIES_API_KEY`, `SLACK_BOT_TOKEN`) | Skip that source, inform user: "Skipping {source} — {ENV_VAR} not found. Set it in your `.env` file." |
| Script not found | Skip that source, inform user: "Skipping {source} — script not found at expected path. Is the {skill-name} skill installed?" |
| API error (rate limit, auth failure) | Skip that source, inform user with the error message. Continue with other sources. |
| No results returned | Skip that source silently — no error, just no new source material from it. |
| OAuth credentials missing (Google Drive) | Skip Drive, inform user: "Skipping Google Drive — OAuth not configured. Run the google-workspace skill setup first." |

**Never let a single source failure block the entire flow.** Pull what you can, skip what you can't, and generate from whatever source material is available.
