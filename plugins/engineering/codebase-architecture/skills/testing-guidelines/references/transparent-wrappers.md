# Transparent Wrappers

Do not test an HTTP client forwarding request parameters or another wrapper returning a dependency's result unchanged. Test a wrapper only when it adds project-owned behavior beyond delegation.

Mechanical renaming, wrapping, serialization, omission, filtering, or forwarding does not automatically create project-owned behavior. State the invariant without collaborator API details. If the invariant requires method names, command shapes, or response fields owned by the collaborator, the test is describing wiring rather than independent project policy.

```text
// BAD: The test proves forwarding.
given dependency returns value
when wrapper calls dependency
then wrapper returns value
```

```text
// GOOD: The test proves owned policy.
given the provider returns several eligible records
when project selection policy runs
then the newest permitted record is selected
```

If deleting the wrapper would leave the same test against the dependency, delete the test. Also delete the test when changing a configured collaborator result requires changing the expected result mechanically; that expectation is not an independent oracle.
