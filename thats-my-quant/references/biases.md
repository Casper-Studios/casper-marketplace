# Analytical Bias Checklist

Use this checklist before finalizing any analysis. Each bias includes finance/RevOps examples and mitigation strategies.

---

## Pre-Interpretation Checklist

Run through this checklist before drawing conclusions:

- [ ] **Survivorship Bias** - Am I only looking at "survivors"?
- [ ] **Simpson's Paradox** - Do segment trends differ from aggregate?
- [ ] **Selection Bias** - Is my sample representative?
- [ ] **Collider Bias** - Am I conditioning on an outcome?
- [ ] **Confounding** - Are there omitted variables?
- [ ] **Small-n Warning** - Is sample size sufficient?
- [ ] **Recency Bias** - Am I overweighting recent data?
- [ ] **Confirmation Bias** - Am I seeking data to confirm beliefs?

---

## Survivorship Bias

**Definition:** Drawing conclusions only from entities that "survived" a selection process, ignoring those that didn't.

### Finance/RevOps Examples

| Scenario | Bias Risk | What's Missing |
|----------|-----------|----------------|
| Analyzing successful customers | High | Churned customers excluded |
| Studying high-performing reps | High | Reps who left/underperformed |
| Looking at surviving startups | High | Failed companies |
| Reviewing winning deals | High | Lost deals |

### Red Flags

- "Our customers say..." (only current customers)
- "Our best customers do X" (survivorship in sample)
- "Successful companies have Y" (failed companies ignored)

### Mitigation

1. **Include churned customers** in retention analysis
2. **Analyze lost deals** alongside won deals
3. **Track cohorts from start** - don't backfill
4. **Ask:** "What am I not seeing because it no longer exists?"

### Logging Format

```
BIAS CHECK - Survivorship: [PASS/FLAG]
- Churned customers: [included/excluded]
- Action: [mitigation taken]
```

---

## Simpson's Paradox

**Definition:** A trend in aggregated data reverses or disappears when data is separated into groups.

### Finance/RevOps Examples

**Classic case:** Overall conversion rate is up, but conversion is down in every segment.

| Aggregate | Segment A | Segment B | Why? |
|-----------|-----------|-----------|------|
| Conv up 5% | Conv down 2% | Conv down 3% | Mix shifted to higher-converting segment |

**Revenue example:**
- Overall ARPU increased
- ARPU decreased in both SMB and Enterprise
- Mix shifted toward Enterprise (higher ARPU base)

### Red Flags

- Aggregate trend seems strong
- No segment breakdown provided
- Mix/composition changed over time

### Mitigation

1. **Always segment** key metrics before concluding
2. **Control for mix shifts** in trend analysis
3. **Report both** aggregate and segment views
4. **Weight by segment** when appropriate

### Logging Format

```
BIAS CHECK - Simpson's: [PASS/FLAG]
- Segments checked: [list]
- Mix shift: [yes/no - details]
```

---

## Selection Bias

**Definition:** Sample is not representative of the population you're trying to understand.

### Finance/RevOps Examples

| Analysis | Selection Risk | Issue |
|----------|----------------|-------|
| Survey responses | Self-selection | Happy/angry customers overrepresent |
| Pilot program results | Cherry-picking | Best candidates selected |
| Sales rep analysis | Territory assignment | Top reps get best territories |
| Product usage data | Active user bias | Inactive users underrepresented |

### Red Flags

- Opt-in surveys or programs
- "Hand-picked" samples
- Non-random assignment
- Response rates < 30%

### Mitigation

1. **Document selection criteria** explicitly
2. **Compare sample to population** on key dimensions
3. **Use stratified sampling** when possible
4. **Adjust for non-response** if data available
5. **Acknowledge limitations** in findings

### Logging Format

```
BIAS CHECK - Selection: [PASS/FLAG]
- Selection method: [random/convenience/other]
- Sample vs population: [comparison]
- Representativeness: [strong/moderate/weak]
```

---

## Collider Bias

**Definition:** Conditioning on a variable that is caused by both the treatment and outcome, creating spurious associations.

### Finance/RevOps Examples

**Classic case:** Analyzing only closed deals to understand what drives winning.

```
           Marketing Spend
                  ↓
            [Deal Size] ← Sales Effort
                  ↓
              Deal Won (collider)
```

If you only analyze won deals, you may find marketing spend negatively correlates with deal size - but this is spurious.

**Other examples:**
- Analyzing only retained customers for churn factors
- Studying only hired candidates for interview performance
- Looking at only successful products for launch factors

### Red Flags

- Filtering data to an outcome (won deals, retained customers)
- "Among successful X, we find..."
- Post-hoc analysis of survivors

### Mitigation

1. **Include all observations** - won AND lost, retained AND churned
2. **Be explicit** about conditioning variables
3. **Use causal diagrams** to identify colliders
4. **Run sensitivity analysis** with different filters

