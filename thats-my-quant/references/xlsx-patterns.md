# Excel Output Patterns

Patterns for outputting analysis results to Excel with proper formulas, formatting, and financial model standards.

*Adapted from [Anthropic's xlsx skill](https://github.com/anthropics/skills/tree/main/skills/xlsx)*

---

## Core Requirements

### Zero Formula Errors

**Every Excel output MUST be delivered with ZERO formula errors:**
- `#REF!` - Invalid cell references
- `#DIV/0!` - Division by zero
- `#VALUE!` - Wrong data type in formula
- `#N/A` - Value not available
- `#NAME?` - Unrecognized formula name

### Use Formulas, Not Hardcoded Values

Always use Excel formulas instead of calculating in Python and hardcoding results. This keeps spreadsheets dynamic and updateable.

```python
# BAD - Hardcoding calculated values
total = df['Revenue'].sum()
sheet['B10'] = total  # Hardcodes 500000

# GOOD - Using Excel formulas
sheet['B10'] = '=SUM(B2:B9)'
```

---

## Financial Model Standards

### Color Coding Convention

| Color | RGB | Use For |
|-------|-----|---------|
| **Blue text** | (0, 0, 255) | Hardcoded inputs, user-changeable values |
| **Black text** | (0, 0, 0) | ALL formulas and calculations |
| **Green text** | (0, 128, 0) | Links to other worksheets in same workbook |
| **Red text** | (255, 0, 0) | External file references |
| **Yellow background** | (255, 255, 0) | Key assumptions needing attention |

```python
from openpyxl.styles import Font, PatternFill

# Input cell (user can change)
sheet['B3'].font = Font(color='0000FF')  # Blue

# Formula cell
sheet['B4'].font = Font(color='000000')  # Black
sheet['B4'] = '=B2*B3'

# Key assumption
sheet['B5'].fill = PatternFill('solid', fgColor='FFFF00')  # Yellow
```

### Number Formatting Standards

| Type | Format | Example |
|------|--------|---------|
| Years | Text string | "2024" not "2,024" |
| Currency | $#,##0 | $1,234,567 |
| Currency (negative) | $#,##0;($#,##0);- | ($1,234) or - |
| Percentages | 0.0% | 12.5% |
| Multiples | 0.0x | 3.5x |
| Large numbers | Always specify units in headers | "Revenue ($mm)" |

```python
from openpyxl.styles import numbers

# Currency with parentheses for negative, dash for zero
sheet['B5'].number_format = '$#,##0;($#,##0);"-"'

# Percentage
sheet['C5'].number_format = '0.0%'

# Multiple
sheet['D5'].number_format = '0.0x'
```

---

## Tool Selection

| Task | Best Tool | Notes |
|------|-----------|-------|
| Data analysis, aggregation | pandas | `df.to_excel()` for simple output |
| Formulas and formatting | openpyxl | Full Excel feature support |
| Large file reading | pandas with `read_only=True` | Memory efficient |
| Preserving existing formulas | openpyxl | Don't use `data_only=True` when saving |

---

## Interactive Workbook Architecture

When building Excel workbooks that users will interact with (adjusting parameters, testing scenarios), use this multi-sheet pattern:

### Sheet Structure

```
Config sheet:    Editable parameters (weights, thresholds) in yellow cells
Data sheet:      Raw data only (source of truth, never edited)
Calculated:      ALL columns use formulas referencing Config + Data
Summary:         COUNTIF/COUNTIFS formulas referencing Calculated
```

### Implementation Pattern

```python
def create_interactive_workbook(df, config_params, filename):
    """Create workbook with editable parameters driving all calculations."""
    wb = Workbook()

    # === CONFIG SHEET ===
    ws_config = wb.active
    ws_config.title = "Config"
    ws_config['A1'] = "PARAMETERS (Edit yellow cells)"
    ws_config['A1'].font = Font(bold=True, size=12)

    row = 3
    for param_name, param_value in config_params.items():
        ws_config[f'A{row}'] = param_name
        ws_config[f'B{row}'] = param_value
        ws_config[f'B{row}'].font = Font(color='0000FF')  # Blue = input
        ws_config[f'B{row}'].fill = PatternFill('solid', fgColor='FFFF00')  # Yellow
        row += 1

    # === DATA SHEET ===
    ws_data = wb.create_sheet("Data")
    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 1):
        for c_idx, value in enumerate(row, 1):
            ws_data.cell(row=r_idx, column=c_idx, value=value)

    # === CALCULATED SHEET ===
    ws_calc = wb.create_sheet("Calculated")
    # Headers
    ws_calc['A1'] = "Name"
    ws_calc['B1'] = "Raw_Score"
    ws_calc['C1'] = "Weighted_Score"
    ws_calc['D1'] = "Classification"

    # Formulas referencing Config + Data
    for i in range(2, len(df) + 2):
        ws_calc[f'A{i}'] = f"=Data!A{i}"
        ws_calc[f'B{i}'] = f"=Data!B{i}"
        # Weighted score references Config!B3 (the weight parameter)
        ws_calc[f'C{i}'] = f"=B{i}*Config!$B$3"
        # Classification based on threshold in Config!B4
        ws_calc[f'D{i}'] = f'=IF(C{i}>=Config!$B$4,"High","Low")'

    # === SUMMARY SHEET ===
    ws_summary = wb.create_sheet("Summary")
    ws_summary['A1'] = "Summary Statistics"
    ws_summary['A1'].font = Font(bold=True, size=12)

    ws_summary['A3'] = "High Performers"
    ws_summary['B3'] = f'=COUNTIF(Calculated!D:D,"High")'

    ws_summary['A4'] = "Low Performers"
    ws_summary['B4'] = f'=COUNTIF(Calculated!D:D,"Low")'

    ws_summary['A5'] = "Total"
    ws_summary['B5'] = '=B3+B4'

    wb.save(filename)
    return filename
```

### Key Principles

1. **All formulas reference Config:** When user changes a parameter, all calculations update
2. **Data sheet is read-only:** Never put formulas in the Data sheet
3. **Calculated sheet has only formulas:** No hardcoded values
4. **Summary uses COUNTIF/SUMIF:** Dynamic aggregation from Calculated

---

## Auto-Size Columns

When outputting data, auto-size columns based on rendered content:

```python
def auto_size_columns(ws, min_width=10, max_width=50):
    """
    Size columns based on rendered content, not formula text.

    Note: Uses cell.value (the rendered value) not the formula string,
    so =SUM(A1:A100) doesn't cause the column to be too wide.
    """
    for col in ws.columns:
        max_len = 0
        col_letter = col[0].column_letter
        for cell in col:
            try:
                # Use value (rendered), not formula text
                val = str(cell.value) if cell.value else ""
                max_len = max(max_len, len(val))
            except:
                pass
        ws.column_dimensions[col_letter].width = min(max(max_len + 2, min_width), max_width)
```

### Usage

```python
# After populating worksheet
auto_size_columns(ws_data)
auto_size_columns(ws_summary, min_width=12, max_width=40)
wb.save(filename)
```

---

## Common Workflows

### Export Analysis Results

```python
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows

def export_analysis_to_excel(df, summary_stats, filename):
    """Export analysis results with proper formatting."""
    wb = Workbook()

    # === DATA SHEET ===
    ws_data = wb.active
    ws_data.title = "Data"

    # Write DataFrame
    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 1):
        for c_idx, value in enumerate(row, 1):
            cell = ws_data.cell(row=r_idx, column=c_idx, value=value)
            if r_idx == 1:  # Header row
                cell.font = Font(bold=True)
                cell.fill = PatternFill('solid', fgColor='E0E0E0')

    # === SUMMARY SHEET ===
    ws_summary = wb.create_sheet("Summary")

    # Title
    ws_summary['A1'] = "Analysis Summary"
    ws_summary['A1'].font = Font(bold=True, size=14)

    # Add summary metrics with formulas referencing data sheet
    ws_summary['A3'] = "Total Revenue"
    ws_summary['B3'] = f"=SUM(Data!B2:B{len(df)+1})"
    ws_summary['B3'].number_format = '$#,##0'

    ws_summary['A4'] = "Average Revenue"
    ws_summary['B4'] = f"=AVERAGE(Data!B2:B{len(df)+1})"
    ws_summary['B4'].number_format = '$#,##0'

    wb.save(filename)
    return filename
```

### Create Financial Model Template

```python
def create_model_template(filename, years=5):
    """Create a financial model template with proper structure."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Model"

    # Header row
    ws['A1'] = "Metric"
    for i, year in enumerate(range(2024, 2024 + years)):
        col = chr(ord('B') + i)
        ws[f'{col}1'] = str(year)
        ws[f'{col}1'].font = Font(bold=True)
        ws[f'{col}1'].alignment = Alignment(horizontal='center')

    # Assumptions section (blue = inputs)
    ws['A3'] = "ASSUMPTIONS"
    ws['A3'].font = Font(bold=True)

    ws['A4'] = "Growth Rate"
    ws['B4'] = 0.10  # 10% default
    ws['B4'].font = Font(color='0000FF')  # Blue = input
    ws['B4'].number_format = '0.0%'
    ws['B4'].fill = PatternFill('solid', fgColor='FFFF00')  # Yellow = key assumption

    # Calculations section (black = formulas)
    ws['A6'] = "CALCULATIONS"
    ws['A6'].font = Font(bold=True)

    ws['A7'] = "Revenue"
    ws['B7'] = 1000000  # Base year input
    ws['B7'].font = Font(color='0000FF')
    ws['B7'].number_format = '$#,##0'

    # Revenue projections with formulas
    for i in range(1, years):
        col = chr(ord('B') + i)
        prev_col = chr(ord('B') + i - 1)
        ws[f'{col}7'] = f'={prev_col}7*(1+$B$4)'  # Reference growth rate
        ws[f'{col}7'].font = Font(color='000000')  # Black = formula
        ws[f'{col}7'].number_format = '$#,##0'

    wb.save(filename)
    return filename
```

### Cohort Analysis Output

```python
def export_cohort_analysis(cohort_df, filename):
    """Export cohort retention table with heatmap formatting."""
    from openpyxl.formatting.rule import ColorScaleRule

    wb = Workbook()
    ws = wb.active
    ws.title = "Cohort Retention"

    # Write cohort data
    for r_idx, row in enumerate(dataframe_to_rows(cohort_df, index=True, header=True), 1):
        for c_idx, value in enumerate(row, 1):
            cell = ws.cell(row=r_idx, column=c_idx, value=value)
            if r_idx == 1 or c_idx == 1:  # Headers
                cell.font = Font(bold=True)
            elif isinstance(value, (int, float)):
                cell.number_format = '0.0%'

    # Add color scale (green = high retention, red = low)
    data_range = f"B2:{chr(ord('A') + cohort_df.shape[1])}{cohort_df.shape[0] + 1}"
    ws.conditional_formatting.add(
        data_range,
        ColorScaleRule(
            start_type='min', start_color='F8696B',  # Red
            mid_type='percentile', mid_value=50, mid_color='FFEB84',  # Yellow
            end_type='max', end_color='63BE7B'  # Green
        )
    )

    wb.save(filename)
    return filename
```

---

## Formula Patterns for Analysis

### Common Formulas

```python
# Totals
sheet['B10'] = '=SUM(B2:B9)'

# Averages
sheet['B11'] = '=AVERAGE(B2:B9)'

# Growth rate
sheet['C5'] = '=(B5-B4)/B4'

# Year-over-year change
sheet['D5'] = '=(C5-B5)/B5'

# Percentage of total
sheet['E5'] = '=B5/SUM($B$2:$B$9)'

# CAGR (Compound Annual Growth Rate)
# End Value, Start Value, Years
sheet['F5'] = '=(B9/B2)^(1/7)-1'

# Conditional sum
sheet['B12'] = '=SUMIF(A2:A9,"Enterprise",B2:B9)'

# Weighted average
sheet['B13'] = '=SUMPRODUCT(B2:B9,C2:C9)/SUM(C2:C9)'
```

### Cross-Sheet References

```python
# Reference another sheet
sheet['B5'] = "=Data!B10"

# Sum from another sheet
sheet['B6'] = "=SUM(Revenue!B2:B100)"

# VLOOKUP across sheets
sheet['C5'] = "=VLOOKUP(A5,Mapping!A:B,2,FALSE)"
```

---

## Verification Workflow

### After Creating Excel File

1. **Save the file**
2. **Run recalc.py** to calculate formulas:
   ```bash
   python scripts/recalc.py output.xlsx
   ```
3. **Check JSON output** for errors:
   ```json
   {
     "status": "success",
     "total_errors": 0,
     "total_formulas": 42
   }
   ```
4. **Fix any errors** and re-run recalc

### Common Error Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `#REF!` | Invalid cell reference | Check range boundaries |
| `#DIV/0!` | Division by zero | Add `IFERROR()` wrapper or check data |
| `#VALUE!` | Wrong data type | Ensure numeric values in formula cells |
| `#NAME?` | Typo in formula | Check function spelling |
| `#N/A` | VLOOKUP not found | Verify lookup value exists |

```python
# Wrap formulas to handle errors gracefully
sheet['B5'] = '=IFERROR(A5/A4,0)'  # Returns 0 instead of #DIV/0!
sheet['C5'] = '=IFERROR(VLOOKUP(A5,Data!A:B,2,FALSE),"")'  # Returns blank if not found
```

---

## Best Practices

### Do

- Use formulas for all calculations
- Apply consistent color coding
- Include units in headers
- Document assumptions with yellow highlighting
- Test formulas with edge cases (zero, negative values)
- Run recalc.py before delivering

### Don't

- Hardcode calculated values
- Mix formatting conventions
- Leave formula errors unchecked
- Use `data_only=True` when saving (destroys formulas)
- Skip the recalculation step

---

## Decision Logging

```python
# === EXCEL OUTPUT LOG ===
# FORMAT: Financial model color coding applied
# FORMULAS: Revenue projections use growth rate from B4
# ASSUMPTION: Growth rate (10%) highlighted in yellow - user should validate
# VERIFICATION: recalc.py run, 0 errors found
```
