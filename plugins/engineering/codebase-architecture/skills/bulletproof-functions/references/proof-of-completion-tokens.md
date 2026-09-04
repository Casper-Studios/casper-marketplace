# Motivating Example

A common scenario in synchronizing external systems involves implicit dependencies between side effector functions.

```rust
// Invocation order matters!
do_first_step();
do_second_step();
```

## Solution: Pass Tokens as Proof of Completion/Validity

Instead of documenting precondtions, impose runtime invariants in the type system by passing zero-sized tokens as proof of completion/validity.

```rust
/// Intentionally zero-sized to avoid any runtime overhead, but can carry payloads if needed.
/// This is a compile-time proof of completion/validity.
struct FirstStepCompletedToken;

fn do_first_step() -> FirstStepCompletedToken {
    todo!()
}

/// Consumes the completion token.
fn do_second_step(_: FirstStepCompletedToken) {
    todo!()
}

fn main() {
    let token = do_first_step(); // receipt
    do_second_step(token); // proof satisfied!
}
```

## Example: Named Lock Guards in Rust and C++

Mutexes serialize resource access, and it's often helpful to encode the critical section as a named lock guard. Such a lock guard can only be obtained by acquiring the lock, thereby enforcing the atomicity of the critical section.

```rust
fn increment(guard: &mut i32) {
    *guard += 1; // only callable with proof of lock acquisition
}

fn main() {
    let mutex = Mutex::new(0);
    let mut guard = mutex.lock().unwrap(); // proof of lock acquisition
    increment(&mut guard); // proof satisfied!
}
```

```cpp
void increment([[maybe_unused]] std::scoped_lock<std::mutex>& lock, int& value) {
    ++value; // only callable with proof of lock acquisition
}

int main() {
    std::mutex mutex;
    int value = 0;
    std::scoped_lock lock(mutex); // proof of lock acquisition
    increment(lock, value); // proof satisfied!
}
```
