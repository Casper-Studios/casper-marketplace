# Regular Expression Capture Groups

Treat named and positional regular-expression captures as optional. Validate a required capture before assigning it to a required domain field.

```typescript
// BAD: either expression can be undefined.
content: match.groups?.name ?? match[1];

// GOOD: preserve absence until the operation establishes its invariant.
const content = match.groups?.name ?? match[1];
if (typeof content === 'undefined')
	throw new Error('Expected the regular expression to capture content');
```

Do not replace a missing capture with an arbitrary empty value.
