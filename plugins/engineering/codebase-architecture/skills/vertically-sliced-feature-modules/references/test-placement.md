# Test Placement

Collocate each unit test with the narrowest leaf that owns the behavior.

```text
# BAD: a feature-level test directory obscures the behavior's actual owner.
features/
  task-board/
    tests/
      calculate-summary.test
    summarize/
      calculate-summary
```

```text
# GOOD: the behavior and its unit test share the narrowest owner.
features/
  task-board/
    summarize/
      calculate-summary
      calculate-summary.test
```

Calculations, transformations, state transitions, and other sans-I/O behavior stay with the leaf that implements them. Move their tests and leaf-specific fixtures with that implementation during a structural refactor.

Keep a helper with its consumer when its behavior is incidental to that file. Extract a utility file when meaningful project-owned sans-I/O behavior needs a direct colocated test, even with one production consumer. Do not invent tests for trivial glue or promote the utility to shared code until multiple owners require a stable contract.

Place a scenario involving several leaves or features at the nearest caller, orchestrator, or package that owns their combined behavior. Classify it by the boundary it observes, not the number of files or helpers it calls. A sans-I/O composition of several helpers can remain a pure test. Real route interpretation, persistence constraints, process behavior, resource lifecycle, or external-adapter effects require suitable contract or integration evidence. Do not place a combined scenario inside one participating feature and imply that it owns the other participants.

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
