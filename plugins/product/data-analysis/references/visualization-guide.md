# Visualization Guide

Chart selection logic, anti-patterns to avoid, and Matplotlib/Seaborn code patterns for financial and RevOps analysis.

---

## Chart Selection Decision Tree

```
What are you showing?
│
├── CHANGE OVER TIME
│   └── Line chart
│       └── Multiple series? Use distinct colors, consider small multiples
│
├── COMPARISON
│   ├── Few categories (< 7)?
│   │   └── Vertical bar chart
│   └── Many categories (7+)?
│       └── Horizontal bar chart (easier to read labels)
│
├── DISTRIBUTION
│   ├── Single variable?
│   │   └── Histogram or box plot
│   └── Compare distributions?
│       └── Side-by-side box plots or overlaid histograms
│
├── RELATIONSHIP
│   ├── Two variables?
│   │   └── Scatter plot
│   └── Multiple variables?
│       └── Pair plot or correlation heatmap
│
├── COMPOSITION
│   ├── Parts of a whole at one point?
│   │   ├── Few parts (< 5)?
│   │   │   └── Pie chart (use sparingly)
│   │   └── More parts?
│   │       └── Stacked bar chart
│   └── Parts over time?
│       └── Stacked area or 100% stacked bar
│
└── RANKING
    └── Horizontal bar chart (sorted)
```

---

## Chart Type Reference

### Time Series - Line Chart

**Use when:** Showing trends, patterns over time

**Best practices:**
- Start y-axis at zero (or clearly label if not)
- Limit to 4-5 lines max
- Use consistent time intervals
- Mark significant events with annotations

```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_time_series(df, x_col, y_col, title, hue_col=None):
    """Create a clean time series line chart."""
    fig, ax = plt.subplots(figsize=(10, 6))

    if hue_col:
        for label in df[hue_col].unique():
            subset = df[df[hue_col] == label]
            ax.plot(subset[x_col], subset[y_col], label=label, linewidth=2)
        ax.legend(loc='upper left', frameon=False)
    else:
        ax.plot(df[x_col], df[y_col], linewidth=2, color='#2E86AB')

    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('')
    ax.set_ylabel(y_col)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    return fig, ax
```

### Comparison - Bar Chart

**Use when:** Comparing values across categories

**Best practices:**
- Sort bars by value (unless natural order exists)
- Use horizontal bars for many categories or long labels
- Start y-axis at zero
- Use consistent colors (highlight key bar if needed)

```python
def plot_bar_comparison(df, category_col, value_col, title, horizontal=False):
    """Create a comparison bar chart."""
    # Sort by value
    df_sorted = df.sort_values(value_col, ascending=horizontal)

    fig, ax = plt.subplots(figsize=(10, 6))

    if horizontal:
        ax.barh(df_sorted[category_col], df_sorted[value_col], color='#2E86AB')
        ax.set_xlabel(value_col)
    else:
        ax.bar(df_sorted[category_col], df_sorted[value_col], color='#2E86AB')
        ax.set_ylabel(value_col)
        plt.xticks(rotation=45, ha='right')

    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    return fig, ax
```

### Distribution - Histogram/Box Plot

**Use when:** Understanding spread of values

**Best practices:**
- Choose appropriate bin width for histograms
- Show outliers clearly in box plots
- Add median/mean annotations when useful

```python
def plot_distribution(data, title, bins=30):
    """Create a histogram with KDE overlay."""
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(data, bins=bins, color='#2E86AB', alpha=0.7, edgecolor='white')

    # Add mean and median lines
    mean_val = data.mean()
    median_val = data.median()
    ax.axvline(mean_val, color='red', linestyle='--', label=f'Mean: {mean_val:.2f}')
    ax.axvline(median_val, color='orange', linestyle='-', label=f'Median: {median_val:.2f}')

    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.legend(frameon=False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    return fig, ax
```

### Relationship - Scatter Plot

**Use when:** Exploring correlation between two variables

**Best practices:**
- Add trend line if relationship exists
- Use color/size to encode additional dimensions
- Consider sampling if > 10,000 points

