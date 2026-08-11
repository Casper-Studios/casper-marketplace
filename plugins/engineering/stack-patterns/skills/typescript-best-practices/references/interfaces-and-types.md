# Interfaces and Types

Default handwritten object contracts to `interface`. When composing object shapes, prefer `extends` over `&`: interface relationships are cached, while intersections recursively merge their constituents and require more work during type checking. At scale, `extends` is far cheaper, and it is sufficient for most object composition.

```typescript
interface Identified {
	id: string;
}

interface Named {
	name: string;
}

// BAD: an intersection makes the compiler merge every constituent.
type IntersectedUserRecord = Identified & Named & { createdAt: Date };

// GOOD: extends creates one flat, cacheable object relationship.
interface ExtendedUserRecord extends Identified, Named {
	createdAt: Date;
}
```

Use `type` where `interface` cannot express the contract naturally: structured unions, mapped types, conditional types, primitives, and schema-inferred outputs. Use `const enum` for named closed primitive values.

Do not replace a natural interface with an intersection solely to avoid `extends`.
