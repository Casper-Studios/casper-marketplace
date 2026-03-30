---
name: modals
description: Modal component patterns using ShadCN Dialog with tRPC mutations
user-invocable: false
---

# Modal Components

## Overview
Modal components follow a consistent pattern using ShadCN Dialog components with tRPC mutations for data operations.

## File Naming
Use the naming pattern `{feature}-modal.tsx` (e.g., `edit-user-modal.tsx`, `create-item-modal.tsx`)

## Props Interface Pattern
```typescript
interface FeatureModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
  entityId?: string;
  mode?: "create" | "edit";
}
```

## Component Structure
```typescript
import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { api } from "@/trpc/client";
import { toast } from "sonner";

export function FeatureModal({ open, onOpenChange, entityId, onSuccess }: FeatureModalProps) {
  // 1. Local form state
  const [fieldValue, setFieldValue] = useState("");

  // 2. tRPC utilities for cache invalidation
  const utils = api.useUtils();

  // 3. Query for existing data (if editing)
  const { data, isLoading } = api.route.getData.useQuery(
    { entityId },
    { enabled: open && !!entityId }
  );

  // 4. Effect to populate form when data loads
  useEffect(() => {
    if (open && data) setFieldValue(data.field ?? "");
  }, [open, data]);

  // 5. Effect to reset form when modal closes
  useEffect(() => {
    if (!open) setFieldValue("");
  }, [open]);

  // 6. Mutation
  const mutation = api.route.save.useMutation({
    onSuccess: () => {
      toast.success("Saved successfully");
      utils.route.getData.invalidate();
      onOpenChange(false);
      onSuccess?.();
    },
    onError: (error) => toast.error(error.message || "Failed to save"),
  });

  // 7. Submit handler
  const handleSave = async () => {
    await mutation.mutateAsync({ entityId, field: fieldValue.trim() });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]" data-testid="feature-modal">
        <DialogHeader><DialogTitle>Modal Title</DialogTitle></DialogHeader>
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="size-6 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <div className="flex flex-col gap-4">{/* Form fields */}</div>
        )}
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={mutation.isPending}>Cancel</Button>
          <Button onClick={handleSave} disabled={mutation.isPending}>
            {mutation.isPending ? (<><Loader2 className="size-4 animate-spin mr-2" />Saving...</>) : "Save"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
```

## Key Patterns
- Show spinner when fetching existing data
- Disable buttons when mutation is pending
- Use `useState` for form fields, populate from query data in `useEffect`
- Reset form state when modal closes
- Call `utils.routeName.queryName.invalidate()` after successful mutation
- Add `data-testid` to modal content and important elements
- Use `toast.error()` in mutation `onError` callback

## Multi-Purpose Modals
```typescript
interface MultiPurposeModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  mode: "create" | "edit";
}
export function MultiPurposeModal({ mode, ...props }: MultiPurposeModalProps) {
  const title = mode === "edit" ? "Edit Item" : "Create Item";
  const buttonText = mode === "edit" ? "Save" : "Create";
}
```
