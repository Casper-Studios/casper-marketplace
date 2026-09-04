---
name: python-best-practices
description: Python 3.13+ conventions for typed application and library boundaries. Use when writing or reviewing Python contracts, packages, validation, or async resource ownership.
license: MPL-2.0
metadata:
  author: 'Basti Ortiz <ortiz@bastidood.dev>'
  source: 'https://github.com/BastiDood/skills'
---

# Python Best Practices

This skill applies modern Python mechanisms without adding annotation or packaging ceremony. It favors inference, precise structural contracts, explicit runtime validation, side-effect-free imports, and context-managed resource ownership.

## Effective Strategies for Python

Read the linked guidance that governs the current task before writing or reviewing Python.

1. Make type contracts precise without annotation ceremony.
   - Let the checker infer obvious implementation results; add [annotations](./references/inference-and-annotations.md) only when inference cannot express the contract.
   - Depend on the smallest required behavior with [protocols](./references/protocols.md), not a vendor's concrete client.
   - In Python 3.13+, express caller-relevant relationships with [PEP 695 generics](./references/pep-695-generics.md), avoiding module-level `TypeVar` declarations and needless generics.
   - Make a new finite-state member a type-checking failure with [exhaustive handling](./references/finite-state-exhaustiveness.md).
   - Narrow [optional values](./references/optional-narrowing.md) before use so the owning layer—not a cast or fabricated fallback—decides whether absence is preserved or rejected.
2. Validate untrusted data and make invalid states explicit.
   - Parse serialized input once at the controlled [boundary](./references/boundary-validation.md) so untrusted mappings do not spread inward.
   - Do not turn missing required data into a plausible value; [preserve absence or fail](./references/no-fabricated-defaults.md) at the owning boundary.
   - Keep required runtime checks active under optimization; [do not use assertions](./references/no-runtime-asserts.md) for validation.
   - Catch only expected exceptions at the operation that raises them through [narrow exception handling](./references/exception-handling.md).
3. Keep packages explicit, inert, and independently distributable.
   - Keep imports inert and consumer-facing names deliberate with [explicit public exports](./references/public-exports.md).
   - Prevent checkout-dependent imports by following the [Python naming and `src` layout](./references/naming-and-src-layout.md).
   - Publish intentional inline types with [`py.typed`, reserving third-party stubs](./references/py-typed-and-stubs.md) for dependencies that lack complete inline types instead of adding markers merely to silence diagnostics.
   - Give every independently buildable distribution its own declared [metadata](./references/project-metadata.md) and direct dependencies.
   - Make packaging errors visible by [not mutating import paths](./references/no-import-path-mutation.md).
4. Keep asynchronous resource and traversal ownership visible.
   - Make async cleanup inseparable from acquisition with [async context managers](./references/async-context-managers.md).
   - Preserve page boundaries and consumer control over remote traversal through [async pagination](./references/async-pagination.md).
