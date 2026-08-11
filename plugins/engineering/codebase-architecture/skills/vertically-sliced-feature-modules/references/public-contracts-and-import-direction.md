# Public Contracts and Import Direction

Expose a deliberate feature entry to callers and orchestrators. Keep feature implementation isolated from peer features.

```typescript
// BAD: one feature depends on another feature, even through its public entry.
import { submitApplication } from '@/features/applications';

// GOOD: the caller composes isolated feature capabilities.
import { submitApplication } from '@/features/applications';
import { showSubmissionReceipt } from '@/features/receipts';

// GOOD: independently shared logic has an explicit non-feature owner.
import { calculateEligibility } from '@/shared/eligibility';
```

```typescript
// GOOD: a feature root exposes only its caller-facing capability.
export { submitApplication } from './submit-application';
```

A feature entry is a contract for an orchestrator, route, page, layout, application root, or runtime registry. It is not permission for peer features to depend on one another.

When multiple features need the same behavior, promote that behavior to a shared module with an explicit owner. When one workflow needs multiple feature capabilities, keep the sequencing in the caller. Do not make either feature the hidden orchestrator.

Imports must reveal ownership:

- Same-directory imports can be relative.
- Parent traversal into an owner's internals is forbidden.
- Features do not import other features.
- Orchestrators import feature roots, not implementation leaves.
- Shared modules do not import the features that consume them.
- Lower-level infrastructure does not import the application that composes it.

Do not create barrels solely to shorten paths. A feature entry must represent a stable caller-facing capability.
