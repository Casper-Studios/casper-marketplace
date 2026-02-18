# Data Wishlisting Guide

Document data gaps, evaluate proxies, and rate quality of workarounds. Every analysis should include a wishlist of ideal data that wasn't available.

---

## Why Wishlist Data?

1. **Transparency** - Stakeholders know what's missing
2. **Prioritization** - Helps data team know what to collect
3. **Hedge appropriately** - Findings are qualified correctly
4. **Future-proofing** - Next iteration can improve

---

## Wishlist Format

Use this table format in every analysis:

```markdown
## Data Wishlist

| Missing Data | Proxy Used | Quality | Impact on Analysis | Data Source If Available |
|--------------|------------|---------|-------------------|--------------------------|
| [Ideal data] | [What we used instead] | Strong/Moderate/Weak | [How it affects findings] | [Where we could get it] |
```

### Example

```markdown
## Data Wishlist

| Missing Data | Proxy Used | Quality | Impact on Analysis | Data Source If Available |
|--------------|------------|---------|-------------------|--------------------------|
| Customer NPS scores | Support ticket sentiment | Weak | Core finding re: satisfaction needs validation | Quarterly NPS survey (Delighted) |
| True customer LTV | 12-month revenue | Moderate | Acceptable for segmentation, not for CAC analysis | 24+ month cohort tracking |
| Marketing attribution | Last-touch attribution | Weak | Cannot assess multi-channel impact | Multi-touch attribution tool |
| Product usage depth | Login frequency | Moderate | Directionally correct, misses engagement quality | In-app analytics (Amplitude) |
```

---

## Quality Rating Scale

### Strong

**Definition:** Proxy closely approximates the ideal data with minimal information loss.

**Characteristics:**
- High correlation with ideal metric (r > 0.8)
- Same underlying construct
- Validated in similar contexts
- Widely accepted in industry

**Examples:**
| Ideal Data | Strong Proxy |
|------------|--------------|
| Total contract value | Sum of invoices (complete billing data) |
| Active users | Users with activity in last 30 days |
| Revenue retention | MRR comparison period-over-period |

### Moderate

**Definition:** Proxy provides directional signal but has known limitations.

**Characteristics:**
- Moderate correlation with ideal (0.5 < r < 0.8)
- Captures part of the construct
- Some information loss
- Requires caveats in interpretation

**Examples:**
| Ideal Data | Moderate Proxy |
|------------|----------------|
| Customer lifetime value | 12-month cumulative revenue |
| Product satisfaction | Feature adoption rate |
| Sales capacity | Quota attainment |
| Market size | Top-down estimate from reports |

### Weak

**Definition:** Proxy provides rough signal with significant limitations. Use with heavy caveats.

**Characteristics:**
- Low correlation with ideal (r < 0.5)
- Different underlying construct
- Significant information loss
- Should note as "directional only"

**Examples:**
| Ideal Data | Weak Proxy |
|------------|------------|
| Customer NPS | Support ticket sentiment |
| Marketing ROI | Last-touch attribution |
| Employee satisfaction | Voluntary turnover |
| Feature value | Click count |

---

## Common Proxy Patterns by Domain

### Revenue & Finance

| Missing | Common Proxy | Quality | Notes |
|---------|--------------|---------|-------|
| True LTV | 12-24 month value | Moderate | Improve as cohorts age |
| CAC by channel | Blended CAC | Weak | Need attribution |
| Expansion potential | Current contract value | Moderate | Whitespace analysis helps |
| Churn risk | Engagement decline | Moderate | Combine with other signals |

### Customer Success

| Missing | Common Proxy | Quality | Notes |
|---------|--------------|---------|-------|
| NPS | Support sentiment | Weak | Different construct |
| Health score | Composite of signals | Moderate | Depends on signals |
| Satisfaction | Renewal rate | Moderate | Lagging indicator |
| Feature value | Usage frequency | Moderate | Missing engagement quality |

### Sales & Pipeline

