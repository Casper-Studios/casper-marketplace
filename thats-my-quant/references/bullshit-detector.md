# Bullshit Detector Reference

Statistical sins, chart crimes, logic fallacies, and sanity checks for reviewing analytical claims.

---

## Pre-Review Checklist

Before accepting any analytical finding, run through these checks:

```
## BS Detection Checklist

### Quick Smell Test
- [ ] Does the conclusion seem too good/bad to be true?
- [ ] Can I explain the finding to someone in plain English?
- [ ] What would have to be true for this to be wrong?

### Statistical Checks
- [ ] Sample size disclosed and appropriate?
- [ ] Confidence intervals or p-values provided?
- [ ] Multiple comparisons accounted for?
- [ ] Base rates considered?

### Visual Checks
- [ ] Y-axis starts at zero (or justified if not)?
- [ ] Scales consistent across comparisons?
- [ ] Chart type appropriate for the data?

### Logic Checks
- [ ] Correlation claimed as causation?
- [ ] Selection/survivorship bias addressed?
- [ ] Alternative explanations considered?

### Sanity Checks
- [ ] Back-of-envelope math works?
- [ ] Consistent with historical patterns?
- [ ] Consistent with other data sources?
```

---

## Critical Analysis Patterns

### Market Context

**Principle:** Always compare YoY changes against market or baseline performance.

**Why It Matters:**
- A rep down -5% sounds bad
- But if the market is down -14%, they're actually +9% vs market
- Without market context, you're measuring luck, not skill

**Standard Analysis Pattern:**
```python
# Add market-relative performance to all YoY analyses
df['YoY_vs_Market'] = df['YoY_Change'] - market_yoy_change
```

**Report Output:**
```
Rep A: -5% YoY (but +9% vs market)
Rep B: +3% YoY (but -11% vs market)
```

**Questions to Ask:**
- What's the relevant baseline (market, industry, portfolio average)?
- Are we measuring absolute performance or relative performance?
- Is "down" actually "outperforming in a down market"?

---

### Weighting Sensitivity

**Principle:** When composite scores use arbitrary weights, test sensitivity across multiple scenarios.

**Why It Matters:**
- If someone is ranked #1 with weights 40/30/30 but #8 with weights 33/33/33, the ranking isn't robust
- Arbitrary weight choices can drive conclusions more than underlying data
- "Top performer" claims need to hold across reasonable weight variations

**Testing Protocol:**
```python
# Test 5-6 weighting scenarios
weight_scenarios = [
    {'revenue': 0.40, 'growth': 0.30, 'retention': 0.30},
    {'revenue': 0.33, 'growth': 0.33, 'retention': 0.33},
    {'revenue': 0.50, 'growth': 0.25, 'retention': 0.25},
    {'revenue': 0.25, 'growth': 0.50, 'retention': 0.25},
    {'revenue': 0.25, 'growth': 0.25, 'retention': 0.50},
]

# Track classification stability
classifications = []
for weights in weight_scenarios:
    score = compute_composite(df, weights)
    classifications.append(classify(score))

# Only "confident" if classification holds across ALL scenarios
df['Robust_Classification'] = 'confident' if all_same(classifications) else 'uncertain'
```

**Reporting Guidance:**
- Flag classifications that flip with different weightings as "uncertain"
- Only call something "top tier" if it's top tier across all reasonable weightings
- Document which weight assumptions would change the conclusion

---

### Bootstrap Confidence Intervals

**Principle:** For small samples, use bootstrap to generate P10/P50/P90 ranges.

**Why It Matters:**
- Point estimates are misleading when 59 vs 61 is statistically indistinguishable
- Small samples (n < 30 or few time periods) have high variance
- Rankings based on point estimates overstate precision

**Code Pattern:**
```python
import numpy as np

def bootstrap_confidence(data, n_bootstrap=1000, metric_func=np.mean):
    """Generate P10/P50/P90 for any metric."""
    bootstrap_scores = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=len(data), replace=True)
        bootstrap_scores.append(metric_func(sample))

    p10, p50, p90 = np.percentile(bootstrap_scores, [10, 50, 90])
    return {'P10': p10, 'P50': p50, 'P90': p90}

# Usage
result = bootstrap_confidence(rep_performance_scores)
# Report: "Score: 61 (P10-P90: 54-68)" not just "Score: 61"
```

**When to Use:**
- Any ranking with < 30 observations per entity
- Performance scores based on < 5 time periods
- Any "top performer" or "bottom performer" claim

