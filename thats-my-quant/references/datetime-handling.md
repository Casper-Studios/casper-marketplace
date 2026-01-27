# Datetime Handling Reference

Timezone hell, format parsing, fiscal calendars, and common datetime gotchas for financial and RevOps analysis.

---

## Timezone Fundamentals

### Golden Rules

1. **Store in UTC** - Always convert to UTC for storage and computation
2. **Display in local** - Convert to user's timezone only for display
3. **Document the timezone** - Every timestamp should have explicit timezone info
4. **Be consistent** - All datetimes in one analysis should use the same timezone

### Timezone Conversion Patterns

```python
import pandas as pd
from datetime import datetime
import pytz

# Make naive datetime timezone-aware
naive_dt = datetime(2024, 1, 15, 9, 0, 0)
utc_dt = pytz.UTC.localize(naive_dt)

# Convert between timezones
eastern = pytz.timezone('US/Eastern')
pacific = pytz.timezone('US/Pacific')
eastern_dt = utc_dt.astimezone(eastern)
pacific_dt = utc_dt.astimezone(pacific)

# Pandas timezone operations
df['timestamp_utc'] = pd.to_datetime(df['timestamp']).dt.tz_localize('UTC')
df['timestamp_eastern'] = df['timestamp_utc'].dt.tz_convert('US/Eastern')

# Remove timezone info (for comparisons)
df['timestamp_naive'] = df['timestamp_utc'].dt.tz_localize(None)
```

### Common Timezone Codes

| Code | Description | UTC Offset (Standard) |
|------|-------------|----------------------|
| `UTC` | Coordinated Universal Time | +0:00 |
| `US/Eastern` | US Eastern (EST/EDT) | -5:00 / -4:00 |
| `US/Pacific` | US Pacific (PST/PDT) | -8:00 / -7:00 |
| `US/Central` | US Central (CST/CDT) | -6:00 / -5:00 |
| `Europe/London` | UK (GMT/BST) | +0:00 / +1:00 |
| `Europe/Paris` | Central Europe (CET/CEST) | +1:00 / +2:00 |
| `Asia/Tokyo` | Japan (JST) | +9:00 |
| `Asia/Singapore` | Singapore (SGT) | +8:00 |

### DST Gotchas

```python
# Daylight Saving Time creates problems
# Spring forward: 2:00 AM doesn't exist (March)
# Fall back: 2:00 AM happens twice (November)

# Handle ambiguous times (fall back)
df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(
    'US/Eastern',
    ambiguous='NaT'  # Mark ambiguous as NaT
    # or ambiguous='infer' to guess
)

# Handle non-existent times (spring forward)
df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(
    'US/Eastern',
    nonexistent='shift_forward'  # Shift to valid time
    # or nonexistent='NaT' to mark as missing
)
```

---

## Date Parsing

### Common Format Codes

| Code | Meaning | Example |
|------|---------|---------|
| `%Y` | 4-digit year | 2024 |
| `%y` | 2-digit year | 24 |
| `%m` | Month (zero-padded) | 01, 12 |
| `%d` | Day (zero-padded) | 01, 31 |
| `%H` | Hour (24-hour) | 00, 23 |
| `%I` | Hour (12-hour) | 01, 12 |
| `%M` | Minute | 00, 59 |
| `%S` | Second | 00, 59 |
| `%p` | AM/PM | AM, PM |
| `%B` | Full month name | January |
| `%b` | Abbreviated month | Jan |

### Parsing Common Formats

```python
# ISO 8601 (ideal format)
df['date'] = pd.to_datetime(df['date'])  # Auto-detects

# American format (MM/DD/YYYY)
df['date'] = pd.to_datetime(df['date'], format='%m/%d/%Y')

# European format (DD/MM/YYYY)
df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')

# With time
df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')

# 12-hour time with AM/PM
df['datetime'] = pd.to_datetime(df['datetime'], format='%m/%d/%Y %I:%M %p')

# Excel serial dates
df['date'] = pd.to_datetime(df['date'], unit='D', origin='1899-12-30')

# Unix timestamps (seconds since 1970)
df['date'] = pd.to_datetime(df['timestamp'], unit='s')

# Unix timestamps (milliseconds)
df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
```

### Handling Mixed Formats

```python
# Let pandas infer (slower but flexible)
df['date'] = pd.to_datetime(df['date'], infer_datetime_format=True)

# Handle errors gracefully
df['date'] = pd.to_datetime(df['date'], errors='coerce')  # Invalid -> NaT

# Try multiple formats
def parse_date_flexible(date_str):
    """Try multiple date formats."""
    formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y/%m/%d',
        '%B %d, %Y',
        '%d-%b-%Y',
    ]
    for fmt in formats:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except ValueError:
            continue
    return pd.NaT

df['date'] = df['date_str'].apply(parse_date_flexible)
```

---

## Fiscal Calendar Handling

