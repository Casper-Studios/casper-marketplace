# Entry Points and Composition

Treat route, page, application, and runtime entry points as composition surfaces. They select features, provide framework context, acquire resources, and register executable capabilities.

```typescript
// BAD: a feature imports and orchestrates a peer feature.
import { showSubmissionReceipt } from '@/features/receipts';

export async function submitApplication(input: ApplicationInput) {
	const application = await persistApplication(input);
	return showSubmissionReceipt(application);
}

// GOOD: page.tsx owns cross-feature composition.
import { submitApplication } from '@/features/applications';
import { showSubmissionReceipt } from '@/features/receipts';

export async function submitFromPage(input: ApplicationInput) {
	const application = await submitApplication(input);
	return showSubmissionReceipt(application);
}
```

A feature entry imports and composes its implementation subtree. Private leaves must not import their own entry point; extract the needed logic into a lower module instead.

Thin presentation routes normally render one feature entry. A caller such as `index.ts`, `mod.rs`, `__init__.py`, `__main__.py`, `page.tsx`, `+page.svelte`, or `+layout.svelte` can compose multiple isolated features when the screen or route owns the combined outcome.

Framework-owned server routes can retain authorization, request parsing, form actions, transaction coordination, and response construction when those responsibilities belong to the transport boundary.

Runtime registries and application roots can import many features. They own sequencing and dependency injection, but they must not absorb the business logic of the capabilities they register.
