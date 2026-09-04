# Motivating Example

An implementation anti-pattern and code smell is when an abstraction digs into the guts of the abstraction layer beneath it rather than its public interface. The pattern looks like "zooming in" the implementation details and then "zooming out" to accomplish the desired functionality.

The following example comically illustrates this pattern for exaggerated effect.

```cpp
bool AssetManager::is_asset_of_type(std::string asset_name, AssetType asset_type) const {
    // Registry only allow lowercase asset names, so normalize as ASCII.
    for (char& c : asset_name)
        if (c >= 'A' && c <= 'Z')
            c += 32;

    // Binary search for the asset in the registry.
    for (auto first = assets.cbegin(), last = assets.cend(); first != last;) {
        const auto mid = first + (last - first) / 2;
        if (mid->name < asset_name)
            first = mid + 1;
        else if (asset_name < mid->name)
            last = mid;
        else
            return mid->type == asset_type;
    }

    // Crash if not found
    std::exit(EXIT_FAILURE);
}
```

## Solution: Breaking into "Indentations" of Abstraction Levels

There are a couple dead giveaways that the function is mixing levels of abstraction:

- Code comments hinting at structural subsystems
- Raw `for` loops with intricate logic
- Doing too much work in a single function body (zoom-in, zoom-out)

### The Same Indentation Rule

Visualize the function as a tree of abstraction levels. Keep the caller at one readable level of intent: it must not inspect another abstraction's implementation to understand the operation. Ordinary control flow is not a separate abstraction level, and comments or loops do not by themselves require extraction.

In the example, a possible decomposition of the sub-problems would be as follows:

- Find the asset in the registry.
  - Normalize the asset name.
    - Convert each character to lowercase.
  - Binary-search for the asset in the registry.
    - Find the lower bound matching the asset name.
    - Check for matches.
- Check for the asset type if found.

```cpp
// In a perfect world, this is the correct abstraction level for `is_asset_of_type`.
// We don't have to care about the guts of the search procedure to understand the functionality.
// If we must dig in, we can rest assured that we land in a lower but same-depth level of abstraction.
bool AssetManager::is_asset_of_type(std::string asset_name, AssetType asset_type) const {
    auto* asset = find_asset(std::move(asset_name));
    if (!asset) std::exit(EXIT_FAILURE);
    return asset->type == asset_type;
}
```

```cpp
// Find the asset in the registry.
auto* AssetManager::find_asset(std::string asset_name) const {
    // Normalize the asset name.
    to_lower_in_place(asset_name);

    // Binary-search for the asset in the registry.
    auto asset = std::lower_bound(assets, asset_name, {}, &Asset::name);
    if (asset == assets.cend() || asset_name < asset->name)
        return nullptr;

    // Note: control flow is fine here, but inspecting the guts of binary search is not.
    // Control flow is not always a license to extract, but a necessary part of the logic.
    return asset;
}

// Convert each character to lowercase.
void to_lower_in_place(std::string& input) {
    ranges::transform(
        input,
        input.begin(),
        [](auto c) {
            return std::tolower(c); // honest
        },
    );
}
```

## Bonus: Recognize Top-Level Data Structures

The long-term solution is to recognize that we've been emulating an ad-hoc data structure instead of imposing a proper top-level data structure. Consider the code smell that future methods in `AssetManager` will need to always remember invoking `to_lower_in_place` on the asset name.

```cpp
auto* AssetManager::find_asset(std::string asset_name) const {
    // Ultimately, we should encapsulate this logic into some `CaseInsensitiveMap<Asset>`.
    // The Same Indentation Rule still applies, but now at the `CaseInsensitiveMap<...>` level.
    return assets_by_name.find(std::move(asset_name));
}
```

Arguably, the `AssetManager::find_asset` method is no longer pulling its weight as a worthwhile function in the private interface now that the `assets_by_name` map field has effectively subsumed its functionality.

```cpp
// The final implementation can therefore be inlined and simplified as follows.
bool AssetManager::is_asset_of_type(std::string asset_name, AssetType asset_type) const {
    auto* asset = assets_by_name.find(std::move(asset_name)); // no more `find_asset` intermediary
    if (!asset) std::exit(EXIT_FAILURE);
    return asset->type == asset_type;
}
```

This illustrates how abstraction is good, but we should equally be cognizant of pruning unworthy abstractions (that should be inlined instead).
