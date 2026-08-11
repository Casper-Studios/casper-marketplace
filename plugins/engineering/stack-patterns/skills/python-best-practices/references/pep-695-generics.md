# PEP 695 Generics

Use PEP 695 type parameters in Python 3.13+ for generic declarations. State only the relationship that callers need.

```python
from collections.abc import Callable, Iterable


def first[T](values: Iterable[T]):
    return next(iter(values), None)


def map_values[T, U](values: Iterable[T], transform: Callable[[T], U]):
    return [transform(value) for value in values]
```

Prefer this syntax over module-level `TypeVar` declarations for new code. Do not make a function generic when a concrete type communicates the actual contract.
