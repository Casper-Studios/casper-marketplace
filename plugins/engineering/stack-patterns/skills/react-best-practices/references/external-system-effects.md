# External-System Effects

Default to no effect. Treat `useEffect` as an escape hatch used only to synchronize React with a system that React does not control.

An effect is data-reactive: React reruns it because a synchronization input changed. An event handler is event-based: it runs because a discrete event occurred. Do not call event handling effect handling, and do not route an event through state so an effect can react to it.

```tsx
// BAD: a click is an event, not a synchronization input.
function BadDraftButton() {
	const [shouldSave, setShouldSave] = useState(false);
	useEffect(() => {
		if (shouldSave === true) void saveDraft();
	}, [shouldSave]);
	return <button onClick={() => setShouldSave(true)}>Save</button>;
}

// GOOD: synchronize a real external resource with reactive input.
function Messages({ url }: { url: string }) {
	const [messages, setMessages] = useState<string[]>([]);
	useEffect(() => {
		const socket = new WebSocket(url);
		socket.onmessage = event => setMessages(previous => [...previous, event.data]);
		return () => socket.close();
	}, [url]);
	return <MessageList messages={messages} />;
}
```

Valid external systems include subscriptions, browser APIs, DOM measurement, and third-party widgets that require a DOM node.

The effect must return cleanup for every acquired subscription or resource. Keep its dependency list aligned with the synchronization inputs.

React Strict Mode can run a development setup-cleanup-setup cycle before the component's first real mount. Make every effect setup and cleanup idempotent as a pair. Do not suppress the second setup with a ref; fix the resource ownership so cleanup makes a subsequent setup safe.

```tsx
// BAD: the ref hides Strict Mode's setup/cleanup check and risks a leaked resource.
function BadAnalytics() {
	const initialized = useRef(false);
	useEffect(() => {
		if (initialized.current === true) return;
		initialized.current = true;
		startAnalytics();
	}, []);
	return null;
}

// GOOD: mount-scoped setup has matching cleanup and tolerates development re-entry.
function Analytics() {
	useEffect(() => {
		const analytics = startAnalytics();
		return () => analytics.stop();
	}, []);
	return null;
}
```

Use an empty dependency list only for a resource owned by the component's mount lifetime. Include every reactive synchronization input when the resource must follow changing props or state.

Do not use an effect for derivation, user-initiated work, server-state loading, or state reset. Those concerns have their own boundaries.

Before adding an effect, identify the external system and the reactive value that must remain synchronized with it. If neither exists, do not add the effect.

Keep an effect scoped to one external synchronization concern. Split unrelated subscriptions so each setup, dependency list, and cleanup path stays independently correct.

Do not suppress dependency diagnostics to force an effect to run less often. Restructure the synchronization inputs instead.
