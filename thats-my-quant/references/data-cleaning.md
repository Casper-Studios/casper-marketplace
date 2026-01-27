# Data Cleaning Reference

Data quality checklist, common transforms, and cleaning patterns for financial and RevOps data.

---

## Data Quality Dimensions

Before cleaning, assess data quality across these dimensions:

| Dimension | Question | Check |
|-----------|----------|-------|
| **Completeness** | Are there missing values? | `df.isnull().sum()` |
| **Accuracy** | Are values correct and realistic? | Domain validation |
| **Consistency** | Are formats and values uniform? | `df[col].unique()` |
| **Timeliness** | Is the data current enough? | Check date ranges |
| **Uniqueness** | Are there duplicates? | `df.duplicated().sum()` |
| **Validity** | Do values match expected formats/ranges? | Schema validation |

---

## Pre-Cleaning Checklist

Run this checklist before any analysis:

```python
def data_quality_check(df, name="Dataset"):
    """Run comprehensive data quality check."""
    print(f"=== DATA QUALITY CHECK: {name} ===\n")

    # Shape
    print(f"Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")

    # Missing values
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(1)
    missing_df = pd.DataFrame({
        'missing': missing,
        'pct': missing_pct
    }).query('missing > 0').sort_values('pct', ascending=False)

    if len(missing_df) > 0:
        print(f"\n Missing Values:")
        print(missing_df.to_string())
    else:
        print("\n No missing values")

    # Duplicates
    dupes = df.duplicated().sum()
    print(f"\n Duplicates: {dupes:,} ({dupes/len(df)*100:.1f}%)")

    # Data types
    print(f"\n Data Types:")
    print(df.dtypes.value_counts().to_string())

    return missing_df
```

---

## Missing Value Strategies

### Strategy Selection Guide

```
Is the missing data random (MCAR)?
├── YES → Safe to drop or impute
│   ├── < 5% missing → Drop rows
│   ├── 5-20% missing → Impute
│   └── > 20% missing → Flag column, consider dropping
└── NO (systematic) → Understand why before handling
    ├── MNAR (value-dependent) → Model the missingness
    └── MAR (dependent on other columns) → Conditional imputation
```

### Drop Strategies

```python
# Drop rows with any missing values (use sparingly)
df_clean = df.dropna()

# Drop rows with missing values in specific columns
df_clean = df.dropna(subset=['critical_column'])

# Drop columns with too many missing values
threshold = 0.3  # 30% missing
cols_to_drop = df.columns[df.isnull().mean() > threshold]
df_clean = df.drop(columns=cols_to_drop)

# Log the decision
# FILTER: Dropped 247 rows with missing revenue values
# RATIONALE: Revenue is required for analysis, < 2% of data
```

### Imputation Strategies

| Data Type | Strategy | When to Use |
|-----------|----------|-------------|
| Numeric | Mean/median | Normal/skewed distributions |
| Numeric | Mode | Categorical-ish numbers |
| Numeric | Forward/back fill | Time series data |
| Categorical | Mode | Most common category |
| Categorical | 'Unknown' | Preserve missingness signal |
| Time series | Interpolation | Regular intervals |

```python
# Numeric imputation
df['value'] = df['value'].fillna(df['value'].median())

# Segment-based imputation (better for heterogeneous data)
df['value'] = df.groupby('segment')['value'].transform(
    lambda x: x.fillna(x.median())
)

# Categorical imputation
df['category'] = df['category'].fillna('Unknown')

# Time series interpolation
df['metric'] = df['metric'].interpolate(method='linear')

# Log imputation decisions
# IMPUTE: Filled 142 missing deal_size values with segment median
# QUALITY: Moderate - assumes within-segment similarity
```

### Flag Missing Data

Sometimes preserving the fact that data was missing is valuable:

```python
# Create indicator for missingness
df['value_was_missing'] = df['value'].isnull().astype(int)

# Then impute
df['value'] = df['value'].fillna(df['value'].median())

# Log the approach
# DERIVED: value_was_missing flag for ML feature
# RATIONALE: Missingness may be predictive of outcome
```

---

## Outlier Detection

### Detection Methods

| Method | Formula | Best For |
|--------|---------|----------|
| IQR | < Q1 - 1.5*IQR or > Q3 + 1.5*IQR | Most cases |
| Z-score | \|z\| > 3 | Normal distributions |
| MAD | \|x - median\| / MAD > 3 | Robust to extremes |
| Domain | Business rules | Known constraints |

```python
def detect_outliers_iqr(series, multiplier=1.5):
    """Detect outliers using IQR method."""
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - multiplier * IQR
    upper = Q3 + multiplier * IQR

    outliers = (series < lower) | (series > upper)
    return outliers, lower, upper

def detect_outliers_zscore(series, threshold=3):
    """Detect outliers using z-score."""
    z_scores = (series - series.mean()) / series.std()
    return abs(z_scores) > threshold
```

