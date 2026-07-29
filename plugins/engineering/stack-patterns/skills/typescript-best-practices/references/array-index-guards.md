# Array Index Guards

With `noUncheckedIndexedAccess: true`, bracket access and array destructuring produce `T | undefined`. Guard before using the value; destructuring does not prove an element exists.

```typescript
// BAD: the indexed value can be undefined.
insertMention(filteredAnalysts[selectedIndex]);

// GOOD: guard narrows the value to T.
const selected = filteredAnalysts[selectedIndex];
if (typeof selected !== 'undefined') insertMention(selected);

// Also guard destructured results.
const [first] = values;
if (typeof first === 'undefined') throw new Error('Expected a first value');
```
