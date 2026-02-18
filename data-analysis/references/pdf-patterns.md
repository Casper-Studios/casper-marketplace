# PDF Handling Patterns

Patterns for extracting data from PDFs and creating PDF reports.

*Adapted from [Anthropic's pdf skill](https://github.com/anthropics/skills/tree/main/skills/pdf)*

---

## Tool Selection

| Task | Best Tool | Notes |
|------|-----------|-------|
| Extract text (simple) | pypdf | Fast, built-in |
| Extract text (layout) | pdfplumber | Preserves formatting |
| Extract tables | pdfplumber | Best table detection |
| Create PDFs | reportlab | Full control |
| Merge/split PDFs | pypdf | Simple operations |
| OCR scanned PDFs | pytesseract + pdf2image | Requires Tesseract |
| Command line | qpdf, pdftotext | Fast batch operations |

---

## Extracting Data from PDFs

### Basic Text Extraction

```python
from pypdf import PdfReader

def extract_text(pdf_path):
    """Extract all text from a PDF."""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Usage
text = extract_text("report.pdf")
print(f"Pages: {len(PdfReader('report.pdf').pages)}")
```

### Text with Layout Preservation

```python
import pdfplumber

def extract_text_with_layout(pdf_path):
    """Extract text preserving layout (columns, spacing)."""
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n\n"
    return text
```

### Extract Tables to DataFrame

```python
import pdfplumber
import pandas as pd

def extract_tables(pdf_path):
    """Extract all tables from PDF as DataFrames."""
    tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_tables = page.extract_tables()
            for j, table in enumerate(page_tables):
                if table and len(table) > 1:
                    # First row as header
                    df = pd.DataFrame(table[1:], columns=table[0])
                    df['_source_page'] = i + 1
                    df['_table_num'] = j + 1
                    tables.append(df)

    return tables

# Usage
tables = extract_tables("financial_report.pdf")
for i, df in enumerate(tables):
    print(f"Table {i+1}: {df.shape}")
    print(df.head())
```

### Advanced Table Extraction

```python
def extract_tables_advanced(pdf_path, table_settings=None):
    """Extract tables with custom settings for complex layouts."""
    default_settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "intersection_tolerance": 3,
    }
    settings = table_settings or default_settings

    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Find tables with custom settings
            page_tables = page.extract_tables(table_settings=settings)

            # Alternative: extract with explicit lines
            if not page_tables:
                # Try text-based extraction
                page_tables = page.extract_tables(table_settings={
                    "vertical_strategy": "text",
                    "horizontal_strategy": "text",
                })

            for table in page_tables:
                if table:
                    tables.append(table)

    return tables
```

### Extract Specific Pages

```python
from pypdf import PdfReader

def extract_page_range(pdf_path, start_page, end_page):
    """Extract text from specific page range (1-indexed)."""
    reader = PdfReader(pdf_path)
    text = ""
    for i in range(start_page - 1, min(end_page, len(reader.pages))):
        text += reader.pages[i].extract_text() + "\n"
    return text
```

---

## Creating PDF Reports

### Basic Report

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_simple_report(filename, title, content):
    """Create a simple PDF report."""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(72, height - 72, title)

    # Content
    c.setFont("Helvetica", 12)
    y = height - 120
    for line in content.split('\n'):
        if y < 72:  # New page if near bottom
            c.showPage()
            y = height - 72
        c.drawString(72, y, line)
        y -= 15

    c.save()
    return filename
```

### Professional Report with Sections

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

def create_analysis_report(filename, title, sections, tables=None):
    """
    Create a professional analysis report.

    Args:
        filename: Output PDF path
        title: Report title
        sections: List of dicts with 'heading' and 'content'
        tables: Optional list of (headers, rows) tuples
    """
    doc = SimpleDocTemplate(filename, pagesize=letter,
                           leftMargin=72, rightMargin=72,
                           topMargin=72, bottomMargin=72)

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontSize=14,
        spaceBefore=20,
        spaceAfter=10
    )

    story = []

    # Title
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 12))

    # Sections
    for section in sections:
        story.append(Paragraph(section['heading'], heading_style))
        story.append(Paragraph(section['content'], styles['Normal']))
        story.append(Spacer(1, 12))

    # Tables
    if tables:
        for header_row, data_rows in tables:
            table_data = [header_row] + data_rows
            t = Table(table_data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(t)
            story.append(Spacer(1, 20))

    doc.build(story)
    return filename


# Usage
sections = [
    {
        'heading': 'Executive Summary',
        'content': 'Revenue grew 15% YoY driven by enterprise expansion...'
    },
    {
        'heading': 'Key Findings',
        'content': '1. NRR improved to 115%\n2. Churn decreased to 2.1%\n3. Pipeline coverage at 3.2x'
    }
]

tables = [
    (['Metric', 'Q1', 'Q2', 'Q3', 'Q4'],
     [['Revenue', '$1.2M', '$1.4M', '$1.5M', '$1.7M'],
      ['Customers', '120', '135', '148', '162']])
]

create_analysis_report('analysis.pdf', 'Q4 Revenue Analysis', sections, tables)
```

### Add Charts to PDF

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import io

def create_report_with_charts(filename, title, charts_data):
    """Create PDF report with embedded matplotlib charts."""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 20))

    for chart_title, fig in charts_data:
        # Add chart title
        story.append(Paragraph(chart_title, styles['Heading2']))

        # Convert matplotlib figure to image
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close(fig)

        # Add to PDF
        img = Image(img_buffer, width=6*inch, height=4*inch)
        story.append(img)
        story.append(Spacer(1, 20))

    doc.build(story)
    return filename


