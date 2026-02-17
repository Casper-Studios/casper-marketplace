#!/usr/bin/env python3
"""
Google Drive Search

Search for files and folders in Google Drive.
Used for client overview and document discovery.

Directive: directives/gdrive_search.md

Usage:
    # Find client folder
    python execution/gdrive_search.py folder "Microsoft"

    # Search for documents
    python execution/gdrive_search.py files "proposal" --modified-days 30

    # Search in specific folder
    python execution/gdrive_search.py files "transcript" --in-folder "1abc123xyz"
"""

import os
import sys
import re
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# Configuration
SETTINGS_FILE = "settings.yaml"
CREDENTIALS_FILE = "mycreds.txt"
CLIENT_SECRETS_FILE = "client_secrets.json"

# Shared drive configuration (set via env vars or .env)
SHARED_DRIVE_ID = os.getenv("SHARED_DRIVE_ID", "")


class DriveSearchError(Exception):
    """Custom exception for Drive search operations."""
    pass


def validate_setup():
    """Validate required files exist."""
    if not Path(CLIENT_SECRETS_FILE).exists():
        raise FileNotFoundError(
            f"{CLIENT_SECRETS_FILE} not found. "
            "Download OAuth credentials from Google Cloud Console."
        )
    if not Path(SETTINGS_FILE).exists():
        raise FileNotFoundError(f"{SETTINGS_FILE} not found.")


def authenticate() -> GoogleDrive:
    """Authenticate with Google Drive."""
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(CREDENTIALS_FILE)

    if gauth.credentials is None:
        print("First time setup - opening browser for authentication...")
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        print("Refreshing credentials...")
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile(CREDENTIALS_FILE)
    return GoogleDrive(gauth)


def find_client_folder(
    drive: GoogleDrive,
    client_name: str,
    shared_drive_id: str = SHARED_DRIVE_ID
) -> Optional[dict]:
    """
    Find a client folder by name.

    Client folders follow pattern: [XX] Client Name

    Args:
        drive: GoogleDrive instance
        client_name: Client name to search for
        shared_drive_id: Shared drive ID

    Returns:
        Folder info dict or None
    """
    # Query folders in shared drive
    query = (
        f"'{shared_drive_id}' in parents and "
        "mimeType='application/vnd.google-apps.folder' and "
        "trashed=false"
    )

    file_list = drive.ListFile({
        'q': query,
        'supportsAllDrives': True,
        'includeItemsFromAllDrives': True,
        'corpora': 'drive',
        'driveId': shared_drive_id
    }).GetList()

    # Search for matching folder
    client_lower = client_name.lower()
    pattern = re.compile(r'^\[(\d+)\]\s*(.+)$')

    for folder in file_list:
        title = folder['title']
        match = pattern.match(title)

        if match:
            folder_name = match.group(2).strip().lower()
            if client_lower in folder_name or folder_name in client_lower:
                return {
                    'id': folder['id'],
                    'title': folder['title'],
                    'number': int(match.group(1)),
                    'webViewLink': folder['alternateLink']
                }

    return None


