# Test-Level Selection

Choose the lowest test level that can observe the realistic defect named during test admission.

- Use a pure test for project-owned decisions, calculations, state transitions, and transformations. Design the business core as sans-I/O: accept values and events, then return decisions, state transitions, or effect descriptions.
- Use a contract test for compatibility between independently implemented boundaries when the contract can be exercised by both sides.
- Use an integration test for real boundary interpretation, effects, resource lifecycle, enforced constraints, or resulting state.
- Use an interaction test only when invocation, omission, count, or order is itself a stable project-owned observable contract.
- Add no test when the available level cannot meaningfully observe the relevant defect. Record the coverage gap when the behavior still requires protection.

Keep resource acquisition and effects in entry points, drivers, and boundary adapters. When owned policy requires preventing an effect, test the policy directly. Assert omission at the boundary only when non-invocation is itself the owned postcondition.

The absence of a contract or integration harness does not make a test double capable of proving boundary behavior. Do not weaken the claimed evidence to fit the available test infrastructure.

```text
// BAD: a sink assertion cannot prove how the real boundary performs the effect.
given an approved input and a sink double
when the subject runs
then the sink double receives a publish command

// GOOD: the expected decision follows from independently specified policy.
given an input that is eligible and not blocked
when project publication policy runs
then the decision is publish
```

The entry point performs the resulting effect. Test that real effect only at a level that can observe its interpretation or resulting state.
