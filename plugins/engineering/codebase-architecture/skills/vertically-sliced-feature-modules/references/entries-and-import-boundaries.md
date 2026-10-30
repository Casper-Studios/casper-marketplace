# Entries and Import Boundaries

An entry implements or composes one complete operation for its caller. External consumers import the entry; private files import the exact lower implementation they need.

The following TypeScript excerpts omit component props and private implementation leaves:

```typescript
// BAD: the filename creates the appearance of a boundary, but this is only a barrel.
export { TaskFilter } from './view';
export { useTaskFilter } from './query';
export { updateTaskFilter } from './action';
```

```tsx
// GOOD: the entry composes the complete filtering operation exposed to its caller.
export function TaskFilter({ workspaceId }: TaskFilterProps) {
	const filter = useTaskFilter(workspaceId);
	return <TaskFilterView filter={filter} />;
}
```

Do not import an entry from inside its own subsystem. An internal module-root or self-import hides the actual dependency direction and often indicates a barrel. Private files import precise private leaves; callers import the operational entry.

Imports must preserve the recursive boundary:

```text
# GOOD: callers and parents use entries; implementation leaves stay private.
page                 -> task-board/index
task-board/index     -> filter/index
task-board/index     -> edit/index
filter/index         -> filter/query
filter/index         -> filter/view

# BAD: callers and siblings bypass the owning entries.
page                 -X filter/query
edit/title           -X filter/query
filter/query         -X task-board/private-policy
```

A child can import a sibling only through that sibling's operational entry. Repeated, cyclic, or private sibling imports show that composition or ownership is misplaced. Move common behavior to the lowest common owner, or let the parent compose the child entries.

A child can also consume a dependency deliberately owned by an ancestor for several descendants. Give that dependency a clear descendant-facing contract. Do not confuse this lowest-common-owner dependency with the ancestor's private composition state or implementation leaves.

Features remain isolated siblings. A feature entry is a contract for an orchestrator, route, page, application root, or runtime registry; it is not permission for a peer feature to depend on it.

```typescript
// BAD: one feature orchestrates a peer feature.
import { createReceipt } from '@/features/receipt';

export async function submitOrder(input: OrderInput) {
	const order = await persistOrder(input);
	return createReceipt(order);
}
```

```
// GOOD: the application entry composes isolated feature operations.
import { submitOrder } from '@/features/order';
import { createReceipt } from '@/features/receipt';

export async function submitFromPage(input: OrderInput) {
	const order = await submitOrder(input);
	return createReceipt(order);
}
```

Routes and runtime entries can acquire resources, provide framework context, and sequence features. They must not absorb reusable business behavior from the capabilities they compose. Framework-owned server routes can retain authorization, request parsing, transaction coordination, and response construction when those responsibilities belong to the transport boundary.

Recognizable filenames such as `index.ts`, `mod.rs`, `__init__.py`, `page.tsx`, and `+page.svelte` help readers locate entries across ecosystems. Judge the boundary by the operation it provides, not by its filename.
