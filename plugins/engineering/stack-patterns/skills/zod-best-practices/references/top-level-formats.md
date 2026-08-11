# Top-Level Format Validators

Use Zod's top-level format validators for string formats. They read clearly and tree-shake to only the formats used by the module.

```typescript
const Endpoint = z.object({
	email: z.email(),
	id: z.uuid(),
	website: z.url(),
});
```

Do not reconstruct a built-in format validator with a custom regular expression unless the protocol defines a different contract.
