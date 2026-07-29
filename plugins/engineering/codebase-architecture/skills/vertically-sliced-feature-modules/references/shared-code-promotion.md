# Shared-Code Promotion

Promote code only after it has multiple real consumers or a stable responsibility independent of its original feature.

```text
# BAD: familiar technical names become dumping grounds.
shared/
  helpers
  models
  services
  utils

# GOOD: shared modules name an owned cross-feature responsibility.
shared/
  ui-primitives
  query-transport
  document-upload
  database
  provider-api
```

Shared UI primitives, integration transports, persistence infrastructure, protocol models, and cross-feature domain concepts are valid technical boundaries. Feature-specific fallback, selection, workflow, and presentation policy remain with the feature.

If one feature needs logic that currently belongs to another feature, do not import the owning feature. Promote the genuinely common logic to a shared module, then let both features depend on that lower boundary.

Do not promote code because it looks reusable. Wait until consumers prove the common contract, then move the shared behavior without making its original feature the hidden owner.

If the consumers require different policy, keep separate feature-local implementations rather than forcing them behind a generic abstraction.
