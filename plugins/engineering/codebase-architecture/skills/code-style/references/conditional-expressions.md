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

When a branch adds an optional field or element, construct a locally owned result once and insert conditionally. Avoid both empty-branch spreads and a ternary that repeats the base object just to add a field.

```typescript
interface Update {
	title: string;
	summary?: string;
}

// BAD: conditional spreads obscure insertion and create empty placeholders.
const spreadUpdate = { title, ...(typeof summary !== 'undefined' ? { summary } : {}) };
const spreadTags = [...tags, ...(typeof extraTag !== 'undefined' ? [extraTag] : [])];

// BAD: the base object is repeated to express one optional field.
const branchedUpdate = typeof summary === 'undefined' ? { title } : { title, summary };

// GOOD: build owned results once, then insert the optional values.
const update: Update = { title };
if (typeof summary !== 'undefined') update.summary = summary;

const nextTags = [...tags];
if (typeof extraTag !== 'undefined') nextTags.push(extraTag);
```

Mutate only the result owned by this construction step. Copy borrowed input before inserting, and preserve any caller-visible immutability or identity contract. Keep a property absent when absence is its contract; assigning `undefined` is a different state. Simple scalar selection still belongs in a conditional expression.

Do not nest conditional-value expressions. Replace one with statements when either branch needs explanation, mutation, or multiple operations. Use the target language's conventional construct; the semantic distinction between value selection and effectful control flow is normative, not its spelling.
