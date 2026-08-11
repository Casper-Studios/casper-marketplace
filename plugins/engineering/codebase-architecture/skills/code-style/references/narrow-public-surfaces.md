# Narrow Public Surfaces

Expose only stable capabilities intended for consumers. Keep construction details, vendor types, environment loading, mutable lifecycle state, and internal helpers behind the owning boundary.

```typescript
// BAD: a root import activates unrelated infrastructure.
import { Model } from '@project/database';

// GOOD: consumers import the precise, side-effect-free surface.
import { Model } from '@project/database/models';

// GOOD: only the entry point imports resource construction.
import { openDatabase } from '@project/database/client';
```

A package root can remain empty when no cohesive root API exists. Re-export a symbol only when the root export is stable, intentional, and free of unrelated initialization.

Do not expose raw vendor clients or response types when the package exists to insulate consumers from that dependency. Do not create re-exports merely to shorten import paths.
