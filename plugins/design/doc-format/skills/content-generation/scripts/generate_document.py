#!/usr/bin/env python3
"""
Generic Document Generator - Create branded Google Docs from structured content.

Creates professional Google Docs with Casper Studios branding:
- Logo from template
- Source Sans Pro font
- Brand colors (#548ce9 headers, #4a86e8 links)
- Proper spacing and formatting
- Real tables with styled headers

Directive: directives/generate_document.md

Usage:
    # From JSON file
    python execution/generate_document.py --input content.json --title "My Report"

    # From JSON string
    python execution/generate_document.py --json '{"sections": [...]}' --title "Notes"

    # Quick text input
    python execution/generate_document.py --title "Notes" --content "Paragraph text here..."
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Google API imports
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

# Configuration
SETTINGS_FILE = "settings.yaml"
CREDENTIALS_FILE = "mycreds.txt"
DEFAULT_TEMPLATE_ID = os.environ.get("DOC_TEMPLATE_ID", "")

# =============================================================================
# BRAND STYLING (Casper Studios)
# =============================================================================

BRAND_COLORS = {
    # Section headers - #548ce9 (blue)
    "blue_header": {"red": 0.33, "green": 0.55, "blue": 0.91},
    # Links and table headers - #4a86e8
    "blue_link": {"red": 0.29, "green": 0.53, "blue": 0.91},
    # Body text - black
    "black": {"red": 0.0, "green": 0.0, "blue": 0.0},
    # Table header text
    "white": {"red": 1.0, "green": 1.0, "blue": 1.0},
}

BRAND_STYLES = {
    # Centered title
    "title": {
        "bold": True,
        "fontSize": {"magnitude": 11, "unit": "PT"},
        "weightedFontFamily": {"fontFamily": "Source Sans Pro", "weight": 700},
        "foregroundColor": {"color": {"rgbColor": BRAND_COLORS["black"]}}
    },
    # Blue section headers
    "section_header": {
        "bold": True,
        "fontSize": {"magnitude": 11, "unit": "PT"},
        "weightedFontFamily": {"fontFamily": "Source Sans Pro", "weight": 700},
        "foregroundColor": {"color": {"rgbColor": BRAND_COLORS["blue_header"]}}
    },
    # Black subsection headers
    "subsection_header": {
        "bold": True,
        "fontSize": {"magnitude": 11, "unit": "PT"},
        "weightedFontFamily": {"fontFamily": "Source Sans Pro", "weight": 700},
        "foregroundColor": {"color": {"rgbColor": BRAND_COLORS["black"]}}
    },
    # Normal body text
    "body": {
        "fontSize": {"magnitude": 11, "unit": "PT"},
        "weightedFontFamily": {"fontFamily": "Source Sans Pro", "weight": 400},
        "foregroundColor": {"color": {"rgbColor": BRAND_COLORS["black"]}}
    },
    # Bold text within body
    "bold_body": {
        "bold": True,
        "fontSize": {"magnitude": 11, "unit": "PT"},
        "weightedFontFamily": {"fontFamily": "Source Sans Pro", "weight": 700},
        "foregroundColor": {"color": {"rgbColor": BRAND_COLORS["black"]}}
    },
    # Table header text (white on blue)
    "table_header": {
        "bold": True,
        "fontSize": {"magnitude": 10, "unit": "PT"},
        "weightedFontFamily": {"fontFamily": "Source Sans Pro", "weight": 700},
        "foregroundColor": {"color": {"rgbColor": BRAND_COLORS["white"]}}
    },
    # Table body text
    "table_body": {
        "fontSize": {"magnitude": 10, "unit": "PT"},
        "weightedFontFamily": {"fontFamily": "Source Sans Pro", "weight": 400},
        "foregroundColor": {"color": {"rgbColor": BRAND_COLORS["black"]}}
    },
}


# =============================================================================
# GOOGLE AUTHENTICATION
# =============================================================================

def authenticate_google():
    """Authenticate with Google APIs using OAuth 2.0."""
    print("🔐 Authenticating with Google...")

    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(CREDENTIALS_FILE)

    if gauth.credentials is None:
        print("   First time setup - opening browser for authentication...")
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        print("   Refreshing expired credentials...")
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile(CREDENTIALS_FILE)
    print("   ✅ Authentication successful!")

    drive = GoogleDrive(gauth)
    return drive, gauth.credentials


def copy_template_and_clear(drive, credentials, template_id: str, doc_name: str, folder_id: str = None) -> str:
    """Copy the template (to get logo) then clear content except logo."""
    print("📄 Copying template for logo...")

    drive_service = build('drive', 'v3', credentials=credentials)
    docs_service = build('docs', 'v1', credentials=credentials)

    # Copy the template
    body = {'name': doc_name}
    if folder_id:
        body['parents'] = [folder_id]

    copied_file = drive_service.files().copy(
        fileId=template_id,
        body=body
    ).execute()

    new_doc_id = copied_file['id']
    print(f"   ✅ Created document: {new_doc_id}")

    # Get document content to find logo position
    doc = docs_service.documents().get(documentId=new_doc_id).execute()
    body_content = doc.get('body', {}).get('content', [])

    # Find where to start deleting (after logo)
    delete_start = None
    delete_end = None

    for element in body_content:
        if 'paragraph' in element:
            para = element['paragraph']
            elements = para.get('elements', [])
            has_image = any('inlineObjectElement' in el for el in elements)

            if has_image:
                # Found logo - delete starts after it
                delete_start = element.get('endIndex')
            elif delete_start is None:
                delete_start = element.get('startIndex')

        if 'endIndex' in element:
            delete_end = element.get('endIndex')

    # Clear template content (keep logo)
    if delete_start and delete_end and delete_end > delete_start:
        try:
            docs_service.documents().batchUpdate(
                documentId=new_doc_id,
                body={'requests': [{
                    'deleteContentRange': {
                        'range': {
                            'startIndex': delete_start,
                            'endIndex': delete_end - 1
                        }
                    }
                }]}
            ).execute()
            print(f"   ✅ Cleared template content (kept logo)")
        except Exception as e:
            print(f"   ⚠️ Could not clear content: {e}")

    return new_doc_id


def create_blank_document(credentials, doc_name: str, folder_id: str = None) -> str:
    """Create a blank document (fallback if template not available)."""
    print("📄 Creating blank document...")

    docs_service = build('docs', 'v1', credentials=credentials)
    drive_service = build('drive', 'v3', credentials=credentials)

    # Create blank doc
    doc = docs_service.documents().create(body={'title': doc_name}).execute()
    doc_id = doc['documentId']

    # Move to folder if specified
    if folder_id:
        drive_service.files().update(
            fileId=doc_id,
            addParents=folder_id,
            removeParents='root'
        ).execute()

    print(f"   ✅ Created document: {doc_id}")
    return doc_id


# =============================================================================
# DOCUMENT BUILDER
# =============================================================================

class DocumentBuilder:
    """Builds Google Doc content with proper Casper Studios formatting.

    Tables are handled in a two-phase approach:
    1. First pass: Build all text content, record table placeholders
    2. Second pass: Insert and populate tables at recorded positions
    """

    def __init__(self, credentials, doc_id: str):
        self.credentials = credentials
        self.doc_id = doc_id
        self.docs_service = build('docs', 'v1', credentials=credentials)
        self.requests = []
        self.current_index = 1
        self.pending_tables = []  # Store tables to insert in second pass

        # Get current document end position
        doc = self.docs_service.documents().get(documentId=doc_id).execute()
        body_content = doc.get('body', {}).get('content', [])
        for element in body_content:
            end_idx = element.get('endIndex', 0)
            if end_idx > self.current_index:
                self.current_index = end_idx
        self.current_index = max(self.current_index - 1, 1)

    def add_text(self, text: str, style_name: str, center: bool = False,
                 space_above: float = 0, space_below: float = 0):
        """Add styled text to the document."""
        style = BRAND_STYLES.get(style_name, BRAND_STYLES['body'])
        text_start = self.current_index

        # Insert text
        self.requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': text
            }
        })

        text_end = self.current_index + len(text)
        if text.endswith('\n'):
            text_end -= 1

        # Apply text style
        if text_end > self.current_index:
            self.requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': self.current_index,
                        'endIndex': text_end
                    },
                    'textStyle': style,
                    'fields': 'bold,italic,fontSize,weightedFontFamily,foregroundColor'
                }
            })

        # Paragraph style
        para_style = {
            'lineSpacing': 115,
            'spaceAbove': {'magnitude': space_above, 'unit': 'PT'},
            'spaceBelow': {'magnitude': space_below, 'unit': 'PT'}
        }
        fields = 'lineSpacing,spaceAbove,spaceBelow'

        if center:
            para_style['alignment'] = 'CENTER'
            fields += ',alignment'

        self.requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': self.current_index,
                    'endIndex': self.current_index + len(text)
                },
                'paragraphStyle': para_style,
                'fields': fields
            }
        })

        self.current_index += len(text)
        return text_start, self.current_index

    def add_empty_line(self):
        """Add an empty line for spacing."""
        start_idx = self.current_index
        self.requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': '\n'
            }
        })
        self.current_index += 1
        self.requests.append({
            'updateParagraphStyle': {
                'range': {'startIndex': start_idx, 'endIndex': self.current_index},
                'paragraphStyle': {
                    'lineSpacing': 100,
                    'spaceAbove': {'magnitude': 0, 'unit': 'PT'},
                    'spaceBelow': {'magnitude': 0, 'unit': 'PT'}
                },
                'fields': 'lineSpacing,spaceAbove,spaceBelow'
            }
        })

    def add_title(self, text: str):
        """Add centered document title."""
        self.add_text(text + '\n', 'title', center=True)
        self.add_empty_line()

    def add_section_header(self, text: str):
        """Add blue section header."""
        self.add_empty_line()
        self.add_text(text + '\n', 'section_header')

    def add_subsection_header(self, text: str):
        """Add black bold subsection header."""
        self.add_text(text + '\n', 'subsection_header')

    def add_paragraph(self, text: str, space_above: float = 0, space_below: float = 0):
        """Add body paragraph."""
        self.add_text(text + '\n', 'body', space_above=space_above, space_below=space_below)

    def add_list(self, items: list, numbered: bool = False):
        """Add bullet or numbered list."""
        list_start = self.current_index

        for item in items:
            if isinstance(item, dict):
                title = item.get('title', '')
                desc = item.get('description', '')

                if title and desc:
                    self.add_text(title, 'bold_body')
                    self.add_text(': ' + desc + '\n', 'body')
                elif title:
                    self.add_text(title + '\n', 'bold_body')
                elif desc:
                    self.add_text(desc + '\n', 'body')
            else:
                # Plain string item
                self.add_text(str(item) + '\n', 'body')

        # Apply bullet/number formatting
        if items and self.current_index > list_start:
            preset = 'NUMBERED_DECIMAL_NESTED' if numbered else 'BULLET_DISC_CIRCLE_SQUARE'
            self.requests.append({
                'createParagraphBullets': {
                    'range': {
                        'startIndex': list_start,
                        'endIndex': self.current_index - 1
                    },
                    'bulletPreset': preset
                }
            })

    def queue_table(self, headers: list, rows: list):
        """Queue a table to be inserted in the second pass.

        Tables require a two-phase approach because:
        1. insertTable creates the structure but shifts all indices
        2. We need to re-fetch the document to get cell positions
        3. Then we populate the cells with content
        """
        if not headers or not rows:
            return

        # Record the position where this table should go
        # We'll insert tables in reverse order (last first) to preserve positions
        self.pending_tables.append({
            'position': self.current_index,
            'headers': headers,
            'rows': rows
        })

        # Add a newline as placeholder for the table
        self.add_empty_line()

    def add_divider(self):
        """Add a horizontal divider line."""
        self.add_empty_line()
        self.add_text('─' * 50 + '\n', 'body')
        self.add_empty_line()

    def build_section(self, section: dict):
        """Build a single section from its definition."""
        section_type = section.get('type', 'paragraph')
        content = section.get('content', '')
        items = section.get('items', [])

        if section_type == 'title':
            self.add_title(content)

        elif section_type == 'section_header':
            self.add_section_header(content)

        elif section_type == 'subsection_header':
            self.add_subsection_header(content)

        elif section_type == 'paragraph':
            self.add_paragraph(content)

        elif section_type == 'bullet_list':
            self.add_list(items, numbered=False)

        elif section_type == 'numbered_list':
            self.add_list(items, numbered=True)

        elif section_type == 'table':
            headers = section.get('headers', [])
            rows = section.get('rows', [])
            self.queue_table(headers, rows)

        elif section_type == 'divider':
            self.add_divider()

        else:
            print(f"   ⚠️ Unknown section type: {section_type}")

    def _insert_table_at_position(self, position: int, headers: list, rows: list):
        """Insert a single table and populate its cells.

        This is called in the second pass after all text content is in place.
        Cell content is inserted in REVERSE order (last cell first) because
        inserting text shifts all subsequent indices.
        """
        num_cols = len(headers)
        num_rows = len(rows) + 1  # +1 for header row

        # Step 1: Insert the table structure
        self.docs_service.documents().batchUpdate(
            documentId=self.doc_id,
            body={'requests': [{
                'insertTable': {
                    'location': {'index': position},
                    'rows': num_rows,
                    'columns': num_cols
                }
            }]}
        ).execute()

        # Step 2: Fetch document to get cell positions
        doc = self.docs_service.documents().get(documentId=self.doc_id).execute()

        # Step 3: Find the table we just inserted
        table_element = None
        for element in doc.get('body', {}).get('content', []):
            if 'table' in element:
                start_idx = element.get('startIndex', 0)
                # Find table closest to our insertion position
                if start_idx >= position - 5:  # Allow small offset
                    table_element = element
                    break

        if not table_element:
            print(f"   ⚠️ Could not find inserted table at position {position}")
            return

        table = table_element['table']
        table_rows = table.get('tableRows', [])

        # Step 4: Collect ALL cell insertions with their positions
        # We'll sort by position descending and insert last-to-first
        cell_insertions = []

        # Header row cells
        if table_rows:
            header_row = table_rows[0]
            for col_idx, header_text in enumerate(headers):
                if col_idx < len(header_row.get('tableCells', [])):
                    cell = header_row['tableCells'][col_idx]
                    cell_content = cell.get('content', [])
                    if cell_content and 'paragraph' in cell_content[0]:
                        cell_start = cell_content[0].get('startIndex', 0)
                        cell_insertions.append({
                            'index': cell_start,
                            'text': str(header_text)
                        })

        # Data row cells
        for row_idx, row_data in enumerate(rows):
            if row_idx + 1 < len(table_rows):
                table_row = table_rows[row_idx + 1]  # +1 to skip header
                for col_idx, cell_text in enumerate(row_data):
                    if col_idx < len(table_row.get('tableCells', [])):
                        cell = table_row['tableCells'][col_idx]
                        cell_content = cell.get('content', [])
                        if cell_content and 'paragraph' in cell_content[0]:
                            cell_start = cell_content[0].get('startIndex', 0)
                            cell_insertions.append({
                                'index': cell_start,
                                'text': str(cell_text)
                            })

        # Sort by index DESCENDING (insert last cells first to preserve indices)
        cell_insertions.sort(key=lambda x: x['index'], reverse=True)

        # Build requests in reverse order
        requests = []
        for insertion in cell_insertions:
            requests.append({
                'insertText': {
                    'location': {'index': insertion['index']},
                    'text': insertion['text']
                }
            })

        # Execute text insertion
        if requests:
            self.docs_service.documents().batchUpdate(
                documentId=self.doc_id,
                body={'requests': requests}
            ).execute()

        # Step 5: Apply styling (need to re-fetch for updated indices)
        doc = self.docs_service.documents().get(documentId=self.doc_id).execute()

        # Find the table again
        for element in doc.get('body', {}).get('content', []):
            if 'table' in element:
                start_idx = element.get('startIndex', 0)
                if start_idx >= position - 5:
                    table_element = element
                    break

        if not table_element:
            return

        table = table_element['table']
        table_rows = table.get('tableRows', [])

        style_requests = []

        # Style header row cells
        if table_rows:
            header_row = table_rows[0]
            for cell in header_row.get('tableCells', []):
                # Background color for header
                style_requests.append({
                    'updateTableCellStyle': {
                        'tableRange': {
                            'tableCellLocation': {
                                'tableStartLocation': {'index': table_element['startIndex']},
                                'rowIndex': 0,
                                'columnIndex': header_row['tableCells'].index(cell)
                            },
                            'rowSpan': 1,
                            'columnSpan': 1
                        },
                        'tableCellStyle': {
                            'backgroundColor': {'color': {'rgbColor': BRAND_COLORS['blue_link']}}
                        },
                        'fields': 'backgroundColor'
                    }
                })

                # Text style for header
                cell_content = cell.get('content', [])
                if cell_content and 'paragraph' in cell_content[0]:
                    para = cell_content[0]['paragraph']
                    elements = para.get('elements', [])
                    if elements:
                        start = elements[0].get('startIndex', 0)
                        end = elements[-1].get('endIndex', start + 1)
                        if end > start:
                            style_requests.append({
                                'updateTextStyle': {
                                    'range': {'startIndex': start, 'endIndex': end},
                                    'textStyle': BRAND_STYLES['table_header'],
                                    'fields': 'bold,fontSize,weightedFontFamily,foregroundColor'
                                }
                            })

        # Style data rows
        for row_idx, table_row in enumerate(table_rows[1:], 1):  # Skip header
            for cell in table_row.get('tableCells', []):
                cell_content = cell.get('content', [])
                if cell_content and 'paragraph' in cell_content[0]:
                    para = cell_content[0]['paragraph']
                    elements = para.get('elements', [])
                    if elements:
                        start = elements[0].get('startIndex', 0)
                        end = elements[-1].get('endIndex', start + 1)
                        if end > start:
                            style_requests.append({
                                'updateTextStyle': {
                                    'range': {'startIndex': start, 'endIndex': end},
                                    'textStyle': BRAND_STYLES['table_body'],
                                    'fields': 'fontSize,weightedFontFamily,foregroundColor'
                                }
                            })

        # Execute styling
        if style_requests:
            try:
                self.docs_service.documents().batchUpdate(
                    documentId=self.doc_id,
                    body={'requests': style_requests}
                ).execute()
            except Exception as e:
                print(f"   ⚠️ Table styling error (non-critical): {str(e)[:100]}")

    def execute(self):
        """Execute all pending requests to build the document."""
        # Phase 1: Build text content
        if self.requests:
            print(f"   Applying {len(self.requests)} text formatting operations...")
            try:
                self.docs_service.documents().batchUpdate(
                    documentId=self.doc_id,
                    body={'requests': self.requests}
                ).execute()
            except Exception as e:
                print(f"   ❌ Text build failed: {str(e)[:200]}")
                raise

        # Phase 2: Insert tables (in reverse order to preserve positions)
        if self.pending_tables:
            print(f"   Inserting {len(self.pending_tables)} tables...")
            # Sort by position descending (insert last tables first)
            for table_info in sorted(self.pending_tables, key=lambda x: x['position'], reverse=True):
                try:
                    self._insert_table_at_position(
                        table_info['position'],
                        table_info['headers'],
                        table_info['rows']
                    )
                except Exception as e:
                    print(f"   ⚠️ Table insertion error: {str(e)[:100]}")

        print("   ✅ Document built successfully!")


# =============================================================================
# CONTENT PARSING
# =============================================================================

def parse_markdown_to_sections(text: str) -> list:
    """Parse simple markdown-like text into sections."""
    sections = []
    lines = text.strip().split('\n')
    current_paragraph = []

    for line in lines:
        line = line.rstrip()

        # Headers
        if line.startswith('## '):
            if current_paragraph:
                sections.append({'type': 'paragraph', 'content': ' '.join(current_paragraph)})
                current_paragraph = []
            sections.append({'type': 'section_header', 'content': line[3:]})

        elif line.startswith('### '):
            if current_paragraph:
                sections.append({'type': 'paragraph', 'content': ' '.join(current_paragraph)})
                current_paragraph = []
            sections.append({'type': 'subsection_header', 'content': line[4:]})

        elif line.startswith('# '):
            if current_paragraph:
                sections.append({'type': 'paragraph', 'content': ' '.join(current_paragraph)})
                current_paragraph = []
            sections.append({'type': 'title', 'content': line[2:]})

        # Bullet list
        elif line.startswith('- ') or line.startswith('* '):
            if current_paragraph:
                sections.append({'type': 'paragraph', 'content': ' '.join(current_paragraph)})
                current_paragraph = []

            item_text = line[2:]
            # Check for bold title pattern: **Title**: Description
            bold_match = re.match(r'\*\*(.+?)\*\*:\s*(.+)', item_text)
            if bold_match:
                item = {'title': bold_match.group(1), 'description': bold_match.group(2)}
            else:
                item = {'description': item_text}

            # Add to existing list or create new one
            if sections and sections[-1]['type'] == 'bullet_list':
                sections[-1]['items'].append(item)
            else:
                sections.append({'type': 'bullet_list', 'items': [item]})

        # Numbered list
        elif re.match(r'^\d+\.\s', line):
            if current_paragraph:
                sections.append({'type': 'paragraph', 'content': ' '.join(current_paragraph)})
                current_paragraph = []

            item_text = re.sub(r'^\d+\.\s', '', line)
            item = {'description': item_text}

            if sections and sections[-1]['type'] == 'numbered_list':
                sections[-1]['items'].append(item)
            else:
                sections.append({'type': 'numbered_list', 'items': [item]})

        # Divider
        elif line.startswith('---') or line.startswith('***'):
            if current_paragraph:
                sections.append({'type': 'paragraph', 'content': ' '.join(current_paragraph)})
                current_paragraph = []
            sections.append({'type': 'divider'})

        # Empty line = paragraph break
        elif not line:
            if current_paragraph:
                sections.append({'type': 'paragraph', 'content': ' '.join(current_paragraph)})
                current_paragraph = []

        # Regular text
        else:
            current_paragraph.append(line)

    # Don't forget last paragraph
    if current_paragraph:
        sections.append({'type': 'paragraph', 'content': ' '.join(current_paragraph)})

    return sections


# =============================================================================
# MAIN GENERATION FUNCTION
# =============================================================================

def generate_document(
    title: str,
    sections: list,
    doc_name: str = None,
    template_id: str = None,
    folder_id: str = None,
    use_template: bool = True
) -> dict:
    """
    Generate a branded Google Doc from structured content.

    Args:
        title: Document title (displayed centered at top)
        sections: List of section dicts with 'type' and 'content'/'items'
        doc_name: Google Doc filename (default: title)
        template_id: Template document ID for logo
        folder_id: Google Drive folder ID
        use_template: Whether to copy template for logo (default: True)

    Returns:
        Dict with document_id, document_url, title
    """
    template_id = template_id or DEFAULT_TEMPLATE_ID
    doc_name = doc_name or title

    # Authenticate
    drive, credentials = authenticate_google()

    # Create document
    if use_template:
        try:
            doc_id = copy_template_and_clear(drive, credentials, template_id, doc_name, folder_id)
        except Exception as e:
            print(f"   ⚠️ Template copy failed: {e}")
            print("   Falling back to blank document...")
            doc_id = create_blank_document(credentials, doc_name, folder_id)
    else:
        doc_id = create_blank_document(credentials, doc_name, folder_id)

    # Build content
    print("✏️  Building document content...")
    builder = DocumentBuilder(credentials, doc_id)

    # Add title
    builder.add_title(title)

    # Add sections
    for section in sections:
        builder.build_section(section)

    # Execute (two-phase: text first, then tables)
    builder.execute()

    document_url = f"https://docs.google.com/document/d/{doc_id}/edit"

    return {
        'document_id': doc_id,
        'document_url': document_url,
        'title': title
    }


def generate_from_text(title: str, content: str, **kwargs) -> dict:
    """Generate document from plain text/markdown content."""
    sections = parse_markdown_to_sections(content)
    return generate_document(title=title, sections=sections, **kwargs)


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate branded Google Docs from structured content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_document.py --input content.json --title "My Report"
  python generate_document.py --json '{"sections": [...]}' --title "Notes"
  python generate_document.py --title "Notes" --content "Text here..."
        """
    )

    parser.add_argument("--title", required=True, help="Document title")

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--input", help="JSON file with sections")
    input_group.add_argument("--json", help="JSON string with sections")
    input_group.add_argument("--content", help="Plain text/markdown content")

    parser.add_argument("--doc-name", help="Google Doc filename (default: title)")
    parser.add_argument("--template-id", help="Template ID for logo")
    parser.add_argument("--folder-id", help="Google Drive folder ID")
    parser.add_argument("--no-template", action="store_true", help="Don't use template (no logo)")
    parser.add_argument("--output-json", help="Save result to JSON file")

    args = parser.parse_args()

    try:
        # Parse input
        if args.input:
            input_path = Path(args.input)
            if not input_path.exists():
                print(f"❌ Input file not found: {args.input}")
                return 1
            data = json.loads(input_path.read_text())
            sections = data.get('sections', data) if isinstance(data, dict) else data

        elif args.json:
            data = json.loads(args.json)
            sections = data.get('sections', data) if isinstance(data, dict) else data

        else:
            # Plain text/markdown input
            sections = parse_markdown_to_sections(args.content)

        print(f"\n📄 Generating document: {args.title}")
        print(f"   Sections: {len(sections)}\n")

        result = generate_document(
            title=args.title,
            sections=sections,
            doc_name=args.doc_name,
            template_id=args.template_id,
            folder_id=args.folder_id,
            use_template=not args.no_template
        )

        print(f"\n✅ Document generated!")
        print(f"📄 URL: {result['document_url']}")

        if args.output_json:
            output_path = Path(args.output_json)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(result, indent=2))
            print(f"📁 Result saved to: {args.output_json}")

        return 0

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