### Fiscal Year Setup

```python
def get_fiscal_year(date, fy_start_month=1):
    """
    Get fiscal year for a date.

    Args:
        date: datetime
        fy_start_month: Month when FY starts (1=Jan, 2=Feb, etc.)

    Returns:
        Fiscal year (int)
    """
    if date.month >= fy_start_month:
        return date.year if fy_start_month == 1 else date.year + 1
    else:
        return date.year if fy_start_month == 1 else date.year

def get_fiscal_quarter(date, fy_start_month=1):
    """Get fiscal quarter (1-4) for a date."""
    # Adjust month to fiscal calendar
    adjusted_month = (date.month - fy_start_month) % 12 + 1
    return (adjusted_month - 1) // 3 + 1

# Apply to DataFrame
df['fiscal_year'] = df['date'].apply(lambda x: get_fiscal_year(x, fy_start_month=2))
df['fiscal_quarter'] = df['date'].apply(lambda x: get_fiscal_quarter(x, fy_start_month=2))
```

### Common Fiscal Year Patterns

| Company Type | FY Start | Example |
|--------------|----------|---------|
| Calendar year | January 1 | FY2024 = Jan-Dec 2024 |
| US Federal | October 1 | FY2024 = Oct 2023 - Sep 2024 |
| Retail (4-5-4) | Various | Based on week patterns |
| UK Tax Year | April 6 | FY2024 = Apr 2024 - Mar 2025 |

### FY vs CY Comparison

```python
# Create both calendar and fiscal year columns
df['calendar_year'] = df['date'].dt.year
df['calendar_quarter'] = df['date'].dt.quarter

# Fiscal year starting February
df['fiscal_year'] = df['date'].apply(lambda x: x.year if x.month < 2 else x.year + 1)
df['fiscal_quarter'] = df['date'].apply(
    lambda x: ((x.month - 2) % 12) // 3 + 1
)

# Log the convention
# ASSUMPTION: Using February fiscal year (FY2024 = Feb 2023 - Jan 2024)
```

---

## Period Aggregation

### Daily to Weekly

```python
# Week starting Monday (default)
df['week'] = df['date'].dt.to_period('W').dt.start_time

# Week starting Sunday
df['week'] = df['date'].dt.to_period('W-SAT').dt.start_time

# ISO week number
df['iso_week'] = df['date'].dt.isocalendar().week
df['iso_year'] = df['date'].dt.isocalendar().year
```

### Daily to Monthly

```python
# Month period
df['month'] = df['date'].dt.to_period('M')

# First of month
df['month_start'] = df['date'].dt.to_period('M').dt.start_time

# Last of month
df['month_end'] = df['date'] + pd.offsets.MonthEnd(0)

# Month aggregation
monthly = df.groupby(df['date'].dt.to_period('M')).agg({
    'revenue': 'sum',
    'customers': 'nunique'
})
```

### Monthly to Quarterly

```python
# Quarter period
df['quarter'] = df['date'].dt.to_period('Q')

# Quarter label (Q1 2024)
df['quarter_label'] = df['date'].dt.year.astype(str) + ' Q' + df['date'].dt.quarter.astype(str)

# Quarterly aggregation
quarterly = df.groupby(df['date'].dt.to_period('Q')).agg({
    'revenue': 'sum'
})
```

### Rolling Periods

```python
# Last 30 days (trailing)
df_last_30 = df[df['date'] >= df['date'].max() - pd.Timedelta(days=30)]

# Rolling 3-month sum
df['rolling_3mo'] = df.groupby('customer_id')['revenue'].transform(
    lambda x: x.rolling(3, min_periods=1).sum()
)

# Year-to-date
df['ytd'] = df.groupby(df['date'].dt.year)['revenue'].cumsum()

# Trailing twelve months (TTM)
df['ttm_revenue'] = df.sort_values('date').groupby('customer_id')['revenue'].transform(
    lambda x: x.rolling(12, min_periods=1).sum()
)
```

---

## Business Day Calculations

### Business Days Between Dates

```python
import numpy as np

# Business days between two dates
def business_days_between(start, end):
    """Count business days (excluding weekends)."""
    return np.busday_count(
        start.date() if hasattr(start, 'date') else start,
        end.date() if hasattr(end, 'date') else end
    )

df['days_to_close'] = df.apply(
    lambda row: business_days_between(row['created_date'], row['closed_date']),
    axis=1
)

# Add business days to date
from pandas.tseries.offsets import BusinessDay

df['due_date'] = df['created_date'] + BusinessDay(5)
```

### Custom Holidays

```python
from pandas.tseries.holiday import USFederalHolidayCalendar

# US federal holidays
cal = USFederalHolidayCalendar()
holidays = cal.holidays(start='2024-01-01', end='2024-12-31')

# Business days excluding holidays
def business_days_with_holidays(start, end, holidays):
    """Business days excluding holidays."""
    return np.busday_count(
        start.date(),
        end.date(),
        holidays=holidays.to_numpy().astype('datetime64[D]')
    )

# Custom business day offset
from pandas.tseries.offsets import CustomBusinessDay

custom_bd = CustomBusinessDay(holidays=holidays)
df['next_business_day'] = df['date'] + custom_bd
```

