# Cell Rendering

Render column definitions through the v9 table instance. Never place a header, cell, or footer definition itself in JSX.

```tsx
// BAD: raw definitions are not React children.
function RawCell({ cell }: CellProps) {
	return <td>{cell.column.columnDef.cell}</td>;
}
```

```tsx
// GOOD: delegate definition rendering to the table that owns its generics and context.
function HeaderCell({ table, header }: HeaderCellProps) {
	return <th>{header.isPlaceholder ? null : <table.FlexRender header={header} />}</th>;
}

function BodyCell({ table, cell }: BodyCellProps) {
	return (
		<td>
			<table.FlexRender cell={cell} />
		</td>
	);
}
```

Use the same pattern for a footer definition. Prefer `table.FlexRender` over manually pairing a definition with a context: the instance preserves the schema's generic and feature contract.
