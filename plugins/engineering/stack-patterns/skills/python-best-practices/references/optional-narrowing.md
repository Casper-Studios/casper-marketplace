# Narrow Optional Values

Narrow `T | None` before passing it to a required parameter or accessing its members. Keep the failure or absence policy at the layer that owns it.

```python
from typing import cast


# BAD: suppresses the type checker without resolving absence.
def normalize_name_with_cast(name: str | None):
    return cast(str, name).upper()


# GOOD: preserve absence when this operation permits it.
def normalize_name(name: str | None):
    if name is None:
        return
    return name.upper()
```

Use a guard when absence violates the current operation's contract:

```python
def require_name(name: str | None):
    if name is None:
        raise ValueError("Customer name is required.")
    return name
```

Do not use `cast(str, name)` or `name or ""` to evade narrowing.
