# Declare Project Metadata Per Distribution

Every independently buildable Python distribution owns its own PEP 517 build-system configuration and PEP 621 project metadata. A monorepo or workspace root does not publish that metadata for child distributions.

```toml
[build-system]
requires = ["uv_build>=0.9,<0.10"]
build-backend = "uv_build"

[project]
name = "acme-mail"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = ["httpx>=0.28"]
```

Declare each direct runtime import in the distribution that uses it. A shared lockfile resolves compatible versions; it does not make another member's dependencies part of this project's contract.
