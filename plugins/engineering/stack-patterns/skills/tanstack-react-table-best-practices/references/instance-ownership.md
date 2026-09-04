# Instance Ownership

Call row, cell, column, and header methods through their owner. These methods live on shared prototypes, so destructuring or passing one as a bare callback loses its `this` binding.

```typescript
import { tableFeatures, type Row } from '@tanstack/react-table';

interface Person {
	name: string;
}

const features = tableFeatures({});

// BAD: the extracted method has lost the row that supplies its data and caches.
function readNameWithoutOwner(row: Row<typeof features, Person>) {
	const { getValue } = row;
	return getValue('name');
}

// GOOD: call the shared method through the object that owns its state.
function readName(row: Row<typeof features, Person>) {
	return row.getValue('name');
}
```

`useTable(options)` already selects full registered state. Omit the redundant identity selector. Provide a selector only when the component truly needs a narrower selected value.

```tsx
import { rowSelectionFeature, Subscribe, tableFeatures, type Row } from '@tanstack/react-table';

interface Person {
	id: string;
}

const features = tableFeatures({ rowSelectionFeature });

function SelectionCell({ row }: { row: Row<typeof features, Person> }) {
	return (
		<Subscribe source={row.table.atoms.rowSelection} selector={selection => selection[row.id]}>
			{selected => (
				<input
					type="checkbox"
					checked={Boolean(selected)}
					onChange={row.getToggleSelectedHandler()}
				/>
			)}
		</Subscribe>
	);
}
```

Use standalone `Subscribe` with a narrow atom inside row, cell, column, or header render contexts. Use the bound `table.Subscribe` only in a component that owns the React-facing value returned by `useTable`. Do not subscribe solely to force a render and then read unrelated state outside the render prop.

React Compiler can retain nested JSX that receives a stable `row`, `cell`, `column`, or `header` object. Put the subscription inside that nested component and derive its output from the selected value, as above. Continue to use disciplined stable references and memoization; compiler-specific simplification is the caller's choice.
