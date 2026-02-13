# uv Dependencies

Configuration for FastAPI (Python) backend projects.

## Check Outdated Dependencies

```bash
uv sync --upgrade --dry-run
```

## Upgrade Commands

```bash
# Sync and upgrade all dependencies
uv sync --upgrade

# Add/upgrade a specific package
uv add <package-name>

# Add with version constraint
uv add <package-name>@<version>
```

## Directory

Run from `backend/` directory.
