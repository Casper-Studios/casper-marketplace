# Finite-State Exhaustiveness

Represent a finite state space with a `Literal`, `Enum`, or discriminated model. Match every member explicitly so a new member becomes a type-checking failure. Do not add a `case _` branch to a `match` that already covers every member.

```python
from typing import Literal

type JobState = Literal["queued", "running", "complete"]


def label(state: JobState):
    match state:
        case "queued":
            return "Waiting"
        case "running":
            return "In progress"
        case "complete":
            return "Done"
```

Configure the type checker to report non-exhaustive `match` statements. Add a `case _` branch only when the matched type is open, such as `str` or `int`, and the remaining values share one defined behavior.
