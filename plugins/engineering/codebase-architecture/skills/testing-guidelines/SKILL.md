---
name: testing-guidelines
description: Opinionated language-agnostic test-admission and sans-I/O unit-testing rules. Use when proposing, writing, reviewing, or deleting tests; deciding whether behavior is project-owned; rejecting circular test-double fixtures; evaluating wrappers, schemas, ORMs, frameworks, test doubles (e.g., mocks and spies), or third-party-library tests; or separating pure business policy from wiring and I/O.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# Testing Guidelines

This skill treats tests as protection for project-owned behavior, not as a coverage ritual. It favors cheap sans-I/O tests and rejects tests that merely restate test-double configuration, third-party libraries, or transparent wiring.

A meaningful test protects an exact project-owned invariant with an independently derived oracle at a level capable of observing a realistic defect. When the available infrastructure cannot provide that evidence, add no test and record the coverage gap when protection is still required.

## Test Admission

Test behavior that the project owns. Assume third-party libraries are correct and already tested.

Add a test only when it can fail because project-owned behavior is wrong.

Before adding or retaining a test, require all of the following:

- Name the exact project-owned invariant that the test protects.
- Name a realistic defect that violates that invariant and causes the test to fail.
- Derive the expected result independently of test-double configuration.
- Select the test level capable of observing that defect.
- Treat missing contract or integration infrastructure as a coverage gap. Test doubles cannot substitute for that infrastructure.

Project-owned behavior includes:

- Business rules and calculations.
- State-machine transitions and exhaustive decisions.
- Transformations that add domain meaning.
- Selection, retry, fallback, caching, and persistence policy.
- Error translation that adds a stable project contract.

Do not add a test when the implementation only forwards values to a dependency and returns its result unchanged.

## Existing-Test Review

Delete a test when it only:

- Repeats third-party documentation.
- Asserts schema-library mechanics.
- Verifies a one-to-one forwarding wrapper.
- Asserts test-double configuration.
- Checks getters, constructors, or field assignment without behavior.
- Exercises framework plumbing without a project-owned contract.

Do not preserve a useless test for coverage. Coverage is evidence of execution, not evidence of meaningful verification.

## References

Read as many linked references as are relevant to the current task before writing, approving, or retaining tests.

- Do not claim ownership of documented library behavior; treat [third-party dependencies](./references/third-party-dependencies.md) as already verified.
- Exclude tests that only prove delegation through [transparent wrappers](./references/transparent-wrappers.md).
- Reject circular fixtures and substituted-boundary claims with the [test-double admission diagnostics](./references/test-double-admission.md).
- Match each defect to an observable [test level](./references/test-level-selection.md), including no test when the available level cannot provide meaningful evidence.
