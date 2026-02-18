# SaaS & RevOps Metrics Reference

## Revenue Metrics

### ARR (Annual Recurring Revenue)

**Definition:** The annualized value of recurring revenue from subscriptions.

**Formula:**
```
ARR = MRR × 12
```

**Edge cases:**
- Exclude one-time fees (setup, professional services)
- Include only committed, contracted revenue
- For mid-contract changes, use the new rate going forward

### MRR (Monthly Recurring Revenue)

**Definition:** Normalized monthly value of recurring subscriptions.

**Formula:**
```
MRR = Sum of (each customer's monthly subscription value)
```

**For non-monthly contracts:**
```
Annual contract: MRR = Annual value / 12
Quarterly contract: MRR = Quarterly value / 3
```

### MRR Components

| Component | Definition | Formula |
|-----------|------------|---------|
| **New MRR** | Revenue from new customers | Sum of first-month MRR for new logos |
| **Expansion MRR** | Upgrades, add-ons, price increases | Current MRR - Prior MRR (for existing customers with increases) |
| **Contraction MRR** | Downgrades, discounts | Prior MRR - Current MRR (for existing customers with decreases) |
| **Churned MRR** | Lost revenue from cancelled customers | MRR of customers who churned |

**MRR Movement:**
```
Ending MRR = Starting MRR + New MRR + Expansion MRR - Contraction MRR - Churned MRR
```

---

## Churn Metrics

### Logo Churn Rate (Customer Churn)

**Definition:** Percentage of customers lost in a period.

**Formula:**
```
Logo Churn Rate = (Customers lost in period / Customers at start of period) × 100
```

**Gotcha:** Does NOT account for customer value. A $100/mo customer = a $100,000/mo customer.

### Revenue Churn Rate (Gross Revenue Churn)

**Definition:** Percentage of MRR lost from existing customers.

**Formula:**
```
Gross Revenue Churn = (Churned MRR + Contraction MRR) / Starting MRR × 100
```

**Note:** This is always positive or zero. Does not include expansion.

### Net Revenue Retention (NRR)

**Definition:** Revenue retained from existing customers including expansion.

**Formula:**
```
NRR = (Starting MRR - Churned MRR - Contraction MRR + Expansion MRR) / Starting MRR × 100
```

**Interpretation:**
- NRR > 100%: Expansion exceeds churn (healthy)
- NRR = 100%: Breaking even on existing customers
- NRR < 100%: Losing revenue from existing base

**Benchmarks:**
| Rating | NRR |
|--------|-----|
| Elite | > 130% |
| Strong | 110-130% |
| Healthy | 100-110% |
| Concerning | < 100% |

### Gross Revenue Retention (GRR)

**Definition:** Revenue retained excluding expansion (floor of retention).

**Formula:**
```
GRR = (Starting MRR - Churned MRR - Contraction MRR) / Starting MRR × 100
```

**Note:** GRR can never exceed 100%. It's capped by definition.

**Logo vs Revenue Churn Decision:**
- Use **logo churn** when: customer count matters (product-led growth, network effects)
- Use **revenue churn** when: revenue concentration exists, enterprise focus

---

## Customer Value Metrics

### LTV (Lifetime Value)

**Definition:** Total revenue expected from a customer over their lifetime.

**Simple formula:**
```
LTV = ARPU / Monthly Churn Rate
```

**With margin:**
```
LTV = (ARPU × Gross Margin) / Monthly Churn Rate
```

**With discount rate (DCF approach):**
```
LTV = (ARPU × Gross Margin) / (Monthly Churn Rate + Monthly Discount Rate)
```

**Cohort-based LTV:**
Track actual revenue per cohort over time. More accurate but requires historical data.

### CAC (Customer Acquisition Cost)

**Definition:** Cost to acquire one new customer.

**Formula:**
```
CAC = Total Sales & Marketing Spend / Number of New Customers Acquired
```

**Include:**
- Marketing spend (ads, content, events)
- Sales salaries and commissions
- Sales tools and infrastructure

**Exclude:**
- Customer success (post-acquisition)
- Product development

### LTV:CAC Ratio

**Definition:** Return on customer acquisition investment.

**Formula:**
```
LTV:CAC = LTV / CAC
```

