# Simple Abstractions

Use the most direct code that preserves the domain model and required behavior. An abstraction must remove real duplication, establish a stable boundary, own a dependency closure or resource lifetime, or give a precise name to a domain concept.

```typescript
// BAD: an invented source contract only packs a query for immediate unpacking.
function buildFileSource(database: Database) {
	return { query: buildFilesQuery(database) };
}

function buildPeopleSource(source: { query: FilesQuery }) {
	return { query: buildPeopleQuery(source.query) };
}

const source = buildPeopleSource(buildFileSource(database));
const query = source.query.as(alias);

// GOOD: compose the existing query contracts directly.
const directQuery = buildPeopleQuery(buildFilesQuery(database)).as(alias);
```

Keep the same contract through adjacent layers when an adapter only packs values for the next layer to unpack. Keep meaningful builders, discriminated state objects, and separate representations that enforce an invariant, change domain meaning, or provide a stable boundary.

One consumer can justify a function that hides meaningful work. Typically, give a utility its own file because its sans-I/O behavior needs a separate colocated test; keep both under their owner. Do not invent tests for trivial glue or promote a utility merely because its test also imports it.

Do not wrap a library only to rename its operations. Do not create a package, manager, provider, model, or exception unless it hides a dependency, enforces a contract, owns a lifecycle, preserves type safety, or gives consumers a smaller stable capability.

Prefer deleting, merging, or simplifying existing code before adding another layer.
