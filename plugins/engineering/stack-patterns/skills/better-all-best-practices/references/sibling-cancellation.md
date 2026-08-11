# Sibling Cancellation

Use `this.$signal` inside a task when its child operation accepts an `AbortSignal`.

```typescript
const results = await all({
	async download() {
		return await fetch(url, { signal: this.$signal });
	},
});
```

`better-all` aborts each task signal when a sibling task fails. Pass the signal to operations that can stop work. Do not create a second cancellation mechanism for the same graph.