### Logging Format

```
BIAS CHECK - Collider: [PASS/FLAG]
- Conditioning on: [variable]
- Risk assessment: [describe]
```

---

## Confounding (Omitted Variable Bias)

**Definition:** A third variable influences both the predictor and outcome, creating a spurious correlation.

### Finance/RevOps Examples

| Observed | Confounder | Reality |
|----------|------------|---------|
| Feature X users retain better | Customer sophistication | Sophisticated users adopt features AND retain |
| Training improves performance | Manager quality | Good managers invest in training AND coach well |
| Pricing tier correlates with NPS | Company size | Larger companies pay more AND have different needs |

### Red Flags

- Strong correlation without plausible mechanism
- "Users who do X have higher Y" (no randomization)
- No control variables in analysis

### Mitigation

1. **List potential confounders** before analysis
2. **Control for confounders** in regression
3. **Use quasi-experimental methods** when possible (diff-in-diff, matching)
4. **Acknowledge** when confounding can't be ruled out
5. **Say "associated with"** not "causes"

### Logging Format

```
BIAS CHECK - Confounding: [PASS/FLAG]
- Potential confounders: [list]
- Controls used: [list]
- Causal claim appropriate: [yes/no]
```

---

## Small-n Warning

**Definition:** Drawing strong conclusions from insufficient sample sizes.

### Minimum Sample Guidance

| Analysis Type | Minimum n | Notes |
|---------------|-----------|-------|
| Proportions (conversion rates) | 100+ per group | For detecting 5%+ differences |
| Means comparison | 30+ per group | Central limit theorem |
| Regression | 10-20x predictors | Rule of thumb |
| Segmentation | 30+ per segment | For stable estimates |

### Finance/RevOps Red Flags

- "Enterprise customers prefer X" (n=12)
- "Q4 trend shows Y" (4 data points)
- "New feature increased Z" (tested on 50 users)

### When to Flag

```python
# Quick significance check
import scipy.stats as stats

# For proportions
n1, n2 = sample_sizes
if n1 < 100 or n2 < 100:
    print("SMALL-N WARNING: Results may be unstable")

# For segment analysis
if any(segment_counts < 30):
    print("SMALL-N WARNING: Some segments too small")
```

### Mitigation

1. **Report confidence intervals** - wide CIs = small n
2. **Pool small segments** when appropriate
3. **Use Bayesian methods** for small samples
4. **Clearly label** preliminary/directional findings
5. **Wait for more data** before major decisions

### Logging Format

```
BIAS CHECK - Small-n: [PASS/FLAG]
- Sample size: [n]
- Minimum recommended: [threshold]
- Action: [proceed/flag/wait for data]
```

---

## Recency Bias

**Definition:** Overweighting recent observations relative to historical patterns.

### Finance/RevOps Examples

- Last quarter's churn spike drives panic (but it's seasonal)
- Recent win streak leads to over-hiring
- Latest customer feedback dominates roadmap

### Mitigation

1. **Show historical context** - at least 2-3 years
2. **Adjust for seasonality** explicitly
3. **Use rolling averages** to smooth noise
4. **Compare to same period last year** (YoY)

### Logging Format

```
BIAS CHECK - Recency: [PASS/FLAG]
- Time period analyzed: [range]
- Historical comparison: [included/missing]
- Seasonality adjustment: [yes/no]
```

---

## Confirmation Bias

**Definition:** Seeking or interpreting data to confirm pre-existing beliefs.

### Warning Signs

- Analysis started with a conclusion
- Only supportive evidence presented
- Contradictory findings dismissed or unexplored
- "We knew X, and data confirms"

### Mitigation

1. **Pre-register hypotheses** before analysis
2. **Actively seek disconfirming evidence**
3. **Present contradictory findings** prominently
4. **Have someone else review** the analysis
5. **Document the question** before starting

### Logging Format

```
BIAS CHECK - Confirmation: [PASS/FLAG]
- Hypothesis stated upfront: [yes/no]
- Contradictory evidence explored: [yes/no]
- Alternative explanations: [list]
```

---

## Summary Checklist Template

Copy this to your analysis notebook:

```markdown
## Bias Checklist

| Bias | Status | Notes |
|------|--------|-------|
| Survivorship | [ ] Pass / [ ] Flag | |
| Simpson's Paradox | [ ] Pass / [ ] Flag | |
| Selection | [ ] Pass / [ ] Flag | |
| Collider | [ ] Pass / [ ] Flag | |
| Confounding | [ ] Pass / [ ] Flag | |
| Small-n | [ ] Pass / [ ] Flag | |
| Recency | [ ] Pass / [ ] Flag | |
| Confirmation | [ ] Pass / [ ] Flag | |

**Overall assessment:** [Ready to present / Needs caveats / Needs more work]

**Key caveats to include in findings:**
1.
2.
3.
```
