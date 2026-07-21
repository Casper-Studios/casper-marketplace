#!/usr/bin/env python3
"""
Google Drive Folder Structure Generator

Auto-generate nested folder structures in Google Drive with a single command.

Usage:
    # Create folder structure from JSON
    python execution/gdrive_folder_structure.py --structure '{
      "Folder 1": {
        "subfolder a": {},
        "subfolder b": {}
      }
    }'

    # Create from a JSON file
    python execution/gdrive_folder_structure.py --file structure.json

    # Create in specific parent folder
    python execution/gdrive_folder_structure.py --structure '{"Project": {}}' --parent-path "Clients/Acme"
"""

import os
import sys
import json
import argparse
from pathlib import Path
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# Configuration
SETTINGS_FILE = "settings.yaml"
CREDENTIALS_FILE = "mycreds.txt"
CLIENT_SECRETS_FILE = "client_secrets.json"


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


def authenticate():
    """
    Authenticate with Google Drive using OAuth 2.0.

    Returns:
        GoogleDrive: Authenticated drive instance
    """
    print("🔐 Authenticating with Google Drive...")

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
    print("✅ Authentication successful!")

    return GoogleDrive(gauth)


def find_folder_by_path(drive, folder_path, parent_id='root'):
    """
    Find folder ID by path, traversing nested structure.

    Args:
        drive: GoogleDrive instance
        folder_path: Path like "Clients/Acme/Images"
        parent_id: Parent folder ID (default: 'root' for My Drive)

    Returns:
        str: Folder ID or None if not found
    """
    if not folder_path:
        return parent_id

    parts = folder_path.split('/')
    current_id = parent_id

    for folder_name in parts:
        query = f"'{current_id}' in parents and title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        file_list = drive.ListFile({'q': query}).GetList()

        if file_list:
            current_id = file_list[0]['id']
        else:
            return None

    return current_id


def create_folder(drive, name, parent_id='root'):
    """
    Create a single folder in Google Drive.

    Args:
        drive: GoogleDrive instance
        name: Folder name
        parent_id: Parent folder ID

    Returns:
        dict: Folder info with id and webViewLink
    """
    # Check if folder already exists
    query = f"'{parent_id}' in parents and title='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    file_list = drive.ListFile({'q': query}).GetList()

    if file_list:
        existing = file_list[0]
        return {
            'id': existing['id'],
            'name': name,
            'webViewLink': existing['alternateLink'],
            'existed': True
        }

    # Create new folder
    folder = drive.CreateFile({
        'title': name,
        'parents': [{'id': parent_id}],
        'mimeType': 'application/vnd.google-apps.folder'
    })
    folder.Upload()

    return {
        'id': folder['id'],
        'name': name,
        'webViewLink': folder['alternateLink'],
        'existed': False
    }


def create_structure_recursive(drive, structure, parent_id='root', path_prefix=''):
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
        result = create_folder(drive, folder_name, parent_id)

        status = "exists" if result['existed'] else "created"
        print(f"   {'✓' if result['existed'] else '✅'} {current_path} ({status})")

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


def parse_structure(structure_str):
    """
    Parse structure from JSON string.

    Args:
        structure_str: JSON string or file path

    Returns:
        dict: Parsed structure
    """
    try:
        return json.loads(structure_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON structure: {e}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Create folder structure in Google Drive",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple structure
  %(prog)s --structure '{"Folder 1": {"subfolder a": {}, "subfolder b": {}}}'

  # From file
  %(prog)s --file structure.json

  # In specific parent
  %(prog)s --structure '{"Project": {}}' --parent-path "Clients/Acme"
        """
    )

    parser.add_argument("--structure", help="JSON structure string")
    parser.add_argument("--file", help="Path to JSON structure file")
    parser.add_argument("--parent-path", help="Parent folder path (e.g., 'Clients/Acme')")
    parser.add_argument("--parent-id", default="root", help="Parent folder ID (default: My Drive root)")

    args = parser.parse_args()

    # Validate inputs
    if not args.structure and not args.file:
        parser.error("Must specify --structure or --file")

    try:
        # Validate setup
        validate_setup()

        # Parse structure
        if args.file:
            with open(args.file, 'r') as f:
                structure = json.load(f)
            print(f"📄 Loaded structure from: {args.file}")
        else:
            structure = parse_structure(args.structure)

        print(f"\n📁 Folder structure to create:")
        print(json.dumps(structure, indent=2))

        # Authenticate
        drive = authenticate()

        # Resolve parent folder
        parent_id = args.parent_id
        if args.parent_path:
            print(f"\n🔍 Finding parent folder: {args.parent_path}")
            parent_id = find_folder_by_path(drive, args.parent_path)
            if parent_id is None:
                print(f"❌ Parent folder not found: {args.parent_path}")
                return 1
            print(f"   ✓ Found: {parent_id}")

        # Create structure
        print(f"\n📁 Creating folder structure...")
        created_folders = create_structure_recursive(drive, structure, parent_id)

        # Summary
        new_count = sum(1 for f in created_folders if not f['existed'])
        existing_count = sum(1 for f in created_folders if f['existed'])

        print(f"\n✅ Done!")
        print(f"   Created: {new_count} new folders")
        print(f"   Existing: {existing_count} folders (skipped)")

        if created_folders:
            root_folder = created_folders[0]
            print(f"\n📂 Root folder: {root_folder['webViewLink']}")

        # Output JSON result
        result = {
            'root_folder_id': created_folders[0]['id'] if created_folders else None,
            'root_folder_url': created_folders[0]['webViewLink'] if created_folders else None,
            'created_folders': created_folders,
            'summary': {
                'total': len(created_folders),
                'new': new_count,
                'existing': existing_count
            }
        }

        # Save result to .tmp
        output_dir = Path('.tmp/gdrive_structure')
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / 'last_result.json'
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n📋 Result saved to: {output_file}")

        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
