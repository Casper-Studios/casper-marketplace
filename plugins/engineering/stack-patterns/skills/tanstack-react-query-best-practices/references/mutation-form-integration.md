# Mutation Form Integration

Decode and parse user-controlled form input before invoking a mutation.

```tsx
import { decode } from 'decode-formdata';
import * as v from 'valibot';

// BAD: the mutation receives form transport data.
function BadJobForm() {
	const mutation = useMutation({ mutationFn: updateJob });

	function onSubmit(event: React.FormEvent<HTMLFormElement>) {
		event.preventDefault();
		mutation.mutate(decode(new FormData(event.currentTarget)));
	}

	return <form onSubmit={onSubmit} />;
}

// GOOD: the form boundary parses domain variables before mutation work.
function JobForm() {
	const mutation = useMutation({ mutationFn: updateJob });

	function onSubmit(event: React.FormEvent<HTMLFormElement>) {
		event.preventDefault();
		const input = v.parse(updateJobInput, decode(new FormData(event.currentTarget)));
		mutation.mutate(input);
	}

	return <form onSubmit={onSubmit} />;
}
```

Keep mutation configuration stable in the hook. Pass changing operation input through `mutate` variables, and keep success/error consequences with the invocation that caused them. Use `decode-formdata` for representation conversion, then validate before invoking the mutation.
