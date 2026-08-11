# Catch Narrowly and Chain Meaningfully

Catch only expected exceptions around the operation that can raise them. Add context with `raise ... from error` when the caller needs a domain-specific failure.

```python
from pathlib import Path


# BAD: catches programming errors and unrelated failures from future code.
def load_template_too_broadly(path: Path):
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


# GOOD: catches the expected failure at the operation that raises it.
def load_template(path: Path):
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        raise RuntimeError(f"Could not load template: {path}") from error
```

Do not catch `Exception` to turn unrelated programming failures into ordinary control flow. Do not add a `try` block when a caller can handle the original exception directly.
