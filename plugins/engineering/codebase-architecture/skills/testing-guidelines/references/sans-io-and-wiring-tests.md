# Sans-I/O and Wiring Tests

Design the business core as sans-I/O: it accepts values and events, then returns decisions, state transitions, or effect descriptions without performing network, filesystem, database, clock, process, or framework lifecycle operations.

Unit-test that sans-I/O core directly. Keep resource acquisition and effects in entry points, drivers, and boundary adapters.

When owned policy requires preventing an effect, test the policy directly. Add one narrow wiring test only when the pure test cannot prove that the prohibited effect was not invoked.

Use an integration test when the project owns a boundary contract that a sans-I/O test cannot prove. Do not introduce mocks merely to make transparent I/O delegation look like unit-testable behavior.

```typescript
// BAD: this only proves that Vitest and the transport wrapper both work.
it('sends a welcome email', async () => {
	const mailer = { send: vi.fn().mockResolvedValue(undefined) };

	await sendWelcomeEmail(mailer, 'ada@example.com');

	expect(mailer.send).toHaveBeenCalledWith('ada@example.com', 'Welcome');
});

// GOOD: test the owned decision without I/O.
it('welcomes a newly activated member once', () => {
	expect(welcomeDecision({ activated: true, welcomed: false })).toEqual({
		kind: 'send-welcome-email',
	});
});
```

The entry point performs the resulting effect. Test its wiring only when the project owns behavior that the pure decision cannot establish, such as preventing a prohibited effect.
