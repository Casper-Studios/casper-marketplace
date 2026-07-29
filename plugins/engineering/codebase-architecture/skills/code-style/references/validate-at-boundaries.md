# Validate at Boundaries

Treat data from users, files, databases with untyped fields, networks, subprocesses, and external libraries without trustworthy type contracts as untrusted. Validate it at the first boundary controlled by the application.

```typescript
// BAD: unchecked structure spreads inward.
const response = await transport.receive();
processStatus(response.items[0].status);

// GOOD: validation produces a trusted value immediately.
const rawResponse: unknown = await transport.receive();
const page = PageSchema.parse(rawResponse);
const [firstItem] = page.items;
if (typeof firstItem === 'undefined') throw new Error('Expected the page to contain an item');
processStatus(firstItem.status);
```

Reject missing fields, extra fields, invalid variants, and incorrect primitive types according to the contract. Do not use permissive containers or casts as substitutes for validation.

After validation, internal code can enforce invariants instead of repeatedly treating trusted values as untrusted. Do not revalidate values already guaranteed by a typed, trusted dependency unless crossing a new trust boundary.
