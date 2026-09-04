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

## Performance Optimization: Out-Parameter Injection

One performance optimization is to use an out-parameter instead of a return value. Allocating a `std::vector` (or any other expensive analogous resource) can be expensive, so it's preferable to defer that decision to the caller.

```cpp
auto all_permutations(std::vector<std::string> permutations, std::string input) {
    std::sort(input.begin(), input.end()); // honest
    do {
        permutations.push_back(input); // honest
    } while (std::next_permutation(input.begin(), input.end())); // honest
    return permutations;
}
```

## Performance Optimization: Dependency Inversion

In the spirit of functional programming, a generalization of the previous technique involves injecting a callback for each intermediate result. The honest walker never allocates a result collection and never prints. The caller injects printing, collection, or test assertions as the callback.

```cpp
template <std::invocable<const std::string&> F>
void for_each_permutation(std::string input, F&& on_permutation) {
    std::sort(input.begin(), input.end()); // honest
    do {
        std::invoke(std::forward<F>(on_permutation), input); // honest: side effects live in the callback
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

In languages like Python and JavaScript, we can instead use generators to `yield` values lazily. In Go, the analogous mechanism involves channels and message passing.

```typescript
function* forEachPermutation(input: string) {
	input = sort(input); // honest
	do {
		yield input; // not a callback, but still inversion of control
	} while (nextPermutation(input)); // honest
}
```
