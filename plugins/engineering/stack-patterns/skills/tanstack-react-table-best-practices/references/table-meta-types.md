# Typed Table Meta

TanStack Table v9 beta supports a per-table metadata slot. Prefer declaring metadata on the table's `features` with `metaHelper` instead of using v8-style global `TableMeta` module augmentation, so each table has only the capabilities its column schema needs.

```typescript
import { metaHelper, tableFeatures } from '@tanstack/react-table';

// BAD: metadata is untyped, so columns cannot safely consume it.
const features = tableFeatures({});

// BAD: use a type assertion to manufacture a metadata slot.
const assertedFeatures = tableFeatures({
	tableMeta: {} as { onEdit?: (id: string) => void },
});

// GOOD: metaHelper creates a type-only, per-table metadata slot.
interface EditableTableMeta {
	onEdit: (id: string) => void;
	onDelete: (id: string) => void;
}

const editableFeatures = tableFeatures({
	tableMeta: metaHelper<EditableTableMeta>(),
});
```

```tsx
function useEditableTable(data: Row[]) {
	function onEdit(id: string) {
		openEditor(id);
	}

	function onDelete(id: string) {
		void deleteRow(id);
	}

	return useTable(
		{ features: editableFeatures, columns, data, meta: { onEdit, onDelete } },
		state => state,
	);
}
```

Make a capability required when every instance of that table schema needs it. Define a separate feature set when another table has a different contract. Do not turn table metadata into application state or a global capability bag.
