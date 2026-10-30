# Indexed Access and Destructuring

With `noUncheckedIndexedAccess` enabled, unchecked array and index-signature reads include `undefined`. Destructuring retains that uncertainty; it does not prove that an element or property exists. Narrow a required value before passing it to its consumer.

```typescript
declare function useLabel(label: string): void;

// BAD: destructuring does not establish the required-string contract.
const [first] = labels;
useLabel(first);
```

```typescript
// GOOD: fail when a required value is absent, then use the narrowed value.
const [first] = labels;
if (typeof first === 'undefined') throw new Error('Expected a first label');
useLabel(first);

// GOOD: when absence is expected, handle only a present indexed value.
const selected = labels[selectedIndex];
if (typeof selected !== 'undefined') useLabel(selected);

// GOOD: the same rule applies when destructuring an index-signature object.
const { primary } = labelsByRole;
if (typeof primary !== 'undefined') useLabel(primary);
```

Preserve absence in the consumer's state or result contract when it is expected. Do not invent an empty-string fallback, use truthiness that rejects valid empty strings or zeroes, or assert presence with `!`. Keep checks where the inferred type admits absence; known tuple elements and required object properties do not need artificial guards.
