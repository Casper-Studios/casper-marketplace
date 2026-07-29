---
name: testing-guidelines
description: Opinionated language-agnostic test-admission and sans-I/O unit-testing rules. Use when proposing, writing, reviewing, or deleting tests; deciding whether behavior is project-owned; evaluating wrapper, schema, ORM, framework, mock, or third-party-library tests; or separating pure business policy from wiring and I/O.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# Testing Guidelines

This skill treats tests as protection for project-owned behavior, not as a coverage ritual. It favors cheap sans-I/O tests and rejects tests that merely restate third-party libraries or transparent wiring.

## Test Admission

Test behavior that the project owns. Assume third-party libraries are correct and already tested.

Add a test only when it can fail because project-owned behavior is wrong.

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
- Asserts mock configuration.
- Checks getters, constructors, or field assignment without behavior.
- Exercises framework plumbing without a project-owned contract.

Do not preserve a useless test for coverage. Coverage is evidence of execution, not evidence of meaningful verification.

## References

Read as many linked references as are relevant to the current task before writing, approving, or retaining tests.

- Do not claim ownership of documented library behavior; treat [third-party dependencies](./references/third-party-dependencies.md) as already verified.
- Exclude tests that only prove delegation through [transparent wrappers](./references/transparent-wrappers.md).
- Prove project-owned policy through cheap [sans-I/O tests](./references/sans-io-and-wiring-tests.md), adding wiring coverage only for owned boundary behavior.
