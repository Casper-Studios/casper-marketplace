# Dashboard Patterns Reference

Marimo layout patterns, KPI cards, interactivity, and dashboard design for financial and RevOps dashboards.

---

## Dashboard Design Principles

### Information Hierarchy

```
1. TOP: Key metrics (KPIs) - What matters most?
2. MIDDLE: Trends and comparisons - How are we doing?
3. BOTTOM: Details and drill-downs - Why?
```

### Dashboard Types

| Type | Purpose | Primary Elements |
|------|---------|------------------|
| **Executive** | High-level status | KPIs, trends, alerts |
| **Operational** | Daily monitoring | Tables, real-time metrics |
| **Analytical** | Deep exploration | Filters, drill-downs, multiple views |
| **Reporting** | Scheduled updates | Automated snapshots, comparisons |

---

## Marimo Layout Patterns

### Sidebar Layout

```python
import marimo as mo

@app.cell
def _(mo):
    # Create sidebar with filters
    segment_filter = mo.ui.dropdown(
        options=['All', 'Enterprise', 'Mid-Market', 'SMB'],
        value='All',
        label='Segment'
    )

    date_range = mo.ui.date_range(
        start=datetime(2024, 1, 1),
        stop=datetime.now(),
        label='Date Range'
    )

    sidebar = mo.vstack([
        mo.md("## Filters"),
        segment_filter,
        date_range,
        mo.md("---"),
        mo.md("Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    ])

    return segment_filter, date_range, sidebar


@app.cell
def _(mo, sidebar, main_content):
    # Layout with sidebar
    mo.hstack([
        mo.vstack([sidebar], align='start'),
        mo.vstack([main_content], grow=True)
    ], widths=[1, 4])
    return
```

### Tab Layout

```python
@app.cell
def _(mo, overview_content, details_content, trends_content):
    # Tabbed navigation
    tabs = mo.ui.tabs({
        "Overview": overview_content,
        "Details": details_content,
        "Trends": trends_content
    })

    mo.vstack([
        mo.md("# Revenue Dashboard"),
        tabs
    ])
    return (tabs,)
```

### Grid Layout

```python
@app.cell
def _(mo, kpi_cards, main_chart, table):
    # KPI row at top
    kpi_row = mo.hstack(kpi_cards, justify='space-around')

    # Main content below
    main_row = mo.hstack([
        main_chart,
        table
    ], widths=[2, 1])

    mo.vstack([
        kpi_row,
        mo.md("---"),
        main_row
    ])
    return
```

---

## KPI Card Templates

### Basic KPI Card

```python
def kpi_card(title, value, subtitle=None, delta=None, delta_color=None):
    """
    Create a KPI card with optional delta indicator.

    Args:
        title: KPI name
        value: Current value (formatted string)
        subtitle: Optional context
        delta: Optional change indicator (e.g., "+5%")
        delta_color: 'green', 'red', or None
    """
    delta_html = ""
    if delta:
        color = delta_color or ('green' if delta.startswith('+') else 'red')
        delta_html = f'<span style="color: {color}; font-size: 0.9em;">{delta}</span>'

    subtitle_html = f'<div style="color: #666; font-size: 0.8em;">{subtitle}</div>' if subtitle else ""

    return mo.md(f"""
    <div style="
        background: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        min-width: 150px;
    ">
        <div style="color: #666; font-size: 0.9em; margin-bottom: 5px;">{title}</div>
        <div style="font-size: 2em; font-weight: bold; color: #333;">{value}</div>
        {delta_html}
        {subtitle_html}
    </div>
    """)
```

### KPI with Sparkline

