# Pure Core, Imperative Shell

Keep decisions, calculations, and state transitions free of I/O (i.e., sans-IO). Let boundary adapters validate external values. Let entry points and drivers acquire resources, read external state, call the pure core, and apply effects.

```typescript
// BAD: domain decisions are coupled to effects.
async function approve(orderId: string) {
	const order = await database.load(orderId);
	if (await paymentGateway.charge(order.total)) await database.markApproved(orderId);
}

const enum PaymentResult {
	Approved = 'approved',
	Declined = 'declined',
}

const enum Decision {
	ApproveOrder = 'approve-order',
	RejectPayment = 'reject-payment',
}

// GOOD: this transition is pure and exhaustive.
function decideApproval(paymentResult: PaymentResult) {
	switch (paymentResult) {
		case PaymentResult.Approved:
			return Decision.ApproveOrder;
		case PaymentResult.Declined:
			return Decision.RejectPayment;
		default:
			throw new Error('unknown payment result');
	}
}
```

The imperative shell loads the order, charges the payment, calls `decideApproval`, and applies the returned decision. Test the pure decision directly. Do not force effectful transport or lifecycle behavior into a fake pure abstraction.
