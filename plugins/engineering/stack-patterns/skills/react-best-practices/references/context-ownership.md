# Context Ownership

Keep props for short, explicit composition paths. Use context when one coherent subsystem owns state or behavior consumed at multiple depths, rather than to hide ordinary prop forwarding.

Component excerpts:

```tsx
// BAD: a context exists only to forward one value to one direct child.
const SessionContext = createContext<Session | null>(null);

function BadToolbar({ session }: ToolbarProps) {
	return (
		<SessionContext value={session}>
			<Toolbar />
		</SessionContext>
	);
}

// GOOD: the direct dependency stays visible.
function SessionToolbar({ session }: ToolbarProps) {
	return <Toolbar session={session} />;
}
```

Create context around a coherent multi-depth subsystem and validate its provider boundary when absence is invalid. An external store earns its place when independent subtrees share state or consumers need selective subscriptions; reuse the project's instance/provider pattern and intended lifetime.

Existing selector-hook excerpts:

```tsx
// BAD: the consumer subscribes to the entire store before selecting fields.
const { selectedIds } = useDocumentSelection();

// GOOD: the consumer subscribes only to what it uses.
const selectedIds = useDocumentSelection(state => state.selectedIds);
```

Keep selectors narrow through convenience hooks instead of returning the whole store for later destructuring. Preserve separate subscriptions for unrelated state and stable actions. A count of actions alone does not require a store.
