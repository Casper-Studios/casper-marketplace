#!/usr/bin/env python3
"""
Initialize a Marimo dashboard with common patterns.

Creates a .py file with pre-built cells for:
- KPI cards row
- Filter sidebar
- Time series chart
- Data table
- Layout scaffolding

Usage:
    python init_dashboard.py <dashboard_name> [--output-dir <dir>]

Examples:
    python init_dashboard.py revenue_dashboard
    python init_dashboard.py metrics_dashboard --output-dir ./dashboards
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

DASHBOARD_TEMPLATE = '''"""
{title}

Created: {date}
Interactive Marimo dashboard with KPI cards, filters, and visualizations.

Run with: marimo edit {filename}
"""

import marimo

__generated_with = "0.10.0"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from datetime import datetime, timedelta

    # Set plotting defaults
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({{
        'figure.figsize': (10, 6),
        'figure.dpi': 100,
        'axes.titlesize': 14,
        'axes.titleweight': 'bold',
        'axes.spines.top': False,
        'axes.spines.right': False,
    }})

    return datetime, mo, np, pd, plt, timedelta


@app.cell
def _(pd, np, datetime, timedelta):
    # === DATA LOADING ===
    # Replace this with your actual data loading code

    # Example: Generate sample data
    np.random.seed(42)
    n_days = 365
    dates = pd.date_range(end=datetime.now(), periods=n_days, freq='D')

    df = pd.DataFrame({{
        'date': dates,
        'revenue': np.random.normal(50000, 10000, n_days).cumsum() / 100 + 100000,
        'customers': np.random.randint(800, 1200, n_days),
        'new_customers': np.random.randint(10, 50, n_days),
        'churn_rate': np.random.uniform(0.01, 0.05, n_days),
        'segment': np.random.choice(['Enterprise', 'Mid-Market', 'SMB'], n_days)
    }})

    # Ensure date is datetime
    df['date'] = pd.to_datetime(df['date'])

    print(f"Loaded {{len(df)}} rows")
    return (df,)


# ==============================================================================
# FILTERS
# ==============================================================================

@app.cell
def _(mo, df):
    # Segment filter
    segment_options = ['All'] + sorted(df['segment'].unique().tolist())
    segment_filter = mo.ui.dropdown(
        options=segment_options,
        value='All',
        label='Segment'
    )

    # Date range filter
    date_range = mo.ui.date_range(
        start=df['date'].min().date(),
        stop=df['date'].max().date(),
        label='Date Range'
    )

    # Aggregation period
    period_filter = mo.ui.dropdown(
        options=['Daily', 'Weekly', 'Monthly'],
        value='Monthly',
        label='Aggregation'
    )

    return segment_filter, date_range, period_filter


@app.cell
def _(df, segment_filter, date_range, pd):
    # Apply filters
    df_filtered = df.copy()

    # Segment filter
    if segment_filter.value != 'All':
        df_filtered = df_filtered[df_filtered['segment'] == segment_filter.value]

    # Date range filter
    start_date, end_date = date_range.value
    df_filtered = df_filtered[
        (df_filtered['date'] >= pd.Timestamp(start_date)) &
        (df_filtered['date'] <= pd.Timestamp(end_date))
    ]

    return (df_filtered,)


# ==============================================================================
# KPI CARDS
# ==============================================================================

@app.cell
def _(mo):
    def kpi_card(title, value, delta=None, delta_color=None):
        """Create a styled KPI card."""
        delta_html = ""
        if delta:
            color = delta_color or ('green' if delta.startswith('+') else 'red')
            delta_html = f'<span style="color: {{color}}; font-size: 0.9em;">{{delta}}</span>'

        return mo.md(f\"\"\"
        <div style="
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            min-width: 180px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        ">
            <div style="color: #666; font-size: 0.9em; margin-bottom: 8px;">{{title}}</div>
            <div style="font-size: 2em; font-weight: bold; color: #333;">{{value}}</div>
            {{delta_html}}
        </div>
        \"\"\")

    return (kpi_card,)


@app.cell
def _(df_filtered, kpi_card, mo):
    # Calculate KPIs
    total_revenue = df_filtered['revenue'].sum()
    avg_customers = df_filtered['customers'].mean()
    total_new = df_filtered['new_customers'].sum()
    avg_churn = df_filtered['churn_rate'].mean()

    # Calculate period-over-period change (example: vs prior period)
    mid_point = len(df_filtered) // 2
    if mid_point > 0:
        current_rev = df_filtered.iloc[mid_point:]['revenue'].sum()
        prior_rev = df_filtered.iloc[:mid_point]['revenue'].sum()
        rev_change = ((current_rev - prior_rev) / prior_rev * 100) if prior_rev > 0 else 0
        rev_delta = f"{{'+' if rev_change >= 0 else ''}}{{rev_change:.1f}}%"
    else:
        rev_delta = None

    # Build KPI row
    kpi_row = mo.hstack([
        kpi_card('Total Revenue', f'${{total_revenue:,.0f}}', rev_delta, 'green' if rev_delta and rev_delta.startswith('+') else 'red'),
        kpi_card('Avg Customers', f'{{avg_customers:,.0f}}'),
        kpi_card('New Customers', f'{{total_new:,}}'),
        kpi_card('Avg Churn Rate', f'{{avg_churn:.1%}}'),
    ], justify='space-around')

    return (kpi_row,)


# ==============================================================================
# CHARTS
# ==============================================================================

@app.cell
def _(df_filtered, period_filter, plt, pd):
    # Aggregate by period
    period_map = {{
        'Daily': 'D',
        'Weekly': 'W',
        'Monthly': 'M'
    }}

    df_agg = df_filtered.set_index('date').resample(period_map[period_filter.value]).agg({{
        'revenue': 'sum',
        'customers': 'mean',
        'new_customers': 'sum',
        'churn_rate': 'mean'
    }}).reset_index()

    # Create trend chart
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df_agg['date'], df_agg['revenue'], marker='o', linewidth=2, markersize=4, color='#2E86AB')
    ax.fill_between(df_agg['date'], df_agg['revenue'], alpha=0.2, color='#2E86AB')
    ax.set_title(f'Revenue Trend ({{period_filter.value}})', fontsize=14, fontweight='bold')
    ax.set_xlabel('')
    ax.set_ylabel('Revenue ($)')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${{x:,.0f}}'))
    plt.xticks(rotation=45)
    plt.tight_layout()

    trend_chart = fig
    return trend_chart, df_agg


# ==============================================================================
# DATA TABLE
# ==============================================================================

@app.cell
def _(mo, df_filtered):
    # Create summary table by segment
    summary = df_filtered.groupby('segment').agg({{
        'revenue': ['sum', 'mean'],
        'customers': 'mean',
        'new_customers': 'sum',
        'churn_rate': 'mean'
    }}).round(2)

    # Flatten column names
    summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
    summary = summary.reset_index()

    # Format for display
    summary_display = summary.copy()
    summary_display['revenue_sum'] = summary_display['revenue_sum'].apply(lambda x: f'${{x:,.0f}}')
    summary_display['revenue_mean'] = summary_display['revenue_mean'].apply(lambda x: f'${{x:,.0f}}')
    summary_display['customers_mean'] = summary_display['customers_mean'].apply(lambda x: f'{{x:,.0f}}')
    summary_display['churn_rate_mean'] = summary_display['churn_rate_mean'].apply(lambda x: f'{{x:.1%}}')

    # Rename columns for clarity
    summary_display.columns = ['Segment', 'Total Revenue', 'Avg Revenue', 'Avg Customers', 'New Customers', 'Avg Churn']

    data_table = mo.ui.table(summary_display, selection=None)
    return (data_table,)


# ==============================================================================
# LAYOUT
# ==============================================================================

@app.cell(hide_code=True)
def _(mo):
    mo.md(\"\"\"
    # {title}

    Interactive dashboard for monitoring key metrics.
    \"\"\")
    return


@app.cell
def _(mo, segment_filter, date_range, period_filter, kpi_row, trend_chart, data_table, datetime):
    # Build sidebar
    sidebar = mo.vstack([
        mo.md("## Filters"),
        segment_filter,
        date_range,
        period_filter,
        mo.md("---"),
        mo.md(f"*Updated: {{datetime.now().strftime('%Y-%m-%d %H:%M')}}*")
    ], align='start')

    # Build main content
    main_content = mo.vstack([
        kpi_row,
        mo.md("---"),
        mo.md("### Revenue Trend"),
        trend_chart,
        mo.md("---"),
        mo.md("### Summary by Segment"),
        data_table
    ])

    # Combine in layout
    mo.hstack([
        mo.vstack([sidebar], align='start'),
        mo.vstack([main_content], grow=True)
    ], widths=[1, 5])
    return


if __name__ == "__main__":
    app.run()
'''


def create_dashboard(name: str, output_dir: Path) -> Path:
    """
    Create a Marimo dashboard with the given name.

    Args:
        name: Name for the dashboard (without .py extension)
        output_dir: Directory to create the dashboard in

    Returns:
        Path to created dashboard
    """
    # Ensure name is valid
    safe_name = name.replace("-", "_").replace(" ", "_")
    if not safe_name.replace("_", "").isalnum():
        raise ValueError(f"Invalid dashboard name: {name}")

    # Create output directory if needed
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate dashboard content
    date_str = datetime.now().strftime("%Y-%m-%d")
    title = name.replace("_", " ").replace("-", " ").title()
    filename = f"{safe_name}.py"

    content = DASHBOARD_TEMPLATE.format(
        title=title,
        date=date_str,
        filename=filename
    )

    # Write dashboard
    dashboard_path = output_dir / filename
    dashboard_path.write_text(content)

    return dashboard_path


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a Marimo dashboard with common patterns"
    )
    parser.add_argument(
        "name",
        help="Name for the dashboard (e.g., 'revenue_dashboard')"
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to create the dashboard in (default: current directory)"
    )

    args = parser.parse_args()

    try:
        dashboard_path = create_dashboard(args.name, Path(args.output_dir))
        print(f"Created Marimo dashboard: {dashboard_path}")
        print(f"\nTo run the dashboard:")
        print(f"  marimo edit {dashboard_path}")
        print(f"\nFeatures included:")
        print("  - KPI cards row with delta indicators")
        print("  - Segment and date range filters")
        print("  - Period aggregation selector")
        print("  - Revenue trend chart")
        print("  - Summary data table")
        print("  - Sidebar layout")
    except Exception as e:
        print(f"Error creating dashboard: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
