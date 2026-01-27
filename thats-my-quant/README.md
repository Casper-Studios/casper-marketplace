# That's My Quant - Data Analysis Plugin for Claude Code

A comprehensive data analysis and storytelling skill optimized for financial, SaaS, and RevOps contexts. This plugin provides structured workflows for turning raw data into actionable insights with full transparency on analytical decisions, bias awareness, and progressive disclosure reporting.

## Features

- **Decision Logging**: Track every analytical choice for audit trails and reproducibility
- **Bias-Aware Interpretation**: Built-in checklists for survivorship bias, Simpson's paradox, and more
- **Progressive Disclosure**: Slide deck -> detailed report -> full notebook with all decisions documented
- **Financial Standards**: Excel output with proper formulas, color coding, and zero formula errors
- **Dashboard Building**: Marimo-based interactive dashboards with KPI cards and filters

## Installation

### Option 1: Marketplace (Recommended)

```bash
# 1. Add the Casper Studios marketplace
/plugin marketplace add Casper-Studios/plugin-marketplace

# 2. Install the plugin
/plugin install thats-my-quant
```

### Option 2: Git Clone + Local Plugin Directory

```bash
# Clone the repository
git clone git@github.com:Casper-Studios/plugin-marketplace.git

# Run Claude Code with the plugin directory
claude --plugin-dir ./plugin-marketplace
```

## Commands

### `/thats-my-quant:analyze`

Run the full data analysis workflow with decision logging and bias checking.

## Workflow Overview

Every analysis follows a 7-phase process:

```
1. SETUP    → Initialize Marimo notebook (run init_marimo_notebook.py)
2. INGEST   → Load data, document sources and assumptions
3. EXPLORE  → EDA with logged decisions (why this viz, why this filter)
4. MODEL    → If needed, with interpretable-first approach
5. INTERPRET → Apply bias checklist, hedge appropriately
6. WISHLIST → Document data gaps and proxies used
7. OUTPUT   → Generate appropriate tier (slides/report/notebook)
```

## Reference Files

| Reference | When to Use |
|-----------|-------------|
| `references/metrics.md` | Calculating SaaS/RevOps metrics (ARR, MRR, NRR, churn, LTV, CAC) |
| `references/biases.md` | Interpretation phase, before finalizing insights |
| `references/bullshit-detector.md` | Sanity checking claims, detecting statistical sins |
| `references/data-cleaning.md` | Data quality checks, cleaning patterns |
| `references/datetime-handling.md` | Timezone, parsing, fiscal calendars |
| `references/dashboard-patterns.md` | Marimo layouts, KPIs, interactivity |
| `references/visualization-guide.md` | Choosing chart types, avoiding anti-patterns |
| `references/report-templates.md` | Pyramid Principle vs Consulting structure |
| `references/data-wishlisting.md` | Documenting gaps, rating proxy quality |
| `references/xlsx-patterns.md` | Excel output, financial model standards, formulas |
| `references/pdf-patterns.md` | PDF extraction, report creation, manipulation |

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `init_marimo_notebook.py` | Initialize analysis workspace | `python scripts/init_marimo_notebook.py <name>` |
| `profile_data.py` | Generate data quality report | `python scripts/profile_data.py <csv_file>` |
| `init_dashboard.py` | Scaffold interactive dashboard | `python scripts/init_dashboard.py <name>` |
| `generate_pptx_summary.py` | Create slide deck from findings | `python scripts/generate_pptx_summary.py <config.json>` |
| `recalc.py` | Recalculate Excel formulas | `python scripts/recalc.py <xlsx_file>` |

## Technology Stack

| Tool | Purpose | Why |
|------|---------|-----|
| **Marimo** | Notebook environment | Pure Python files, reactive, git-friendly |
| **pandas** | Data manipulation | Reliable LLM code generation, mature ecosystem |
| **Matplotlib/Seaborn** | Visualization | Publication-quality, static, well-supported |
| **python-pptx** | Slide generation | Programmatic PowerPoint creation |
| **openpyxl** | Excel files | Formulas, formatting, financial models |
| **pypdf/pdfplumber** | PDF handling | Extract text, tables; create reports |
| **reportlab** | PDF creation | Professional PDF reports |

## Example Invocations

```
"Analyze our ARR trends by segment and identify drivers of growth/churn"
"Build a win rate analysis by deal size and sales rep"
"Create a retention cohort analysis for customers acquired in 2023"
"Project next quarter revenue based on current pipeline"
"Create an executive summary deck of our key SaaS metrics"
"Clean this messy CSV and profile the data quality"
"Build a dashboard to monitor our key SaaS metrics"
"Sanity check these findings before I present them"
"Export this analysis to Excel with proper formulas and formatting"
"Extract the tables from this quarterly report PDF"
```

## Directory Structure

```
thats-my-quant/
├── .claude-plugin/
│   ├── plugin.json              # Plugin manifest
│   └── marketplace.json         # Marketplace metadata
├── commands/
│   └── analyze.md               # Main analysis command
├── scripts/
│   ├── init_marimo_notebook.py  # Notebook scaffolding
│   ├── profile_data.py          # Data quality profiling
│   ├── init_dashboard.py        # Dashboard scaffolding
│   ├── generate_pptx_summary.py # PowerPoint generation
│   └── recalc.py                # Excel formula recalc
├── references/
│   ├── metrics.md               # SaaS metrics definitions
│   ├── biases.md                # Analytical bias checklist
│   ├── bullshit-detector.md     # Statistical sanity checks
│   ├── data-cleaning.md         # Cleaning patterns
│   ├── datetime-handling.md     # Date/time patterns
│   ├── dashboard-patterns.md    # Marimo dashboard patterns
│   ├── visualization-guide.md   # Chart selection guide
│   ├── report-templates.md      # Report structures
│   ├── data-wishlisting.md      # Data gap documentation
│   ├── xlsx-patterns.md         # Excel output patterns
│   └── pdf-patterns.md          # PDF handling patterns
├── SKILL.md                     # Main skill documentation
└── README.md                    # This file
```

## License

MIT
