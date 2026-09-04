# Explicit Capabilities

Register every table capability in `tableFeatures()`. Include the feature, its required row-model factory, and only the named built-in functions that columns reference. This keeps the table contract explicit and preserves tree shaking.

```tsx
import {
	columnFilteringFeature,
	createColumnHelper,
	createFilteredRowModel,
	createSortedRowModel,
	filterFn_includesString,
	rowSortingFeature,
	sortFn_alphanumeric,
	tableFeatures,
	useTable,
} from '@tanstack/react-table';

interface Person {
	name: string;
}

// GOOD: features, row models, and named functions form one explicit capability contract.
const features = tableFeatures({
	columnFilteringFeature,
	filteredRowModel: createFilteredRowModel(),
	filterFns: { includesString: filterFn_includesString },
	rowSortingFeature,
	sortedRowModel: createSortedRowModel(),
	sortFns: { alphanumeric: sortFn_alphanumeric },
});

const columnHelper = createColumnHelper<typeof features, Person>();
const columns = columnHelper.columns([
	columnHelper.accessor('name', {
		filterFn: 'includesString',
		sortFn: 'alphanumeric',
	}),
]);

function PeopleTable({ data }: { data: Person[] }) {
	const table = useTable({ features, columns, data });
	return <div>{table.getRowModel().rows.length}</div>;
}
```

Do not register `filterFns`, `sortFns`, or `aggregationFns` wholesale unless the table intentionally exposes every built-in function. Do not use `stockFeatures` in new code; it hides dependencies and retains features the table does not use.

Use `tableOptions()` to compose reusable option fragments without erasing the schema-specific options at the call site. Use `createTableHook()` for a shared table system with fixed features, defaults, or rendering primitives. Keep state ownership and table-specific `meta` explicit in the consuming schema; do not turn either helper into a global application-table abstraction.
