# Functional State Updates

When the next value of a state variable depends on its previous value, pass a pure updater function to its setter. Do not read the render's state snapshot solely to calculate that transition.

```tsx
// BAD: the callback captures isToggled and must be recreated when it changes.
import { useCallback, useState } from 'react';

function ToggleButton() {
	const [isToggled, setIsToggled] = useState(false);
	const toggle = useCallback(() => setIsToggled(!isToggled), [isToggled]);

	return <button onClick={toggle}>{isToggled ? 'On' : 'Off'}</button>;
}
```

```tsx
// GOOD: React supplies the previous value when it applies the transition.
import { useCallback, useState } from 'react';

function ToggleButton() {
	const [isToggled, setIsToggled] = useState(false);
	const toggle = useCallback(() => setIsToggled(isToggled => !isToggled), []);

	return <button onClick={toggle}>{isToggled ? 'On' : 'Off'}</button>;
}
```

Updater functions compose correctly when React queues multiple transitions. They also remove state that is read only for the transition from a memoized callback's dependency list.

Keep every other reactive value read by the callback in its dependency list. Use `useCallback` only when stable function identity has an independent, documented purpose.
