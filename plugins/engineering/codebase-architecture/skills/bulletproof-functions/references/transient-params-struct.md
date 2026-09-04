# Motivating Example

Consider a hypothetically opaque `set_timer` function.

```cpp
void set_timer(void*, const string&, float, bool, bool, bool); // what?

int main() {
    set_timer(
        nullptr,
        "id",
        5, // implicit coercion?
        true,
        false, // prone to switch arguments of the same type
        true, // which argument was this again?
    );
}
```

This function has more than three arguments and contains several same-typed flags that callers can easily swap. It therefore satisfies both parameter-object admission conditions.

## Solution: Use a Transient Parameter Object

A cleaner formulation that communicates clearly to a human reader is a **transient parameter object**. The only caveat is to be mindful of ownership semantics when copying/moving values into the transient parameter object.

### Admission Criteria

Consider a transient parameter object only when the function has more than three arguments or at least two bug-prone arguments of the same type that callers can easily swap.

#### More Than Three Arguments

Consider a transient parameter object when a function has more than three arguments. The `set_timer` example crosses this threshold regardless of the individual parameter types.

#### Swappable Same-Typed Arguments

Consider a transient parameter object when at least two arguments share a type and callers can easily swap them by mistake. Shared types alone do not make arguments bug-prone.

#### Hierarchical Positional Arguments

Keep positional arguments when their relationship and order are clearly hierarchical. Put contextual arguments first, followed by operation-specific arguments.

```ts
interface Database {
	insertRedirect(redirectUri: string, randomBytes: Uint8Array): Promise<void>;
}

async function create(database: Database, redirectUri: string) {
	// dishonest orchestration boundary
	const randomBytes = crypto.getRandomValues(new Uint8Array(32));
	await database.insertRedirect(redirectUri, randomBytes);
}
```

The injected `database` resource is contextual, and `redirectUri` is operation-specific. Their order follows that hierarchy. Web Crypto remains direct standard-platform usage rather than another parameter or a member of a dependency bag.

```cpp
struct SetTimerParams {
    void* context;
    std::string id;
    float interval;
    bool should_delay;
    bool should_loop;
    bool can_retrigger;
};

void set_timer(SetTimerParams params);

int main() {
    set_timer(SetTimerParams{
        .context = nullptr,
        .id = "id",
        .interval = 5,
        .should_delay = true,
        .should_loop = false,
        .can_retrigger = true,
    });
}
```

Note that transient parameter objects are analogous to named parameters in languages like Python (via `TypedDict` for `**kwargs`).

```python
from typing import Any

class SetTimerParams(TypedDict):
    context: Any
    id: str
    interval: float
    should_delay: bool
    should_loop: bool
    can_retrigger: bool

set_timer(
    context=None,
    id="id",
    interval=5,
    should_delay=True,
    should_loop=False,
    can_retrigger=True,
)
```

## Important: Not to be Confused for Passing God Classes

This technique should not be confused for the anti-pattern of passing entire class instances as parameters. Not only does this oversubscribe the function's interface (i.e., many fields/methods are irrelevant), but it also implies coupling between the function and the class, which is typically not the intention.

```cpp
void set_timer(const EntireClass& object);
```

The operative keyword here is **transient**. Any caller of any shape should be able to pass named parameters to the function; the parameter object only cares that the values are mapped correctly.
