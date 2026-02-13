# Source Material

Shared content that ships with the plugin. The LinkedIn Post Generator reads all `.md` files in this directory (except this README) during post generation.

## What goes here

- Meeting transcripts
- Slack exports / dumps
- Document summaries or notes
- Any raw content you want to generate posts from

## Adding source material

**Via command:** Run `/casper:generate-linkedin-post --add-source` and paste content interactively.

**Manually:** Drop `.md` files into this directory. Use descriptive kebab-case filenames (e.g., `team-retro-jan-2025.md`, `client-kickoff-notes.md`).

## Confidentiality

Source material may contain sensitive details — the skill applies strict confidentiality rules during generation and will never surface client names, financials, deal sizes, or team member names in output. That said, avoid committing source material with highly sensitive information to shared repos when possible.
