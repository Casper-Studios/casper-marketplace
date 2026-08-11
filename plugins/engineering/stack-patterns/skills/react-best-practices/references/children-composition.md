# Children Composition

Use `ReactNode` for passive content that the component places in its layout.

```tsx
import type { ReactNode } from 'react';

// BAD: static content does not need a behavior callback.
function BadNotice() {
	return <Panel>{() => <p>Saved</p>}</Panel>;
}

// GOOD: ordinary children express passive layout content.
interface PanelProps {
	children: ReactNode;
}

function Panel({ children }: PanelProps) {
	return <section className="rounded border p-4">{children}</section>;
}
```

Use a typed render prop only when the parent must provide behavior or state to the child.

```tsx
// GOOD: use a render callback only when the child needs owner-provided behavior.
interface ToggleProps {
	children(state: { isOpen: boolean; toggle(): void }): ReactNode;
}
```

Do not use a render prop for static markup. Do not accept both ordinary children and a render callback for the same slot unless the API defines two genuinely distinct composition modes.

Require `children` when the component is meaningless without content. Mark it optional only when an empty composition is valid.