```python
def plot_scatter(df, x_col, y_col, title, hue_col=None, add_trend=True):
    """Create a scatter plot with optional trend line."""
    fig, ax = plt.subplots(figsize=(10, 6))

    if hue_col:
        scatter = ax.scatter(df[x_col], df[y_col], c=df[hue_col],
                            cmap='viridis', alpha=0.6, s=50)
        plt.colorbar(scatter, label=hue_col)
    else:
        ax.scatter(df[x_col], df[y_col], color='#2E86AB', alpha=0.6, s=50)

    if add_trend:
        import numpy as np
        z = np.polyfit(df[x_col], df[y_col], 1)
        p = np.poly1d(z)
        x_line = np.linspace(df[x_col].min(), df[x_col].max(), 100)
        ax.plot(x_line, p(x_line), color='red', linestyle='--', linewidth=2)

    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    return fig, ax
```

### Cohort Analysis - Heatmap

**Use when:** Showing retention cohorts, matrix data

```python
def plot_cohort_heatmap(cohort_df, title):
    """Create a cohort retention heatmap."""
    fig, ax = plt.subplots(figsize=(12, 8))

    sns.heatmap(cohort_df, annot=True, fmt='.0%', cmap='Blues',
                ax=ax, cbar_kws={'label': 'Retention Rate'})

    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Months Since Signup')
    ax.set_ylabel('Cohort')

    plt.tight_layout()
    return fig, ax
```

### Slope Chart (Ranking Changes)

**Use when:** Showing how rankings shifted between two periods or methodologies.

**Layout:**
- Figure: `(11, 13)` for ~15 items
- Columns: left `x=0.35`, right `x=0.65`
- Row spacing: `1.0` units

**Lines:** Bezier curves with control points at midpoint:
```python
def draw_bezier(ax, x1, y1, x2, y2, color, lw=2.2, alpha=0.65):
    mid_x = (x1 + x2) / 2
    verts = [(x1, y1), (mid_x, y1), (mid_x, y2), (x2, y2)]
    codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
    path = Path(verts, codes)
    patch = patches.PathPatch(path, facecolor='none', edgecolor=color,
                               lw=lw, alpha=alpha, capstyle='round')
    ax.add_patch(patch)
```

**Colors:**
- Improved: `#22c55e` (green)
- Dropped: `#ef4444` (red)
- Neutral: `#9ca3af` (gray)

**Dropouts** (items leaving the ranking):
- No connecting line
- Annotation `→ #XX` immediately right of left label (size 9, bold, red)

**Typography:** Title 16pt bold, headers 12pt bold, labels 10pt, annotations 9pt

---

## Anti-Patterns to Avoid

### 1. 3D Charts

**Problem:** Distorts perception, adds no information, looks unprofessional.

**Fix:** Use 2D charts. If you need to show a third dimension, use color, size, or small multiples.

### 2. Dual Y-Axes

**Problem:** Easy to misread, can imply false correlation, scale manipulation.

**Fix:** Use small multiples (two charts stacked) or normalize to same scale.

```python
# BAD: Dual y-axes
# ax1.plot(x, y1)
# ax2 = ax1.twinx()
# ax2.plot(x, y2)

# GOOD: Small multiples
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
ax1.plot(x, y1)
ax1.set_title('Metric 1')
ax2.plot(x, y2)
ax2.set_title('Metric 2')
```

### 3. Truncated Y-Axes (Without Clear Labeling)

**Problem:** Exaggerates differences, misleading visualization.

**When acceptable:** Focus on small changes with clear labeling.

**Fix:** Start at zero, or clearly label the truncation with a break indicator.

```python
# If you must truncate, be explicit
ax.set_ylim(bottom=95)
ax.text(0.02, 0.02, 'Note: Y-axis starts at 95', transform=ax.transAxes,
        fontsize=9, style='italic')
```

### 4. Rainbow Color Schemes

**Problem:** Not colorblind-friendly, no natural ordering, distracting.

**Fix:** Use sequential or diverging color palettes.

```python
# Sequential (for ordered data)
cmap = 'Blues'  # or 'viridis', 'plasma'

# Diverging (for data with meaningful midpoint)
cmap = 'RdBu'  # or 'coolwarm'

# Categorical (for unordered categories)
palette = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B']
```

### 5. Pie Charts with Many Slices

**Problem:** Hard to compare, especially with > 5 slices.

**Fix:** Use horizontal bar chart instead.

```python
# Only use pie for <=5 categories, and only when showing parts of 100%
if len(categories) <= 5 and show_parts_of_whole:
    ax.pie(values, labels=categories, autopct='%1.1f%%')
else:
    ax.barh(categories, values)  # Better for comparison
```

