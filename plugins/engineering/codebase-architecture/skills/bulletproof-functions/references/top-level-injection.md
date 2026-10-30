# Motivating Example

Consider a function that haphazardly mixes honesty and dishonesty. The goal is to print all permutations of an input string.

```cpp
#include <algorithm>
#include <iostream>
#include <print>
#include <string>

int main() { // framework hook
    std::string input; std::cin >> input; // dishonest
    std::sort(input.begin(), input.end()); // honest
    do {
        std::println("{}", input); // dishonest
    } while (std::next_permutation(input.begin(), input.end())); // honest
}
```

Observe that we can't write a unit test for the loop. All we can do is run the entire program to completion and check the output.

## Solution: Extract the Honest Work

```cpp
auto all_permutations(std::string input) {
    std::sort(input.begin(), input.end()); // honest
    std::vector<std::string> permutations;
    do {
        permutations.push_back(input); // honest
    } while (std::next_permutation(input.begin(), input.end())); // honest
    return permutations;
}

int main() { // framework hook
    std::string input; std::cin >> input; // dishonest
    std::println( // dishonest
        "{}",
        all_permutations(std::move(input)), // honest
    );
}
```

Now we can invoke/test `all_permutations` in isolation. For instance, we can trivially switch the entry point so that it tests for a file stream instead of a console stream. That's the beauty of insulating application-owned resources and stateful external handles at the topmost level while stable standard-library algorithms remain inside the honest work.

## Reuse Caller-Owned Storage

If measured allocation cost matters, a caller may supply reusable output storage. This example receives a vector by value, appends permutations, and returns it. Moving a vector into the call can reuse its capacity; passing an lvalue copies it. This is a move-in/move-out contract, not a mutable-reference out-parameter. Prefer an ordinary return value when caller storage reuse is not required.

```cpp
auto all_permutations(std::vector<std::string> permutations, std::string input) {
    std::sort(input.begin(), input.end()); // honest
    do {
        permutations.push_back(input); // honest
    } while (std::next_permutation(input.begin(), input.end())); // honest
    return permutations;
}
```

## Caller-Controlled Result Handling

A callback lets the caller handle each result without requiring the walker to allocate a collection. The callback is an explicit dependency, but invoking it may perform effects: the walker is not guaranteed pure. Injection does not expose application dependencies hidden inside the callback. Keep valid callback composition; choose a collection, callback, or lazy producer according to the consumption contract and measured costs.

```cpp
template <std::invocable<const std::string&> F>
void for_each_permutation(std::string input, F&& on_permutation) {
    std::sort(input.begin(), input.end()); // honest
    do {
        std::invoke(std::forward<F>(on_permutation), input); // explicit callback invocation; effects depend on its implementation
    } while (std::next_permutation(input.begin(), input.end())); // honest
}

int main() { // framework hook
    std::string input;
    std::cin >> input; // dishonest
    for_each_permutation(std::move(input), [](const auto& permutation) {
        std::println("{}", permutation); // dishonest
    });
}
```

```cpp
// In fact, we can even define `all_permutations` in terms of `for_each_permutation`.
auto all_permutations(std::string input) {
    std::vector<std::string> permutations;
    for_each_permutation(std::move(input), [&](const auto& permutation) {
        permutations.push_back(permutation); // honest
    }); // honest
    return permutations;
}
```

When the algorithm can yield values, a lazy producer lets the caller collect, print, or stop without embedding result handling in the producer. Python and JavaScript have generators; channels and message passing provide a different concurrency contract in Go.

```typescript
function* forEachPermutation(input: string) {
	input = sort(input); // honest
	do {
		yield input; // not a callback, but still inversion of control
	} while (nextPermutation(input)); // honest
}
```