### Handling Outliers

```
Is the outlier a data error?
├── YES (impossible value) → Fix or remove
│   └── e.g., negative revenue, 200% churn rate
└── NO (extreme but valid)
    ├── Keep but flag → Mark for separate analysis
    ├── Winsorize → Cap at percentile threshold
    └── Transform → Log transform for skewed data
```

```python
# Cap outliers at percentiles (winsorization)
def winsorize(series, lower_pct=0.01, upper_pct=0.99):
    """Cap values at percentile thresholds."""
    lower = series.quantile(lower_pct)
    upper = series.quantile(upper_pct)
    return series.clip(lower=lower, upper=upper)

# Log transform for right-skewed data
df['revenue_log'] = np.log1p(df['revenue'])  # log(1+x) handles zeros

# Flag outliers for review
outliers, lower, upper = detect_outliers_iqr(df['deal_size'])
df['deal_size_outlier'] = outliers

# Log the decision
# OUTLIER: Capped 23 deal_size values at 99th percentile ($500K)
# RATIONALE: Valid large deals but skewing averages
```

---

## Common Transforms

### Pivot and Melt

```python
# Wide to long (melt)
df_long = df.melt(
    id_vars=['customer_id', 'date'],
    value_vars=['mrr_jan', 'mrr_feb', 'mrr_mar'],
    var_name='month',
    value_name='mrr'
)

# Long to wide (pivot)
df_wide = df.pivot_table(
    index='customer_id',
    columns='month',
    values='mrr',
    aggfunc='sum'
).reset_index()

# Log transformation
# TRANSFORM: Pivoted monthly MRR to wide format for cohort analysis
```

### Merge Patterns

```python
# Inner join (keep only matches)
df_merged = df1.merge(df2, on='customer_id', how='inner')

# Left join (keep all from left)
df_merged = df1.merge(df2, on='customer_id', how='left')

# Check for merge issues
print(f"Left rows: {len(df1)}")
print(f"Merged rows: {len(df_merged)}")
print(f"Unmatched: {len(df1) - len(df_merged)}")

# Handle many-to-many carefully
# Log merge decisions
# MERGE: Joined customers to transactions on customer_id
# NOTE: 47 customers had no transactions (excluded from analysis)
```

### GroupBy Patterns

```python
# Basic aggregation
summary = df.groupby('segment').agg({
    'revenue': ['sum', 'mean', 'median', 'count'],
    'churn': 'mean'
}).round(2)

# Multiple grouping levels
summary = df.groupby(['segment', 'month']).agg({
    'mrr': 'sum',
    'customers': 'nunique'
}).reset_index()

# Rolling calculations
df['mrr_3mo_avg'] = df.groupby('customer_id')['mrr'].transform(
    lambda x: x.rolling(3, min_periods=1).mean()
)

# Percentage of total
df['pct_of_total'] = df.groupby('segment')['revenue'].transform(
    lambda x: x / x.sum() * 100
)
```

---

## Type Coercion Recipes

### Numeric Coercion

```python
# String to numeric (handle errors)
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
# 'coerce' turns unparseable values to NaN

# Remove currency symbols and convert
df['price'] = (df['price']
    .str.replace('$', '', regex=False)
    .str.replace(',', '', regex=False)
    .astype(float)
)

# Percentage strings to float
df['rate'] = (df['rate']
    .str.rstrip('%')
    .astype(float) / 100
)
```

### Categorical Coercion

```python
# String to category (memory efficient)
df['segment'] = df['segment'].astype('category')

# Ordered categories
segment_order = ['SMB', 'Mid-Market', 'Enterprise']
df['segment'] = pd.Categorical(
    df['segment'],
    categories=segment_order,
    ordered=True
)

# Boolean coercion
df['is_active'] = df['status'].map({'Active': True, 'Inactive': False})
```

### Date Coercion

```python
# String to datetime
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

# Multiple formats (let pandas infer)
df['date'] = pd.to_datetime(df['date'], infer_datetime_format=True)

# Handle errors
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Extract components
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['quarter'] = df['date'].dt.quarter
df['day_of_week'] = df['date'].dt.dayofweek
```

---

## Deduplication Patterns

### Identify Duplicates

```python
# Exact duplicates (all columns)
dupes = df[df.duplicated(keep=False)]

# Duplicates on specific columns
dupes = df[df.duplicated(subset=['customer_id', 'date'], keep=False)]

# Count duplicates
dupe_counts = df.groupby(['customer_id', 'date']).size()
dupe_counts[dupe_counts > 1]
```

### Handle Duplicates

