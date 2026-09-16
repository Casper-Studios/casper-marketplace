# telemetry

Output of `sync.py export`, which publishes this repository's skills to the `claude-telemtery`
Logfire project so the "Casper Skills Usage" dashboard can classify skill usage without a
hand-typed list. The scripts under `.github/scripts/registry-sync/` are a copy of the ones in
casper-secret-sauce; see that repository's README for the full description.

- `casper-skills.json`: generated. Every skill and command here. A pull request that adds or
  renames a skill must regenerate it (`sync.py export --dry-run`); the registry check fails
  otherwise.