**Reporting Pattern:**
```
Rep A: 61 points (P10-P90: 54-68)
Rep B: 59 points (P10-P90: 52-66)
Conclusion: Statistically indistinguishable
```

---

### Survivorship Bias Quantification

**Principle:** Don't just acknowledge survivorship bias—quantify it with a `Data_Availability` column.

**Why It Matters:**
- Saying "note: excludes reps with incomplete data" is not enough
- Readers need to know what % of the population is analyzed
- Missing data often correlates with poor performance (non-random)

**Implementation Pattern:**
```python
# Add Data_Availability column to all entity-level analyses
df['Data_Availability'] = df.apply(
    lambda row: f"{row['periods_with_data']}/{total_periods} periods",
    axis=1
)

# Calculate coverage statistics
coverage_stats = {
    'total_population': total_entities,
    'included_in_analysis': included_count,
    'excluded_count': excluded_count,
    'coverage_pct': included_count / total_entities * 100
}
```

**Required Reporting:**
```
## Data Coverage

- Total reps in organization: 45
- Reps with complete data (all 12 quarters): 32 (71%)
- Reps with partial data (included with caveats): 8 (18%)
- Reps excluded (< 4 quarters): 5 (11%)

**Excluded reps:** [Names] - reasons: [new hire, territory change, leave]

**Caveat:** Results may overstate performance if excluded reps
were terminated for poor performance.
```

**Questions to Ask:**
- What % of the population has complete data?
- Is the missingness random or correlated with outcome?
- How would conclusions change if we included partial data?

---

## Statistical Sins

### P-Hacking / Multiple Comparisons

**The Sin:** Running many statistical tests until finding a "significant" result, then reporting only that one.

**Warning Signs:**
- "We found a significant effect" without mentioning what else was tested
- Subgroup analysis that wasn't pre-specified
- P-values just barely under 0.05 (p=0.048, p=0.049)
- No mention of multiple comparison corrections

**Questions to Ask:**
- How many comparisons were tested?
- Was the hypothesis stated before or after seeing the data?
- Is there a Bonferroni or FDR correction applied?

**Rule of Thumb:**
```
If you test 20 things at p<0.05, you expect 1 false positive by chance.
```

---

### Small Sample Extrapolation

**The Sin:** Drawing strong conclusions from insufficient data.

**Warning Signs:**
- Strong claims from n < 30
- No confidence intervals shown
- "100% of customers" when n = 3
- Percentages from small counts (20% = 1 out of 5)

**Questions to Ask:**
- What's the sample size?
- How wide would the confidence interval be?
- Would the conclusion hold if 2-3 observations were different?

**Quick Check:**
```
For proportions: Need ~385 samples for 95% CI within +/- 5%
For means: Need ~30 per group for t-test validity
For segments: Need 20+ per segment for stable estimates
```

---

### Missing Confidence Intervals

**The Sin:** Presenting point estimates without uncertainty.

**Warning Signs:**
- "The conversion rate is 5.2%" (no range)
- "Sales increased 12%" (no confidence bound)
- Single numbers presented as truth
- No mention of variance or error

**Questions to Ask:**
- What's the margin of error?
- How confident are we in this estimate?
- What's the range of plausible values?

**Rule of Thumb:**
```
Any metric should be: Value +/- Range (Confidence Level)
Example: "5.2% +/- 1.1% (95% CI)"
```

---

### Cherry-Picked Baselines

**The Sin:** Choosing comparison points that make results look better.

**Warning Signs:**
- "Since [specific date]..." without justification
- Comparing to worst historical period
- Excluding "outlier" periods that don't support the narrative
- Different baselines for different metrics

**Questions to Ask:**
- Why was this baseline chosen?
- What would the result look like with a different baseline?
- Is this baseline representative?

**Always Check:**
- Last month, quarter, year
- Same period last year (YoY)
- Trailing average (3mo, 6mo, 12mo)
- Pre-COVID if comparing to 2020-2021

---

### Survivorship Bias

**The Sin:** Only analyzing successes while ignoring failures.

**Warning Signs:**
- "Successful customers do X" (what about unsuccessful ones?)
- "Our retained customers say..." (what about churned?)
- Historical analysis starting after failures were removed
- Case studies only of wins

**Questions to Ask:**
- Who/what is excluded from this analysis?
- Would the conclusion change if we included failures?
- Is this sample representative of all cases?

---

### Base Rate Neglect

**The Sin:** Ignoring how common something is overall when interpreting results.