```python
import matplotlib.pyplot as plt
import io
import base64

def kpi_card_with_sparkline(title, value, trend_data, delta=None):
    """
    KPI card with embedded sparkline.

    Args:
        title: KPI name
        value: Current value
        trend_data: List of values for sparkline
        delta: Change indicator
    """
    # Create sparkline
    fig, ax = plt.subplots(figsize=(3, 1))
    ax.plot(trend_data, color='#2E86AB', linewidth=2)
    ax.fill_between(range(len(trend_data)), trend_data, alpha=0.2, color='#2E86AB')
    ax.axis('off')
    plt.tight_layout()

    # Convert to base64
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, transparent=True)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()
    plt.close()

    delta_html = f'<span style="color: green;">{delta}</span>' if delta else ""

    return mo.md(f"""
    <div style="
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    ">
        <div style="color: #666; font-size: 0.9em;">{title}</div>
        <div style="font-size: 1.8em; font-weight: bold;">{value} {delta_html}</div>
        <img src="data:image/png;base64,{img_base64}" style="width: 100%; height: 40px;">
    </div>
    """)
```

### KPI Row Builder

```python
def build_kpi_row(metrics):
    """
    Build a row of KPI cards.

    Args:
        metrics: List of dicts with keys: title, value, delta (optional)

    Returns:
        Marimo hstack of KPI cards
    """
    cards = [
        kpi_card(
            title=m['title'],
            value=m['value'],
            delta=m.get('delta'),
            delta_color=m.get('delta_color')
        )
        for m in metrics
    ]

    return mo.hstack(cards, justify='space-around')


# Usage example
kpi_metrics = [
    {'title': 'MRR', 'value': '$1.2M', 'delta': '+8%', 'delta_color': 'green'},
    {'title': 'Customers', 'value': '1,247', 'delta': '+12'},
    {'title': 'NRR', 'value': '112%', 'delta': '+3pp'},
    {'title': 'Churn', 'value': '2.1%', 'delta': '-0.3pp', 'delta_color': 'green'},
]

kpi_row = build_kpi_row(kpi_metrics)
```

---

## Filter and Interactivity Patterns

### Dropdown Filter

```python
@app.cell
def _(mo, df):
    # Single select dropdown
    segment_filter = mo.ui.dropdown(
        options=['All'] + df['segment'].unique().tolist(),
        value='All',
        label='Segment'
    )
    return (segment_filter,)


@app.cell
def _(df, segment_filter):
    # Apply filter
    if segment_filter.value == 'All':
        df_filtered = df
    else:
        df_filtered = df[df['segment'] == segment_filter.value]

    return (df_filtered,)
```

### Multi-Select Filter

```python
@app.cell
def _(mo, df):
    # Multi-select for segments
    segment_multiselect = mo.ui.multiselect(
        options=df['segment'].unique().tolist(),
        value=df['segment'].unique().tolist(),  # All selected by default
        label='Segments'
    )
    return (segment_multiselect,)


@app.cell
def _(df, segment_multiselect):
    # Apply multi-select filter
    df_filtered = df[df['segment'].isin(segment_multiselect.value)]
    return (df_filtered,)
```

### Date Range Picker

```python
@app.cell
def _(mo, df):
    # Date range picker
    date_range = mo.ui.date_range(
        start=df['date'].min(),
        stop=df['date'].max(),
        label='Date Range'
    )
    return (date_range,)


@app.cell
def _(df, date_range):
    # Apply date filter
    start_date, end_date = date_range.value
    df_filtered = df[
        (df['date'] >= pd.Timestamp(start_date)) &
        (df['date'] <= pd.Timestamp(end_date))
    ]
    return (df_filtered,)
```

### Slider Filter

```python
@app.cell
def _(mo, df):
    # Numeric slider
    min_revenue = mo.ui.slider(
        start=0,
        stop=int(df['revenue'].max()),
        step=1000,
        value=0,
        label='Min Revenue',
        show_value=True
    )
    return (min_revenue,)


@app.cell
def _(df, min_revenue):
    df_filtered = df[df['revenue'] >= min_revenue.value]
    return (df_filtered,)
```

### Checkbox Toggles

