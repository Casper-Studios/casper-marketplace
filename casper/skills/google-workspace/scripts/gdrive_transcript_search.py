#!/usr/bin/env python3
"""
Google Drive Transcript Search
Searches for transcript files in client folders based on company name.

Directive: directives/google_workspace_integration.md

Usage:
    # Find transcript for a client
    python execution/gdrive_transcript_search.py --client "Acme Corp"

    # Find transcript and return folder info
    python execution/gdrive_transcript_search.py --client "Acme Corp" --verbose

    # Search with specific keywords
    python execution/gdrive_transcript_search.py --client "Acme" --keywords "transcript,notes,meeting"
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# Configuration
SETTINGS_FILE = "settings.yaml"
CREDENTIALS_FILE = "mycreds.txt"

# Default search keywords for transcript files
DEFAULT_TRANSCRIPT_KEYWORDS = [
    "transcript",
    "transcription",
    "meeting notes",
    "call notes",
    "discovery",
    "kick-off",
    "kickoff"
]


def authenticate() -> GoogleDrive:
    """
    Authenticate with Google Drive using OAuth 2.0.

    Returns:
        GoogleDrive: Authenticated drive instance
    """
    print("Authenticating with Google Drive...")

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
    print("Authentication successful!")

    return GoogleDrive(gauth)


def search_client_folders(drive: GoogleDrive, client_name: str) -> list:
    """
    Search for folders containing the client name.

    Args:
        drive: GoogleDrive instance
        client_name: Client/company name to search for

    Returns:
        List of folder metadata dicts
    """
    print(f"   Searching for folders matching: {client_name}")

    # Search for folders containing client name (case-insensitive via contains)
    query = (
        f"mimeType='application/vnd.google-apps.folder' "
        f"and title contains '{client_name}' "
        f"and trashed=false"
    )

    file_list = drive.ListFile({'q': query}).GetList()

    # Sort by most recently modified
    file_list.sort(key=lambda x: x.get('modifiedDate', ''), reverse=True)

    print(f"   Found {len(file_list)} matching folders")
    return file_list


def search_transcripts_in_folder(
    drive: GoogleDrive,
    folder_id: str,
    keywords: list = None
) -> list:
    """
    Search for transcript files within a specific folder.

    Args:
        drive: GoogleDrive instance
        folder_id: Google Drive folder ID
        keywords: List of keywords to search for in file names

    Returns:
        List of file metadata dicts
    """
    keywords = keywords or DEFAULT_TRANSCRIPT_KEYWORDS
    all_files = []

    # Search for each keyword
    for keyword in keywords:
        query = (
            f"'{folder_id}' in parents "
            f"and title contains '{keyword}' "
            f"and trashed=false"
        )
        files = drive.ListFile({'q': query}).GetList()
        all_files.extend(files)

    # Deduplicate by file ID
    seen_ids = set()
    unique_files = []
    for f in all_files:
        if f['id'] not in seen_ids:
            seen_ids.add(f['id'])
            unique_files.append(f)

    # Sort by most recently modified
    unique_files.sort(key=lambda x: x.get('modifiedDate', ''), reverse=True)

    return unique_files


def search_transcripts_recursive(
    drive: GoogleDrive,
    folder_id: str,
    keywords: list = None,
    max_depth: int = 3,
    current_depth: int = 0
) -> list:
    """
    Recursively search for transcripts in folder and subfolders.

    Args:
        drive: GoogleDrive instance
        folder_id: Starting folder ID
        keywords: Keywords to search for
        max_depth: Maximum recursion depth
        current_depth: Current depth (for recursion)

    Returns:
        List of (file_metadata, folder_path) tuples
    """
    if current_depth > max_depth:
        return []

    results = []

    # Search current folder
    transcripts = search_transcripts_in_folder(drive, folder_id, keywords)
    for t in transcripts:
        results.append((t, folder_id))

    # Search subfolders
    subfolders_query = (
        f"'{folder_id}' in parents "
        f"and mimeType='application/vnd.google-apps.folder' "
        f"and trashed=false"
    )
    subfolders = drive.ListFile({'q': subfolders_query}).GetList()

    for subfolder in subfolders:
        sub_results = search_transcripts_recursive(
            drive,
            subfolder['id'],
            keywords,
            max_depth,
            current_depth + 1
        )
        results.extend(sub_results)

    return results


def get_file_content(drive: GoogleDrive, file_id: str) -> Optional[str]:
    """
    Download and return content of a text-based file.

    Supports: Google Docs, plain text, markdown

    Args:
        drive: GoogleDrive instance
        file_id: File ID to download

    Returns:
        File content as string, or None if not readable
    """
    try:
        file_obj = drive.CreateFile({'id': file_id})
        file_obj.FetchMetadata()

        mime_type = file_obj.get('mimeType', '')

        # Google Docs - export as plain text
        if mime_type == 'application/vnd.google-apps.document':
            content = file_obj.GetContentString(mimetype='text/plain')
            return content

        # Plain text files
        elif mime_type in ['text/plain', 'text/markdown', 'text/x-markdown']:
            content = file_obj.GetContentString()
            return content

        # Try to get content anyway for other text types
        elif 'text' in mime_type:
            content = file_obj.GetContentString()
            return content

        else:
            print(f"   Unsupported file type: {mime_type}")
            return None

    except Exception as e:
        print(f"   Error reading file: {e}")
        return None


def find_client_transcript(
    drive: GoogleDrive,
    client_name: str,
    keywords: list = None,
    verbose: bool = False
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Find transcript file for a client.

    Args:
        drive: GoogleDrive instance
        client_name: Client/company name
        keywords: Optional custom keywords to search
        verbose: Print detailed progress

    Returns:
        Tuple of (file_content, file_id, folder_id) or (None, None, None)
    """
    print(f"\nSearching for transcript for: {client_name}")

    # Step 1: Find client folders
    folders = search_client_folders(drive, client_name)

    if not folders:
        print(f"   No folders found matching '{client_name}'")
        return None, None, None

    if verbose:
        print(f"   Found folders:")
        for f in folders[:5]:
            print(f"      - {f['title']} (modified: {f.get('modifiedDate', 'N/A')[:10]})")

    # Step 2: Search for transcripts in each folder
    all_transcripts = []

    for folder in folders:
        if verbose:
            print(f"   Searching in: {folder['title']}")

        results = search_transcripts_recursive(
            drive,
            folder['id'],
            keywords,
            max_depth=2
        )

        for file_meta, parent_folder_id in results:
            all_transcripts.append({
                'file': file_meta,
                'folder_id': parent_folder_id,
                'client_folder_id': folder['id'],
                'client_folder_name': folder['title']
            })

    if not all_transcripts:
        print(f"   No transcript files found in client folders")
        return None, None, None

    # Step 3: Select best transcript (most recent)
    all_transcripts.sort(
        key=lambda x: x['file'].get('modifiedDate', ''),
        reverse=True
    )

    best_match = all_transcripts[0]
    transcript_file = best_match['file']

    print(f"\n   Found transcript: {transcript_file['title']}")
    print(f"   In folder: {best_match['client_folder_name']}")
    print(f"   Modified: {transcript_file.get('modifiedDate', 'N/A')[:10]}")

    # Step 4: Download content
    print(f"   Downloading content...")
    content = get_file_content(drive, transcript_file['id'])

    if content:
        print(f"   Downloaded {len(content)} characters")
        return content, transcript_file['id'], best_match['client_folder_id']
    else:
        print(f"   Could not read file content")
        return None, transcript_file['id'], best_match['client_folder_id']