| Missing | Common Proxy | Quality | Notes |
|---------|--------------|---------|-------|
| Win probability | Stage-based rates | Moderate | Improve with ML |
| Deal timeline | Historical averages | Moderate | High variance |
| Decision maker sentiment | Email engagement | Weak | Very indirect |
| Competitive intel | Win/loss reasons | Moderate | Self-reported bias |

### Marketing

| Missing | Common Proxy | Quality | Notes |
|---------|--------------|---------|-------|
| True attribution | Last touch | Weak | Misses multi-touch |
| Brand awareness | Direct traffic | Weak | Many confounders |
| Content engagement | Time on page | Moderate | Doesn't measure comprehension |
| Lead quality | Form completeness | Weak | Gaming risk |

---

## Derivation Patterns

When the exact data doesn't exist, sometimes you can derive it from combinations of available data.

### Pattern: Calculate from Components

**Example:** Gross margin % not available

```python
# Derive from available data
gross_margin_pct = (revenue - cogs) / revenue * 100

# Log the derivation
# DERIVED: Gross margin calculated from revenue and COGS
# ASSUMPTION: COGS is complete - confidence: High
```

### Pattern: Impute from Segments

**Example:** Missing values in a field

```python
# Use segment averages for imputation
df['value_imputed'] = df.groupby('segment')['value'].transform(
    lambda x: x.fillna(x.median())
)

# Log the imputation
# DERIVED: Missing values imputed with segment median (n=47 records)
# QUALITY: Moderate - assumes within-segment similarity
```

### Pattern: Historical Averages

**Example:** Forecasting without complete data

```python
# Use historical patterns
seasonal_factor = historical_data.groupby('month').mean()

# Log the assumption
# DERIVED: Seasonal factors from 2022-2023 data
# ASSUMPTION: Seasonality consistent year-over-year - confidence: Medium
```

### Pattern: Proxy Combination

**Example:** Health score from multiple weak signals

```python
# Combine multiple weak proxies into stronger composite
health_score = (
    0.3 * normalized_login_frequency +
    0.3 * normalized_feature_adoption +
    0.2 * normalized_support_tickets_inverse +
    0.2 * normalized_nps_score
)

# Log the construction
# DERIVED: Health score composite from 4 signals
# QUALITY: Moderate - validated against historical churn (AUC=0.72)
```

---

## Impact Assessment

For each data gap, assess how it affects your analysis:

### High Impact

- Affects core finding or recommendation
- Would change conclusion if different
- Central to the analysis question

**Action:** Heavy caveats, consider waiting for better data, flag as preliminary

### Medium Impact

- Affects supporting analysis
- Wouldn't change main conclusion
- Useful but not critical

**Action:** Note in methodology, include in appendix

### Low Impact

- Nice to have
- Marginal improvement
- Doesn't affect conclusions

**Action:** Note in wishlist, deprioritize for future collection

---

## Wishlist Template

Copy this to your analysis notebook:

```markdown
## Data Wishlist

### High Impact Gaps

| Missing | Proxy | Quality | Impact | Source |
|---------|-------|---------|--------|--------|
| | | | | |

### Medium Impact Gaps

| Missing | Proxy | Quality | Impact | Source |
|---------|-------|---------|--------|--------|
| | | | | |

### Low Impact Gaps

| Missing | Proxy | Quality | Impact | Source |
|---------|-------|---------|--------|--------|
| | | | | |

### Derivations Used

| Derived Metric | Components | Method | Confidence |
|----------------|------------|--------|------------|
| | | | |

### Recommendations for Data Collection

1. [Highest priority data to start collecting]
2. [Second priority]
3. [Third priority]
```

---

## Decision Log Format

When using proxies, log them:

```python
# PROXY: Support ticket sentiment for NPS - quality: Weak
# IMPACT: Core finding - needs validation with actual NPS data
# RATIONALE: Only available satisfaction signal; directional use only

# DERIVED: LTV calculated as 24-month cumulative revenue
# ASSUMPTION: Customer relationships > 24 months follow similar pattern
# CONFIDENCE: Medium - based on cohort analysis showing stabilization at 18mo
```
