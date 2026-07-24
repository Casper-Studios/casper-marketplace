---
name: pr-summary
description: Create a PR to provided base branch using the pull request template. Use when opening a new PR.
user-invocable: true
argument-hint: "[base-branch]"
arguments: [base]
---

Summarize the latest changes in this branch to create a pull request on GitHub.

<workflow-steps>

1. Compare the current branch against the base branch to see what changes need to be described in the pull request. Use the `$base` argument if provided, otherwise the repository's default branch (`origin/HEAD`):
   ```bash
   git log "${base:-origin/HEAD}"..HEAD --oneline
   git diff "${base:-origin/HEAD}"...HEAD
   ```
Make sure to only focus on the finalized implementation details. Since pull requests tend to have work-in-progress commits at the beginning, you should be extra mindful on whether these are still relevant in the finalized snapshot.
2. Use the [pull request template](assets/pull-request-template.md) to generate a `.agents/scratchpad/PR.md`.
3. Pause here and prompt the user to check the `.agents/scratchpad/PR.md` before proceeding.
4. Once edited and approved by the user, fill in the missing details in the following script and then run it. With no `$base`, `gh` targets the repository's default branch:
   ```bash
   gh pr create ${base:+--base "$base"} \
     --head "$(git rev-parse --abbrev-ref HEAD)" \
     --title '[TICKET-123] category: short title' \
     --body-file .agents/scratchpad/PR.md
   ```
5. Delete `.agents/scratchpad/PR.md` once successfully submitted.

</workflow-steps>
