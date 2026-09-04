# Test Placement

Collocate each unit test with the narrowest leaf that owns the behavior.

```text
# BAD: a feature-level test directory obscures the behavior's actual owner.
features/
  timeline/
    tests/
      calculate-summary.test
    summary/
      calculate-summary
```

```text
# GOOD: the behavior and its unit test share the narrowest owner.
features/
  timeline/
    summary/
      calculate-summary
      calculate-summary.test
```

Calculations, transformations, state transitions, and other sans-I/O behavior stay with the leaf that implements them. Move their tests and leaf-specific fixtures with that implementation during a structural refactor.

Keep a helper with its consumer when its behavior is incidental to that file. Extract a utility file when meaningful project-owned sans-I/O behavior needs a direct colocated test, even with one production consumer. Do not invent tests for trivial glue or promote the utility to shared code until multiple owners require a stable contract.

A test that crosses leaf, feature, persistence, route, process, or external-adapter boundaries is an integration test. Hoist it to the nearest caller, orchestrator, package, or dedicated integration boundary that owns the combined behavior. Do not place it inside one participating feature and imply that the feature owns the other participants.

```text
# BAD: one feature appears to own a cross-feature scenario.
features/
  applications/
    complete-application.integration.test

# GOOD: the composing route owns the integration scenario.
routes/
  application/
    page
    complete-application.integration.test
```

Use a centralized integration suite only when the combined behavior has no narrower orchestrator or when the runtime requires a shared harness. Do not move unit tests into a mirrored central hierarchy.
