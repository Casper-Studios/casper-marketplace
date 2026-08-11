# Conditional Expressions

Use the language's concise conditional-value expression when one condition selects one of two simple values. Use statements when a branch performs work, changes control flow, or needs more than one operation.

```typescript
// BAD: short-circuit syntax hides effectful control flow.
isReady && start();

// GOOD: a statement makes the effect conditional explicitly.
if (isReady) start();

// GOOD: a ternary selects one of two values.
const color = isSelected ? selectedColor : defaultColor;

// GOOD: conjunction expresses one boolean predicate.
const canSubmit = form.isValid && user.hasPermission;
```

Do not nest conditional-value expressions. Replace one with statements when either branch needs explanation, mutation, or multiple operations. Use the target language's conventional construct; the semantic distinction between value selection and effectful control flow is normative, not its spelling.