### 6. Overloaded Charts

**Problem:** Too much information, cognitive overload.

**Fix:** Split into multiple focused charts. One insight per chart.

### 7. Subtraction Over Addition

**Principle:** When a chart is messy, the fix is usually subtraction (remove elements) not addition (add annotations, multiple views, legends).

**Problem:** Instinct is to "explain" messy charts by adding more—annotations, multiple panel views, elaborate redesigns. This usually makes things worse.

**Examples:**

**Slope chart with dropouts (items leaving the ranking):**
```
BAD approach:
- Add elaborate connecting lines to "dropped out" annotation box
- Create separate "dropout panel"
- Add legend explaining line types

GOOD approach:
- NO connecting line for dropouts
- Small annotation "→ #XX" immediately right of left label
- Size 9pt, bold, red color
- That's it. Subtraction, not addition.
```

**Cluttered time series:**
```
BAD approach:
- Add more labels and annotations
- Create inset zoom panels
- Add shaded regions with legends

GOOD approach:
- Remove least important series
- Increase line weight on key series
- Remove gridlines if not needed
- Let whitespace do the work
```

**Questions to Ask Before Adding:**
- Can I remove something instead?
- Does this annotation help or clutter?
- Would a simpler chart type work?
- What's the ONE thing this chart should communicate?

**Rule of Thumb:**
```
If you're adding elements to "fix" a chart, you probably
picked the wrong chart type. Start over with something simpler.
```

---

## Default Style Settings

Apply these at the start of any analysis notebook:

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette('colorblind')

# Default figure settings
plt.rcParams.update({
    'figure.figsize': (10, 6),
    'figure.dpi': 100,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.frameon': False,
    'axes.spines.top': False,
    'axes.spines.right': False,
})
```

---

## Color Palette Recommendations

### Primary Palette (Categorical)

```python
# Professional, colorblind-friendly
COLORS = {
    'primary': '#2E86AB',    # Blue
    'secondary': '#A23B72',  # Purple
    'accent1': '#F18F01',    # Orange
    'accent2': '#C73E1D',    # Red
    'neutral': '#6C757D',    # Gray
}

# For multiple series
CATEGORICAL_PALETTE = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B']
```

### Sequential Palette (Ordered Data)

```python
# For heatmaps, choropleth, intensity
SEQUENTIAL = 'Blues'  # or 'viridis' for perceptually uniform
```

### Diverging Palette (Midpoint Matters)

```python
# For positive/negative, above/below target
DIVERGING = 'RdBu'  # Red negative, blue positive
```

### Highlighting

```python
def highlight_bar(values, highlight_index, base_color='#6C757D', highlight_color='#2E86AB'):
    """Return color list with one highlighted bar."""
    colors = [base_color] * len(values)
    colors[highlight_index] = highlight_color
    return colors
```

---

## Annotation Patterns

### Adding Value Labels

```python
def add_bar_labels(ax, bars, fmt='{:.0f}'):
    """Add value labels to bars."""
    for bar in bars:
        height = bar.get_height()
        ax.annotate(fmt.format(height),
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)
```

### Marking Events on Time Series

```python
def add_event_marker(ax, x_pos, label, y_pos=None):
    """Add vertical line with annotation."""
    if y_pos is None:
        y_pos = ax.get_ylim()[1] * 0.9

    ax.axvline(x=x_pos, color='gray', linestyle='--', alpha=0.7)
    ax.annotate(label, xy=(x_pos, y_pos), xytext=(10, 0),
                textcoords='offset points', fontsize=9,
                arrowprops=dict(arrowstyle='->', color='gray'))
```

### Callout Boxes

```python
def add_callout(ax, text, xy, xytext):
    """Add callout box with arrow."""
    ax.annotate(text, xy=xy, xytext=xytext,
                fontsize=10,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
```

---

## Export Settings

### For Slides/Reports

```python
def save_for_presentation(fig, filename):
    """Save figure at presentation quality."""
    fig.savefig(filename, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
```

### For Print/Publication

```python
def save_for_print(fig, filename):
    """Save figure at print quality."""
    fig.savefig(filename, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
```

---

## Decision Logging for Visualizations

When creating charts, log your decisions:

```python
# VIZ: Line chart for ARR trend because showing change over time
# VIZ: Horizontal bar for segment comparison because 12 categories
# VIZ: Small multiples instead of dual y-axis for clarity
```