```python
@app.cell
def _(mo):
    # Toggle options
    show_trend = mo.ui.checkbox(label='Show trend line', value=True)
    exclude_outliers = mo.ui.checkbox(label='Exclude outliers', value=False)

    filter_options = mo.vstack([show_trend, exclude_outliers])
    return show_trend, exclude_outliers, filter_options
```

---

## Data Table Patterns

### Basic Sortable Table

```python
@app.cell
def _(mo, df_filtered):
    # Interactive data table
    table = mo.ui.table(
        data=df_filtered,
        selection='single',  # or 'multi' for multiple selection
        pagination=True,
        page_size=20
    )
    return (table,)
```

### Styled Table with Formatting

```python
def format_table(df):
    """Apply formatting to DataFrame for display."""
    styled = df.style

    # Format currency columns
    currency_cols = ['revenue', 'mrr', 'arr']
    for col in currency_cols:
        if col in df.columns:
            styled = styled.format({col: '${:,.0f}'})

    # Format percentage columns
    pct_cols = ['churn_rate', 'growth_rate', 'conversion']
    for col in pct_cols:
        if col in df.columns:
            styled = styled.format({col: '{:.1%}'})

    # Highlight conditions
    if 'churn_rate' in df.columns:
        styled = styled.applymap(
            lambda x: 'color: red' if x > 0.05 else '',
            subset=['churn_rate']
        )

    return styled


@app.cell
def _(mo, df_filtered):
    styled_df = format_table(df_filtered)
    mo.ui.table(styled_df.data, pagination=True)
    return
```

### Summary Table

```python
def create_summary_table(df, group_by, metrics):
    """
    Create a summary table with aggregated metrics.

    Args:
        df: DataFrame
        group_by: Column to group by
        metrics: Dict of {column: aggregation}

    Returns:
        Summary DataFrame
    """
    summary = df.groupby(group_by).agg(metrics).round(2)
    summary = summary.sort_values(
        summary.columns[0],
        ascending=False
    )

    return summary


# Example usage
summary = create_summary_table(
    df=df_filtered,
    group_by='segment',
    metrics={
        'revenue': ['sum', 'mean'],
        'customers': 'nunique',
        'churn_rate': 'mean'
    }
)
```

---

## Time Series Patterns

### Time Series with Range Selection

```python
@app.cell
def _(mo, df):
    # Period selector
    period = mo.ui.dropdown(
        options=['Daily', 'Weekly', 'Monthly', 'Quarterly'],
        value='Monthly',
        label='Aggregation'
    )
    return (period,)


@app.cell
def _(df, period, plt):
    # Aggregate based on period
    period_map = {
        'Daily': 'D',
        'Weekly': 'W',
        'Monthly': 'M',
        'Quarterly': 'Q'
    }

    df_agg = df.set_index('date').resample(period_map[period.value]).agg({
        'revenue': 'sum',
        'customers': 'nunique'
    }).reset_index()

    # Create chart
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df_agg['date'], df_agg['revenue'], marker='o', linewidth=2)
    ax.set_title(f'Revenue Trend ({period.value})')
    ax.set_xlabel('')
    ax.set_ylabel('Revenue ($)')
    plt.xticks(rotation=45)
    plt.tight_layout()

    return (fig,)
```

### Comparison Chart (vs Prior Period)

```python
def create_comparison_chart(df, date_col, value_col, prior_periods=12):
    """Create chart comparing current to prior period."""
    fig, ax = plt.subplots(figsize=(12, 5))

    # Current period
    ax.plot(df[date_col], df[value_col], label='Current', linewidth=2, color='#2E86AB')

    # Prior period (shifted)
    df_prior = df.copy()
    df_prior[date_col] = df_prior[date_col] + pd.DateOffset(months=prior_periods)
    ax.plot(df_prior[date_col], df_prior[value_col], label='Prior Year',
            linewidth=2, color='#A23B72', linestyle='--', alpha=0.7)

    ax.legend()
    ax.set_title('Year-over-Year Comparison')
    plt.tight_layout()

    return fig
```

