# Form Validation

Decode form input into its intended representation, then parse it at the form boundary. Mutations receive validated domain input, never raw `FormData`.

```tsx
import { decode } from 'decode-formdata';
import * as v from 'valibot';

// BAD: decoding changes representation but does not validate the result.
function BadItemForm() {
	const mutation = useMutation({ mutationFn: createItem });

	function onSubmit(event: React.FormEvent<HTMLFormElement>) {
		event.preventDefault();
		mutation.mutate(decode(new FormData(event.currentTarget)));
	}

	return <form onSubmit={onSubmit} />;
}

// GOOD: decode the representation, then parse the boundary.
function ItemForm() {
	const mutation = useMutation({ mutationFn: createItem });

	function onSubmit(event: React.FormEvent<HTMLFormElement>) {
		event.preventDefault();
		const input = v.parse(createItemSchema, decode(new FormData(event.currentTarget)));
		mutation.mutate(input);
	}

	return <form onSubmit={onSubmit} />;
}
```

Use `decode-formdata` for representation conversion and Valibot for validation. Decoding does not establish trust.
