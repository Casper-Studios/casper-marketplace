# Query-Backed Selection

When current query records define the eligible selection and the user can override individual defaults, store only those explicit overrides. Derive visible selection from the current records and overrides; a missing override and an explicit `false` have different meanings.

```tsx
import { useMemo, useState, type ReactNode } from 'react';

interface SelectionDocument {
	id: string;
	isSelected: boolean;
}

interface DocumentPickerProps {
	documents: readonly SelectionDocument[];
	selectedIds: readonly string[];
	onSelect: (id: string, isSelected: boolean) => void;
}

declare function DocumentPicker(props: DocumentPickerProps): ReactNode;

interface DocumentSelectionProps {
	documents: readonly SelectionDocument[];
}

function DocumentSelection({ documents }: DocumentSelectionProps) {
	const [overrides, setOverrides] = useState(() => new Map<string, boolean>());
	const selectedIds = useMemo(() => {
		const selectedIds: string[] = [];
		for (const document of documents) {
			if (overrides.get(document.id) ?? document.isSelected) {
				selectedIds.push(document.id);
			}
		}
		return selectedIds;
	}, [documents, overrides]);

	function select(id: string, isSelected: boolean) {
		setOverrides(previous => new Map(previous).set(id, isSelected));
	}

	return <DocumentPicker documents={documents} selectedIds={selectedIds} onSelect={select} />;
}
```

The current authoritative records determine visibility, so removed records disappear from the derived selection without an effect, query-client subscription, or render-time store write. A temporarily absent paginated row is not deletion unless the feature's contract says so. Place override state at the editor's intended lifetime and reset that owner when its domain identity changes.

Keep absent query collections referentially stable when downstream memoization or subscriptions observe their identity. Reuse an existing stable empty value or memoize the complete derivation; a one-shot local `?? []` needs no identity mechanism.
