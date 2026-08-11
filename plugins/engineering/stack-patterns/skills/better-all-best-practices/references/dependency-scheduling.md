# Dependency Scheduling

Declare a task dependency where the task needs the result. `better-all` derives the graph and schedules independent tasks concurrently.

```typescript
// BAD: manual sequencing serializes independent work.
const user = await fetchUser();
const posts = await fetchPosts();
const profile = await buildProfile(user, posts);
const feed = await buildFeed(profile, posts);
const stats = await buildStats(profile);

// GOOD: each task declares only its direct dependencies.
const results = await all({
	async user() {
		return await fetchUser();
	},
	async posts() {
		return await fetchPosts();
	},
	async profile() {
		return buildProfile(await this.$.user, await this.$.posts);
	},
	async feed() {
		return buildFeed(await this.$.profile, await this.$.posts);
	},
	async stats() {
		return buildStats(await this.$.profile);
	},
});
```

Do not await a sibling result that the task does not need. Do not add manual `Promise.all` stages around a graph that `better-all` can schedule.
