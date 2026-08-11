# Loader Prop Contracts

Export the Loader props as the public component contract. Extend one shared capability contract for callbacks used by both layers.

```tsx
// BAD: an Inner contract leaks transport state into presentation.
interface LeakyInnerProps {
	data: JobData | undefined;
	isPending: boolean;
}

// GOOD: Loader identity becomes resolved data at the component boundary.
interface JobDetailActions {
	onAction(id: string): void;
}

export interface JobDetailLoaderProps extends JobDetailActions {
	jobId: string;
}

interface JobDetailInnerProps extends JobDetailActions {
	data: JobData;
}
```

The Loader contract owns query identity. The Inner contract replaces query state with resolved data and retains only caller capabilities it uses.

Do not expose the query result object through either prop contract. Do not export the Inner contract unless direct Inner rendering is a supported module API.

Use `extends` for named object contracts rather than copying callback declarations.
