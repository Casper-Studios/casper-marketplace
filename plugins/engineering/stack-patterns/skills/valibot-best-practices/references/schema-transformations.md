# Schema Transformations and Built-ins

Parse and normalize in the schema so consumers receive the final contract. Prefer the library's matching action or schema over custom coercion, format expressions, or membership scaffolding.

```typescript
// BAD: custom conversion repeats a built-in operation.
const Count = v.pipe(
	v.string(),
	v.transform(value => Number(value)),
	v.integer(),
	v.minValue(0),
);

// GOOD: retain the nonnegative integer contract after conversion.
const Count = v.pipe(v.string(), v.toNumber(), v.integer(), v.minValue(0));

// GOOD: compose a standard format action with its input schema.
const UserId = v.pipe(v.string(), v.uuid());

// GOOD: the schema owns the allowed wire values.
const Channel = v.picklist(['email', 'sms']);
```

`v.toNumber()` uses numeric conversion semantics; it does not authorize truncating decimals or accepting numeric prefixes with `parseInt`. Add the owned constraints, such as `v.integer()`, `v.finite()`, or range checks. If empty or whitespace-only strings are invalid for the protocol, reject them before conversion rather than accepting their conversion to zero. Preserve string representation when consumers need it; normalize to a number only when that is the intended output contract.

`v.uuid()` is a validation action, not a standalone string predicate. At an untrusted boundary, use the schema above. For an already trusted string that needs only a UUID-format decision, the exported `v.UUID_REGEX.test(value)` checks that format without rechecking the primitive type or creating a new schema. Verify that the library's UUID format matches the protocol before reusing it; format validity alone proves neither existence nor authorization.

Use a custom transform when it expresses a conversion without a matching built-in:

```typescript
const Timestamp = v.pipe(
	v.number(),
	v.transform(value => new Date(value)),
);
```