# Usage
fig1, ax1 = plt.subplots(figsize=(8, 5))
ax1.plot([1, 2, 3, 4], [100, 120, 115, 140])
ax1.set_title('Revenue Trend')

charts = [('Revenue Over Time', fig1)]
create_report_with_charts('report_with_charts.pdf', 'Financial Report', charts)
```

---

## PDF Manipulation

### Merge PDFs

```python
from pypdf import PdfWriter, PdfReader

def merge_pdfs(pdf_list, output_path):
    """Merge multiple PDFs into one."""
    writer = PdfWriter()

    for pdf_path in pdf_list:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            writer.add_page(page)

    with open(output_path, 'wb') as output:
        writer.write(output)

    return output_path

# Usage
merge_pdfs(['report1.pdf', 'report2.pdf', 'appendix.pdf'], 'combined.pdf')
```

### Split PDF

```python
from pypdf import PdfReader, PdfWriter

def split_pdf(pdf_path, output_dir):
    """Split PDF into individual pages."""
    reader = PdfReader(pdf_path)
    paths = []

    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)
        output_path = f"{output_dir}/page_{i+1}.pdf"
        with open(output_path, 'wb') as output:
            writer.write(output)
        paths.append(output_path)

    return paths

def extract_pages(pdf_path, page_range, output_path):
    """Extract specific pages from PDF."""
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for i in page_range:
        writer.add_page(reader.pages[i - 1])  # 1-indexed

    with open(output_path, 'wb') as output:
        writer.write(output)

    return output_path

# Usage
extract_pages('report.pdf', range(1, 6), 'first_5_pages.pdf')
```

### Add Watermark

```python
from pypdf import PdfReader, PdfWriter

def add_watermark(input_pdf, watermark_pdf, output_pdf):
    """Add watermark to all pages."""
    reader = PdfReader(input_pdf)
    watermark = PdfReader(watermark_pdf).pages[0]
    writer = PdfWriter()

    for page in reader.pages:
        page.merge_page(watermark)
        writer.add_page(page)

    with open(output_pdf, 'wb') as output:
        writer.write(output)

    return output_pdf
```

---

## OCR for Scanned PDFs

```python
# Requires: pip install pytesseract pdf2image
# Also requires Tesseract OCR installed on system

import pytesseract
from pdf2image import convert_from_path

def ocr_pdf(pdf_path, language='eng'):
    """Extract text from scanned PDF using OCR."""
    # Convert PDF pages to images
    images = convert_from_path(pdf_path)

    text = ""
    for i, image in enumerate(images):
        page_text = pytesseract.image_to_string(image, lang=language)
        text += f"--- Page {i+1} ---\n{page_text}\n\n"

    return text

def ocr_pdf_to_dataframe(pdf_path):
    """OCR PDF tables to DataFrame (best effort)."""
    import pandas as pd

    images = convert_from_path(pdf_path)
    all_data = []

    for image in images:
        # Get structured data
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DATAFRAME)
        all_data.append(data)

    return pd.concat(all_data, ignore_index=True)
```

---

## Command Line Tools

### Quick Text Extraction

```bash
# Using pdftotext (poppler-utils)
pdftotext input.pdf output.txt

# Preserve layout
pdftotext -layout input.pdf output.txt

# Specific pages
pdftotext -f 1 -l 5 input.pdf output.txt
```

### Merge/Split with qpdf

```bash
# Merge
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# Extract pages 1-5
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf

# Split into chunks
qpdf input.pdf --split-pages=10 output_%d.pdf
```

### Extract Images

```bash
# Using pdfimages (poppler-utils)
pdfimages -j input.pdf output_prefix
# Creates output_prefix-000.jpg, output_prefix-001.jpg, etc.
```

---

## Data Extraction Workflow

For extracting data from PDF reports for analysis:

```python
def extract_financial_data(pdf_path):
    """
    Extract financial data from PDF report.
    Returns dict with metadata and DataFrames.
    """
    import pdfplumber
    import pandas as pd
    from pypdf import PdfReader

    result = {
        'metadata': {},
        'text': '',
        'tables': []
    }

    # Get metadata
    reader = PdfReader(pdf_path)
    result['metadata'] = {
        'pages': len(reader.pages),
        'title': reader.metadata.title if reader.metadata else None,
        'author': reader.metadata.author if reader.metadata else None,
    }

    # Extract text and tables
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            # Text
            result['text'] += page.extract_text() or ''

            # Tables
            tables = page.extract_tables()
            for j, table in enumerate(tables):
                if table and len(table) > 1:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    df['_page'] = i + 1
                    result['tables'].append(df)

    return result


# Usage
data = extract_financial_data('quarterly_report.pdf')
print(f"Found {len(data['tables'])} tables")

# Combine all tables if similar structure
if data['tables']:
    combined = pd.concat(data['tables'], ignore_index=True)
```

---

## Quick Reference

| Task | Code |
|------|------|
| Read PDF | `PdfReader("file.pdf")` |
| Extract text | `page.extract_text()` |
| Extract tables | `pdfplumber: page.extract_tables()` |
| Create PDF | `reportlab: SimpleDocTemplate()` |
| Merge PDFs | `PdfWriter.add_page()` |
| Split PDF | Loop through `reader.pages` |
| OCR scanned | `pytesseract.image_to_string()` |

---

## Decision Logging

```python
# === PDF HANDLING LOG ===
# SOURCE: quarterly_report.pdf - 12 pages
# EXTRACTION: Used pdfplumber for tables, 4 tables found
# QUALITY: Tables on pages 3-6 extracted cleanly, page 8 required manual cleanup
# OUTPUT: Combined to financial_data.xlsx for analysis
```