```python
# Keep first occurrence
df_deduped = df.drop_duplicates(keep='first')

# Keep last occurrence (often want most recent)
df_deduped = df.drop_duplicates(
    subset=['customer_id', 'date'],
    keep='last'
)

# Aggregate duplicates
df_deduped = df.groupby(['customer_id', 'date']).agg({
    'revenue': 'sum',      # Sum values
    'status': 'last',       # Keep last status
    'notes': lambda x: '; '.join(x.dropna())  # Concatenate
}).reset_index()

# Log deduplication
# DEDUP: Removed 156 duplicate customer-date records, kept most recent
```

---

## Data Smell Detection

Common suspicious patterns to check for:

### Suspicious Distributions

```python
def check_suspicious_patterns(df, column):
    """Flag suspicious data patterns."""
    series = df[column].dropna()

    issues = []

    # Excessive zeros
    zero_pct = (series == 0).mean() * 100
    if zero_pct > 50:
        issues.append(f"High zero rate: {zero_pct:.1f}%")

    # Suspiciously round numbers
    round_pct = (series % 100 == 0).mean() * 100
    if round_pct > 30:
        issues.append(f"Many round numbers: {round_pct:.1f}%")

    # Negative values where unexpected
    if series.min() < 0 and 'revenue' in column.lower():
        issues.append(f"Negative values present")

    # Single value dominance
    mode_pct = (series == series.mode()[0]).mean() * 100
    if mode_pct > 50:
        issues.append(f"Single value dominates: {mode_pct:.1f}%")

    return issues
```

### Common Data Smells

| Smell | Pattern | Likely Issue |
|-------|---------|--------------|
| Spike at round numbers | 100, 1000, 10000 | Manual entry, estimates |
| Excessive nulls in recent data | Nulls increasing over time | ETL failure, schema change |
| Future dates | Dates > today | Data entry error |
| Negative durations | End < start | Timestamp issues |
| Perfect correlation | r = 1.0 | Derived columns, data leakage |
| Uniform distribution | Equal frequencies | Synthetic or test data |

### Referential Integrity Checks

```python
# Check foreign key relationships
missing_customers = set(transactions['customer_id']) - set(customers['customer_id'])
if missing_customers:
    print(f"WARNING: {len(missing_customers)} transactions have unknown customers")

# Check date ranges align
if transactions['date'].max() > customers['signup_date'].max():
    print("WARNING: Transactions exist after latest customer signup")

# Check value ranges
invalid_rates = df[df['churn_rate'] > 1.0]
if len(invalid_rates) > 0:
    print(f"WARNING: {len(invalid_rates)} records have churn rate > 100%")
```

---

## Cleaning Pipeline Template

```python
def clean_pipeline(df):
    """
    Standard cleaning pipeline. Customize per dataset.

    Returns cleaned df and cleaning log.
    """
    log = []
    df = df.copy()
    original_rows = len(df)

    # 1. Remove exact duplicates
    df = df.drop_duplicates()
    log.append(f"DEDUP: Removed {original_rows - len(df)} exact duplicates")

    # 2. Standardize column names
    df.columns = df.columns.str.lower().str.replace(' ', '_')

    # 3. Parse dates
    date_cols = ['created_at', 'updated_at', 'date']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # 4. Handle missing values
    # (customize based on columns)

    # 5. Validate ranges
    # (customize based on domain)

    # 6. Create derived columns
    # (customize based on needs)

    log.append(f"FINAL: {len(df)} rows, {len(df.columns)} columns")

    return df, log
```

---

## Decision Logging for Cleaning

Log every cleaning decision:

```python
# === CLEANING LOG ===
# FILTER: Removed 247 rows with null revenue (1.6% of data)
# IMPUTE: Filled 89 missing segment values with 'Unknown'
# OUTLIER: Capped deal_size at 99th percentile (23 values affected)
# DEDUP: Removed 156 duplicate customer-month records, kept latest
# TRANSFORM: Converted revenue from cents to dollars
# DERIVED: Created mrr_change = current_mrr - prior_mrr
```

---

## Quality Score Template

Grade overall data quality:

| Grade | Criteria |
|-------|----------|
| **A** | < 2% missing, no duplicates, passes all validations |
| **B** | 2-5% missing, minor duplicates, minor validation issues |
| **C** | 5-15% missing, some duplicates, some validation issues |
| **D** | 15-30% missing, significant issues |
| **F** | > 30% missing or critical validation failures |

```python
def calculate_quality_score(df):
    """Calculate data quality score A-F."""
    missing_pct = df.isnull().mean().mean() * 100
    dupe_pct = df.duplicated().mean() * 100

    # Simple scoring (customize based on domain)
    score = 100 - missing_pct - dupe_pct

    if score >= 95: return 'A'
    elif score >= 85: return 'B'
    elif score >= 70: return 'C'
    elif score >= 50: return 'D'
    else: return 'F'
```
