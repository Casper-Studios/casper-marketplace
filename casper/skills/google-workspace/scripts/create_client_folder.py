#!/usr/bin/env python3
"""
Create Client Folder Structure in Google Drive

Creates a numbered client folder in the Casper Studios shared drive with
the standard folder structure. Replicates the n8n workflow.

Structure created:
    [XX] {Client Name}/
    ├── [1] Admin/
    └── [2] Discovery/
        ├── [1] Reference/Data/
        ├── [2] Interviews/
        │   ├── [1] Leads/
        │   └── [2] Team/
        ├── [3] Meeting Transcripts/
        └── [4] Functional Read Out/

Directive: directives/create_client_folder.md

Usage:
    # Create folder structure for a new client
    python execution/create_client_folder.py "Microsoft"

    # Dry run to see what would be created
    python execution/create_client_folder.py "Acme Corp" --dry-run
"""

import os
import re
import sys
import argparse
import json
from pathlib import Path
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# Configuration
SETTINGS_FILE = "settings.yaml"
CREDENTIALS_FILE = "mycreds.txt"
CLIENT_SECRETS_FILE = "client_secrets.json"

# Casper Studios Client Projects shared drive
SHARED_DRIVE_ID = "0APeqlhKR8qTPUk9PVA"
SHARED_DRIVE_NAME = "[03] Casper Studios - Client Projects"

# Standard client folder structure
CLIENT_FOLDER_STRUCTURE = {
    "[1] Admin": {},
    "[2] Discovery": {
        "[1] Reference/Data": {},
        "[2] Interviews": {
            "[1] Leads": {},
            "[2] Team": {}
        },
        "[3] Meeting Transcripts": {},
        "[4] Functional Read Out": {}
    }
}


class ClientFolderError(Exception):
    """Custom exception for client folder operations."""
    pass


def validate_setup():
    """Validate required files exist."""
    if not Path(CLIENT_SECRETS_FILE).exists():
        raise FileNotFoundError(
            f"{CLIENT_SECRETS_FILE} not found!\n\n"
            "Setup instructions:\n"
            "1. Go to https://console.cloud.google.com\n"
            "2. Enable Google Drive API\n"
            "3. Create OAuth 2.0 credentials (Desktop app)\n"
            "4. Download JSON and save as 'client_secrets.json'\n"
        )

    if not Path(SETTINGS_FILE).exists():
        raise FileNotFoundError(f"{SETTINGS_FILE} not found! This should be in project root.")


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
        print("   Using saved credentials...")
        gauth.Authorize()

    gauth.SaveCredentialsFile(CREDENTIALS_FILE)
    print("   Authentication successful")

    return GoogleDrive(gauth)


def get_next_folder_number(drive: GoogleDrive) -> int:
    """
    Find the highest numbered folder in the shared drive and return next number.

    Folders are named like "[15] Client Name". We find the highest number
    and increment by 1.

    Args:
        drive: Authenticated GoogleDrive instance

    Returns:
        int: Next folder number to use
    """
    print(f"Scanning {SHARED_DRIVE_NAME} for existing folders...")

    # Query folders in the shared drive root
    # For shared drives, we use driveId and corpora='drive'
    query = (
        f"'{SHARED_DRIVE_ID}' in parents and "
        "mimeType='application/vnd.google-apps.folder' and "
        "trashed=false"
    )

    file_list = drive.ListFile({
        'q': query,
        'supportsAllDrives': True,
        'includeItemsFromAllDrives': True,
        'corpora': 'drive',
        'driveId': SHARED_DRIVE_ID
    }).GetList()

    # Find folders matching pattern [XX]
    pattern = re.compile(r'^\[(\d+)\]')
    max_number = 0

    for folder in file_list:
        match = pattern.match(folder['title'])
        if match:
            num = int(match.group(1))
            if num > max_number:
                max_number = num

    next_number = max_number + 1
    print(f"   Found highest number: [{max_number:02d}]")
    print(f"   Next number will be: [{next_number:02d}]")

    return next_number


def create_folder_in_shared_drive(
    drive: GoogleDrive,
    name: str,
    parent_id: str
) -> dict:
    """
    Create a folder in a shared drive.

    Args:
        drive: Authenticated GoogleDrive instance
        name: Folder name
        parent_id: Parent folder ID

    Returns:
        Dict with folder id and webViewLink
    """
    # Check if folder already exists
    query = (
        f"'{parent_id}' in parents and "
        f"title='{name}' and "
        "mimeType='application/vnd.google-apps.folder' and "
        "trashed=false"
    )

    file_list = drive.ListFile({
        'q': query,
        'supportsAllDrives': True,
        'includeItemsFromAllDrives': True,
        'corpora': 'drive',
        'driveId': SHARED_DRIVE_ID
    }).GetList()

    if file_list:
        existing = file_list[0]
        return {
            'id': existing['id'],
            'name': name,
            'webViewLink': existing['alternateLink'],
            'existed': True
        }

    # Create new folder in shared drive
    folder = drive.CreateFile({
        'title': name,
        'parents': [{'id': parent_id}],
        'mimeType': 'application/vnd.google-apps.folder'
    })

    # Must set supportsAllDrives for shared drive operations
    folder.Upload(param={'supportsAllDrives': True})

    return {
        'id': folder['id'],
        'name': name,
        'webViewLink': folder['alternateLink'],
        'existed': False
    }