**Benchmarks:**
| Ratio | Interpretation |
|-------|----------------|
| < 1:1 | Losing money on each customer |
| 1:1 - 3:1 | Inefficient acquisition |
| 3:1 | Healthy benchmark target |
| > 5:1 | May be under-investing in growth |

### CAC Payback Period

**Definition:** Months to recover customer acquisition cost.

**Formula:**
```
CAC Payback = CAC / (ARPU × Gross Margin)
```

**Benchmarks:**
- < 12 months: Excellent
- 12-18 months: Good
- 18-24 months: Acceptable for enterprise
- > 24 months: Concerning

---

## Pipeline Metrics

### Win Rate

**Definition:** Percentage of opportunities that convert to closed-won.

**Formula:**
```
Win Rate = Closed Won Deals / Total Closed Deals × 100
```

**Note:** Denominator is closed deals only (won + lost), not all opportunities.

**By stage:**
```
Stage Win Rate = Deals reaching Closed Won from Stage X / Deals entering Stage X
```

### Sales Velocity

**Definition:** Speed at which pipeline generates revenue.

**Formula:**
```
Sales Velocity = (# Opportunities × Win Rate × Average Deal Size) / Sales Cycle Length
```

**Interpretation:** Revenue generated per day/week/month from pipeline.

### Pipeline Coverage

**Definition:** Ratio of pipeline to quota/target.

**Formula:**
```
Pipeline Coverage = Total Pipeline Value / Revenue Target
```

**Benchmarks:**
- 3x coverage: Standard target
- 4x coverage: Conservative/enterprise deals
- 2x coverage: Risky, may miss target

### Average Contract Value (ACV)

**Definition:** Average annualized value of new contracts.

**Formula:**
```
ACV = Total Contract Value of New Deals / Number of New Deals
```

**For multi-year deals:** Annualize the value.

### Bookings vs Revenue

| Term | Definition |
|------|------------|
| **Bookings** | Value of signed contracts (committed future revenue) |
| **Revenue** | Recognized revenue per accounting rules |
| **Billings** | Invoiced amount |

**Example:** 3-year, $120K contract signed Jan 1
- Bookings (Jan): $120K
- Monthly revenue: $3,333 (recognized over 36 months)
- Billings: Depends on payment terms

---

## Cohort Analysis

### Retention Cohorts

**Structure:**
- Rows: Cohort (usually by signup month)
- Columns: Periods since signup (Month 0, Month 1, etc.)
- Values: Retention rate or revenue retained

**Example format:**
```
Cohort    | M0   | M1   | M2   | M3   | M6   | M12
----------|------|------|------|------|------|-----
Jan 2024  | 100% | 92%  | 87%  | 84%  | 78%  | 71%
Feb 2024  | 100% | 94%  | 89%  | 85%  | 80%  | -
Mar 2024  | 100% | 91%  | 86%  | 82%  | -    | -
```

### Cohort LTV

**Formula:**
```
Cohort LTV = Sum of revenue from cohort over N periods / Customers in cohort at M0
```

**Usage:** More accurate than formula-based LTV when you have sufficient history.

### Time-to-Value (TTV)

**Definition:** Time from signup to first value realization.

**Measurement options:**
- First login after onboarding
- First key action completed
- First positive outcome achieved

**Why it matters:** Shorter TTV correlates with better retention.

---

## Common Calculation Gotchas

### Churn Calculation Timing

**Problem:** When does a churned customer count?
- **Cancellation date:** When they say they're leaving
- **Contract end date:** When service actually ends
- **Last payment date:** When revenue stops

**Best practice:** Use contract end date for revenue churn, be consistent.

### Handling Free Trials

**Problem:** Should trials be in MRR calculations?

**Best practice:**
- Exclude free trials from MRR
- Track trial-to-paid conversion separately
- Include only when customer converts to paid

### Multi-year Contracts

**Problem:** How to handle 2-3 year deals?

**For MRR/ARR:** Normalize to monthly/annual value
**For bookings:** Record full contract value at signing
**For churn:** Track at contract end, not artificially earlier

### Refunds and Credits

**Problem:** How do refunds affect metrics?

**Best practice:**
- Partial refunds: Reduce MRR proportionally
- Full refunds: Treat as churn (or never count as new)
- Credits: Don't affect MRR unless applied
