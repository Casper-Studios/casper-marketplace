# Directory Structure

Organize product code by capability first. Keep technical roles inside the capability that owns them.

```text
# BAD: one feature is scattered across global technical layers.
components/
  application-form
hooks/
  use-application
schemas/
  application
actions/
  submit-application
```

```text
# GOOD: one feature owns its complete presentation workflow.
features/
  applications/
    index
    types
    journey/
      registration/
        index
        form
        validation
      review/
        index
        loader
        content
    calculations
    calculations.test
```

Follow the business journey when a feature has meaningful phases, roles, or states. Let the parent entry select the active phase. Do not flatten phase-specific forms, dialogs, tables, and helpers into broad sibling directories.

The same ownership shape applies to asynchronous use cases:

```text
# GOOD: one worker owns one completed business outcome.
runtime/
  registry
  process-submission/
    index
    schema
    query
    state
    attachment
    attachment.test
```

Technical top-level modules remain valid for genuinely shared infrastructure, external protocols, persistence, and framework runtime boundaries. Do not force feature colocation across separate languages, deployments, packages, or processes.
