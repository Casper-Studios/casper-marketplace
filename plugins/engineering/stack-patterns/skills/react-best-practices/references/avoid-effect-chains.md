# Avoid Effect Chains

Do not model one logical operation as a chain of effects that react to each other's state.

```tsx
// BAD: each effect creates another intermediate state boundary.
function BadLoader() {
	const [a, setA] = useState<A>();
	const [b, setB] = useState<B>();

	useEffect(() => {
		void fetchA().then(setA);
	}, []);
	useEffect(() => {
		if (typeof a !== 'undefined') void fetchB(a).then(setB);
	}, [a]);

	return <Result a={a} b={b} />;
}

// GOOD: one operation owns its ordered work.
function Loader() {
	const [state, setState] = useState<LoadState>();

	async function handleLoad() {
		const a = await fetchA();
		const b = await fetchB(a);
		setState({ a, b });
	}

	return <button onClick={() => void handleLoad()}>Load</button>;
}
```

Use a single event handler, query function, or server operation for dependent work. That boundary owns ordering, failure handling, and the final state transition.

Independent server data belongs in separate queries; do not force unrelated requests into a sequential chain.
