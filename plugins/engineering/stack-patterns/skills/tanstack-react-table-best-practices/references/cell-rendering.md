# Cell Rendering

Render column definitions through the table instance. Never place a header, cell, or footer definition itself in JSX.

```tsx
import { tableFeatures, type Cell, type ReactTable, type TableState } from '@tanstack/react-table';

interface Person {
	name: string;
}

const features = tableFeatures({});

interface CellProps {
	cell: Cell<typeof features, Person, unknown>;
	table: ReactTable<typeof features, Person, TableState<typeof features>>;
}

// BAD: coercing the definition renders schema data or function source, not the cell result.
function RawCell({ cell }: CellProps) {
	return <td>{String(cell.column.columnDef.cell)}</td>;
}

// GOOD: the owning table supplies the cell context and preserves feature-local types.
function BodyCell({ cell, table }: CellProps) {
	return (
		<td>
			<table.FlexRender cell={cell} />
		</td>
	);
}
```

Apply the same pattern to headers and footers. Suppress placeholder headers before rendering them.
