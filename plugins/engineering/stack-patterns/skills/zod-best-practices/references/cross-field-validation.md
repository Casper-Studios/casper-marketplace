# Cross-Field Validation

Use `.check()` when validation needs multiple issues or relationships among several values. Push each issue directly onto the check context.

```typescript
// BAD: Collapse Several Relationship Failures Into One Root Issue
const AccountChange = z
	.object({
		email: z.email(),
		emailConfirmation: z.email(),
		password: z.string().min(12),
		passwordConfirmation: z.string(),
	})
	.refine(
		value =>
			value.email === value.emailConfirmation && value.password === value.passwordConfirmation,
		{ message: 'Confirm the email and password' },
	);
```

One `.refine()` predicate produces one issue, so the form cannot tell which confirmations failed when both are wrong.

```typescript
// GOOD: Report Each Relationship Failure at Its Field
const AccountChange = z
	.object({
		email: z.email(),
		emailConfirmation: z.email(),
		password: z.string().min(12),
		passwordConfirmation: z.string(),
	})
	.check(context => {
		if (context.value.email !== context.value.emailConfirmation) {
			context.issues.push({
				code: 'custom',
				message: 'Emails must match',
				path: ['emailConfirmation'],
				input: context.value.emailConfirmation,
			});
		}

		if (context.value.password !== context.value.passwordConfirmation) {
			context.issues.push({
				code: 'custom',
				message: 'Passwords must match',
				path: ['passwordConfirmation'],
				input: context.value.passwordConfirmation,
			});
		}
	});
```

Use `.refine()` for one object-level failure with one meaningful error location. Use `.check()` when a form needs several field-specific issues.
