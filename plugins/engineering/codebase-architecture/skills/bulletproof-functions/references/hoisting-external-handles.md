# Motivating Example

Consider a particle system that requires PRNG-backed particle instantiations for position, velocity, and scale.

```cpp
#include <algorithm>
#include <iterator>

auto ParticleWorld::populate(const size_t count) {
    std::generate_n( // honest
        std::back_inserter(this->particles),
        count,
        []() { // dishonest lambda
            return Particle{
                .position = get_rng().random_vec3(), // dishonest global
                .velocity = get_rng().random_vec3(), // dishonest global
                .scale = get_rng().random_float(), // dishonest global
            };
        },
    );
}

int main() {
    auto seed = get_time(); // dishonest external system
    get_rng() // dishonest global handle
        .seed(seed); // honest seeding

    ParticleWorld world;
    world.populate(100); // dishonest
}
```

Although the PRNG is a deterministic state machine, it is often seeded with a non-deterministic seed like the current timestamp or a cryptographically secure random number. The mutable `get_rng` state is therefore a dishonest global.

## Solution: Hoist the PRNG State to the Topmost Level

Hiding the PRNG state behind a global variable is fundamentally dishonest. Instead, explicitly inject the PRNG state into an honest function.

```cpp
auto ParticleWorld::populate(Random& rng, const size_t count) {
    std::generate_n( // honest
        std::back_inserter(this->particles),
        count,
        [&rng]() { // honest lambda
            return Particle{
                .position = rng.random_vec3(), // honest
                .velocity = rng.random_vec3(), // honest
                .scale = rng.random_float(), // honest
            };
        },
    );
}

int main() {
    auto seed = get_time(); // dishonest
    Random rng{seed}; // or some hard-coded seed for testing!

    ParticleWorld world;
    world.populate(rng, 100); // honest
}
```
