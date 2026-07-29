# Finite-State Exhaustiveness

Represent a finite state space with a `Literal`, `Enum`, or discriminated model. Pass the unmatched value to a `Never`-typed failure function so a new member becomes a type-checking failure.

```python
from typing import Literal, Never

type JobState = Literal["queued", "running", "complete"]


# BAD: a new state silently inherits an unrelated label.
def label_with_fallback(state: JobState):
    if state == "queued":
        return "Waiting"
    return "Done"


# GOOD: the type checker rejects an unmatched state.
def label(state: JobState):
    match state:
        case "queued":
            return "Waiting"
        case "running":
            return "In progress"
        case "complete":
            return "Done"
        case _:
            raise RuntimeError("Unhandled state")
```

The type checker rejects the `Never` assignment when a newly added state lacks a case. The runtime failure remains active under optimization.
