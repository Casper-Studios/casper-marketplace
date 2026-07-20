#!/usr/bin/env python3
"""
Basic Company Research

Researches a company using Parallel AI and saves the research report
to Google Drive as a document.

Directive: directives/basic_research.md

Usage:
    # Research a company and save to Drive
    python execution/basic_research.py "Microsoft" --folder-id 1234abc

    # Research with custom prompt
    python execution/basic_research.py "Acme Corp" --prompt "Focus on their AI initiatives"

    # Dry run (research but don't save to Drive)
    python execution/basic_research.py "Test Company" --dry-run
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
import requests

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# Load environment variables
load_dotenv()

# Configuration
PARALLEL_API_KEY = os.getenv("PARALLEL_API_KEY")
TASK_API_URL = "https://api.parallel.ai/v1/tasks/runs"
SHARED_DRIVE_ID = os.getenv("SHARED_DRIVE_ID", "")

# Output directory
OUTPUT_DIR = Path(".tmp/basic_research")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class ResearchError(Exception):
    """Custom exception for research operations."""
    pass


def authenticate_drive() -> GoogleDrive:
    """Authenticate with Google Drive."""
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("mycreds.txt")

    if gauth.credentials is None:
        print("First time setup - opening browser for authentication...")
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        print("Refreshing credentials...")
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile("mycreds.txt")
    return GoogleDrive(gauth)


def research_company(company_name: str, additional_context: str = None) -> dict:
    """
    Research a company using Parallel AI deep research.

    Args:
        company_name: Name of the company to research
        additional_context: Optional additional research focus

    Returns:
        Dict with research report content
    """
    if not PARALLEL_API_KEY:
        raise ResearchError(
            "PARALLEL_API_KEY not found. Add it to your .env file."
        )

    # Build research prompt
    prompt = f"""Research the company "{company_name}" comprehensively. Include:

1. **Company Overview**
   - What they do (core business)
   - Industry/sector
   - Founded year, headquarters
   - Company size (employees, if available)

2. **Products & Services**
   - Main offerings
   - Target market/customers
   - Key differentiators

3. **Leadership & Team**
   - Key executives (CEO, founders)
   - Notable team members

4. **Recent News & Developments**
   - Latest news (past 6 months)
   - Product launches
   - Partnerships or acquisitions

5. **Technology Stack** (if relevant)
   - Known technologies used
   - Technical approach

6. **Market Position**
   - Competitors
   - Market share (if available)
   - Unique value proposition

7. **Potential Pain Points**
   - Common challenges in their industry
   - Areas where automation/AI could help