---

## Refresh Patterns

### Manual Refresh Button

```python
@app.cell
def _(mo):
    refresh_button = mo.ui.button(label="Refresh Data")
    return (refresh_button,)


@app.cell
def _(refresh_button, load_data):
    # Re-run when button clicked
    refresh_button  # Reference triggers re-run
    df = load_data()
    last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return df, last_refresh
```

### Auto-Refresh Display

```python
@app.cell(hide_code=True)
def _(mo, last_refresh):
    mo.md(f"""
    <div style="text-align: right; color: #666; font-size: 0.8em;">
        Last updated: {last_refresh}
    </div>
    """)
    return
```

---

## Dashboard Template

Complete dashboard structure:

```python
"""
Revenue Dashboard

A Marimo dashboard for monitoring key SaaS metrics.
Run with: marimo edit dashboard.py
"""

import marimo
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

__generated_with = "0.10.0"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("# Revenue Dashboard")
    return


@app.cell
def _(mo, df):
    # === FILTERS ===
    segment_filter = mo.ui.dropdown(
        options=['All'] + df['segment'].unique().tolist(),
        value='All',
        label='Segment'
    )

    date_range = mo.ui.date_range(
        start=df['date'].min(),
        stop=df['date'].max(),
        label='Date Range'
    )

    return segment_filter, date_range


@app.cell
def _(df, segment_filter, date_range):
    # === APPLY FILTERS ===
    df_filtered = df.copy()

    if segment_filter.value != 'All':
        df_filtered = df_filtered[df_filtered['segment'] == segment_filter.value]

    start, end = date_range.value
    df_filtered = df_filtered[
        (df_filtered['date'] >= pd.Timestamp(start)) &
        (df_filtered['date'] <= pd.Timestamp(end))
    ]

    return (df_filtered,)


@app.cell
def _(mo, df_filtered, kpi_card):
    # === KPI CARDS ===
    total_revenue = df_filtered['revenue'].sum()
    total_customers = df_filtered['customer_id'].nunique()
    avg_revenue = df_filtered.groupby('customer_id')['revenue'].sum().mean()

    kpi_row = mo.hstack([
        kpi_card('Total Revenue', f'${total_revenue:,.0f}'),
        kpi_card('Customers', f'{total_customers:,}'),
        kpi_card('Avg Revenue/Customer', f'${avg_revenue:,.0f}'),
    ], justify='space-around')

    return (kpi_row,)


@app.cell
def _(mo, kpi_row, trend_chart, segment_filter, date_range, data_table):
    # === LAYOUT ===
    sidebar = mo.vstack([
        mo.md("## Filters"),
        segment_filter,
        date_range,
    ])

    main_content = mo.vstack([
        kpi_row,
        mo.md("---"),
        trend_chart,
        mo.md("---"),
        data_table,
    ])

    mo.hstack([
        sidebar,
        main_content
    ], widths=[1, 4])
    return


if __name__ == "__main__":
    app.run()
```

---

## Dashboard Anti-Patterns

### Avoid These

| Anti-Pattern | Problem | Better Approach |
|--------------|---------|-----------------|
| Too many KPIs | Information overload | Max 4-6 key metrics |
| No context | Numbers without meaning | Add comparisons, targets |
| Deep nesting | Hard to navigate | Flat hierarchy with tabs |
| Auto-refresh chaos | Constant distraction | Manual refresh + timestamp |
| No filters | One-size-fits-none | User-controlled views |
| Raw data dumps | Not actionable | Aggregated summaries |

### Best Practices

1. **Start with questions**: What decisions does this dashboard support?
2. **Hierarchy matters**: Most important info at top
3. **Consistent formatting**: Same scales, colors, formats
4. **Context is king**: Comparisons, targets, benchmarks
5. **Mobile consideration**: Design for smallest screen first
6. **Performance**: Pre-aggregate, limit data points
