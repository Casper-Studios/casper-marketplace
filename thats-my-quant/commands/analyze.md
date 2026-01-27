---
description: Run data analysis workflow with decision logging and bias checking
---

# Data Analysis Skill

Use this skill for data analysis, visualization, and storytelling in financial and RevOps contexts.

## When to Use

- Analyzing revenue data, building forecasts, cohort analysis
- Churn modeling, pipeline analytics
- Creating data-driven reports, building dashboards
- Cleaning messy data, sanity-checking analytical claims
- Exporting to Excel with formulas, extracting data from PDFs

## Instructions

1. Read `${CLAUDE_PLUGIN_ROOT}/SKILL.md` for the complete workflow guide
2. Follow the 7-phase analysis process:
   - SETUP: Initialize Marimo notebook
   - INGEST: Load data, document sources
   - EXPLORE: EDA with logged decisions
   - MODEL: If needed, interpretable-first
   - INTERPRET: Apply bias checklist
   - WISHLIST: Document data gaps
   - OUTPUT: Generate appropriate tier

## Key Reference Files

Load these as needed during analysis:

| Reference | When to Use |
|-----------|-------------|
| `${CLAUDE_PLUGIN_ROOT}/references/metrics.md` | Calculating SaaS/RevOps metrics |
| `${CLAUDE_PLUGIN_ROOT}/references/biases.md` | Interpretation phase, before finalizing insights |
| `${CLAUDE_PLUGIN_ROOT}/references/bullshit-detector.md` | Sanity checking claims, detecting issues |
| `${CLAUDE_PLUGIN_ROOT}/references/data-cleaning.md` | Data quality checks, cleaning patterns |
| `${CLAUDE_PLUGIN_ROOT}/references/visualization-guide.md` | Choosing chart types, avoiding anti-patterns |
| `${CLAUDE_PLUGIN_ROOT}/references/xlsx-patterns.md` | Excel output, financial model standards |
| `${CLAUDE_PLUGIN_ROOT}/references/pdf-patterns.md` | PDF extraction, report creation |

## Scripts

| Script | Purpose |
|--------|---------|
| `${CLAUDE_PLUGIN_ROOT}/scripts/init_marimo_notebook.py` | Initialize analysis workspace |
| `${CLAUDE_PLUGIN_ROOT}/scripts/profile_data.py` | Generate data quality report |
| `${CLAUDE_PLUGIN_ROOT}/scripts/init_dashboard.py` | Scaffold interactive dashboard |
| `${CLAUDE_PLUGIN_ROOT}/scripts/generate_pptx_summary.py` | Create slide deck from findings |
| `${CLAUDE_PLUGIN_ROOT}/scripts/recalc.py` | Recalculate Excel formulas |

## Decision Logging

Every analytical choice must be logged:

```python
# === DECISION LOG ===
# FILTER: Excluded trial accounts - 1,247 records removed
# METRIC: NRR over GRR because expansion is significant factor
# ASSUMPTION: Q4 seasonality similar to prior year - confidence: M
# PROXY: Support ticket sentiment for NPS - quality: Weak
```
