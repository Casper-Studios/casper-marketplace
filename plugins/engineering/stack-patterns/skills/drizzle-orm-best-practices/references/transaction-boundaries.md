# Transaction Boundaries

Use `db.transaction` when several statements create or preserve one domain invariant and the configured driver supports transactions. Pass `tx` through every participating helper so no statement escapes the unit of work. Do not infer support from the presence of the method; MySQL Proxy exposes it but throws when called.

```typescript
// node-postgres
import { and, eq, gte, sql } from 'drizzle-orm';

await db.transaction(async tx => {
	const debit = await tx
		.update(accounts)
		.set({ balance: sql`${accounts.balance} - ${amount}` })
		.where(and(eq(accounts.id, sourceAccountId), gte(accounts.balance, amount)));
	if (debit.rowCount !== 1) throw new Error('Source account is missing or has insufficient funds');

	const credit = await tx
		.update(accounts)
		.set({ balance: sql`${accounts.balance} + ${amount}` })
		.where(eq(accounts.id, destinationAccountId));
	if (credit.rowCount !== 1) throw new Error('Destination account is missing');
});
```

Validate that `amount` is positive before the transaction. Drizzle has no general arithmetic helper, so the non-result-bearing update expressions are valid `sql` uses. The configured driver still parameterizes `amount`.

Let failures escape the transaction callback so Drizzle rolls the transaction back. Do not swallow a failure, continue after an invariant breaks, or perform undocumented compensating writes outside the failed transaction.

Do not wrap one independent statement in a transaction without a separate locking or isolation requirement. Select the transaction isolation and locking behavior from the invariant, not from a blanket convention.
