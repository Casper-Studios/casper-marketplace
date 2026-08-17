# Third-Party Dependencies

Do not test that a library parses, validates, serializes, queries, retries, renders, or raises errors according to its documented contract. A transparent wrapper does not transfer ownership of that behavior to the project.

Replacing a dependency with a test double does not transfer ownership either. Do not recreate a dependency-owned invocation protocol with interconnected doubles and call it compatibility testing. Only a contract or integration test against the independently implemented boundary can establish that compatibility.

```text
// BAD: the tests restate a dependency-owned parsing contract.
given input documented as valid by the dependency
when the dependency parses it
then parsing succeeds

given input documented as invalid by the dependency
when the dependency parses it
then parsing fails
```

The dependency owns both results. Add no test.

When a schema uses project-owned domain logic, extract that logic into a pure predicate or transition and test it directly. Do not use schema parsing as the test harness for business policy.

The same rule applies to:

- A schema library rejecting a missing field.
- An ORM returning mapped records.
- A context manager calling a dependency's close operation.
- A UI primitive rendering the children passed to it.
- A test double returning the value configured on that double.
