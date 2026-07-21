# Analysis Methodology Guide

## Overview

This guide explains the statistical methods and algorithms used by the CSV Analyzer.

## Data Quality Assessment

### Quality Score Calculation

The quality score (0-100) is calculated as:

```
score = completeness - duplicate_penalty
```

Where:
- **Completeness** = 100 - (average missing % across columns)
- **Duplicate Penalty** = min(20, duplicate_rows / total_rows × 100)

### Grade Scale

| Score | Grade | Label |
|-------|-------|-------|
| 90-100 | A | Excellent |
| 80-89 | B | Good |
| 70-79 | C | Fair |
| 60-69 | D | Poor |
| 0-59 | F | Critical |

### Missing Value Analysis

- **Total Missing**: Sum of all null/NaN cells
- **Missing %**: Per-column and total percentages
- **Pattern Detection**: Heatmap shows if missing values cluster

## Statistical Analysis

### Descriptive Statistics

For each numeric column:

| Statistic | Formula | Interpretation |
|-----------|---------|----------------|
| Mean | Σx / n | Central tendency |
| Std | √(Σ(x-μ)²/n) | Spread/dispersion |
| Min/Max | min(x), max(x) | Range boundaries |
| Q1, Q3 | 25th, 75th percentile | Distribution quartiles |
| Median | 50th percentile | Robust central measure |
| IQR | Q3 - Q1 | Interquartile range |
| Skewness | E[(X-μ)³]/σ³ | Asymmetry measure |
| Kurtosis | E[(X-μ)⁴]/σ⁴ - 3 | Tail heaviness |

### Skewness Interpretation

| Value | Interpretation |
|-------|----------------|
| < -1 | Highly left-skewed (long left tail) |
| -1 to -0.5 | Moderately left-skewed |
| -0.5 to 0.5 | Approximately symmetric |
| 0.5 to 1 | Moderately right-skewed |
| > 1 | Highly right-skewed (long right tail) |

**Recommendation**: Highly skewed data (|skew| > 2) may benefit from log transformation.

### Normality Testing

Uses the **Shapiro-Wilk test**:
- H0: Data is normally distributed
- p-value > 0.05: Cannot reject normality
- p-value ≤ 0.05: Data is not normal

**Limitations**: Only performed on samples ≤ 5000 rows.

## Correlation Analysis

### Pearson Correlation

Measures linear relationship between variables:

```
r = Σ[(xi - x̄)(yi - ȳ)] / √[Σ(xi - x̄)² × Σ(yi - ȳ)²]
```

### Interpretation

| |r| Value | Strength |
|-----------|----------|
| 0.0 - 0.3 | Negligible |
| 0.3 - 0.5 | Weak |
| 0.5 - 0.7 | Moderate |
| 0.7 - 0.9 | Strong |
| 0.9 - 1.0 | Very strong |

**Sign**: Positive = variables move together; Negative = inverse relationship

## Outlier Detection

### IQR Method

```
Lower Bound = Q1 - 1.5 × IQR
Upper Bound = Q3 + 1.5 × IQR
Outlier = value < Lower Bound OR value > Upper Bound
```

**Why 1.5?** In a normal distribution, this captures ~99.3% of data. Values outside are statistically unusual.

### Z-Score Method

```
z = (x - μ) / σ
Outlier = |z| > 3
```

**Why 3?** In a normal distribution, 99.7% of data falls within 3 standard deviations.

### Significant Outliers Flag

Set to `true` if > 5% of values are outliers. Indicates data quality issues or natural heavy tails.

## Categorical Analysis

### Entropy Calculation

Measures diversity/randomness in category distribution:

```
H = -Σ(pi × log2(pi))
```

Where pi is the proportion of each category.

### Normalized Entropy

```
H_normalized = H / log2(n_categories)
```

| Value | Interpretation |
|-------|----------------|
| > 0.8 | Balanced distribution |
| 0.5 - 0.8 | Moderate imbalance |
| < 0.5 | Highly imbalanced |

## Temporal Analysis

### Metrics Calculated

- **Date Range**: Min to max date
- **Span**: Days between first and last record
- **Records/Day**: Total records ÷ span days
- **Most Common Day**: Mode of day-of-week
- **Most Common Month**: Mode of month

### Time Series Aggregation

For visualization:
- If > 365 data points: Resample to daily averages
- 7-day moving average overlaid for trend

## Column Type Classification

### Detection Rules

| Type | Rule |
|------|------|
| Numeric | pandas numeric dtypes (int, float) |
| DateTime | datetime64 or contains 'date'/'time' in name |
| Boolean | Numeric with only values {0, 1} |
| ID | Contains 'id'/'uuid'/'key' or unique per row |
| Categorical | Object dtype with ≤ 50 unique values |
| Text | Object dtype with > 50 unique values |

## Large File Handling

### Automatic Sampling

Triggered when:
- File size > 100MB
- User specifies `--sample`

### Sampling Method

Random sampling without replacement:
```python
skip_rows = random.choice(range(1, total_rows), size=total_rows - sample_size)
```

Preserves distribution characteristics while reducing memory usage.

## Performance Considerations

| File Size | Rows | Expected Time |
|-----------|------|---------------|
| < 10 MB | < 100K | < 5 seconds |
| 10-100 MB | 100K-1M | 5-30 seconds |
| > 100 MB | > 1M | Use sampling |

### Memory Optimization

- Charts use sampled data (max 1000 points for scatter)
- Correlation matrix limited to numeric columns
- Pairplot limited to 5 columns