### Month/Quarter Boundaries

```python
from pandas.tseries.offsets import MonthEnd, QuarterEnd, YearEnd

# End of month
df['month_end'] = df['date'] + MonthEnd(0)

# End of quarter
df['quarter_end'] = df['date'] + QuarterEnd(0)

# Start of month
df['month_start'] = df['date'] - MonthEnd(1) + pd.Timedelta(days=1)

# Is end of month?
df['is_month_end'] = df['date'].dt.is_month_end

# Is end of quarter?
df['is_quarter_end'] = df['date'].dt.is_quarter_end
```

---

## Common Datetime Gotchas

### Gotcha 1: Comparing Timezone-Aware and Naive

```python
# This will fail:
# aware_dt > naive_dt  # TypeError!

# Solution: Make both aware or both naive
naive_dt = aware_dt.replace(tzinfo=None)
# or
aware_dt = naive_dt.replace(tzinfo=pytz.UTC)
```

### Gotcha 2: Date vs Datetime Comparisons

```python
# Comparing date to datetime can be tricky
date_val = pd.Timestamp('2024-01-15').date()
datetime_val = pd.Timestamp('2024-01-15 10:00:00')

# This compares correctly:
df[df['datetime'].dt.date == date_val]

# But this includes only midnight:
df[df['datetime'] == pd.Timestamp('2024-01-15')]

# Include full day:
df[(df['datetime'] >= '2024-01-15') & (df['datetime'] < '2024-01-16')]
```

### Gotcha 3: Week Number Boundaries

```python
# ISO week can cross year boundaries
# Week 1 2024 starts on Monday Jan 1 2024
# But Dec 31 2023 might be in Week 1 2024

# Use ISO week/year together
df['iso_year'] = df['date'].dt.isocalendar().year
df['iso_week'] = df['date'].dt.isocalendar().week
df['iso_year_week'] = df['iso_year'].astype(str) + '-W' + df['iso_week'].astype(str).str.zfill(2)
```

### Gotcha 4: Daylight Saving Time Gaps

```python
# Some hours don't exist (spring forward)
# Some hours happen twice (fall back)

# 2024-03-10 02:00 doesn't exist in US/Eastern
# 2024-11-03 01:00 happens twice in US/Eastern

# Always work in UTC, convert for display only
df['timestamp_utc'] = df['timestamp'].dt.tz_convert('UTC')
```

### Gotcha 5: Leap Years and Month Lengths

```python
# February 29 only exists in leap years
# Months have 28-31 days

# Safe "same day last month" calculation
from dateutil.relativedelta import relativedelta

def same_day_last_month(date):
    """Get same day last month (handles varying month lengths)."""
    return date - relativedelta(months=1)

# Same day last year (handles leap years)
def same_day_last_year(date):
    return date - relativedelta(years=1)
```

### Gotcha 6: String Sorting

```python
# String dates sort incorrectly:
# '2024-1-15' < '2024-1-2' (wrong!)

# Always zero-pad or use datetime:
df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')  # Zero-padded

# Or sort as datetime, then convert:
df = df.sort_values('date')
df['date_display'] = df['date'].dt.strftime('%B %d, %Y')
```

---

## Datetime Validation

```python
def validate_dates(df, date_col, min_date=None, max_date=None):
    """Validate date column and report issues."""
    issues = []

    # Check for nulls
    null_count = df[date_col].isnull().sum()
    if null_count > 0:
        issues.append(f"{null_count} null values")

    # Check for future dates
    future = df[df[date_col] > pd.Timestamp.now()]
    if len(future) > 0:
        issues.append(f"{len(future)} future dates")

    # Check for dates outside expected range
    if min_date:
        early = df[df[date_col] < pd.Timestamp(min_date)]
        if len(early) > 0:
            issues.append(f"{len(early)} dates before {min_date}")

    if max_date:
        late = df[df[date_col] > pd.Timestamp(max_date)]
        if len(late) > 0:
            issues.append(f"{len(late)} dates after {max_date}")

    return issues

# Log validation results
# VALIDATION: transaction_date - 12 null values, 3 future dates
```

---

## Decision Logging for Dates

```python
# === DATE HANDLING LOG ===
# TIMEZONE: All timestamps converted to UTC for analysis
# FISCAL: Using February fiscal year (FY2024 = Feb 2023 - Jan 2024)
# AGGREGATION: Weekly aggregation using Monday start (ISO week)
# FILTER: Excluded 47 records with dates > today (future dates)
# ASSUMPTION: Transaction timestamps are in US/Eastern - confidence: High
```
