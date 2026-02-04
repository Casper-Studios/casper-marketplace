#!/usr/bin/env python3
"""
CSV Analyzer - Comprehensive data analysis and visualization tool.

Features:
- Statistical analysis (descriptive stats, correlations, distributions)
- Data quality assessment (missing values, duplicates, outliers)
- Smart visualizations (auto-selects best chart types)
- Multiple output formats (console, markdown, HTML, JSON)
- Memory-efficient handling of large files
"""

import argparse
import json
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Constants
MAX_CATEGORIES_FOR_PLOT = 15
MAX_UNIQUE_FOR_CATEGORICAL = 50
OUTLIER_ZSCORE_THRESHOLD = 3
SAMPLE_SIZE_FOR_LARGE_FILES = 100000


class CSVAnalyzer:
    """Comprehensive CSV analysis and visualization engine."""

    def __init__(
        self,
        file_path: str,
        output_dir: Optional[str] = None,
        sample_size: Optional[int] = None,
        date_columns: Optional[List[str]] = None
    ):
        self.file_path = Path(file_path)
        self.output_dir = Path(output_dir) if output_dir else Path('.tmp/csv_analysis')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.sample_size = sample_size
        self.date_columns = date_columns or []
        self.charts_created = []
        self.insights = []
        self.warnings = []

        # Load data
        self.df = self._load_data()
        self.original_shape = self.df.shape

        # Classify columns
        self._classify_columns()

    def _load_data(self) -> pd.DataFrame:
        """Load CSV with smart type inference and optional sampling."""
        # Check file size
        file_size_mb = self.file_path.stat().st_size / (1024 * 1024)

        # For large files, sample if not specified
        if file_size_mb > 100 and not self.sample_size:
            self.warnings.append(f"Large file ({file_size_mb:.1f}MB) - sampling {SAMPLE_SIZE_FOR_LARGE_FILES:,} rows")
            self.sample_size = SAMPLE_SIZE_FOR_LARGE_FILES

        # Read with sampling if needed
        if self.sample_size:
            # Get total rows first
            total_rows = sum(1 for _ in open(self.file_path)) - 1
            skip_rows = sorted(np.random.choice(
                range(1, total_rows + 1),
                size=max(0, total_rows - self.sample_size),
                replace=False
            ))
            df = pd.read_csv(self.file_path, skiprows=skip_rows)
        else:
            df = pd.read_csv(self.file_path)

        # Parse date columns
        for col in df.columns:
            if col in self.date_columns or any(kw in col.lower() for kw in ['date', 'time', 'created', 'updated']):
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    pass

        return df

    def _classify_columns(self):
        """Classify columns by type for analysis."""
        self.numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = []
        self.text_cols = []
        self.datetime_cols = self.df.select_dtypes(include=['datetime64']).columns.tolist()
        self.boolean_cols = []
        self.id_cols = []

        for col in self.df.select_dtypes(include=['object', 'category']).columns:
            # Check if it's an ID column
            if any(kw in col.lower() for kw in ['id', 'uuid', 'key', 'code']) or \
               self.df[col].nunique() == len(self.df):
                self.id_cols.append(col)
            # Check if categorical (limited unique values)
            elif self.df[col].nunique() <= MAX_UNIQUE_FOR_CATEGORICAL:
                self.categorical_cols.append(col)
            else:
                self.text_cols.append(col)

        # Check for boolean-like columns
        for col in self.numeric_cols[:]:
            if set(self.df[col].dropna().unique()).issubset({0, 1}):
                self.boolean_cols.append(col)
                self.numeric_cols.remove(col)

    def analyze(self) -> Dict[str, Any]:
        """Run comprehensive analysis."""
        results = {
            'file_info': self._analyze_file_info(),
            'data_quality': self._analyze_data_quality(),
            'numeric_analysis': self._analyze_numeric(),
            'categorical_analysis': self._analyze_categorical(),
            'temporal_analysis': self._analyze_temporal(),
            'correlations': self._analyze_correlations(),
            'outliers': self._detect_outliers(),
            'insights': [],
            'warnings': self.warnings,
            'charts': self.charts_created
        }

        # Generate insights
        results['insights'] = self._generate_insights(results)
        self.insights = results['insights']

        return results

    def _analyze_file_info(self) -> Dict:
        """Basic file and dataset information."""
        memory_usage = self.df.memory_usage(deep=True).sum() / (1024 * 1024)

        return {
            'file_name': self.file_path.name,
            'file_size_mb': self.file_path.stat().st_size / (1024 * 1024),
            'rows': len(self.df),
            'columns': len(self.df.columns),
            'memory_usage_mb': memory_usage,
            'sampled': self.sample_size is not None,
            'original_rows': self.original_shape[0] if self.sample_size else len(self.df),
            'column_types': {
                'numeric': len(self.numeric_cols),
                'categorical': len(self.categorical_cols),
                'datetime': len(self.datetime_cols),
                'text': len(self.text_cols),
                'boolean': len(self.boolean_cols),
                'id': len(self.id_cols)
            },
            'columns_list': {
                'numeric': self.numeric_cols,
                'categorical': self.categorical_cols,
                'datetime': self.datetime_cols,
                'text': self.text_cols,
                'boolean': self.boolean_cols,
                'id': self.id_cols
            }
        }

    def _analyze_data_quality(self) -> Dict:
        """Analyze data quality metrics."""
        # Missing values
        missing = self.df.isnull().sum()
        missing_pct = (missing / len(self.df) * 100).round(2)

        # Duplicates
        duplicates = self.df.duplicated().sum()

        # Completeness score
        completeness = (1 - self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns))) * 100

        # Unique values per column
        uniqueness = {col: self.df[col].nunique() for col in self.df.columns}

        quality_score = self._calculate_quality_score(missing_pct, duplicates)

        return {
            'missing_values': missing.to_dict(),
            'missing_percentage': missing_pct.to_dict(),
            'total_missing': int(self.df.isnull().sum().sum()),
            'total_missing_pct': round((self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns))) * 100, 2),
            'duplicate_rows': int(duplicates),
            'duplicate_pct': round(duplicates / len(self.df) * 100, 2),
            'completeness_score': round(completeness, 2),
            'quality_score': quality_score,
            'unique_values': uniqueness
        }

    def _calculate_quality_score(self, missing_pct: pd.Series, duplicates: int) -> Dict:
        """Calculate overall data quality score."""
        # Factors: completeness, uniqueness, consistency
        completeness = max(0, 100 - missing_pct.mean())
        duplicate_penalty = min(20, (duplicates / len(self.df)) * 100)

        score = completeness - duplicate_penalty

        if score >= 90:
            grade = 'A'
            label = 'Excellent'
        elif score >= 80:
            grade = 'B'
            label = 'Good'
        elif score >= 70:
            grade = 'C'
            label = 'Fair'
        elif score >= 60:
            grade = 'D'
            label = 'Poor'
        else:
            grade = 'F'
            label = 'Critical'

        return {
            'score': round(score, 1),
            'grade': grade,
            'label': label
        }

    def _analyze_numeric(self) -> Dict:
        """Comprehensive numeric column analysis."""
        if not self.numeric_cols:
            return {}

        results = {}
        for col in self.numeric_cols:
            data = self.df[col].dropna()
            if len(data) == 0:
                continue

            # Basic stats
            stats_dict = {
                'count': int(len(data)),
                'mean': float(data.mean()),
                'std': float(data.std()),
                'min': float(data.min()),
                'q1': float(data.quantile(0.25)),
                'median': float(data.median()),
                'q3': float(data.quantile(0.75)),
                'max': float(data.max()),
                'range': float(data.max() - data.min()),
                'iqr': float(data.quantile(0.75) - data.quantile(0.25)),
                'skewness': float(data.skew()),
                'kurtosis': float(data.kurtosis()),
                'zeros': int((data == 0).sum()),
                'zeros_pct': float((data == 0).sum() / len(data) * 100),
                'negative': int((data < 0).sum()),
                'negative_pct': float((data < 0).sum() / len(data) * 100)
            }

            # Normality test (for reasonable sample sizes)
            if 8 <= len(data) <= 5000:
                try:
                    _, p_value = stats.shapiro(data.sample(min(5000, len(data))))
                    stats_dict['normality_pvalue'] = float(p_value)
                    stats_dict['is_normal'] = p_value > 0.05
                except:
                    stats_dict['normality_pvalue'] = None
                    stats_dict['is_normal'] = None

            results[col] = stats_dict

        return results

    def _analyze_categorical(self) -> Dict:
        """Analyze categorical columns."""
        if not self.categorical_cols:
            return {}

        results = {}
        for col in self.categorical_cols:
            value_counts = self.df[col].value_counts()
            value_pcts = (value_counts / len(self.df) * 100).round(2)

            # Entropy (measure of randomness/diversity)
            probs = value_counts / value_counts.sum()
            entropy = float(-sum(probs * np.log2(probs + 1e-10)))
            max_entropy = np.log2(len(value_counts))
            normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

            results[col] = {
                'unique_values': int(self.df[col].nunique()),
                'top_values': value_counts.head(10).to_dict(),
                'top_percentages': value_pcts.head(10).to_dict(),
                'mode': str(value_counts.index[0]) if len(value_counts) > 0 else None,
                'mode_frequency': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                'mode_pct': float(value_pcts.iloc[0]) if len(value_pcts) > 0 else 0,
                'entropy': round(entropy, 3),
                'normalized_entropy': round(normalized_entropy, 3),
                'is_balanced': normalized_entropy > 0.8
            }

        return results

    def _analyze_temporal(self) -> Dict:
        """Analyze datetime columns."""
        if not self.datetime_cols:
            return {}

        results = {}
        for col in self.datetime_cols:
            data = self.df[col].dropna()
            if len(data) == 0:
                continue

            results[col] = {
                'min': str(data.min()),
                'max': str(data.max()),
                'range_days': int((data.max() - data.min()).days),
                'most_common_day': str(data.dt.day_name().mode().iloc[0]) if len(data) > 0 else None,
                'most_common_month': int(data.dt.month.mode().iloc[0]) if len(data) > 0 else None,
                'records_per_day': round(len(data) / max(1, (data.max() - data.min()).days), 2),
                'has_time': bool(data.dt.time.nunique() > 1)
            }

        return results

    def _analyze_correlations(self) -> Dict:
        """Analyze correlations between numeric columns."""
        if len(self.numeric_cols) < 2:
            return {}

        # Pearson correlation
        corr_matrix = self.df[self.numeric_cols].corr()

        # Find strong correlations
        strong_correlations = []
        for i, col1 in enumerate(self.numeric_cols):
            for j, col2 in enumerate(self.numeric_cols):
                if i < j:
                    corr = corr_matrix.loc[col1, col2]
                    if abs(corr) >= 0.5:
                        strong_correlations.append({
                            'column1': col1,
                            'column2': col2,
                            'correlation': round(corr, 3),
                            'strength': 'strong' if abs(corr) >= 0.7 else 'moderate'
                        })

        # Sort by absolute correlation
        strong_correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)

        return {
            'matrix': corr_matrix.round(3).to_dict(),
            'strong_correlations': strong_correlations[:20]
        }

    def _detect_outliers(self) -> Dict:
        """Detect outliers in numeric columns."""
        if not self.numeric_cols:
            return {}

        results = {}
        for col in self.numeric_cols:
            data = self.df[col].dropna()
            if len(data) == 0:
                continue

            # IQR method
            q1 = data.quantile(0.25)
            q3 = data.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            iqr_outliers = ((data < lower_bound) | (data > upper_bound)).sum()

            # Z-score method
            z_scores = np.abs(stats.zscore(data))
            zscore_outliers = (z_scores > OUTLIER_ZSCORE_THRESHOLD).sum()

            results[col] = {
                'iqr_outliers': int(iqr_outliers),
                'iqr_outliers_pct': round(iqr_outliers / len(data) * 100, 2),
                'iqr_bounds': {'lower': float(lower_bound), 'upper': float(upper_bound)},
                'zscore_outliers': int(zscore_outliers),
                'zscore_outliers_pct': round(zscore_outliers / len(data) * 100, 2),
                'has_significant_outliers': iqr_outliers / len(data) > 0.05
            }

        return results

    def _generate_insights(self, results: Dict) -> List[str]:
        """Generate human-readable insights from analysis."""
        insights = []

        # Data quality insights
        quality = results['data_quality']
        if quality['quality_score']['grade'] in ['A', 'B']:
            insights.append(f"✅ Data quality is {quality['quality_score']['label'].lower()} (score: {quality['quality_score']['score']})")
        else:
            insights.append(f"⚠️ Data quality needs attention (score: {quality['quality_score']['score']}, grade: {quality['quality_score']['grade']})")

        if quality['total_missing_pct'] > 10:
            insights.append(f"🔍 {quality['total_missing_pct']:.1f}% of data is missing - consider imputation or removal")

        if quality['duplicate_pct'] > 1:
            insights.append(f"📋 Found {quality['duplicate_rows']:,} duplicate rows ({quality['duplicate_pct']:.1f}%)")

        # Numeric insights
        numeric = results.get('numeric_analysis', {})
        for col, stats in numeric.items():
            if stats.get('skewness', 0) > 2:
                insights.append(f"📊 '{col}' is highly right-skewed - consider log transformation")
            elif stats.get('skewness', 0) < -2:
                insights.append(f"📊 '{col}' is highly left-skewed")

            if stats.get('zeros_pct', 0) > 50:
                insights.append(f"⚠️ '{col}' has {stats['zeros_pct']:.1f}% zero values")

        # Correlation insights
        correlations = results.get('correlations', {})
        strong_corrs = correlations.get('strong_correlations', [])
        if strong_corrs:
            top_corr = strong_corrs[0]
            insights.append(f"🔗 Strongest correlation: {top_corr['column1']} ↔ {top_corr['column2']} (r={top_corr['correlation']:.2f})")

        # Outlier insights
        outliers = results.get('outliers', {})
        for col, out in outliers.items():
            if out.get('has_significant_outliers'):
                insights.append(f"📍 '{col}' has {out['iqr_outliers_pct']:.1f}% outliers - review for data errors")

        # Categorical insights
        categorical = results.get('categorical_analysis', {})
        for col, cat in categorical.items():
            if cat.get('mode_pct', 0) > 80:
                insights.append(f"📌 '{col}' is dominated by '{cat['mode']}' ({cat['mode_pct']:.1f}%) - low variance")

        return insights

    def generate_visualizations(self, max_charts: int = 10) -> List[str]:
        """Generate all visualizations."""
        charts = []

        # 1. Data overview dashboard
        charts.append(self._plot_overview_dashboard())

        # 2. Missing values heatmap
        if self.df.isnull().sum().sum() > 0:
            charts.append(self._plot_missing_values())

        # 3. Numeric distributions
        if self.numeric_cols:
            charts.append(self._plot_numeric_distributions())

        # 4. Box plots for outliers
        if self.numeric_cols:
            charts.append(self._plot_box_plots())

        # 5. Correlation heatmap
        if len(self.numeric_cols) >= 2:
            charts.append(self._plot_correlation_heatmap())

        # 6. Categorical distributions
        if self.categorical_cols:
            charts.append(self._plot_categorical_distributions())

        # 7. Time series if applicable
        if self.datetime_cols and self.numeric_cols:
            charts.append(self._plot_time_series())

        # 8. Pair plot for key numeric columns
        if len(self.numeric_cols) >= 2 and len(self.numeric_cols) <= 6:
            charts.append(self._plot_pairplot())

        # 9. Violin plots
        if self.numeric_cols and self.categorical_cols:
            charts.append(self._plot_violin())

        self.charts_created = [c for c in charts if c is not None][:max_charts]
        return self.charts_created

    def _plot_overview_dashboard(self) -> str:
        """Create overview dashboard."""
        fig = plt.figure(figsize=(16, 10))
        fig.suptitle(f'Data Overview: {self.file_path.name}', fontsize=16, fontweight='bold')

        # Layout: 2x3 grid
        gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)

        # 1. Data types pie chart
        ax1 = fig.add_subplot(gs[0, 0])
        type_counts = [
            len(self.numeric_cols), len(self.categorical_cols),
            len(self.datetime_cols), len(self.text_cols), len(self.boolean_cols)
        ]
        type_labels = ['Numeric', 'Categorical', 'DateTime', 'Text', 'Boolean']
        colors = sns.color_palette('husl', n_colors=5)
        non_zero = [(l, c, col) for l, c, col in zip(type_labels, type_counts, colors) if c > 0]
        if non_zero:
            ax1.pie([x[1] for x in non_zero], labels=[x[0] for x in non_zero],
                   autopct='%1.0f%%', colors=[x[2] for x in non_zero])
        ax1.set_title('Column Types')

        # 2. Missing values by column
        ax2 = fig.add_subplot(gs[0, 1])
        missing = self.df.isnull().sum().sort_values(ascending=True)
        missing = missing[missing > 0].tail(10)
        if len(missing) > 0:
            missing.plot(kind='barh', ax=ax2, color=sns.color_palette('Reds', len(missing)))
            ax2.set_title('Missing Values (Top 10)')
            ax2.set_xlabel('Count')
        else:
            ax2.text(0.5, 0.5, 'No Missing Values!', ha='center', va='center', fontsize=14)
            ax2.set_title('Missing Values')

        # 3. Data quality gauge
        ax3 = fig.add_subplot(gs[0, 2])
        quality_score = self._calculate_quality_score(
            self.df.isnull().sum() / len(self.df) * 100,
            self.df.duplicated().sum()
        )['score']

        # Create gauge-like visualization
        theta = np.linspace(0, np.pi, 100)
        r = 1
        ax3.plot(r * np.cos(theta), r * np.sin(theta), 'k-', linewidth=2)

        # Score indicator
        score_angle = np.pi * (1 - quality_score / 100)
        ax3.annotate('', xy=(0.8 * np.cos(score_angle), 0.8 * np.sin(score_angle)),
                    xytext=(0, 0), arrowprops=dict(arrowstyle='->', color='red', lw=2))
        ax3.text(0, -0.3, f'{quality_score:.0f}%', ha='center', fontsize=20, fontweight='bold')
        ax3.text(0, -0.5, 'Quality Score', ha='center', fontsize=12)
        ax3.set_xlim(-1.2, 1.2)
        ax3.set_ylim(-0.7, 1.2)
        ax3.axis('off')
        ax3.set_title('Data Quality')

        # 4. Sample statistics table
        ax4 = fig.add_subplot(gs[1, 0])
        stats_data = [
            ['Rows', f'{len(self.df):,}'],
            ['Columns', f'{len(self.df.columns)}'],
            ['Numeric Cols', f'{len(self.numeric_cols)}'],
            ['Categorical Cols', f'{len(self.categorical_cols)}'],
            ['Missing %', f'{self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns)) * 100:.1f}%'],
            ['Duplicates', f'{self.df.duplicated().sum():,}']
        ]
        ax4.axis('off')
        table = ax4.table(cellText=stats_data, colLabels=['Metric', 'Value'],
                         loc='center', cellLoc='left')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        ax4.set_title('Summary Statistics')

        # 5. Top numeric column histogram
        ax5 = fig.add_subplot(gs[1, 1])
        if self.numeric_cols:
            col = self.numeric_cols[0]
            self.df[col].hist(ax=ax5, bins=30, edgecolor='black', alpha=0.7)
            ax5.set_title(f'Distribution: {col}')
            ax5.set_xlabel(col)
            ax5.set_ylabel('Frequency')
        else:
            ax5.text(0.5, 0.5, 'No numeric columns', ha='center', va='center')

        # 6. Top categorical column bar chart
        ax6 = fig.add_subplot(gs[1, 2])
        if self.categorical_cols:
            col = self.categorical_cols[0]
            self.df[col].value_counts().head(10).plot(kind='bar', ax=ax6, color=sns.color_palette('husl', 10))
            ax6.set_title(f'Top Values: {col}')
            ax6.set_xlabel(col)
            ax6.set_ylabel('Count')
            plt.setp(ax6.xaxis.get_majorticklabels(), rotation=45, ha='right')
        else:
            ax6.text(0.5, 0.5, 'No categorical columns', ha='center', va='center')

        plt.tight_layout()
        path = self.output_dir / 'overview_dashboard.png'
        plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        return str(path)

    def _plot_missing_values(self) -> str:
        """Plot missing values heatmap."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Missing values matrix (sample if too large)
        sample_df = self.df.sample(min(100, len(self.df))) if len(self.df) > 100 else self.df
        sns.heatmap(sample_df.isnull(), cbar=True, yticklabels=False, ax=axes[0], cmap='YlOrRd')
        axes[0].set_title('Missing Values Pattern')
        axes[0].set_xlabel('Columns')

        # Missing values bar chart
        missing = self.df.isnull().sum().sort_values(ascending=False)
        missing = missing[missing > 0]
        if len(missing) > 0:
            missing.head(15).plot(kind='bar', ax=axes[1], color=sns.color_palette('Reds_r', len(missing.head(15))))
            axes[1].set_title('Missing Values by Column')
            axes[1].set_ylabel('Count')
            plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=45, ha='right')

        plt.tight_layout()
        path = self.output_dir / 'missing_values.png'
        plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        return str(path)

    def _plot_numeric_distributions(self) -> str:
        """Plot distributions of numeric columns."""
        n_cols = min(6, len(self.numeric_cols))
        n_rows = (n_cols + 2) // 3

        fig, axes = plt.subplots(n_rows, 3, figsize=(15, 4 * n_rows))
        axes = axes.flatten() if n_cols > 1 else [axes]

        for idx, col in enumerate(self.numeric_cols[:6]):
            ax = axes[idx]
            data = self.df[col].dropna()

            # Histogram with KDE
            sns.histplot(data, kde=True, ax=ax, color=sns.color_palette('husl')[idx % 10])

            # Add mean and median lines
            ax.axvline(data.mean(), color='red', linestyle='--', label=f'Mean: {data.mean():.2f}')
            ax.axvline(data.median(), color='green', linestyle=':', label=f'Median: {data.median():.2f}')

            ax.set_title(f'{col}')
            ax.legend(fontsize=8)

        # Hide unused subplots
        for idx in range(n_cols, len(axes)):
            axes[idx].set_visible(False)

        plt.suptitle('Numeric Distributions', fontsize=14, fontweight='bold')
        plt.tight_layout()
        path = self.output_dir / 'numeric_distributions.png'
        plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        return str(path)

    def _plot_box_plots(self) -> str:
        """Plot box plots for outlier visualization."""
        n_cols = min(8, len(self.numeric_cols))

        fig, ax = plt.subplots(figsize=(14, 6))

        # Normalize data for comparison
        data_normalized = self.df[self.numeric_cols[:n_cols]].apply(
            lambda x: (x - x.mean()) / x.std() if x.std() > 0 else x
        )

        sns.boxplot(data=data_normalized, ax=ax, palette='husl')
        ax.set_title('Box Plots (Normalized for Comparison)')
        ax.set_ylabel('Normalized Value')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

        plt.tight_layout()
        path = self.output_dir / 'box_plots.png'
        plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        return str(path)

    def _plot_correlation_heatmap(self) -> str:
        """Plot correlation heatmap."""
        corr = self.df[self.numeric_cols].corr()

        fig, ax = plt.subplots(figsize=(12, 10))

        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
                   center=0, square=True, linewidths=0.5, ax=ax,
                   cbar_kws={'shrink': 0.8})

        ax.set_title('Correlation Matrix', fontsize=14, fontweight='bold')

        plt.tight_layout()
        path = self.output_dir / 'correlation_heatmap.png'
        plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        return str(path)

    def _plot_categorical_distributions(self) -> str:
        """Plot categorical column distributions."""
        n_cols = min(4, len(self.categorical_cols))

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()

        for idx, col in enumerate(self.categorical_cols[:4]):
            ax = axes[idx]
            value_counts = self.df[col].value_counts().head(MAX_CATEGORIES_FOR_PLOT)

            colors = sns.color_palette('husl', len(value_counts))
            value_counts.plot(kind='barh', ax=ax, color=colors)

            ax.set_title(f'{col}')
            ax.set_xlabel('Count')

            # Add percentage labels
            total = value_counts.sum()
            for i, (val, count) in enumerate(value_counts.items()):
                ax.text(count + total * 0.01, i, f'{count/total*100:.1f}%', va='center', fontsize=8)

        # Hide unused subplots
        for idx in range(n_cols, 4):
            axes[idx].set_visible(False)

        plt.suptitle('Categorical Distributions', fontsize=14, fontweight='bold')
        plt.tight_layout()
        path = self.output_dir / 'categorical_distributions.png'
        plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        return str(path)

    def _plot_time_series(self) -> Optional[str]:
        """Plot time series analysis."""
        if not self.datetime_cols or not self.numeric_cols:
            return None

        date_col = self.datetime_cols[0]
        df_sorted = self.df.sort_values(date_col).dropna(subset=[date_col])

        if len(df_sorted) == 0:
            return None

        n_cols = min(3, len(self.numeric_cols))
        fig, axes = plt.subplots(n_cols, 1, figsize=(14, 4 * n_cols))
        if n_cols == 1:
            axes = [axes]

        for idx, num_col in enumerate(self.numeric_cols[:3]):
            ax = axes[idx]

            # Resample by day if many data points
            if len(df_sorted) > 365:
                daily = df_sorted.set_index(date_col)[num_col].resample('D').mean()
                daily.plot(ax=ax, linewidth=1, alpha=0.7)

                # Add rolling average
                rolling = daily.rolling(7).mean()
                rolling.plot(ax=ax, linewidth=2, color='red', label='7-day MA')
            else:
                df_sorted.plot(x=date_col, y=num_col, ax=ax, linewidth=1, legend=False)

            ax.set_title(f'{num_col} Over Time')
            ax.set_xlabel('Date')
            ax.set_ylabel(num_col)
            ax.legend()
            ax.grid(True, alpha=0.3)

        plt.suptitle('Time Series Analysis', fontsize=14, fontweight='bold')
        plt.tight_layout()
        path = self.output_dir / 'time_series.png'
        plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        return str(path)

    def _plot_pairplot(self) -> Optional[str]:
        """Plot pairwise relationships."""
        if len(self.numeric_cols) < 2:
            return None

        cols = self.numeric_cols[:5]  # Limit to 5 columns

        # Sample if too large
        sample_df = self.df[cols].sample(min(1000, len(self.df)))

        g = sns.pairplot(sample_df, diag_kind='kde', plot_kws={'alpha': 0.5, 's': 20})
        g.fig.suptitle('Pairwise Relationships', y=1.02, fontsize=14, fontweight='bold')

        path = self.output_dir / 'pairplot.png'
        plt.savefig(path, dpi=100, bbox_inches='tight', facecolor='white')
        plt.close()
        return str(path)

    def _plot_violin(self) -> Optional[str]:
        """Plot violin plots for numeric vs categorical."""
        if not self.numeric_cols or not self.categorical_cols:
            return None

        # Find best categorical column (moderate number of categories)
        best_cat = None
        for col in self.categorical_cols:
            n_unique = self.df[col].nunique()
            if 2 <= n_unique <= 8:
                best_cat = col
                break

        if not best_cat:
            best_cat = self.categorical_cols[0]

        n_cats = self.df[best_cat].nunique()
        if n_cats > 10:
            return None

        num_col = self.numeric_cols[0]

        fig, ax = plt.subplots(figsize=(12, 6))
        sns.violinplot(data=self.df, x=best_cat, y=num_col, ax=ax, palette='husl')
        ax.set_title(f'{num_col} by {best_cat}')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

        plt.tight_layout()
        path = self.output_dir / 'violin_plot.png'
        plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        return str(path)

    def generate_report(self, format: str = 'markdown') -> str:
        """Generate analysis report."""
        results = self.analyze()
        self.generate_visualizations()

        if format == 'markdown':
            return self._generate_markdown_report(results)
        elif format == 'html':
            return self._generate_html_report(results)
        elif format == 'json':
            return json.dumps(results, indent=2, default=str)
        else:
            return self._generate_console_report(results)

    def _generate_markdown_report(self, results: Dict) -> str:
        """Generate markdown report."""
        lines = []

        # Header
        lines.append(f"# CSV Analysis Report: {self.file_path.name}")
        lines.append(f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        # Executive Summary
        lines.append("## 📋 Executive Summary\n")
        for insight in results['insights'][:5]:
            lines.append(f"- {insight}")
        lines.append("")

        # Data Overview
        info = results['file_info']
        lines.append("## 📊 Data Overview\n")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| File | {info['file_name']} |")
        lines.append(f"| Rows | {info['rows']:,} |")
        lines.append(f"| Columns | {info['columns']} |")
        lines.append(f"| Size | {info['file_size_mb']:.2f} MB |")
        lines.append(f"| Memory | {info['memory_usage_mb']:.2f} MB |")
        lines.append("")

        # Column Types
        lines.append("### Column Types\n")
        for type_name, count in info['column_types'].items():
            if count > 0:
                cols = info['columns_list'][type_name]
                lines.append(f"- **{type_name.title()}** ({count}): {', '.join(cols[:5])}")
                if len(cols) > 5:
                    lines.append(f"  - *...and {len(cols) - 5} more*")
        lines.append("")

        # Data Quality
        quality = results['data_quality']
        lines.append("## 🔍 Data Quality\n")
        lines.append(f"**Quality Score: {quality['quality_score']['score']}/100 ({quality['quality_score']['label']})**\n")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Completeness | {100 - quality['total_missing_pct']:.1f}% |")
        lines.append(f"| Duplicate Rows | {quality['duplicate_rows']:,} ({quality['duplicate_pct']:.1f}%) |")
        lines.append(f"| Total Missing | {quality['total_missing']:,} cells |")
        lines.append("")

        # Numeric Analysis
        if results['numeric_analysis']:
            lines.append("## 📈 Numeric Analysis\n")
            lines.append("| Column | Mean | Std | Min | Median | Max | Skew |")
            lines.append("|--------|------|-----|-----|--------|-----|------|")
            for col, stats in list(results['numeric_analysis'].items())[:10]:
                lines.append(f"| {col} | {stats['mean']:.2f} | {stats['std']:.2f} | {stats['min']:.2f} | {stats['median']:.2f} | {stats['max']:.2f} | {stats['skewness']:.2f} |")
            lines.append("")

        # Correlations
        if results['correlations'].get('strong_correlations'):
            lines.append("## 🔗 Strong Correlations\n")
            lines.append("| Column 1 | Column 2 | Correlation | Strength |")
            lines.append("|----------|----------|-------------|----------|")
            for corr in results['correlations']['strong_correlations'][:10]:
                lines.append(f"| {corr['column1']} | {corr['column2']} | {corr['correlation']:.3f} | {corr['strength']} |")
            lines.append("")

        # Outliers
        if results['outliers']:
            outlier_cols = [col for col, out in results['outliers'].items() if out['has_significant_outliers']]
            if outlier_cols:
                lines.append("## 📍 Outliers Detected\n")
                lines.append("| Column | Outliers (IQR) | % of Data |")
                lines.append("|--------|----------------|-----------|")
                for col in outlier_cols:
                    out = results['outliers'][col]
                    lines.append(f"| {col} | {out['iqr_outliers']:,} | {out['iqr_outliers_pct']:.1f}% |")
                lines.append("")

        # Categorical Analysis
        if results['categorical_analysis']:
            lines.append("## 📊 Categorical Analysis\n")
            for col, cat in list(results['categorical_analysis'].items())[:5]:
                lines.append(f"### {col}\n")
                lines.append(f"- Unique values: {cat['unique_values']}")
                lines.append(f"- Mode: {cat['mode']} ({cat['mode_pct']:.1f}%)")
                lines.append(f"- Balance: {'Balanced' if cat['is_balanced'] else 'Imbalanced'}\n")

        # Charts
        if self.charts_created:
            lines.append("## 📊 Visualizations\n")
            for chart in self.charts_created:
                chart_name = Path(chart).stem.replace('_', ' ').title()
                lines.append(f"### {chart_name}\n")
                lines.append(f"![{chart_name}]({chart})\n")

        # Warnings
        if results['warnings']:
            lines.append("## ⚠️ Warnings\n")
            for warning in results['warnings']:
                lines.append(f"- {warning}")
            lines.append("")

        report = '\n'.join(lines)

        # Save report
        report_path = self.output_dir / 'analysis_report.md'
        report_path.write_text(report)

        return report

    def _generate_html_report(self, results: Dict) -> str:
        """Generate HTML report with embedded images."""
        import base64

        # Convert images to base64
        def img_to_base64(path):
            with open(path, 'rb') as f:
                return base64.b64encode(f.read()).decode()

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>CSV Analysis: {self.file_path.name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .metric {{ display: inline-block; background: #e8f5e9; padding: 10px 20px; margin: 5px; border-radius: 5px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #2e7d32; }}
        .metric-label {{ font-size: 12px; color: #666; }}
        .insight {{ background: #fff3e0; padding: 10px 15px; margin: 5px 0; border-left: 4px solid #ff9800; border-radius: 0 5px 5px 0; }}
        .warning {{ background: #ffebee; border-left-color: #f44336; }}
        .chart {{ margin: 20px 0; text-align: center; }}
        .chart img {{ max-width: 100%; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .quality-score {{ font-size: 48px; font-weight: bold; color: {'#4CAF50' if results['data_quality']['quality_score']['score'] >= 80 else '#ff9800' if results['data_quality']['quality_score']['score'] >= 60 else '#f44336'}; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 CSV Analysis Report</h1>
        <p><strong>File:</strong> {self.file_path.name} | <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <h2>📋 Executive Summary</h2>
        {''.join(f'<div class="insight">{insight}</div>' for insight in results['insights'][:5])}

        <h2>📊 Data Overview</h2>
        <div class="metrics">
            <div class="metric"><div class="metric-value">{results['file_info']['rows']:,}</div><div class="metric-label">Rows</div></div>
            <div class="metric"><div class="metric-value">{results['file_info']['columns']}</div><div class="metric-label">Columns</div></div>
            <div class="metric"><div class="metric-value">{results['file_info']['file_size_mb']:.1f}MB</div><div class="metric-label">File Size</div></div>
            <div class="metric"><div class="quality-score">{results['data_quality']['quality_score']['score']:.0f}</div><div class="metric-label">Quality Score</div></div>
        </div>

        <h2>📊 Visualizations</h2>
        {''.join(f'<div class="chart"><img src="data:image/png;base64,{img_to_base64(chart)}" alt="{Path(chart).stem}"><p>{Path(chart).stem.replace("_", " ").title()}</p></div>' for chart in self.charts_created)}

        {'<h2>⚠️ Warnings</h2>' + ''.join(f'<div class="insight warning">{w}</div>' for w in results['warnings']) if results['warnings'] else ''}
    </div>
</body>
</html>
"""

        report_path = self.output_dir / 'analysis_report.html'
        report_path.write_text(html)

        return html

    def _generate_console_report(self, results: Dict) -> str:
        """Generate console-friendly report."""
        lines = []

        lines.append("=" * 70)
        lines.append(f"📊 CSV ANALYSIS: {self.file_path.name}")
        lines.append("=" * 70)

        # Quick stats
        info = results['file_info']
        quality = results['data_quality']

        lines.append(f"\n📋 OVERVIEW")
        lines.append(f"  Rows: {info['rows']:,} | Columns: {info['columns']} | Size: {info['file_size_mb']:.2f}MB")
        lines.append(f"  Quality Score: {quality['quality_score']['score']}/100 ({quality['quality_score']['label']})")

        # Insights
        lines.append(f"\n💡 KEY INSIGHTS")
        for insight in results['insights'][:7]:
            lines.append(f"  {insight}")

        # Column types
        lines.append(f"\n📊 COLUMN TYPES")
        for type_name, count in info['column_types'].items():
            if count > 0:
                lines.append(f"  • {type_name.title()}: {count}")

        # Numeric summary
        if results['numeric_analysis']:
            lines.append(f"\n📈 NUMERIC SUMMARY (Top 5)")
            lines.append(f"  {'Column':<20} {'Mean':>12} {'Std':>12} {'Min':>12} {'Max':>12}")
            lines.append(f"  {'-'*20} {'-'*12} {'-'*12} {'-'*12} {'-'*12}")
            for col, stats in list(results['numeric_analysis'].items())[:5]:
                lines.append(f"  {col:<20} {stats['mean']:>12.2f} {stats['std']:>12.2f} {stats['min']:>12.2f} {stats['max']:>12.2f}")

        # Strong correlations
        if results['correlations'].get('strong_correlations'):
            lines.append(f"\n🔗 STRONG CORRELATIONS")
            for corr in results['correlations']['strong_correlations'][:5]:
                lines.append(f"  • {corr['column1']} ↔ {corr['column2']}: {corr['correlation']:.3f}")

        # Charts
        if self.charts_created:
            lines.append(f"\n📊 VISUALIZATIONS CREATED ({len(self.charts_created)})")
            for chart in self.charts_created:
                lines.append(f"  ✓ {chart}")

        # Warnings
        if results['warnings']:
            lines.append(f"\n⚠️ WARNINGS")
            for warning in results['warnings']:
                lines.append(f"  {warning}")

        lines.append("\n" + "=" * 70)
        lines.append("✅ ANALYSIS COMPLETE")
        lines.append("=" * 70)

        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Comprehensive CSV analysis and visualization tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic analysis with visualizations
  python analyze_csv.py data.csv

  # Generate markdown report
  python analyze_csv.py data.csv --format markdown

  # Generate HTML report with all charts
  python analyze_csv.py data.csv --format html --output-dir ./reports

  # Sample large file
  python analyze_csv.py huge_data.csv --sample 50000

  # JSON output for programmatic use
  python analyze_csv.py data.csv --format json --no-charts
        """
    )

    parser.add_argument('file', help='Path to CSV file')
    parser.add_argument('--format', '-f', choices=['console', 'markdown', 'html', 'json'],
                       default='console', help='Output format (default: console)')
    parser.add_argument('--output-dir', '-o', help='Output directory for charts and reports')
    parser.add_argument('--sample', '-s', type=int, help='Sample size for large files')
    parser.add_argument('--no-charts', action='store_true', help='Skip chart generation')
    parser.add_argument('--max-charts', type=int, default=10, help='Maximum number of charts')
    parser.add_argument('--date-columns', nargs='+', help='Specify date columns')

    args = parser.parse_args()

    # Validate file
    if not Path(args.file).exists():
        print(f"Error: File not found: {args.file}")
        return 1

    # Create analyzer
    analyzer = CSVAnalyzer(
        file_path=args.file,
        output_dir=args.output_dir,
        sample_size=args.sample,
        date_columns=args.date_columns
    )

    # Generate charts unless disabled
    if not args.no_charts and args.format != 'json':
        analyzer.generate_visualizations(max_charts=args.max_charts)

    # Generate report
    report = analyzer.generate_report(format=args.format)
    print(report)

    # Print output location
    if args.format in ['markdown', 'html']:
        print(f"\n📁 Report saved to: {analyzer.output_dir / f'analysis_report.{args.format[:4] if args.format == 'markdown' else args.format}'}")

    return 0


if __name__ == '__main__':
    exit(main())
