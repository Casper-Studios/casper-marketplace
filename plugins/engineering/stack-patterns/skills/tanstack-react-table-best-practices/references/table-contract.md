# Table Contract

Treat column definitions as table schema. Hoist immutable schemas and feature definitions to module scope. When a schema depends on render-local values, build it with `useMemo` and complete dependencies. Declare per-schema capabilities with `metaHelper` and pass their implementations through `meta`.

```tsx
import { createColumnHelper, metaHelper, tableFeatures, useTable } from '@tanstack/react-table';

interface Item {
	id: string;
	name: string;
}

interface ItemTableMeta {
	onEdit(id: string): void;
}

// BAD: an assertion manufactures a metadata slot instead of declaring its contract.
const assertedFeatures = tableFeatures({
	tableMeta: {} as ItemTableMeta,
});

// GOOD: this feature set owns the exact capability consumed by its columns.
const features = tableFeatures({ tableMeta: metaHelper<ItemTableMeta>() });
const columnHelper = createColumnHelper<typeof features, Item>();

// BAD: a new schema is created only to capture per-instance behavior.
function useBadItemTable(data: Item[], onEdit: (id: string) => void) {
	const columns = columnHelper.columns([
		columnHelper.display({
			id: 'actions',
			cell: ({ row }) => <button onClick={() => onEdit(row.original.id)}>Edit</button>,
		}),
	]);

	return useTable({ features, columns, data });
}

// GOOD: schema is static; table meta supplies per-instance capability.
const columns = columnHelper.columns([
	columnHelper.accessor('name', { header: 'Name', cell: info => info.getValue() }),
	columnHelper.display({
		id: 'actions',
		cell: ({ row, table }) => {
			const onEdit = table.options.meta?.onEdit;
			if (typeof onEdit === 'undefined') throw new Error('Item table requires onEdit.');
			return <button onClick={() => onEdit(row.original.id)}>Edit</button>;
		},
	}),
]);

function useItemTable(data: Item[], onEdit: (id: string) => void) {
	return useTable({ features, columns, data, meta: { onEdit } });
}
```

Do not capture changing component values in column definitions merely to reach a cell callback. That forces structural column recomputation; it does not inherently invalidate the whole table. The React Compiler does not change this default: callers can opt into compiler-specific simplifications after they establish that the component is covered.

Rebuild columns only when the schema itself changes. Stabilize other option values that carry identity-sensitive behavior, including derived `data`, callbacks, and objects passed into a memoized child.

Make a capability required when every instance of that schema needs it. Define a separate feature set when another table has a different contract. Reserve declaration merging for a contract deliberately shared by every table in the application; do not turn metadata into application state or a global capability bag.
