# Package Admission

A feature module and an independently buildable package solve different problems. Create a package only for a meaningful dependency, build, deployment, or runtime closure.

Application entry points own composition, process lifetime, and product-specific feature modules. One application can own many vertical features when they share one product runtime and dependency closure. Do not create one package per feature for organizational symmetry.

Scripted entry points own one-shot, scheduled, administrative, migration, and other operational invocations. Keep reusable behavior below those entry points in an owning application module or independent library.

Importable libraries must be independently self-contained. A library package is not merely a shared source directory or a convenient place for code used by an entry point.

```text
# GOOD: one possible repository convention makes these roles visible.

apps/
  web/
    features/
      applications/
      reporting/
      administration/

packages/
  environment/
  database/
  provider-api/

scripts/
  synchronize-models/
```

The directory names in this example are illustrative. Follow the repository's established naming convention while preserving the distinction between executable composition and independent importable ownership.

An admitted library package must:

- Own a cohesive capability independent of the application.
- Declare every dependency it imports directly.
- Avoid importing the application or feature-private types.
- Expose a narrow consumer contract.
- Build and install from its own project root.
- Own its source, tests, package data, and runtime resources.

Entry points depend downward on the independent libraries they use. Libraries never import entry-point projects. Shared workspace resolution does not erase package ownership or make an incomplete package self-contained.
