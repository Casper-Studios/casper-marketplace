# Zod Imports

Import `z` once at the top of a module. It owns every schema constructor and top-level format validator.

```typescript
import { z } from 'zod';

const User = z.object({
	id: z.uuid(),
	name: z.string(),
});
```

Use the same `z` import throughout the module instead of mixing import forms.
