# Meta Field Pattern

## Type-Safe Meta Extension

```typescript
import { RowData } from "@tanstack/react-table";

declare module "@tanstack/react-table" {
  interface TableMeta<TData extends RowData> {
    // Optional to avoid affecting other tables
    onEdit?: (id: string) => void;
    onDelete?: (id: string) => void;
    onSelect?: (id: string, selected: boolean) => void;
    isLoading?: boolean;
  }
}
```

## Passing Meta to Table

```typescript
function JobsTable({ data, onEdit, onDelete }: Props) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    meta: {
      onEdit,
      onDelete,
    },
  });

  return <Table>...</Table>;
}
```

## Accessing Meta in Cells

```typescript
columnHelper.display({
  id: "actions",
  cell: ({ row, table }) => {
    const meta = table.options.meta;

    return (
      <div>
        <Button onClick={() => meta?.onEdit?.(row.original.id)}>
          Edit
        </Button>
        <Button
          onClick={() => meta?.onDelete?.(row.original.id)}
          disabled={meta?.isLoading}
        >
          Delete
        </Button>
      </div>
    );
  },
});
```

## Accessing Meta in Headers

```typescript
columnHelper.accessor("name", {
  header: ({ table }) => {
    const meta = table.options.meta;
    return (
      <div className="flex items-center">
        Name
        {meta?.isLoading && <Spinner className="ml-2" />}
      </div>
    );
  },
});
```

## Why Optional Fields?

```typescript
// TableMeta is global - affects ALL tables
interface TableMeta<TData extends RowData> {
  onEdit?: (id: string) => void;  // Optional!
}

// Tables that don't need onEdit aren't forced to provide it
const simpleTable = useReactTable({
  data,
  columns: simpleColumns,
  // No meta needed
});

// Tables that need callbacks provide them
const editableTable = useReactTable({
  data,
  columns: editableColumns,
  meta: { onEdit: handleEdit },
});
```

## Complex Meta Types

```typescript
interface TableMeta<TData extends RowData> {
  // Simple callbacks
  onEdit?: (id: string) => void;

  // Callbacks with data
  onUpdate?: (id: string, data: Partial<TData>) => void;

  // State
  editingId?: string | null;
  isLoading?: boolean;

  // Functions returning values
  getRowClassName?: (row: TData) => string;
}
```
