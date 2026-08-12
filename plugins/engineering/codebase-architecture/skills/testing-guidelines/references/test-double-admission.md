# Test-Double Admission

Use these diagnostics before accepting a test whose evidence depends on test doubles.

## Circular Fixture Test

Reject a test when test double A produces `X`, the subject orchestrates collaborators, and the assertion only proves that test double B received `X` or a mechanical representation of `X`. The configured fixture and interaction assertion form a closed loop with no independent evidence.

```text
// BAD: configured output becomes the expectation.
given source double returns X
when subject runs
then sink double receives mechanicallyTransform(X)
```

Move the subject under test to `mechanicallyTransform` when that transformation implements project-owned policy. Extract it from the orchestration, test it as a pure transformation, and derive the expected result from the invariant rather than from either test double.

```text
// GOOD: the transformation is the minimal owned surface.
given X and an independently specified transformation rule
when mechanicallyTransform runs with X
then the result is Y as derived from that rule
```

Do not extract and test a transformation that only reproduces a collaborator-owned command shape. Without an invariant that can be stated independently of the collaborator API, the smaller test still verifies mechanical wiring.

## Boundary Substitution Test

A test double cannot prove how the replaced boundary interprets commands, produces results, performs effects, enforces constraints, manages lifecycle, or changes state. Use the real boundary at the appropriate test level when any of those behaviors is the claimed invariant.

## Independent-Oracle Test

Change the configured collaborator output mentally. If the expectation is obtained by copying or mechanically reshaping that configured output, the test lacks an independent oracle. Derive the expected result separately from project policy, an independently specified project-owned contract, or an observable real-boundary outcome. A collaborator-owned command or response shape is not an independent oracle.

## Observable-Outcome Test

Mentally remove every interaction assertion. If no meaningful project-owned postcondition remains, the test verifies wiring.

## Narrow Interaction Exception

Invocation, omission, count, or order may be asserted only when that interaction is itself a stable project-owned contract, not merely the current implementation path.

## Replacement Choices

Replace a rejected test with exactly the evidence the invariant requires:

- A pure test for independently specified project policy, including an extracted transformation that is the minimal project-owned surface hidden inside orchestration.
- A contract or integration test for real boundary compatibility, interpretation, effects, lifecycle, constraints, or resulting state.
- No test, with the coverage gap recorded when protection is still required but the harness is absent.
- Deletion when the existing test is misleading and protects no project-owned invariant.
