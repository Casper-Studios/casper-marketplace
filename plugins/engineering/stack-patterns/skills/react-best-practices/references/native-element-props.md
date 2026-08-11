# Native Element Props

Extend the native element contract when a component wraps an intrinsic element. Preserve standard attributes, event handlers, accessibility fields, and the React 19 `ref` prop.

```tsx
import type { ComponentPropsWithRef, ReactNode } from 'react';

// BAD: the handwritten contract silently excludes native capabilities.
interface IncompleteButtonProps {
	onClick(): void;
	children: ReactNode;
}

// GOOD: inherit the native button contract and add only the component API.
interface ButtonProps extends ComponentPropsWithRef<'button'> {
	variant?: ButtonVariant;
}

const enum ButtonVariant {
	Primary = 'primary',
	Secondary = 'secondary',
}

function Button({ variant = ButtonVariant.Primary, className, ...props }: ButtonProps) {
	return <button className={cn(buttonVariants({ variant }), className)} {...props} />;
}
```

Use `ComponentPropsWithRef<'element'>` when callers can pass a ref. Use `ComponentPropsWithoutRef<'element'>` only when the wrapper deliberately does not expose one.

Do not recreate native props by hand. A narrow handwritten interface silently drops `aria-*`, `data-*`, form attributes, keyboard handlers, and future platform additions.

Resolve prop-name collisions deliberately with `Omit` before adding a component-specific meaning. Preserve the native semantic element unless the component contract requires another element.