def create_structure_recursive(
    drive: GoogleDrive,
    structure: dict,
    parent_id: str,
    path_prefix: str = ''
) -> list:
    """
    Recursively create folder structure.

    Args:
        drive: GoogleDrive instance
        structure: Dict representing folder hierarchy
        parent_id: Current parent folder ID
        path_prefix: Current path for logging

    Returns:
        list: All created folders with paths and IDs
    """
    created_folders = []

    for folder_name, children in structure.items():
        current_path = f"{path_prefix}/{folder_name}" if path_prefix else folder_name

        # Create this folder
        result = create_folder_in_shared_drive(drive, folder_name, parent_id)

        status = "exists" if result['existed'] else "created"
        print(f"   {'[exists]' if result['existed'] else '[created]'} {current_path}")

        created_folders.append({
            'path': current_path,
            'id': result['id'],
            'webViewLink': result['webViewLink'],
            'existed': result['existed']
        })

        # Recursively create children
        if children and isinstance(children, dict):
            child_folders = create_structure_recursive(
                drive, children, result['id'], current_path
            )
            created_folders.extend(child_folders)

    return created_folders


def create_client_folder(
    client_name: str,
    dry_run: bool = False
) -> dict:
    """
    Create a complete client folder structure in the shared drive.

    Args:
        client_name: Name of the client (e.g., "Microsoft")
        dry_run: If True, don't actually create folders

    Returns:
        Dict with folder_url, folder_id, all created folders
    """
    validate_setup()

    if dry_run:
        print("\n[DRY RUN] Would create the following structure:")
        print(f"  [XX] {client_name}/")
        for folder, children in CLIENT_FOLDER_STRUCTURE.items():
            print(f"    {folder}/")
            if children:
                for subfolder in children:
                    print(f"      {subfolder}/")
        return {"dry_run": True, "client_name": client_name}

    # Authenticate
    drive = authenticate()

    # Get next folder number
    next_num = get_next_folder_number(drive)

    # Create parent folder name
    parent_folder_name = f"[{next_num:02d}] {client_name}"
    print(f"\nCreating folder structure: {parent_folder_name}")

    # Create parent folder
    parent_result = create_folder_in_shared_drive(
        drive,
        parent_folder_name,
        SHARED_DRIVE_ID
    )

    if parent_result['existed']:
        print(f"   [exists] {parent_folder_name}")
    else:
        print(f"   [created] {parent_folder_name}")

    # Create child structure
    created_folders = create_structure_recursive(
        drive,
        CLIENT_FOLDER_STRUCTURE,
        parent_result['id'],
        parent_folder_name
    )

    # Prepend parent folder to list
    all_folders = [{
        'path': parent_folder_name,
        'id': parent_result['id'],
        'webViewLink': parent_result['webViewLink'],
        'existed': parent_result['existed']
    }] + created_folders

    # Summary
    new_count = sum(1 for f in all_folders if not f['existed'])
    existing_count = sum(1 for f in all_folders if f['existed'])

    print(f"\nDone!")
    print(f"   Created: {new_count} new folders")
    print(f"   Existing: {existing_count} folders (skipped)")
    print(f"\nClient folder: {parent_result['webViewLink']}")

    result = {
        'client_name': client_name,
        'folder_number': next_num,
        'folder_name': parent_folder_name,
        'folder_id': parent_result['id'],
        'folder_url': parent_result['webViewLink'],
        'created_folders': all_folders,
        'summary': {
            'total': len(all_folders),
            'new': new_count,
            'existing': existing_count
        }
    }

    # Save result to .tmp
    output_dir = Path('.tmp/client_folders')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f'{client_name.lower().replace(" ", "_")}.json'
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"   Result saved to: {output_file}")

    return result


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Create client folder structure in Google Drive",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create folder structure for a new client
  %(prog)s "Microsoft"

  # Dry run to see what would be created
  %(prog)s "Acme Corp" --dry-run
        """
    )

    parser.add_argument("client_name", help="Name of the client")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    try:
        result = create_client_folder(
            client_name=args.client_name,
            dry_run=args.dry_run
        )

        if args.json:
            print(json.dumps(result, indent=2))

        return 0

    except FileNotFoundError as e:
        print(f"Setup Error: {e}")
        return 1
    except ClientFolderError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
