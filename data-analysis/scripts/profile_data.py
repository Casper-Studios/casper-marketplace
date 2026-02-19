#!/usr/bin/env python3
"""
Generate a data quality profile report.

Analyzes a DataFrame and produces a comprehensive data quality report including:
- Column-level statistics (nulls, uniques, types, distributions)
- Data quality score (A-F grading)
- Suspicious pattern detection
- Suggested cleaning steps

Usage:
    # As a module
    from profile_data import profile_dataframe, generate_report
    report = profile_dataframe(df)
    print(generate_report(report))

    # From command line
    python profile_data.py <csv_file> [--output <report.md>]

Examples:
    python profile_data.py sales_data.csv
    python profile_data.py sales_data.csv --output data_quality_report.md
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Any

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def profile_column(series: 'pd.Series') -> dict[str, Any]:
    """
    Profile a single column.

    Args:
        series: pandas Series to profile

    Returns:
        Dictionary of column statistics
    """
    profile = {
        'name': series.name,
        'dtype': str(series.dtype),
        'count': len(series),
        'null_count': int(series.isnull().sum()),
        'null_pct': round(series.isnull().mean() * 100, 1),
        'unique_count': int(series.nunique()),
        'unique_pct': round(series.nunique() / len(series) * 100, 1),
    }

    # Non-null values for further analysis
    non_null = series.dropna()

    if len(non_null) == 0:
        profile['status'] = 'all_null'
        return profile

    # Type-specific stats
    if pd.api.types.is_numeric_dtype(series):
        profile['category'] = 'numeric'
        profile['min'] = float(non_null.min())
        profile['max'] = float(non_null.max())
        profile['mean'] = round(float(non_null.mean()), 2)
        profile['median'] = round(float(non_null.median()), 2)
        profile['std'] = round(float(non_null.std()), 2)

        # Detect outliers using IQR
        q1, q3 = non_null.quantile([0.25, 0.75])
        iqr = q3 - q1
        outliers = ((non_null < q1 - 1.5 * iqr) | (non_null > q3 + 1.5 * iqr)).sum()
        profile['outlier_count'] = int(outliers)
        profile['outlier_pct'] = round(outliers / len(non_null) * 100, 1)

        # Check for suspicious patterns
        profile['zero_count'] = int((non_null == 0).sum())
        profile['zero_pct'] = round((non_null == 0).mean() * 100, 1)
        profile['negative_count'] = int((non_null < 0).sum())

    elif pd.api.types.is_datetime64_any_dtype(series):
        profile['category'] = 'datetime'
        profile['min'] = str(non_null.min())
        profile['max'] = str(non_null.max())
        profile['range_days'] = (non_null.max() - non_null.min()).days

        # Check for future dates
        future = (non_null > pd.Timestamp.now()).sum()
        profile['future_dates'] = int(future)

    elif pd.api.types.is_bool_dtype(series):
        profile['category'] = 'boolean'
        profile['true_count'] = int(non_null.sum())
        profile['true_pct'] = round(non_null.mean() * 100, 1)

    else:
        profile['category'] = 'categorical'
        # Top values
        value_counts = non_null.value_counts()
        profile['top_values'] = value_counts.head(5).to_dict()
        profile['mode'] = str(value_counts.index[0]) if len(value_counts) > 0 else None
        profile['mode_pct'] = round(value_counts.iloc[0] / len(non_null) * 100, 1) if len(value_counts) > 0 else 0

        # Check for potential ID columns
        if profile['unique_pct'] > 95:
            profile['likely_id'] = True

    return profile


def detect_suspicious_patterns(df: 'pd.DataFrame', profiles: list[dict]) -> list[dict]:
    """
    Detect suspicious patterns in the data.

    Args:
        df: DataFrame
        profiles: List of column profiles

    Returns:
        List of detected issues
    """
    issues = []

    for p in profiles:
        col = p['name']

        # High null rate
        if p['null_pct'] > 20:
            issues.append({
                'column': col,
                'issue': 'high_null_rate',
                'severity': 'warning' if p['null_pct'] < 50 else 'critical',
                'detail': f"{p['null_pct']}% null values",
                'suggestion': 'Consider imputation or dropping column'
            })

        # Numeric-specific checks
        if p.get('category') == 'numeric':
            # High outlier rate
            if p.get('outlier_pct', 0) > 5:
                issues.append({
                    'column': col,
                    'issue': 'high_outlier_rate',
                    'severity': 'warning',
                    'detail': f"{p['outlier_pct']}% outliers detected",
                    'suggestion': 'Review outliers for data quality or consider winsorization'
                })

            # Excessive zeros
            if p.get('zero_pct', 0) > 50:
                issues.append({
                    'column': col,
                    'issue': 'excessive_zeros',
                    'severity': 'info',
                    'detail': f"{p['zero_pct']}% zero values",
                    'suggestion': 'Verify zeros are meaningful vs. missing data'
                })

            # Unexpected negative values
            if p.get('negative_count', 0) > 0 and any(kw in col.lower() for kw in ['revenue', 'price', 'count', 'quantity', 'age']):
                issues.append({
                    'column': col,
                    'issue': 'unexpected_negatives',
                    'severity': 'warning',
                    'detail': f"{p['negative_count']} negative values in column that should be positive",
                    'suggestion': 'Review negative values for data entry errors'
                })

        # Datetime-specific checks
        if p.get('category') == 'datetime':
            if p.get('future_dates', 0) > 0:
                issues.append({
                    'column': col,
                    'issue': 'future_dates',
                    'severity': 'warning',
                    'detail': f"{p['future_dates']} dates in the future",
                    'suggestion': 'Review future dates for data entry errors'
                })

        # Categorical-specific checks
        if p.get('category') == 'categorical':
            # Single value dominance
            if p.get('mode_pct', 0) > 95:
                issues.append({
                    'column': col,
                    'issue': 'low_variance',
                    'severity': 'info',
                    'detail': f"Single value represents {p['mode_pct']}% of data",
                    'suggestion': 'Column may have limited analytical value'
                })

    # Check for duplicates
    dupe_count = df.duplicated().sum()
    if dupe_count > 0:
        dupe_pct = round(dupe_count / len(df) * 100, 1)
        issues.append({
            'column': '(all)',
            'issue': 'duplicate_rows',
            'severity': 'warning' if dupe_pct < 5 else 'critical',
            'detail': f"{dupe_count} duplicate rows ({dupe_pct}%)",
            'suggestion': 'Review and deduplicate if appropriate'
        })

    return issues


def calculate_quality_score(profiles: list[dict], issues: list[dict]) -> dict:
    """
    Calculate overall data quality score.

    Args:
        profiles: List of column profiles
        issues: List of detected issues

    Returns:
        Dictionary with score and breakdown
    """
    # Start at 100, deduct for issues
    score = 100.0

    # Deduct for missing values
    avg_null_pct = np.mean([p['null_pct'] for p in profiles])
    score -= min(avg_null_pct, 30)  # Cap deduction at 30

    # Deduct for issues
    critical_count = sum(1 for i in issues if i['severity'] == 'critical')
    warning_count = sum(1 for i in issues if i['severity'] == 'warning')

    score -= critical_count * 10
    score -= warning_count * 3

    # Ensure score is between 0 and 100
    score = max(0, min(100, score))

    # Assign letter grade
    if score >= 90:
        grade = 'A'
    elif score >= 80:
        grade = 'B'
    elif score >= 70:
        grade = 'C'
    elif score >= 60:
        grade = 'D'
    else:
        grade = 'F'

    return {
        'score': round(score, 1),
        'grade': grade,
        'critical_issues': critical_count,
        'warning_issues': warning_count,
        'avg_null_pct': round(avg_null_pct, 1)
    }


def profile_dataframe(df: 'pd.DataFrame') -> dict:
    """
    Generate comprehensive data profile for a DataFrame.

    Args:
        df: pandas DataFrame to profile

    Returns:
        Dictionary containing profile information
    """
    if not PANDAS_AVAILABLE:
        raise ImportError("pandas is required. Install with: pip install pandas")

    result = {
        'generated_at': datetime.now().isoformat(),
        'shape': {
            'rows': len(df),
            'columns': len(df.columns)
        },
        'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
        'columns': [],
        'issues': [],
        'quality_score': {}
    }

    # Profile each column
    for col in df.columns:
        profile = profile_column(df[col])
        result['columns'].append(profile)

    # Detect suspicious patterns
    result['issues'] = detect_suspicious_patterns(df, result['columns'])

    # Calculate quality score
    result['quality_score'] = calculate_quality_score(
        result['columns'],
        result['issues']
    )

    return result


def generate_report(profile: dict, format: str = 'markdown') -> str:
    """
    Generate human-readable report from profile.

    Args:
        profile: Profile dictionary from profile_dataframe()
        format: Output format ('markdown' or 'text')

    Returns:
        Formatted report string
    """
    lines = []

    # Header
    lines.append("# Data Quality Report")
    lines.append("")
    lines.append(f"**Generated:** {profile['generated_at']}")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Rows:** {profile['shape']['rows']:,}")
    lines.append(f"- **Columns:** {profile['shape']['columns']}")
    lines.append(f"- **Memory:** {profile['memory_usage_mb']} MB")
    lines.append("")

    # Quality Score
    qs = profile['quality_score']
    lines.append("## Quality Score")
    lines.append("")
    lines.append(f"**Grade: {qs['grade']}** (Score: {qs['score']}/100)")
    lines.append("")
    lines.append(f"- Average null rate: {qs['avg_null_pct']}%")
    lines.append(f"- Critical issues: {qs['critical_issues']}")
    lines.append(f"- Warnings: {qs['warning_issues']}")
    lines.append("")

    # Issues
    if profile['issues']:
        lines.append("## Issues Detected")
        lines.append("")

        # Group by severity
        for severity in ['critical', 'warning', 'info']:
            severity_issues = [i for i in profile['issues'] if i['severity'] == severity]
            if severity_issues:
                lines.append(f"### {severity.title()}")
                lines.append("")
                for issue in severity_issues:
                    lines.append(f"- **{issue['column']}**: {issue['detail']}")
                    lines.append(f"  - {issue['suggestion']}")
                lines.append("")
    else:
        lines.append("## Issues Detected")
        lines.append("")
        lines.append("No issues detected.")
        lines.append("")

    # Column Details
    lines.append("## Column Details")
    lines.append("")

    # Table header
    lines.append("| Column | Type | Nulls | Uniques | Notes |")
    lines.append("|--------|------|-------|---------|-------|")

    for col in profile['columns']:
        null_str = f"{col['null_pct']}%" if col['null_pct'] > 0 else "0%"
        unique_str = f"{col['unique_count']:,}"

        notes = []
        if col.get('category') == 'numeric':
            notes.append(f"range: {col['min']:.2f}-{col['max']:.2f}")
        elif col.get('category') == 'datetime':
            notes.append(f"range: {col.get('range_days', 'N/A')} days")
        elif col.get('category') == 'categorical' and col.get('mode'):
            notes.append(f"mode: {col['mode'][:20]}")

        if col.get('likely_id'):
            notes.append("likely ID")

        notes_str = "; ".join(notes) if notes else ""

        lines.append(f"| {col['name']} | {col['dtype']} | {null_str} | {unique_str} | {notes_str} |")

    lines.append("")

    # Suggested Cleaning Steps
    lines.append("## Suggested Cleaning Steps")
    lines.append("")

    suggestions = []

    # Based on issues
    if any(i['issue'] == 'duplicate_rows' for i in profile['issues']):
        suggestions.append("1. Remove duplicate rows: `df.drop_duplicates()`")

    high_null_cols = [c['name'] for c in profile['columns'] if c['null_pct'] > 20]
    if high_null_cols:
        suggestions.append(f"2. Address high null columns: {', '.join(high_null_cols)}")

    outlier_cols = [c['name'] for c in profile['columns'] if c.get('outlier_pct', 0) > 5]
    if outlier_cols:
        suggestions.append(f"3. Review outliers in: {', '.join(outlier_cols)}")

    if not suggestions:
        suggestions.append("No critical cleaning steps required.")

    for s in suggestions:
        lines.append(s)

    lines.append("")
    lines.append("---")
    lines.append("*Report generated by profile_data.py*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate data quality profile report"
    )
    parser.add_argument(
        "file",
        help="Path to CSV file to profile"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path for report (default: print to stdout)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=['markdown', 'json'],
        default='markdown',
        help="Output format (default: markdown)"
    )

    args = parser.parse_args()

    # Check for pandas
    if not PANDAS_AVAILABLE:
        print("Error: pandas is required. Install with: pip install pandas")
        sys.exit(1)

    # Load data
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Generate profile
    profile = profile_dataframe(df)

    # Generate output
    if args.format == 'json':
        import json
        output = json.dumps(profile, indent=2, default=str)
    else:
        output = generate_report(profile)

    # Write or print
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output)
        print(f"Report written to: {output_path}")
    else:
        print(output)


if __name__ == "__main__":
    main()
