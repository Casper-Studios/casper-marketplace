# Explicit over Implicit

Make behavior visible where it occurs. Name decisions and always await promises so control flow and asynchronous completion are explicit. Avoid truthiness, coercion, hidden mutation, ambient state, order dependence, and fallbacks that silently change meaning.

```typescript
interface Configuration {
	timeout?: number;
}

declare const configuration: Configuration;
declare function applyTimeout(timeout: number): void;

// BAD: truthiness hides the decision and rejects a valid zero timeout.
configuration.timeout && applyTimeout(configuration.timeout);

// GOOD: presence controls the branch explicitly.
if (typeof configuration.timeout !== 'undefined') applyTimeout(configuration.timeout);
```

```typescript
declare function saveDraft(): Promise<void>;

// BAD: the callback hides its asynchronous execution behind a returned promise.
const implicitCallbacks = {
	onSave: () => saveDraft(),
};

// GOOD: the callback explicitly awaits the operation's completion.
const callbacks = {
	onSave: async () => {
		await saveDraft();
	},
};
```

Use implicit behavior only when the target language's construct has one obvious meaning and cannot conceal a valid value or failure. Never treat brevity as evidence of clarity.

During review, ask what a reader must know but cannot see at the call site. Put that decision into the code.
