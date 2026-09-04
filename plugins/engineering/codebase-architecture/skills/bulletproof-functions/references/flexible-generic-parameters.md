# Motivating Example

Empathetic functions show consideration for the caller by minimizing the constraints/preconditions that it imposes on the caller.

```cpp
// This is a bad example because it unnecessarily imposes order and contiguity constraints on the caller.
// Worse: the signature incorrectly imposes that a dynamically sized container is necessary (when it's not).
// It's not fair for this function to dictate those constraints on the caller!
void iterate_values(const std::vector<int>& values) {
    for (const auto& value : values) {
        // We honestly only just care about iterating in general.
    }
}

int main() {
    // What if I have a statically allocated array of values instead?
    std::array<int, 3> values{1, 2, 3};
    iterate_values(values); // compile error!
}
```

## Solution: Allowing Any Contiguous Sequence

```cpp
// This is better because type erasure allows any array-like contiguous sequence.
void iterate_values(const std::span<const int> values) {
    for (const auto& value : values) {
        // ...
    }
}
```

## Solution: Allowing Any Iterator

The previous solution still fails on unordered collections like `std::set`. If the purpose of `iterate_values` is to simply iterate over values, then imposing contiguity is not empathetic enough.

```cpp
// Now this is the most flexible solution. Only constrain according to the bare necessities.
void iterate_values(RangeOf<int> const auto& values) {
    for (const auto& value : values) {
        // ...
    }
}
```

## When to Impose Stronger Guarantees

If the abstraction genuinely requires stronger guarantees, the interface shouldn't be shy to impose them. The key guidance is to reflect on the bare necessities.
