# Ownership Promotion

Place behavior at the narrowest owner that contains all of its real production consumers. Promote it only when a broader consumer set proves the broader contract.

```text
# GOOD: consumer scope determines ownership.

# Used only by the title editor.
task-board/edit/title/validation

# Used by several edit operations.
task-board/edit/validation

# Used by filter and edit operations.
task-board/task-policy

# Used by several independent features.
domain/task-policy
```

Use the lowest common owning ancestor before creating a global shared module. A test consumer does not broaden production ownership.

```text
# BAD: familiar technical names become dumping grounds.
shared/
  helpers
  models
  services
  utils

# GOOD: promoted modules name stable cross-feature responsibilities.
domain/
  task-policy
infrastructure/
  database
  provider-api
ui/
  primitives
```

Shared UI primitives, integration transports, persistence infrastructure, protocol models, and cross-feature domain concepts can be valid broader owners. Feature-specific fallback, selection, workflow, and presentation policy stay with the feature.

If one feature needs behavior that belongs to another feature, do not import the owning feature. Promote only the genuinely common behavior, then let both features depend on the lower owner. If the consumers require different policy, keep separate feature-local implementations instead of forcing them behind a generic abstraction.

Do not promote code because it looks reusable. Wait until production consumers prove one stable contract.