def search_files(
    drive: GoogleDrive,
    query: str = None,
    folder_id: str = None,
    file_types: List[str] = None,
    modified_days: int = None,
    shared_drive_id: str = SHARED_DRIVE_ID,
    limit: int = 50
) -> List[dict]:
    """
    Search for files in Google Drive.

    Args:
        drive: GoogleDrive instance
        query: Text to search in file names
        folder_id: Limit search to specific folder
        file_types: Filter by MIME types (doc, sheet, pdf, etc.)
        modified_days: Only files modified in last N days
        shared_drive_id: Shared drive to search
        limit: Maximum results

    Returns:
        List of file info dicts
    """
    # Build query
    conditions = ["trashed=false"]

    if folder_id:
        conditions.append(f"'{folder_id}' in parents")

    if query:
        conditions.append(f"title contains '{query}'")

    if modified_days:
        cutoff = datetime.utcnow() - timedelta(days=modified_days)
        cutoff_str = cutoff.strftime('%Y-%m-%dT%H:%M:%S')
        conditions.append(f"modifiedDate > '{cutoff_str}'")

    if file_types:
        type_map = {
            'doc': 'application/vnd.google-apps.document',
            'sheet': 'application/vnd.google-apps.spreadsheet',
            'slide': 'application/vnd.google-apps.presentation',
            'pdf': 'application/pdf',
            'folder': 'application/vnd.google-apps.folder'
        }
        mime_conditions = []
        for ft in file_types:
            mime = type_map.get(ft, ft)
            mime_conditions.append(f"mimeType='{mime}'")
        if mime_conditions:
            conditions.append(f"({' or '.join(mime_conditions)})")

    q = " and ".join(conditions)

    # Execute search
    params = {
        'q': q,
        'supportsAllDrives': True,
        'includeItemsFromAllDrives': True,
        'orderBy': 'modifiedDate desc',
        'maxResults': limit
    }

    if shared_drive_id:
        params['corpora'] = 'drive'
        params['driveId'] = shared_drive_id

    file_list = drive.ListFile(params).GetList()

    # Process results
    results = []
    for f in file_list:
        # Parse modified time
        modified = f.get('modifiedDate', '')
        if modified:
            try:
                modified_dt = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                modified_display = modified_dt.strftime('%Y-%m-%d')
            except Exception:
                modified_display = modified
        else:
            modified_display = 'Unknown'

        results.append({
            'id': f['id'],
            'title': f['title'],
            'mimeType': f.get('mimeType', ''),
            'webViewLink': f.get('alternateLink', ''),
            'modifiedDate': modified_display,
            'modifiedBy': f.get('lastModifyingUserName', ''),
            'fileSize': f.get('fileSize', '')
        })

    return results


def list_folder_contents(
    drive: GoogleDrive,
    folder_id: str,
    recursive: bool = False,
    _depth: int = 0,
    _max_depth: int = 2
) -> List[dict]:
    """
    List contents of a folder.

    Args:
        drive: GoogleDrive instance
        folder_id: Folder ID
        recursive: Whether to recurse into subfolders
        _depth: Current recursion depth
        _max_depth: Maximum recursion depth

    Returns:
        List of file/folder info dicts
    """
    query = f"'{folder_id}' in parents and trashed=false"

    file_list = drive.ListFile({
        'q': query,
        'supportsAllDrives': True,
        'includeItemsFromAllDrives': True
    }).GetList()

    results = []
    for f in file_list:
        is_folder = f.get('mimeType') == 'application/vnd.google-apps.folder'

        item = {
            'id': f['id'],
            'title': f['title'],
            'mimeType': f.get('mimeType', ''),
            'webViewLink': f.get('alternateLink', ''),
            'isFolder': is_folder,
            'depth': _depth
        }

        results.append(item)

        # Recurse into subfolders
        if recursive and is_folder and _depth < _max_depth:
            children = list_folder_contents(
                drive, f['id'],
                recursive=True,
                _depth=_depth + 1,
                _max_depth=_max_depth
            )
            results.extend(children)

    return results


