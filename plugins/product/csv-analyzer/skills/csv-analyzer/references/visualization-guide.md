# Visualization Guide

## Overview

The CSV Analyzer generates up to 10 visualizations automatically, selecting the most appropriate charts based on your data types.

## Charts Generated

### 1. Overview Dashboard (`overview_dashboard.png`)

**What it shows:**
- Column types pie chart
- Top 10 columns with missing values
- Quality score gauge (0-100)
- Summary statistics table
- Sample histogram (first numeric column)
- Sample bar chart (first categorical column)

**Best for:** Quick data assessment, presentations

### 2. Missing Values (`missing_values.png`)

**What it shows:**
- Left: Heatmap showing missing value patterns (rows × columns)
- Right: Bar chart of missing counts by column

**Best for:** Identifying missing data patterns
- Vertical stripes = column has many missing
- Horizontal stripes = rows have many missing
- Clusters = correlated missing values

### 3. Numeric Distributions (`numeric_distributions.png`)

**What it shows:**
- Histogram with KDE (kernel density estimate) for each numeric column
- Mean (red dashed line) and median (green dotted line)

**Best for:**
- Understanding data spread
- Identifying skewness
- Detecting bimodal/multimodal distributions

**Interpretation:**
- Bell curve = normal distribution
- Long right tail = right-skewed (consider log transform)
- Multiple peaks = potential subgroups in data

### 4. Box Plots (`box_plots.png`)

**What it shows:**
- Box-and-whisker plots for all numeric columns
- Normalized for comparison (z-scored)

**Components:**
```
       ┌───┬───┐
       │   │   │   ← Max (within 1.5×IQR)
       ├───┼───┤
       │███│███│   ← Q3 (75th percentile)
       │███│███│
       │═══│═══│   ← Median
       │███│███│
       │███│███│   ← Q1 (25th percentile)
       ├───┼───┤
       │   │   │   ← Min (within 1.5×IQR)
       └───┴───┘
           ○       ← Outliers (beyond whiskers)
```

**Best for:** Outlier detection, comparing distributions

### 5. Correlation Heatmap (`correlation_heatmap.png`)

**What it shows:**
- Pairwise Pearson correlations between numeric columns
- Color scale: Blue (negative) → White (zero) → Red (positive)
- Values annotated in cells

**Best for:**
- Feature selection (highly correlated = redundant)
- Identifying predictive relationships
- Multicollinearity detection

**Reading tips:**
- Dark red (>0.7) = strong positive correlation
- Dark blue (<-0.7) = strong negative correlation
- White (~0) = no linear relationship

### 6. Categorical Distributions (`categorical_distributions.png`)

**What it shows:**
- Horizontal bar charts for top 10 values in each categorical column
- Percentage labels on bars

**Best for:**
- Understanding category balance
- Identifying dominant categories
- Spotting rare categories

### 7. Time Series (`time_series.png`)

**When generated:** Only if datetime columns detected

**What it shows:**
- Line plots of numeric columns over time
- 7-day moving average overlay (if many data points)

**Best for:**
- Trend identification
- Seasonality detection
- Anomaly spotting

### 8. Pair Plot (`pairplot.png`)

**When generated:** 2-6 numeric columns

**What it shows:**
- Matrix of scatter plots (off-diagonal)
- KDE distributions (diagonal)
- All pairwise combinations

**Best for:**
- Multivariate relationship exploration
- Cluster identification
- Non-linear relationship detection

**Note:** Limited to 1000 samples for performance

### 9. Violin Plot (`violin_plot.png`)

**When generated:** If categorical + numeric columns exist

**What it shows:**
- Distribution of a numeric column across categories
- Combines box plot + KDE

**Best for:**
- Comparing distributions across groups
- Identifying differences between categories

## Customization

### Color Palettes

The analyzer uses `seaborn`'s `husl` palette by default. To customize:

```python
# In analyze_csv.py, modify:
sns.set_palette("husl")  # Change to: "Set2", "deep", "muted", etc.
```

### Figure Sizes

Default sizes optimized for reports:
- Dashboard: 16×10 inches
- Standard charts: 14×6 to 14×10 inches
- Pair plot: Auto-sized based on columns

### DPI Settings

Default: 150 DPI (good balance of quality/size)
- For print: Increase to 300
- For web: 100 is sufficient

### Style

Uses `seaborn-v0_8-whitegrid` style. Alternatives:
- `seaborn-v0_8-darkgrid` - Grid with dark background
- `seaborn-v0_8-white` - Clean white background
- `ggplot` - R's ggplot2 style

## Output Formats

### PNG (Default)

- Universal compatibility
- Good for reports and presentations
- Rasterized (doesn't scale infinitely)

### SVG (For Web)

Modify the script to use:
```python
plt.savefig(path.with_suffix('.svg'), format='svg')
```

### PDF (For Print)

```python
plt.savefig(path.with_suffix('.pdf'), format='pdf')
```

## Performance Tips

### Large Datasets

Charts automatically sample data:
- Scatter plots: max 1000 points
- Missing value heatmap: max 100 rows
- Pair plots: max 1000 rows

### Memory Management

- Charts are closed after saving (`plt.close()`)
- Use `--no-charts` for analysis-only mode
- Reduce `--max-charts` if needed

### Speed Optimization

Most time-consuming:
1. Pair plot (N² scatter plots)
2. Missing values heatmap (for wide data)
3. Time series (sorting + aggregation)

Use `--max-charts 5` for faster runs.

## Common Issues

### Charts Look Squished

**Cause:** Too many columns/categories
**Solution:** The analyzer limits to top 10 categories and 6 numeric columns

### Text Overlapping

**Cause:** Long column names
**Solution:** Rotation is applied automatically; consider shorter names

### Charts Not Saving

**Cause:** Permission or path issues
**Solution:** Check `--output-dir` is writable

### Memory Error on Charts

**Cause:** Too much data
**Solution:** Use `--sample` flag to reduce data size
