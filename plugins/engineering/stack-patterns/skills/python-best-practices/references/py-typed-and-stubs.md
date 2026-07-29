# Declare Typed Distributions

Include an empty `py.typed` file once at an import package root when a distribution intentionally exposes inline type information.

```text
src/acme_mail/
├── __init__.py
├── client.py
└── py.typed
```

For a namespace package, place `py.typed` inside the concrete subpackage owned by the distribution, not at the shared namespace root.

Use a third-party stub distribution when a runtime dependency lacks complete inline types and precise checking needs its declared API. Do not add `py.typed` to every module, executable-only script package, or an untyped package merely to silence diagnostics.
