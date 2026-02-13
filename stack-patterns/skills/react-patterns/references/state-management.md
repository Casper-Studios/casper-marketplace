# State Management Patterns

## Derived Values Over State

Avoid state variables when values can be derived:

```tsx
// Bad - unnecessary state
const [fullName, setFullName] = useState('');
useEffect(() => {
	setFullName(`${firstName} ${lastName}`);
}, [firstName, lastName]);

// Good - derived value
const fullName = `${firstName} ${lastName}`;
```

## Component Boundaries

Scope state to the smallest subtree that needs it:

```tsx
// Bad - state too high
function Dialog() {
	const [formData, setFormData] = useState({});
	return (
		<DialogContent>
			<Form data={formData} onChange={setFormData} />
		</DialogContent>
	);
}

// Good - state in conditional subtree
function Dialog() {
	return (
		<DialogContent>
			<FormWithState />
		</DialogContent>
	);
}

function FormWithState() {
	const [formData, setFormData] = useState({});
	return <Form data={formData} onChange={setFormData} />;
}
```

## Context API for Sibling Sharing

When props would only be forwarded (not used), use Context:

```tsx
const ValueContext = createContext<{ value: string; setValue: (v: string) => void } | null>(null);

function Provider({ children }: { children: ReactNode }) {
	const [value, setValue] = useState('');
	const ctx = useMemo(() => ({ value, setValue }), [value]);
	return <ValueContext.Provider value={ctx}>{children}</ValueContext.Provider>;
}

function useValue() {
	const ctx = useContext(ValueContext);
	if (!ctx) throw new Error('useValue must be within Provider');
	return ctx;
}
```

## Atomic Context Pattern

One useState per context for atomicity:

```tsx
function AtomicProvider({ init, children }: Props) {
	const [state, setState] = useState(init);
	const derived = useMemo(() => compute(state), [state]);
	const action = useCallback(() => setState(old => transform(old)), [transform]);
	const value = useMemo(() => ({ state, derived, action }), [state, derived, action]);
	return <Context.Provider value={value}>{children}</Context.Provider>;
}
```

## Zustand for Complex State

When Context is unwieldy:

```typescript
import { create } from 'zustand';

interface State {
	items: Item[];
	addItem: (item: Item) => void;
	removeItem: (id: string) => void;
}

export const useStore = create<State>(set => ({
	items: [],
	addItem: item => set(state => ({ items: [...state.items, item] })),
	removeItem: id =>
		set(state => ({
			items: state.items.filter(i => i.id !== id),
		})),
}));

// Use selectors to prevent unnecessary re-renders
const items = useStore(state => state.items);
const addItem = useStore(state => state.addItem);
```

## State Machine Over Multiple useState

```tsx
// Bad - multiple related states
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState<Error | null>(null);
const [data, setData] = useState<Data | null>(null);

// Good - discriminated union
type State =
	| { status: 'idle' }
	| { status: 'loading' }
	| { status: 'error'; error: Error }
	| { status: 'success'; data: Data };

const [state, setState] = useState<State>({ status: 'idle' });
```
