# No Fabricated Defaults

Do not replace missing required information with an invented value, arbitrary first item, empty collection, sentinel, or silent fallback. Preserve absence when it is valid. Fail explicitly when it violates the contract.

```typescript
// BAD: missing data becomes plausible but false data.
const timeout = configuration.timeout ?? 30;
const selected = items.find(item => item.id === id) ?? items[0];

// GOOD: absence remains part of the decision.
if (typeof configuration.timeout === 'undefined') return configurationMissing('timeout');

const selectedItem = items.find(item => item.id === id);
if (typeof selectedItem === 'undefined') throw new Error(`Selected item must exist: ${id}`);
```

Use a default only when the domain contract defines that exact default. Place it at the boundary that owns the policy and name it so consumers can see the decision.

Do not use defaults to satisfy a type checker, simplify control flow, or conceal an incomplete migration.
