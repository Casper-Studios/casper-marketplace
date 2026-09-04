# Interaction Semantics

## Selection and Pinning

Use `row.getToggleSelectedHandler()` and `table.getToggleAllRowsSelectedHandler()` directly. Shift-range selection is on by default; disable it with `enableRowRangeSelection: false` only when unwanted.

```typescript
import { rowSelectionFeature, tableFeatures, type Table } from '@tanstack/react-table';

interface Person {
	id: string;
}

const features = tableFeatures({ rowSelectionFeature });

// BAD: "some" means at least one, so this stays true when every row is selected.
function isIndeterminateAtFullSelection(table: Table<typeof features, Person>) {
	return table.getIsSomeRowsSelected();
}

// GOOD: indeterminate means some rows are selected, but not all.
function isIndeterminate(table: Table<typeof features, Person>) {
	return table.getIsSomeRowsSelected() && !table.getIsAllRowsSelected();
}
```

Use `start`/`end` pinning and CSS logical insets so pinning also works with right-to-left text.

## Sort Defaults

When sorting is removed, leave `sorting` empty. If the API needs a default order, derive it without changing table state.

Here, `sorting: SortRule[]` is table state and `setSorting` updates it.

```typescript
const enum SortColumn {
	Name = 'name',
	CreatedAt = 'createdAt',
}

interface SortRule {
	id: SortColumn;
	desc: boolean;
}

const defaultSort = { id: SortColumn.CreatedAt, desc: true } satisfies SortRule;

// BAD: writing the default back prevents clearing the sort.
const nextSorting = sorting.length === 0 ? [defaultSort] : sorting;
setSorting(nextSorting);

// GOOD: use the default for the request, leaving sorting untouched.
const requestSort = sorting[0] ?? defaultSort;
```

Define `defaultSort` where these parameters are built. Keep column IDs typed through the UI and API; do not add casts or runtime parsing. Use TanStack's sorting cycle instead of writing your own.

## Filters and Pagination

For server-side sorting and filtering, send the sort and filter values to the server. Restart pagination when those values change.

These table-option excerpts use `pageRows`, one page returned by the server. Other options are omitted.

```typescript
// BAD: local sorting and filtering can only process this page.
const localOptions = {
	data: pageRows,
	manualSorting: false,
	manualFiltering: false,
};

// GOOD: the server sorts and filters before returning the page.
const serverOptions = {
	data: pageRows,
	manualSorting: true,
	manualFiltering: true,
};
```

Use server totals for complete result counts. `pageRows.length` describes only the loaded page.
