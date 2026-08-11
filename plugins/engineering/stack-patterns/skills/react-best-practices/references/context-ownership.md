# Context Ownership

Keep props for short, explicit composition paths. Use context when one coherent component subsystem owns shared state or behavior consumed at multiple depths.

```tsx
// BAD: a short composition path does not need ambient state.
function SearchToolbar() {
	const [value, setValue] = useState('');
	return (
		<Toolbar value={value}>
			<FilterInput value={value} onChange={setValue} />
		</Toolbar>
	);
}

// GOOD: a subsystem owns state consumed at several depths.
interface ValueContextValue {
	value: string;
	setValue(value: string): void;
}

const ValueContext = createContext<ValueContextValue | null>(null);

function useValue() {
	const value = useContext(ValueContext);
	if (value === null) throw new Error('useValue must be within ValueProvider');
	return value;
}
```

Forwarding one prop does not justify context. Use an external store only when independent subtrees need the same state or consumers require selective subscriptions.

Keep state and actions in a context boundary that has one coherent owner. Do not use context as a hidden global parameter channel.
