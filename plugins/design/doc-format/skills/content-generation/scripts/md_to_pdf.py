#!/usr/bin/env python3
"""
Markdown to PDF Converter
Converts Markdown files to PDF using Chrome headless print-to-PDF.

Usage:
    python execution/md_to_pdf.py input.md [--output output.pdf] [--style default|minimal|report]
"""

import argparse
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from markdown.extensions.fenced_code import FencedCodeExtension


# CSS Style Presets
STYLES = {
    "default": """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px;
        }
        h1 { color: #1a1a1a; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-top: 40px; }
        h2 { color: #2c3e50; border-bottom: 1px solid #bdc3c7; padding-bottom: 8px; margin-top: 30px; }
        h3 { color: #34495e; margin-top: 25px; }
        h4 { color: #7f8c8d; margin-top: 20px; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 14px; }
        th { background: #3498db; color: white; padding: 12px 15px; text-align: left; font-weight: 600; }
        td { padding: 10px 15px; border-bottom: 1px solid #ddd; }
        tr:nth-child(even) { background: #f8f9fa; }
        tr:hover { background: #e8f4f8; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: 'SF Mono', Monaco, monospace; font-size: 13px; }
        pre { background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; }
        pre code { background: transparent; padding: 0; color: inherit; }
        blockquote { border-left: 4px solid #3498db; margin: 20px 0; padding: 10px 20px; background: #f8f9fa; }
        a { color: #3498db; text-decoration: none; }
        ul, ol { padding-left: 25px; }
        li { margin: 5px 0; }
        hr { border: none; border-top: 1px solid #ddd; margin: 30px 0; }
        .highlight { background: #f8f8f8; padding: 15px; border-radius: 5px; overflow-x: auto; }
        /* Checkmark styling */
        td:first-child { font-weight: 500; }
    """,

    "minimal": """
        body {
            font-family: Georgia, serif;
            line-height: 1.7;
            color: #222;
            max-width: 700px;
            margin: 0 auto;
            padding: 30px;
        }
        h1, h2, h3, h4 { font-weight: normal; }
        h1 { font-size: 2em; margin-top: 40px; }
        h2 { font-size: 1.5em; margin-top: 30px; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ccc; }
        th { font-weight: bold; }
        code { font-family: monospace; background: #f5f5f5; padding: 2px 4px; }
        pre { background: #f5f5f5; padding: 15px; overflow-x: auto; }
        pre code { background: transparent; padding: 0; }
        blockquote { margin: 20px 0; padding-left: 20px; border-left: 3px solid #ccc; color: #666; }
    """,

    "report": """
        @page {
            margin: 1in;
            @bottom-center { content: counter(page); }
        }
        body {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            line-height: 1.5;
            color: #333;
            font-size: 11pt;
        }
        h1 {
            color: #1a365d;
            font-size: 24pt;
            border-bottom: 3px solid #2b6cb0;
            padding-bottom: 15px;
            margin-top: 0;
            page-break-after: avoid;
        }
        h2 {
            color: #2c5282;
            font-size: 16pt;
            border-bottom: 1px solid #4299e1;
            padding-bottom: 8px;
            margin-top: 25px;
            page-break-after: avoid;
        }
        h3 { color: #2d3748; font-size: 13pt; margin-top: 20px; page-break-after: avoid; }
        h4 { color: #4a5568; font-size: 11pt; margin-top: 15px; }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
            font-size: 10pt;
            page-break-inside: avoid;
        }
        th {
            background: #2b6cb0;
            color: white;
            padding: 10px 12px;
            text-align: left;
            font-weight: 600;
        }
        td { padding: 8px 12px; border: 1px solid #e2e8f0; }
        tr:nth-child(even) { background: #f7fafc; }
        code {
            background: #edf2f7;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }
        pre {
            background: #1a202c;
            color: #e2e8f0;
            padding: 12px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 9pt;
            page-break-inside: avoid;
        }
        pre code { background: transparent; padding: 0; color: inherit; }
        blockquote {
            border-left: 4px solid #4299e1;
            margin: 15px 0;
            padding: 10px 15px;
            background: #ebf8ff;
            font-style: italic;
        }
        ul, ol { padding-left: 20px; }
        li { margin: 4px 0; }
        hr { border: none; border-top: 2px solid #e2e8f0; margin: 25px 0; }
        a { color: #2b6cb0; }
        /* Executive summary styling */
        h2 + p { font-size: 11pt; }
        /* Recommendation highlight */
        strong { color: #2d3748; }
    """
}


