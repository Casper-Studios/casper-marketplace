# Class Composition

Use a literal string for static classes. When composition or override merging is needed, let the project's `cn` helper combine its arguments; do not preassemble conditional class lists with interpolation, concatenation, or repeated variable assignment.

```tsx
// BAD: manual string assembly bypasses the composition helper.
const interpolatedClassName = cn(`${baseClass} ${isSelected ? 'bg-accent' : ''}`);

// GOOD: independent conditions are named once.
const className = cn(baseClass, { 'bg-accent': isSelected });

// GOOD: no composition or merging is needed.
const staticClassName = 'flex items-center';

// GOOD: alternatives select one value; incoming overrides still need merging.
const variantClassName = cn(isCompact ? compactClass : regularClass, incomingClass);
```

Start customization from existing component variants, typography, spacing, and tokens. Preserve semantic controls, keyboard/focus behavior, and container-query ownership when making a targeted style change. Keep exact visual choices with the feature that owns them.