"""

    if additional_context:
        prompt += f"\n\n**Additional Focus:**\n{additional_context}"

    print(f"🔍 Researching {company_name}...")
    print(f"   Using Parallel AI deep research...")

    # Call Parallel AI deep research
    headers = {
        "Authorization": f"Bearer {PARALLEL_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "base",  # Use base processor for cost efficiency
        "system": "You are a business research analyst. Provide comprehensive, factual research with sources.",
        "prompt": prompt,
        "response_format": "markdown"
    }

    response = requests.post(
        TASK_API_URL,
        headers=headers,
        json=payload,
        timeout=120
    )

    if response.status_code != 200:
        raise ResearchError(f"Parallel AI error: {response.status_code} - {response.text}")

    result = response.json()

    # Poll for completion if async
    if result.get("status") == "pending":
        run_id = result.get("id")
        print(f"   Task ID: {run_id}")
        print(f"   Waiting for completion...")

        for _ in range(60):  # Max 2 minutes
            import time
            time.sleep(2)

            status_response = requests.get(
                f"{TASK_API_URL}/{run_id}",
                headers=headers
            )
            status = status_response.json()

            if status.get("status") == "completed":
                result = status
                break
            elif status.get("status") == "failed":
                raise ResearchError(f"Research failed: {status.get('error')}")

    # Extract research content
    content = result.get("output", result.get("result", ""))
    if not content:
        raise ResearchError("No research content returned")

    print(f"   ✓ Research complete ({len(content)} characters)")

    return {
        "company_name": company_name,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "model": "parallel-ai-base"
    }


def find_client_folder(drive: GoogleDrive, company_name: str) -> Optional[str]:
    """
    Find client folder in shared drive.

    Args:
        drive: GoogleDrive instance
        company_name: Company name to search for

    Returns:
        Folder ID or None
    """
    query = (
        f"title contains '{company_name}' "
        f"and mimeType = 'application/vnd.google-apps.folder' "
        f"and trashed = false"
    )

    file_list = drive.ListFile({
        'q': query,
        'supportsAllDrives': True,
        'includeItemsFromAllDrives': True,
        'corpora': 'drive',
        'driveId': SHARED_DRIVE_ID
    }).GetList()

    if file_list:
        return file_list[0]['id']
    return None


def save_to_drive(
    drive: GoogleDrive,
    content: str,
    company_name: str,
    folder_id: str = None
) -> dict:
    """
    Save research report to Google Drive as a Google Doc.

    Args:
        drive: GoogleDrive instance
        content: Research content (markdown)
        company_name: Company name for document title
        folder_id: Target folder ID (optional)

    Returns:
        Dict with document_id and document_url
    """
    timestamp = datetime.now().strftime("%Y-%m-%d")
    doc_title = f"[Research] {company_name} - {timestamp}"

    print(f"📄 Creating Google Doc: {doc_title}")

    # Create the file metadata
    file_metadata = {
        'title': doc_title,
        'mimeType': 'application/vnd.google-apps.document'
    }

    if folder_id:
        file_metadata['parents'] = [{'id': folder_id}]

    # For shared drives
    file = drive.CreateFile(file_metadata)

    # Set content
    file.SetContentString(content)

    # Upload to shared drive
    file.Upload(param={'supportsAllDrives': True})

    document_id = file['id']
    document_url = f"https://docs.google.com/document/d/{document_id}/edit"

    print(f"   ✓ Document created: {document_url}")

    return {
        "document_id": document_id,
        "document_url": document_url,
        "document_title": doc_title
    }


def basic_research(
    company_name: str,
    folder_id: str = None,
    additional_context: str = None,
    dry_run: bool = False
) -> dict:
    """
    Main function: Research company and save to Google Drive.

    Args:
        company_name: Name of company to research
        folder_id: Google Drive folder ID to save to
        additional_context: Additional research focus
        dry_run: If True, research but don't save to Drive

    Returns:
        Dict with research content and document URL
    """
    result = {
        "company_name": company_name,
        "success": False,
        "research_content": None,
        "document_url": None,
        "document_id": None,
        "error": None
    }

    try:
        # Step 1: Research the company
        research = research_company(company_name, additional_context)
        result["research_content"] = research["content"]

        # Save locally
        local_file = OUTPUT_DIR / f"{company_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        local_file.write_text(research["content"])
        print(f"   Saved locally: {local_file}")

        if dry_run:
            print("   [DRY RUN] Skipping Google Drive upload")
            result["success"] = True
            return result

        # Step 2: Authenticate with Google Drive
        drive = authenticate_drive()

        # Step 3: Find or use provided folder
        if not folder_id:
            folder_id = find_client_folder(drive, company_name)
            if folder_id:
                print(f"   Found client folder: {folder_id}")

        # Step 4: Save to Google Drive
        doc_result = save_to_drive(
            drive,
            research["content"],
            company_name,
            folder_id
        )

        result["document_url"] = doc_result["document_url"]
        result["document_id"] = doc_result["document_id"]
        result["success"] = True

    except Exception as e:
        result["error"] = str(e)
        print(f"   ✗ Error: {e}")

    return result


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Research a company and save to Google Drive",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Microsoft"
  %(prog)s "Acme Corp" --folder-id 1abc123
  %(prog)s "Test" --dry-run
  %(prog)s "Company" --prompt "Focus on AI capabilities"
        """
    )

    parser.add_argument("company_name", help="Name of company to research")
    parser.add_argument("--folder-id", help="Google Drive folder ID to save to")
    parser.add_argument("--prompt", help="Additional research focus/context")
    parser.add_argument("--dry-run", action="store_true", help="Research but don't save to Drive")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  Basic Company Research")
    print(f"{'='*60}")
    print(f"  Company: {args.company_name}")
    print(f"{'='*60}\n")

    try:
        result = basic_research(
            company_name=args.company_name,
            folder_id=args.folder_id,
            additional_context=args.prompt,
            dry_run=args.dry_run
        )

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n{'='*60}")
            if result["success"]:
                print("  ✅ Research Complete")
                if result["document_url"]:
                    print(f"  📄 Document: {result['document_url']}")
            else:
                print(f"  ❌ Failed: {result['error']}")
            print(f"{'='*60}\n")

        return 0 if result["success"] else 1

    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
