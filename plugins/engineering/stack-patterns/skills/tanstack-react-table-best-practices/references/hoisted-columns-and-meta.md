# Hoisted Columns and Meta

Treat column definitions as table schema. In TanStack Table v9 beta, hoist static schema to module scope and pass per-instance behavior through `meta`.

```tsx
import { createColumnHelper, metaHelper, tableFeatures, useTable } from '@tanstack/react-table';

interface Item {
	id: string;
	name: string;
}

interface ItemTableMeta {
	onEdit(id: string): void;
}

const features = tableFeatures({ tableMeta: metaHelper<ItemTableMeta>() });
const columnHelper = createColumnHelper<typeof features, Item>();

// BAD: a new schema is created only to capture per-instance behavior.
function useBadItemTable(data: Item[], onEdit: (id: string) => void) {
	const columns = columnHelper.columns([
		columnHelper.display({
			id: 'actions',
			cell: ({ row }) => <Button onClick={() => onEdit(row.original.id)}>Edit</Button>,
		}),
	]);

	return useTable({ features, columns, data }, state => state);
}

// GOOD: schema is static; table meta supplies per-instance capability.
const columns = columnHelper.columns([
	columnHelper.accessor('name', { header: 'Name', cell: info => info.getValue() }),
	columnHelper.display({
		id: 'actions',
		cell: ({ row, table }) => {
			const onEdit = table.options.meta?.onEdit;
			if (typeof onEdit === 'undefined') throw new Error('Item table requires onEdit.');
			return <Button onClick={() => onEdit(row.original.id)}>Edit</Button>;
		},
	}),
]);

function useItemTable(data: Item[], onEdit: (id: string) => void) {
	return useTable({ features, columns, data, meta: { onEdit } }, state => state);
}
```

Do not capture changing component values in column definitions merely to reach a cell callback. That forces structural column recomputation; it does not inherently invalidate the whole table.

Rebuild columns only when the schema itself changes.
