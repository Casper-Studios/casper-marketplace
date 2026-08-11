# Do Not Use Runtime Assertions

Do not use `assert` for input validation, resource availability, or any condition required at runtime. Python can remove assertions under optimization.

```python
# BAD: `python -O` can remove this required runtime check.
def require_with_assert(value, message: str):
    assert value is not None, message
    return value


# GOOD: runtime validation always remains active.
def require[T](value: T | None, message: str):
    if value is None:
        raise RuntimeError(message)
    return value
```

Use a `Never`-typed explicit failure function for exhaustiveness after a closed-state match. Do not use an assertion as runtime validation.
