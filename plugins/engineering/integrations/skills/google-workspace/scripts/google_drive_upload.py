#!/usr/bin/env python3
"""
Google Drive File Upload with OAuth
Supports folder management, batch uploads, and sharing.

Usage:
    # First time (opens browser for OAuth)
    python execution/google_drive_upload.py --file image.png --folder "Clients/Acme/Images"

    # Subsequent runs (uses saved credentials)
    python execution/google_drive_upload.py --files *.png --folder "Test" --share anyone

    # Create folder structure
    python execution/google_drive_upload.py --create-folder "Clients/NewClient/Assets/2025"

    # Upload with custom name
    python execution/google_drive_upload.py --file image.png --folder "Test" --name "custom_name.png"
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
import glob
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

    # Try to load saved credentials
    gauth.LoadCredentialsFile(CREDENTIALS_FILE)

    if gauth.credentials is None:
        # First time: open browser for OAuth
        print("   First time setup - opening browser for authentication...")
        print("   Please log in and authorize the application.")
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Refresh expired token
        print("   Refreshing expired credentials...")
        gauth.Refresh()
    else:
        # Use saved credentials
        print("   Using saved credentials...")
        gauth.Authorize()

    # Save credentials for next run
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
        # Search for folder in current parent
        query = f"'{current_id}' in parents and title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        file_list = drive.ListFile({'q': query}).GetList()

        if file_list:
            current_id = file_list[0]['id']
        else:
            return None  # Folder not found

    return current_id

def create_folder_structure(drive, folder_path, parent_id='root'):
    """
    Create nested folder structure, creating missing folders.

    Args:
        drive: GoogleDrive instance
        folder_path: Path like "Clients/Acme/Images"
        parent_id: Parent folder ID

    Returns:
        str: ID of the final folder
    """
    if not folder_path:
        return parent_id

    parts = folder_path.split('/')
    current_id = parent_id

    print(f"📁 Creating folder structure: {folder_path}")

    for folder_name in parts:
        # Check if folder exists
        query = f"'{current_id}' in parents and title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        file_list = drive.ListFile({'q': query}).GetList()

        if file_list:
            # Folder exists
            current_id = file_list[0]['id']
            print(f"   ✓ {folder_name} (exists)")
        else:
            # Create folder
            folder = drive.CreateFile({
                'title': folder_name,
                'parents': [{'id': current_id}],
                'mimeType': 'application/vnd.google-apps.folder'
            })
            folder.Upload()
            current_id = folder['id']
            print(f"   ✅ {folder_name} (created)")

    return current_id

def upload_file(drive, file_path, folder_id, custom_name=None, share=None):
    """
    Upload file to Google Drive.

    Args:
        drive: GoogleDrive instance
        file_path: Local file path
        folder_id: Destination folder ID
        custom_name: Optional custom file name
        share: Sharing option ('anyone', 'email@example.com', or None)

    Returns:
        dict: File metadata (id, name, webViewLink)
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    file_name = custom_name or file_path.name

    print(f"📤 Uploading: {file_name}")

    # Create file
    file = drive.CreateFile({
        'title': file_name,
        'parents': [{'id': folder_id}]
    })

    # Upload content
    file.SetContentFile(str(file_path))
    file.Upload()

    # Handle sharing
    if share:
        if share == 'anyone':
            file.InsertPermission({
                'type': 'anyone',
                'value': 'anyone',
                'role': 'reader'
            })
            print(f"   🔗 Shared with anyone (read-only)")
        else:
            # Assume it's an email
            file.InsertPermission({
                'type': 'user',
                'value': share,
                'role': 'writer'
            })
            print(f"   🔗 Shared with {share}")

    result = {
        'id': file['id'],
        'name': file['title'],
        'webViewLink': file['alternateLink'],
        'size': file.get('fileSize', 'unknown')
    }

    print(f"   ✅ Uploaded: {result['webViewLink']}")

    return result

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Upload files to Google Drive with folder management",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # File arguments
    parser.add_argument("--file", help="Single file to upload")
    parser.add_argument("--files", nargs="+", help="Multiple files to upload")
    parser.add_argument("--name", help="Custom name for uploaded file (single file only)")

    # Folder arguments
    parser.add_argument("--folder", default="", help="Destination folder path (e.g., 'Clients/Acme/Images')")
    parser.add_argument("--create-folder", help="Just create folder structure (no upload)")
    parser.add_argument("--parent-id", default="root", help="Parent folder ID (default: My Drive root)")

    # Sharing arguments
    parser.add_argument("--share", help="Share with 'anyone' or specific email")

    # Options
    parser.add_argument("--no-auto-create", action="store_true", help="Don't auto-create folders")

    args = parser.parse_args()

    try:
        # Validate setup
        validate_setup()

        # Authenticate
        drive = authenticate()

        # Handle folder creation only
        if args.create_folder:
            print(f"\n📁 Creating folder: {args.create_folder}")
            folder_id = create_folder_structure(drive, args.create_folder, args.parent_id)
            print(f"\n✅ Folder created with ID: {folder_id}")
            return 0

        # Get file list
        files_to_upload = []
        if args.file:
            files_to_upload.append(args.file)
        if args.files:
            for pattern in args.files:
                files_to_upload.extend(glob.glob(pattern))

        if not files_to_upload:
            print("❌ No files specified. Use --file or --files")
            return 1

        print(f"\n📋 Files to upload: {len(files_to_upload)}")

        # Get or create destination folder
        if args.folder:
            folder_id = find_folder_by_path(drive, args.folder, args.parent_id)

            if folder_id is None:
                if args.no_auto_create:
                    print(f"❌ Folder not found: {args.folder}")
                    return 1
                else:
                    folder_id = create_folder_structure(drive, args.folder, args.parent_id)
            else:
                print(f"✓ Found folder: {args.folder}")
        else:
            folder_id = args.parent_id

        # Upload files
        print(f"\n📤 Uploading to folder ID: {folder_id}")
        results = []

        for file_path in files_to_upload:
            try:
                custom_name = args.name if (args.file and len(files_to_upload) == 1) else None
                result = upload_file(drive, file_path, folder_id, custom_name, args.share)
                results.append(result)
            except Exception as e:
                print(f"   ❌ Failed to upload {file_path}: {str(e)}")

        # Summary
        print(f"\n✅ Upload complete!")
        print(f"   Successfully uploaded: {len(results)}/{len(files_to_upload)} files")

        if results:
            print(f"\n📋 Uploaded files:")
            for result in results:
                print(f"   • {result['name']}: {result['webViewLink']}")

        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