def search_client_documents(
    client_name: str,
    keywords: List[str] = None,
    modified_days: int = 30
) -> dict:
    """
    Complete client document search.

    Args:
        client_name: Client name
        keywords: Additional keywords to search
        modified_days: Look back period for recent docs

    Returns:
        Dict with folder info and documents
    """
    validate_setup()
    drive = authenticate()

    result = {
        'client_name': client_name,
        'folder': None,
        'folder_contents': [],
        'recent_documents': []
    }

    # Find client folder
    folder = find_client_folder(drive, client_name)
    if folder:
        result['folder'] = folder

        # List folder contents
        contents = list_folder_contents(
            drive, folder['id'],
            recursive=True,
            _max_depth=2
        )
        result['folder_contents'] = contents

    # Search for recent documents mentioning client
    search_terms = [client_name]
    if keywords:
        search_terms.extend(keywords)

    for term in search_terms[:3]:  # Limit searches
        docs = search_files(
            drive,
            query=term,
            modified_days=modified_days,
            limit=10
        )
        result['recent_documents'].extend(docs)

    # Deduplicate
    seen = set()
    unique_docs = []
    for doc in result['recent_documents']:
        if doc['id'] not in seen:
            seen.add(doc['id'])
            unique_docs.append(doc)
    result['recent_documents'] = unique_docs[:20]

    return result


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Search Google Drive for files and folders"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Find client folder
    folder_parser = subparsers.add_parser("folder", help="Find client folder")
    folder_parser.add_argument("client_name", help="Client name")

    # Search files
    files_parser = subparsers.add_parser("files", help="Search for files")
    files_parser.add_argument("query", help="Search query")
    files_parser.add_argument("--in-folder", help="Folder ID to search in")
    files_parser.add_argument("--type", nargs="+", choices=['doc', 'sheet', 'slide', 'pdf'],
                              help="File types to filter")
    files_parser.add_argument("--modified-days", type=int, help="Modified in last N days")
    files_parser.add_argument("--limit", type=int, default=20, help="Max results")

    # List folder contents
    list_parser = subparsers.add_parser("list", help="List folder contents")
    list_parser.add_argument("folder_id", help="Folder ID")
    list_parser.add_argument("--recursive", action="store_true", help="Include subfolders")

    # Client overview search
    client_parser = subparsers.add_parser("client", help="Full client document search")
    client_parser.add_argument("client_name", help="Client name")
    client_parser.add_argument("--keywords", nargs="+", help="Additional search keywords")
    client_parser.add_argument("--days", type=int, default=30, help="Look back period")

    # JSON output
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        validate_setup()
        drive = authenticate()

        if args.command == "folder":
            print(f"Searching for client folder: {args.client_name}")
            folder = find_client_folder(drive, args.client_name)

            if folder:
                print(f"\nFound: {folder['title']}")
                print(f"ID: {folder['id']}")
                print(f"URL: {folder['webViewLink']}")
            else:
                print("Client folder not found")
            return 0

        elif args.command == "files":
            print(f"Searching for: {args.query}")
            files = search_files(
                drive,
                query=args.query,
                folder_id=args.in_folder,
                file_types=args.type,
                modified_days=args.modified_days,
                limit=args.limit
            )

            if hasattr(args, 'json') and args.json:
                print(json.dumps(files, indent=2))
            else:
                print(f"\nFound {len(files)} files:")
                for f in files:
                    print(f"\n  {f['title']}")
                    print(f"    Modified: {f['modifiedDate']} by {f['modifiedBy']}")
                    print(f"    URL: {f['webViewLink']}")
            return 0

        elif args.command == "list":
            print(f"Listing folder: {args.folder_id}")
            contents = list_folder_contents(
                drive,
                args.folder_id,
                recursive=args.recursive
            )

            if hasattr(args, 'json') and args.json:
                print(json.dumps(contents, indent=2))
            else:
                print(f"\nFolder contents ({len(contents)} items):")
                for item in contents:
                    indent = "  " * (item['depth'] + 1)
                    icon = "[D]" if item['isFolder'] else "[F]"
                    print(f"{indent}{icon} {item['title']}")
            return 0

        elif args.command == "client":
            print(f"Full client search: {args.client_name}")
            result = search_client_documents(
                args.client_name,
                keywords=args.keywords,
                modified_days=args.days
            )

            if hasattr(args, 'json') and args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"\n=== Client Documents: {args.client_name} ===")

                if result['folder']:
                    print(f"\nClient Folder: {result['folder']['title']}")
                    print(f"URL: {result['folder']['webViewLink']}")
                    print(f"\nFolder Contents ({len(result['folder_contents'])} items):")
                    for item in result['folder_contents'][:15]:
                        indent = "  " * (item['depth'] + 1)
                        icon = "[D]" if item['isFolder'] else "[F]"
                        print(f"{indent}{icon} {item['title']}")
                else:
                    print("\nNo client folder found")

                if result['recent_documents']:
                    print(f"\nRecent Documents ({len(result['recent_documents'])}):")
                    for doc in result['recent_documents'][:10]:
                        print(f"  - {doc['title']} (modified {doc['modifiedDate']})")
            return 0

    except FileNotFoundError as e:
        print(f"Setup error: {e}")
        return 1
    except DriveSearchError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
