# Inferred Task Results

Let `better-all` infer result types from task return values. Do not annotate the result object or duplicate task result interfaces.

```typescript
// BAD: Duplicate Inferred Task Results
interface Results {
	count: number;
	name: string;
	combined: { count: number; name: string };
}

const results: Results = await all({
	async count() {
		return 42;
	},
	async name() {
		return 'test';
	},
	async combined() {
		return { count: await this.$.count, name: await this.$.name };
	},
});
```

The interface repeats the task returns and can drift when a task changes.

```typescript
// GOOD: Keep the Result Type Inferred From the Tasks
const results = await all({
	async count() {
		return 42;
	},
	async name() {
		return 'test';
	},
	async combined() {
		return { count: await this.$.count, name: await this.$.name };
	},
});

// `results.count` is number.
// `results.name` is string.
// `results.combined` is { count: number; name: string }.
```

Give a task an explicit generic or return annotation only when inference lacks information required by its consumer.
