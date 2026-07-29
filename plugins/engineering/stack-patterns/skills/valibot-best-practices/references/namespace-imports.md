# Namespace Imports

Import Valibot as a namespace. The namespace keeps schema constructors visibly owned by the validation library and avoids a long list of individual imports.

```typescript
import * as v from 'valibot';

const User = v.object({
	id: v.string(),
	name: v.string(),
});
```

Use the same `v` namespace in the module instead of mixing namespace and named imports.
