# Inference and Necessary Annotations

Strongly prefer inferred return types. Omit a return annotation whenever the implementation and type checker already communicate the precise result, including for ordinary public functions.

Annotate parameters because the implementation cannot infer the caller contract from their use. Annotate empty collections and other values whose intended type cannot be inferred accurately.

```python
from collections.abc import Iterable


def total(values: Iterable[int]):
    return sum(values)


names = list[str]()
record = {"id": "acct_123", "active": True}
```

Do not annotate an obvious local merely to repeat the initializer:

```python
count = len(names)
```

An explicit return annotation is an exception. Add one when:

- A declaration has no implementation to infer, such as a `Protocol` member or overload.
- Recursion prevents reliable inference.
- A `Never` return is part of an exhaustiveness contract.
- A decorator or generator API requires an explicit yielded-value contract.
- Inference loses an intentional abstraction, union, or generic relationship.

Do not annotate an obvious return merely because the function is public.