def find_or_create_proposals_folder(
    drive: GoogleDrive,
    client_folder_id: str
) -> str:
    """
    Find or create a Proposals subfolder in the client folder.

    Args:
        drive: GoogleDrive instance
        client_folder_id: Client folder ID

    Returns:
        Proposals folder ID
    """
    # Check if Proposals folder exists
    query = (
        f"'{client_folder_id}' in parents "
        f"and title='Proposals' "
        f"and mimeType='application/vnd.google-apps.folder' "
        f"and trashed=false"
    )
    folders = drive.ListFile({'q': query}).GetList()

    if folders:
        return folders[0]['id']

    # Create Proposals folder
    print("   Creating Proposals folder...")
    folder = drive.CreateFile({
        'title': 'Proposals',
        'parents': [{'id': client_folder_id}],
        'mimeType': 'application/vnd.google-apps.folder'
    })
    folder.Upload()
    print(f"   Created Proposals folder: {folder['id']}")
    return folder['id']


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Search Google Drive for client transcripts",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--client",
        required=True,
        help="Client/company name to search for"
    )
    parser.add_argument(
        "--keywords",
        help="Comma-separated keywords to search for in file names"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed progress"
    )
    parser.add_argument(
        "--output",
        help="Save transcript content to file"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    try:
        # Authenticate
        drive = authenticate()

        # Parse keywords
        keywords = None
        if args.keywords:
            keywords = [k.strip() for k in args.keywords.split(',')]

        # Search for transcript
        content, file_id, folder_id = find_client_transcript(
            drive,
            args.client,
            keywords,
            args.verbose
        )

        if content is None:
            print(f"\nNo transcript found for '{args.client}'")
            return 1

        # Output results
        if args.json:
            result = {
                "client": args.client,
                "file_id": file_id,
                "folder_id": folder_id,
                "content_length": len(content),
                "content_preview": content[:500] + "..." if len(content) > 500 else content
            }
            print(json.dumps(result, indent=2))
        else:
            print(f"\nTranscript found!")
            print(f"   File ID: {file_id}")
            print(f"   Folder ID: {folder_id}")
            print(f"   Content length: {len(content)} characters")

            if args.output:
                Path(args.output).write_text(content)
                print(f"   Saved to: {args.output}")
            else:
                print(f"\n--- Content Preview (first 500 chars) ---")
                print(content[:500])
                if len(content) > 500:
                    print("...")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
