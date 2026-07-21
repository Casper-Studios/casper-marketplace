#!/usr/bin/env python3
"""
Initialize a Marimo notebook with decision logging scaffolding.

Creates a .py file with pre-built cells for:
- Decision log (markdown)
- Data loading template
- EDA templates
- Bias checklist
- Data wishlist

Usage:
    python init_marimo_notebook.py <notebook_name> [--output-dir <dir>]

Examples:
    python init_marimo_notebook.py revenue_analysis
    python init_marimo_notebook.py churn_model --output-dir ./notebooks
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

NOTEBOOK_TEMPLATE = '''"""
{title}

Created: {date}
Analysis notebook with decision logging scaffolding.

Run with: marimo edit {filename}
"""

import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        # {title}

        **Date:** {date}
        **Analyst:** [Your name]
        **Objective:** [What question are we answering?]

        ---
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Decision Log

        Track all analytical decisions here. Update as you work.

        | Decision Type | Decision | Rationale |
        |---------------|----------|-----------|
        | FILTER | | |
        | METRIC | | |
        | ASSUMPTION | | |
        | PROXY | | |
        | VIZ | | |

        ---
        """
    )
    return


@app.cell
def _():
    # === IMPORTS ===
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Set plotting defaults
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette('colorblind')
    plt.rcParams.update({{
        'figure.figsize': (10, 6),
        'figure.dpi': 100,
        'axes.titlesize': 14,
        'axes.titleweight': 'bold',
        'axes.spines.top': False,
        'axes.spines.right': False,
    }})

    print("Libraries loaded successfully")
    return np, pd, plt, sns


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Data Loading

        Document data sources and initial observations.
        """
    )
    return


@app.cell
def _(pd):
    # === DATA SOURCE ===
    # Source: [file path / API / database]
    # Loaded: {date}
    # Records: [update after loading]
    # Note: [data freshness, known issues]

    # Load your data here
    # df = pd.read_csv("your_data.csv")

    # Example placeholder
    df = pd.DataFrame({{
        'date': pd.date_range('2024-01-01', periods=100),
        'revenue': np.random.normal(10000, 2000, 100),
        'customers': np.random.randint(100, 500, 100),
        'segment': np.random.choice(['Enterprise', 'SMB', 'Mid-Market'], 100)
    }})

    print(f"Loaded {{len(df)}} rows, {{len(df.columns)}} columns")
    df.head()
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Exploratory Data Analysis

        Follow the EDA checklist:
        - [ ] Distribution of key numeric variables
        - [ ] Missing value patterns
        - [ ] Outlier detection
        - [ ] Time series patterns (if applicable)
        - [ ] Segment breakdowns
        - [ ] Correlation exploration
        """
    )
    return


@app.cell
def _(df):
    # Data overview
    print("=== DATA OVERVIEW ===")
    print(f"Shape: {{df.shape}}")
    print(f"\\nColumn types:")
    print(df.dtypes)
    print(f"\\nMissing values:")
    print(df.isnull().sum())
    return


@app.cell
def _(df, plt):
    # Numeric distributions
    # VIZ: Histograms for numeric columns to understand distributions

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        fig, axes = plt.subplots(1, min(3, len(numeric_cols)), figsize=(12, 4))
        if len(numeric_cols) == 1:
            axes = [axes]
        for ax, col in zip(axes, numeric_cols[:3]):
            df[col].hist(ax=ax, bins=30, color='#2E86AB', edgecolor='white')
            ax.set_title(col)
        plt.tight_layout()
        plt.show()
    return axes, fig, numeric_cols


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Analysis

        [Add your analysis cells here]
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Bias Checklist

        Run through before finalizing conclusions:

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

        **Overall assessment:** [Ready / Needs caveats / Needs more work]
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Data Wishlist

        | Missing Data | Proxy Used | Quality | Impact |
        |--------------|------------|---------|--------|
        | | | | |
        | | | | |
        | | | | |

        ### Recommendations for Data Collection
        1.
        2.
        3.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Key Findings

        1. **Finding 1:** [Description]
        2. **Finding 2:** [Description]
        3. **Finding 3:** [Description]

        ## Recommendations

        1. [Recommendation 1]
        2. [Recommendation 2]
        3. [Recommendation 3]

        ## Caveats

        - [Key limitation 1]
        - [Key limitation 2]
        """
    )
    return


if __name__ == "__main__":
    app.run()
'''


def create_notebook(name: str, output_dir: Path) -> Path:
    """
    Create a Marimo notebook with the given name.

    Args:
        name: Name for the notebook (without .py extension)
        output_dir: Directory to create the notebook in

    Returns:
        Path to created notebook
    """
    # Ensure name is valid
    safe_name = name.replace("-", "_").replace(" ", "_")
    if not safe_name.replace("_", "").isalnum():
        raise ValueError(f"Invalid notebook name: {name}")

    # Create output directory if needed
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate notebook content
    date_str = datetime.now().strftime("%Y-%m-%d")
    title = name.replace("_", " ").replace("-", " ").title()
    filename = f"{safe_name}.py"

    content = NOTEBOOK_TEMPLATE.format(
        title=title,
        date=date_str,
        filename=filename
    )

    # Write notebook
    notebook_path = output_dir / filename
    notebook_path.write_text(content)

    return notebook_path


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a Marimo notebook with decision logging scaffolding"
    )
    parser.add_argument(
        "name",
        help="Name for the notebook (e.g., 'revenue_analysis')"
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to create the notebook in (default: current directory)"
    )

    args = parser.parse_args()

    try:
        notebook_path = create_notebook(args.name, Path(args.output_dir))
        print(f"Created Marimo notebook: {notebook_path}")
        print(f"\nTo run the notebook:")
        print(f"  marimo edit {notebook_path}")
        print(f"\nOr to run as a script:")
        print(f"  python {notebook_path}")
    except Exception as e:
        print(f"Error creating notebook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