def get_chrome_path() -> str:
    """Get Chrome executable path based on OS."""
    system = platform.system()

    # Check environment variable first
    env_path = os.environ.get("CHROME_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    if system == "Darwin":  # macOS
        paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
    elif system == "Linux":
        paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
        ]
    elif system == "Windows":
        paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
    else:
        paths = []

    for path in paths:
        if os.path.exists(path):
            return path

    raise FileNotFoundError(
        f"Chrome not found. Install Chrome or set CHROME_PATH environment variable.\n"
        f"Searched: {paths}"
    )


def md_to_html(md_content: str, title: str = "Document", style: str = "default") -> str:
    """Convert Markdown to styled HTML."""

    # Configure markdown extensions
    extensions = [
        TableExtension(),
        FencedCodeExtension(),
        CodeHiliteExtension(css_class='highlight', guess_lang=False),
        TocExtension(permalink=False),
        'md_in_html',
    ]

    # Convert markdown to HTML
    md = markdown.Markdown(extensions=extensions)
    html_content = md.convert(md_content)

    # Get CSS
    css = STYLES.get(style, STYLES["default"])

    # Build full HTML document
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        {css}
    </style>
</head>
<body>
    <div class="content">
        {html_content}
    </div>
</body>
</html>"""

    return html


def convert_md_to_pdf(
    input_path: str,
    output_path: Optional[str] = None,
    style: str = "default",
    title: Optional[str] = None,
    page_size: str = "letter",
    timeout: int = 60
) -> Dict[str, Any]:
    """
    Convert a Markdown file to PDF.

    Args:
        input_path: Path to input Markdown file
        output_path: Path for output PDF (defaults to input with .pdf extension)
        style: Style preset ('default', 'minimal', 'report')
        title: Document title (defaults to filename)
        page_size: Paper size ('letter', 'a4', 'legal')
        timeout: Chrome timeout in seconds

    Returns:
        Dict with success status, output_path, and file size
    """
    input_path = Path(input_path).resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Set output path
    if output_path:
        output_path = Path(output_path).resolve()
    else:
        output_path = input_path.with_suffix('.pdf')

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Set title
    if not title:
        title = input_path.stem.replace('_', ' ').replace('-', ' ').title()

    # Read markdown
    md_content = input_path.read_text(encoding='utf-8')

    # Convert to HTML
    html_content = md_to_html(md_content, title=title, style=style)

    # Create temp HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_content)
        temp_html_path = f.name

    try:
        # Get Chrome path
        chrome_path = get_chrome_path()

        # Build Chrome command
        cmd = [
            chrome_path,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-software-rasterizer",
            f"--print-to-pdf={output_path}",
            "--print-to-pdf-no-header",
        ]

        # Add page size
        if page_size == "a4":
            cmd.append("--print-to-pdf-paper-size=a4")
        elif page_size == "legal":
            cmd.append("--print-to-pdf-paper-size=legal")
        # letter is default

        # Add input file
        cmd.append(f"file://{temp_html_path}")

        # Run Chrome
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode != 0:
            raise RuntimeError(f"Chrome failed: {result.stderr}")

        if not output_path.exists():
            raise RuntimeError("PDF file was not created")

        # Get file size
        file_size = output_path.stat().st_size

        return {
            "success": True,
            "output_path": str(output_path),
            "file_size_bytes": file_size,
            "file_size_human": f"{file_size / 1024:.1f} KB" if file_size < 1024*1024 else f"{file_size / 1024/1024:.1f} MB"
        }

    finally:
        # Clean up temp file
        if os.path.exists(temp_html_path):
            os.unlink(temp_html_path)


def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown to PDF using Chrome headless",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python execution/md_to_pdf.py report.md
    python execution/md_to_pdf.py report.md --output final.pdf
    python execution/md_to_pdf.py report.md --style report --page-size a4
        """
    )

    parser.add_argument("input", help="Input Markdown file path")
    parser.add_argument("-o", "--output", help="Output PDF file path")
    parser.add_argument(
        "-s", "--style",
        choices=["default", "minimal", "report"],
        default="default",
        help="Style preset (default: default)"
    )
    parser.add_argument("-t", "--title", help="Document title")
    parser.add_argument(
        "-p", "--page-size",
        choices=["letter", "a4", "legal"],
        default="letter",
        help="Page size (default: letter)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Chrome timeout in seconds (default: 60)"
    )

    args = parser.parse_args()

    try:
        result = convert_md_to_pdf(
            input_path=args.input,
            output_path=args.output,
            style=args.style,
            title=args.title,
            page_size=args.page_size,
            timeout=args.timeout
        )

        print(f"✓ PDF created: {result['output_path']}")
        print(f"  Size: {result['file_size_human']}")

    except FileNotFoundError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print(f"✗ Error: Chrome timed out after {args.timeout} seconds", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
