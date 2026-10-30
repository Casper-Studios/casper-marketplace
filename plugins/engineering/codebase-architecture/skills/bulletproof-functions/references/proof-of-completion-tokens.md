# Motivating Example

A common scenario in synchronizing external systems involves implicit dependencies between side effector functions.

```rust
// Invocation order matters!
do_first_step();
do_second_step();
```

## Solution: Pass Tokens as Proof of Completion/Validity

Instead of documenting preconditions, impose runtime invariants in the type system by passing tokens as proof of completion/validity. A token can be zero-sized when the proof needs no associated data. When the proof concerns a particular resource, carry that resource's borrow so the token cannot be used with another resource or outlive its owner.

```rust
mod workflow {
    use std::io::{self, Write};

    /// Private construction keeps callers from forging the receipt.
    pub struct FirstStepCompletedToken<'a> {
        output: &'a mut dyn Write,
    }

    pub fn do_first_step(output: &mut dyn Write) -> io::Result<FirstStepCompletedToken<'_>> {
        output.write_all(b"BEGIN\n")?;
        Ok(FirstStepCompletedToken { output }) // Issue the receipt only after success.
    }

    /// Consumes the completion token and uses the same prepared writer.
    pub fn do_second_step(token: FirstStepCompletedToken<'_>) -> io::Result<()> {
        token.output.write_all(b"END\n")
    }
}

fn main() -> std::io::Result<()> {
    let mut output = Vec::new();
    let token = workflow::do_first_step(&mut output)?; // receipt
    workflow::do_second_step(token)?; // proof satisfied!
    Ok(())
}
```

The token proves that the first write succeeded. The second write can still fail, so its result remains fallible. Consuming the token prevents reusing the same receipt for another second step.

## Example: Named Lock Guards in Rust and C++

Mutexes serialize resource access, and it's often helpful to encode the critical section as a named lock guard. Rust's mutex guard carries access to the protected value, so the function can require that guard instead of accepting an arbitrary mutable reference.

```rust
use std::sync::{Mutex, MutexGuard};

fn increment(guard: &mut MutexGuard<'_, i32>) {
    **guard += 1; // The value is reached through its acquired lock.
}

fn main() {
    let mutex = Mutex::new(0);
    let mut guard = mutex.lock().unwrap(); // proof of lock acquisition
    increment(&mut guard); // proof satisfied!
}
```

In C++, keep the mutex and protected value with the same owner. Acquiring a lock and passing it alongside an unrelated `int&` would not prove that the lock protects that value.

```cpp
#include <mutex>

class Counter {
    std::mutex mutex;
    int value = 0;

public:
    void increment() {
        std::scoped_lock lock(mutex); // proof of lock acquisition
        ++value; // This owner's mutex protects this owner's value.
    }
};

int main() {
    Counter counter;
    counter.increment();
}
```