**Example:**
- "Our test detected 80% of churners!"
- But: If only 2% of customers churn, and test has 10% false positive rate...
- 80% of 2% = 1.6% true positives
- 10% of 98% = 9.8% false positives
- Precision = 1.6 / 11.4 = 14% (most "detected churners" aren't actually churners)

**Questions to Ask:**
- What's the base rate of the outcome?
- What's the false positive rate?
- In absolute terms, how many true vs false positives?

---

## Chart Crimes

### Truncated Y-Axis

**The Crime:** Starting the y-axis above zero to exaggerate differences.

**Example:**
```
Misleading:         Honest:
|    *              |
|   /               |
|  /                |        ___*
| /                 |    ___/
+----               +----/--------
  Time                   Time
```

**When Acceptable:**
- Clearly labeled
- Focus on small but meaningful changes
- Stock prices, scientific data where zero isn't meaningful

**Red Flags:**
- Bar charts that don't start at zero
- Dramatic-looking line charts
- No axis labels visible

---

### Dual Y-Axes Manipulation

**The Crime:** Using two y-axes scaled to imply false correlation.

**Warning Signs:**
- Two lines that track perfectly on different scales
- No justification for scale choices
- "These two things are clearly related!" (visually)

**Better Approach:**
- Use small multiples (separate charts)
- Normalize both series to same scale (% change, z-score)
- Show actual correlation coefficient

---

### 3D Charts

**The Crime:** Using 3D effects that distort perception.

**Problems:**
- Perspective makes bars/slices look different sizes
- Harder to read exact values
- No additional information conveyed
- Looks "fancy" but communicates worse

**Rule:** Never use 3D charts. Ever.

---

### Misleading Scales/Aspect Ratios

**The Crime:** Stretching or compressing charts to change perception.

**Warning Signs:**
- Very wide or very tall aspect ratios
- Log scale without clear labeling
- Different scales on comparison charts
- Broken axes

**Best Practice:**
- Standard aspect ratio (~1.6:1 or 4:3)
- Consistent scales across comparisons
- Clear axis labels with units

---

### Pie Chart Sins

**The Crimes:**
- More than 5 slices
- Slices that don't sum to 100%
- 3D pie charts
- Exploded slices
- Similar-sized slices that are hard to compare

**When Pie Charts Are OK:**
- 2-4 categories
- Parts of a whole (100%)
- Categories are very different sizes

**Better Alternatives:**
- Horizontal bar chart
- Treemap
- Simple table

---

### Area Chart Manipulation

**The Crime:** Using area to represent single-dimension data.

**Problems:**
- Area grows quadratically, not linearly
- A circle twice as wide has 4x the area
- Icons of different sizes are misleading

**Example:**
```
If sales doubled, but icon is 2x wider AND 2x taller:
Icon appears 4x larger, not 2x
```

---

## Logic Fallacies

### Correlation vs Causation

**The Fallacy:** Assuming that because two things are correlated, one causes the other.

**Classic Examples:**
- Ice cream sales correlate with drowning deaths (both caused by summer)
- Countries that eat more chocolate have more Nobel laureates (wealth confounds both)
- Feature users have lower churn (users who would retain anyway use more features)

**Questions to Ask:**
- Is there a plausible mechanism for causation?
- Could there be a third variable causing both?
- What would a randomized experiment show?

**Language Check:**
- "Associated with" - OK for correlation
- "Causes" / "Results in" / "Leads to" - Requires causal evidence

---

### Ecological Fallacy

**The Fallacy:** Assuming what's true for a group is true for individuals.

**Example:**
- "States with higher average income voted for X"
- Does NOT mean rich individuals voted for X
- Could be that poor people in rich states voted for X

**In Business:**
- "Enterprise segment has higher NPS"
- Doesn't mean every enterprise customer is happier
- Could be a few very happy customers pulling up average

**Fix:** Always check individual-level data when making individual-level claims.

---

### Regression to the Mean

**The Fallacy:** Attributing normal variation to an intervention.

**Example:**
- Sales rep has best month ever
- Gets special coaching
- Next month is worse
- "Coaching didn't work!"

**Reality:** Extreme performance naturally regresses toward average.

**Questions to Ask:**
- Was performance unusually high/low before intervention?
- What's the natural variation in this metric?
- Is there a control group?

---

### Texas Sharpshooter

**The Fallacy:** Drawing the target after the bullets are fired.

**Example:**
- Analyze 100 customer attributes
- Find one that correlates with churn
- Report as "Customers with X are 3x more likely to churn!"

**Fix:** Pre-register hypotheses or adjust for multiple testing.

---

### Availability Heuristic

**The Fallacy:** Overweighting recent or memorable examples.

**In Business:**
- "Customers hate feature X" (based on 3 loud complaints)
- "Deal sizes are increasing" (remembering recent big wins)
- "Churn is spiking" (one notable logo lost)

**Fix:** Always check the aggregate data, not just memorable examples.

---

## Sanity Checks

### The Smell Test

**Questions:**
- Does this pass the "hmm, really?" test?
- Would I bet money on this being true?
- What would a skeptic say?
- What would have to be true for this to be wrong?

**Red Flags:**
- Results that perfectly confirm what stakeholder wanted to hear
- Dramatic changes that no one noticed happening
- Findings that contradict common sense without good explanation

---

### Back-of-Envelope Validation

**Method:** Quick mental math to sanity check claims.

**Example Claims to Validate:**
```
Claim: "New feature increased revenue by $10M"
Check: Total customers * adoption rate * incremental spend
       10,000 * 20% * $X = $10M → X = $5,000 per adopter
       Does $5,000 incremental spend make sense?

Claim: "We have 150% NRR"
Check: Starting MRR * 1.5 = Ending MRR from that cohort
       If 10% churn, need 60% expansion on remaining 90%
       Does 60% expansion rate make sense?

Claim: "Response rate was 85%"
Check: Typical survey response rates are 10-30%
       85% is unusual - was this mandatory? Self-selected?
```

---

### Historical Comparison

**Always Ask:**
- How does this compare to last period?
- How does this compare to same period last year?
- Is this within normal historical range?
- What's the trend over time?

**Suspicious If:**
- Current period is dramatically different with no explanation
- Pattern breaks without known cause
- Results don't match known events (seasonality, launches, etc.)

---

### Cross-Source Validation

**Method:** Check the same metric from different sources.

**Questions:**
- Does CRM data match finance data?
- Does survey data match behavioral data?
- Do different calculation methods give similar results?

**Red Flags:**
- Large discrepancies between sources
- Only one source ever cited
- Metric definition changes between reports

---

### "Too Good to Be True" Patterns

**Watch For:**
- Perfect trends (real data is noisy)
- Round numbers (real metrics are messy)
- Results exactly matching targets/expectations
- No caveats or limitations mentioned
- Universal agreement (some customers always disagree)

**Rule of Thumb:**
```
If it seems too good to be true, it probably is.
Dig deeper or get independent verification.
```

---

## Review Workflow

When reviewing someone's analysis:

### 1. Source Check (2 min)
- Where does the data come from?
- What's the time period?
- Any known data quality issues?

### 2. Method Check (3 min)
- How was the metric calculated?
- What's excluded?
- Are comparisons apples-to-apples?

### 3. Statistical Check (3 min)
- Sample size appropriate?
- Confidence intervals provided?
- Multiple comparisons addressed?

### 4. Visual Check (2 min)
- Do charts follow best practices?
- Are scales appropriate?
- Any visual manipulation?

### 5. Logic Check (3 min)
- Causation claimed without evidence?
- Alternative explanations considered?
- Survivorship/selection bias addressed?

### 6. Sanity Check (2 min)
- Does back-of-envelope math work?
- Consistent with historical patterns?
- Would I bet money on this?

---

## Diplomatic Pushback Phrases

When you spot issues, use these to push back professionally:

**For Missing Information:**
- "Could you share the sample size and confidence interval?"
- "What time period does this cover?"
- "How is [metric] defined in this analysis?"

**For Questionable Methods:**
- "I want to make sure I understand - how was this calculated?"
- "What would this look like with [alternative baseline/method]?"
- "Have we controlled for [potential confounder]?"

**For Suspicious Results:**
- "This is interesting - it's quite different from what I expected. Can we dig in?"
- "Let me do a quick sanity check on the math here..."
- "What would cause this to be wrong?"

**For Chart Issues:**
- "Could we see this with the y-axis starting at zero?"
- "Would it help to show this as [alternative chart type]?"
- "I'm having trouble reading the scale here..."

---

## Summary Checklist

```markdown
## BS Detection Summary

### Before Presenting
- [ ] All data sources documented
- [ ] Sample sizes and confidence intervals included
- [ ] Charts follow best practices
- [ ] Alternative explanations considered
- [ ] Caveats and limitations stated
- [ ] Back-of-envelope math verified
- [ ] Historical context provided

### Before Accepting
- [ ] Passed smell test
- [ ] Method understood and appropriate
- [ ] Statistical validity confirmed
- [ ] Visual integrity verified
- [ ] Logic checked for fallacies
- [ ] Cross-validated where possible
```
