# Markdown to PDF Conversion

## Overview
Convert markdown files to styled PDF documents.

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `input` | string | Yes | Markdown file or text |
| `output` | string | No | Output PDF path |
| `style` | string | No | CSS style file |
| `title` | string | No | PDF title |

## CLI Usage

```bash
# Basic conversion
python scripts/md_to_pdf.py report.md

# Custom output path
python scripts/md_to_pdf.py report.md --output .tmp/final_report.pdf

# With styling
python scripts/md_to_pdf.py report.md --style custom.css
```

## Output
PDF file saved to `.tmp/` or specified path.

## Features

- Code syntax highlighting
- Table rendering
- Header/footer support
- Custom CSS styling
- Page breaks

## Python Usage

### Basic HTML to PDF
```python
from weasyprint import HTML, CSS

html = HTML(string='''
<html>
<body>
<h1>My Report</h1>
<p>Content here...</p>
</body>
</html>
''')

css = CSS(string='body { font-family: Arial; }')
html.write_pdf('output.pdf', stylesheets=[css])
```

### Convert Markdown to PDF
```python
import markdown
from weasyprint import HTML, CSS

def markdown_to_pdf(md_content: str, output_path: str, css_path: str = None):
    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'codehilite']
    )

    # Wrap in HTML document
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body>{html_content}</body>
    </html>
    """

    # Load custom CSS if provided
    stylesheets = []
    if css_path:
        stylesheets.append(CSS(filename=css_path))
    else:
        stylesheets.append(CSS(string='''
            body { font-family: -apple-system, Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #333; border-bottom: 2px solid #548ce9; padding-bottom: 10px; }
            h2 { color: #555; margin-top: 30px; }
            code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
            pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }
            table { border-collapse: collapse; width: 100%; margin: 20px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background: #548ce9; color: white; }
        '''))

    HTML(string=full_html).write_pdf(output_path, stylesheets=stylesheets)
    return output_path

# Usage
md_content = """
# Quarterly Report

## Summary
This quarter showed significant growth.

## Metrics
| Metric | Value |
|--------|-------|
| Revenue | $1.2M |
| Growth | 25% |

## Code Example
```python
print("Hello World")
```
"""

markdown_to_pdf(md_content, ".tmp/report.pdf")
```

### PDF with Header and Footer
```python
from weasyprint import HTML, CSS

def create_pdf_with_header_footer(content: str, output_path: str, title: str = "Document"):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                margin: 2cm;
                @top-center {{
                    content: "{title}";
                    font-size: 10pt;
                    color: #666;
                }}
                @bottom-right {{
                    content: "Page " counter(page) " of " counter(pages);
                    font-size: 10pt;
                    color: #666;
                }}
            }}
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        </style>
    </head>
    <body>{content}</body>
    </html>
    """
    HTML(string=html).write_pdf(output_path)
    return output_path

# Usage
create_pdf_with_header_footer("<h1>Report</h1><p>Content...</p>", "output.pdf", "Q4 Report")
```

### Batch PDF Generation
```python
from pathlib import Path
from weasyprint import HTML, CSS

def batch_convert_markdown(input_dir: str, output_dir: str):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for md_file in input_path.glob("*.md"):
        md_content = md_file.read_text()
        pdf_path = output_path / f"{md_file.stem}.pdf"
        markdown_to_pdf(md_content, str(pdf_path))
        print(f"Created: {pdf_path}")

# Usage
batch_convert_markdown(".tmp/markdown/", ".tmp/pdfs/")
```

## Dependencies

Requires `weasyprint` or similar PDF renderer:
```bash
pip install weasyprint markdown
```

## Testing Checklist

### Pre-flight
- [ ] WeasyPrint installed (`pip install weasyprint`)
- [ ] System dependencies for WeasyPrint (Cairo, Pango, GDK-PixBuf)
  - macOS: `brew install cairo pango gdk-pixbuf libffi`
  - Linux: `apt-get install libcairo2-dev libpango1.0-dev`
- [ ] Test markdown file exists

### Smoke Test
```bash
# Basic conversion
python scripts/md_to_pdf.py test.md

# Custom output path
python scripts/md_to_pdf.py report.md --output .tmp/report.pdf

# With custom styling
python scripts/md_to_pdf.py document.md --style custom.css --title "My Report"
```

### Validation
- [ ] PDF file created at expected path
- [ ] PDF opens without errors in viewer
- [ ] Headers (h1, h2, h3) styled correctly
- [ ] Code blocks have syntax highlighting
- [ ] Tables render with proper borders
- [ ] Images embedded correctly
- [ ] Page breaks work (if specified in markdown)
- [ ] Custom CSS styling applied (if specified)
- [ ] Title appears in PDF metadata
- [ ] Links are clickable in PDF

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `WeasyPrint not found` | Library not installed | Install: `pip install weasyprint` |
| `Missing system deps` | Cairo/Pango not installed | Install system dependencies (see Pre-flight) |
| `Input file not found` | Markdown file doesn't exist | Verify file path |
| `Invalid markdown` | Markdown syntax errors | Check and fix markdown syntax |
| `CSS file not found` | Custom stylesheet missing | Verify CSS path, use default styling |
| `Image not found` | Referenced image missing | Check image paths, use absolute paths |
| `Permission denied` | Cannot write to output path | Check directory permissions |
| `Font not found` | Custom font unavailable | Use system fonts or install required fonts |
| `Memory error` | Document too large | Split into smaller documents |

### Recovery Strategies

1. **Fallback styling**: If custom CSS fails, use default WeasyPrint styling
2. **Image handling**: Skip missing images or use placeholder
3. **Path validation**: Validate all file paths before processing
4. **Incremental rendering**: For large docs, process in chunks
5. **Output directory creation**: Auto-create .tmp/ if it doesn't exist
6. **Font substitution**: Use fallback fonts if specified fonts unavailable
