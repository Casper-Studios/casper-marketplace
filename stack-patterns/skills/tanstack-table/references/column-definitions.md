# Column Definition Patterns

## Column Helper

```typescript
import { createColumnHelper } from "@tanstack/react-table";

interface Job {
  id: string;
  name: string;
  status: string;
  createdAt: Date;
}

const columnHelper = createColumnHelper<Job>();
```

## Accessor Columns

```typescript
const columns = [
  // Simple accessor
  columnHelper.accessor("name", {
    header: "Name",
  }),

  // Accessor with custom cell
  columnHelper.accessor("status", {
    header: "Status",
    cell: (info) => <Badge>{info.getValue()}</Badge>,
  }),

  // Accessor with formatting
  columnHelper.accessor("createdAt", {
    header: "Created",
    cell: (info) => format(info.getValue(), "MMM d, yyyy"),
  }),
];
```

## Sortable Headers

```typescript
columnHelper.accessor("name", {
  header: ({ column }) => (
    <button
      className="flex items-center gap-1"
      onClick={() => column.toggleSorting()}
    >
      Name
      {column.getIsSorted() === "asc" ? (
        <ChevronUp className="h-4 w-4" />
      ) : column.getIsSorted() === "desc" ? (
        <ChevronDown className="h-4 w-4" />
      ) : (
        <ArrowUpDown className="h-4 w-4 opacity-50" />
      )}
    </button>
  ),
});
```

## Display Columns (Non-Data)

```typescript
// Actions column
columnHelper.display({
  id: "actions",
  header: () => null,
  cell: ({ row, table }) => (
    <DropdownMenu>
      <DropdownMenuItem
        onClick={() => table.options.meta?.onEdit?.(row.original.id)}
      >
        Edit
      </DropdownMenuItem>
      <DropdownMenuItem
        onClick={() => table.options.meta?.onDelete?.(row.original.id)}
      >
        Delete
      </DropdownMenuItem>
    </DropdownMenu>
  ),
});

// Selection column
columnHelper.display({
  id: "select",
  header: ({ table }) => (
    <Checkbox
      checked={table.getIsAllRowsSelected()}
      onCheckedChange={(checked) => table.toggleAllRowsSelected(!!checked)}
    />
  ),
  cell: ({ row }) => (
    <Checkbox
      checked={row.getIsSelected()}
      onCheckedChange={(checked) => row.toggleSelected(!!checked)}
    />
  ),
});
```

## Accessing Row Data

```typescript
cell: ({ row }) => {
  // Original data
  const job = row.original;

  // Current cell value
  const value = row.getValue("name");

  // Other cell values
  const status = row.getValue("status");

  return <span>{job.name}</span>;
};
```
