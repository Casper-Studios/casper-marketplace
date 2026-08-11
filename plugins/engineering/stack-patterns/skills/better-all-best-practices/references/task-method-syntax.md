# Task Method Syntax

Define `better-all` tasks with method shorthand or a `function` expression. Tasks access sibling results through `this.$`; arrow functions have no task `this` binding.

```typescript
import { all } from 'better-all';

// BAD: Use an Arrow Task That Needs `this.$`
await all({
	fetchUser: async () => await this.$.user,
	async user() {
		return await fetchUser(userId);
	},
});
```

The arrow captures lexical `this`; it does not receive the `better-all` task context.

```typescript
import { all } from 'better-all';

// GOOD: Use Method Shorthand for Tasks That Read Siblings
const results = await all({
	async fetchUser() {
		return await fetchUser(userId);
	},
	async profile() {
		return buildProfile(await this.$.fetchUser);
	},
});
```
