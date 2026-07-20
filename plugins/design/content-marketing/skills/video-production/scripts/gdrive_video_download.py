#!/usr/bin/env python3
"""
Google Drive Video Downloader
Downloads video files from a Google Drive folder.

Directive: directives/video_course_stitcher.md

Usage:
    python execution/gdrive_video_download.py --folder-url "https://drive.google.com/drive/folders/FOLDER_ID"
    python execution/gdrive_video_download.py --folder-id "1D9EeN1IAVDbSthdj9ME7ol64qE8It86l" --output-dir .tmp/videos
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# Configuration
SETTINGS_FILE = "settings.yaml"
CREDENTIALS_FILE = "mycreds.txt"
CLIENT_SECRETS_FILE = "client_secrets.json"
DEFAULT_OUTPUT_DIR = Path(".tmp/video_downloads")

# Supported video formats
VIDEO_MIMETYPES = [
    'video/mp4',
    'video/quicktime',  # .mov
    'video/x-matroska',  # .mkv
    'video/x-msvideo',  # .avi
    'video/webm',
]


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
    """Authenticate with Google Drive using OAuth 2.0."""
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


def extract_folder_id(folder_url: str) -> str:
    """
    Extract folder ID from various Google Drive URL formats.

    Supports:
    - https://drive.google.com/drive/folders/FOLDER_ID
    - https://drive.google.com/drive/u/0/folders/FOLDER_ID
    - https://drive.google.com/drive/u/1/folders/FOLDER_ID
    - Just the folder ID itself
    """
    # If it's just an ID (no slashes), return as-is
    if '/' not in folder_url:
        return folder_url

    # Try to extract from URL
    patterns = [
        r'/folders/([a-zA-Z0-9_-]+)',
        r'id=([a-zA-Z0-9_-]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, folder_url)
        if match:
            return match.group(1)

    raise ValueError(f"Could not extract folder ID from URL: {folder_url}")


def list_videos_in_folder(drive: GoogleDrive, folder_id: str) -> List[Dict]:
    """
    List all video files in a Google Drive folder.

    Returns list of dicts with: id, title, mimeType, fileSize
    """
    print(f"📂 Listing videos in folder: {folder_id}")

    # Build query for video files
    mime_conditions = " or ".join([f"mimeType='{mt}'" for mt in VIDEO_MIMETYPES])
    query = f"'{folder_id}' in parents and ({mime_conditions}) and trashed=false"

    try:
        file_list = drive.ListFile({
            'q': query,
            'supportsAllDrives': True,
            'includeItemsFromAllDrives': True,
        }).GetList()
    except Exception as e:
        # Try without shared drive support (for personal drives)
        file_list = drive.ListFile({'q': query}).GetList()

    # Sort by title (natural sort for episode numbers)
    def natural_sort_key(item):
        title = item['title']
        # Extract episode number if present (e.g., [e1], [e2], etc.)
        match = re.search(r'\[e(\d+)\]', title.lower())
        if match:
            return (0, int(match.group(1)), title)
        # Also try other patterns like "Episode 1", "Ep1", "1.", "01 -"
        match = re.search(r'(?:episode\s*|ep\s*)?(\d+)[\.\s\-]', title.lower())
        if match:
            return (0, int(match.group(1)), title)
        # No episode number, sort alphabetically at the end
        return (1, 0, title)

    file_list.sort(key=natural_sort_key)

    videos = []
    for f in file_list:
        videos.append({
            'id': f['id'],
            'title': f['title'],
            'mimeType': f['mimeType'],
            'fileSize': int(f.get('fileSize', 0)),
        })

    print(f"   Found {len(videos)} video files")
    for i, v in enumerate(videos, 1):
        size_mb = v['fileSize'] / (1024 * 1024)
        print(f"   {i}. {v['title']} ({size_mb:.1f} MB)")

    return videos


def download_video(drive: GoogleDrive, file_id: str, title: str, output_dir: Path) -> Path:
    """
    Download a single video file from Google Drive.

    Returns the local file path.
    """
    # Clean filename (remove problematic characters)
    safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
    output_path = output_dir / safe_title

    print(f"📥 Downloading: {title}")

    try:
        file = drive.CreateFile({'id': file_id})
        file.GetContentFile(str(output_path))

        # Verify download
        if output_path.exists() and output_path.stat().st_size > 0:
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"   ✅ Downloaded: {output_path.name} ({size_mb:.1f} MB)")
            return output_path
        else:
            raise Exception("Downloaded file is empty or missing")

    except Exception as e:
        print(f"   ❌ Download failed: {str(e)}")
        raise


def download_all_videos(
    folder_url: str,
    output_dir: Optional[Path] = None
) -> Tuple[List[Path], List[Dict]]:
    """
    Download all videos from a Google Drive folder.

    Args:
        folder_url: Google Drive folder URL or ID
        output_dir: Local directory for downloads

    Returns:
        Tuple of (list of local file paths, list of video metadata)
    """
    validate_setup()
    drive = authenticate()

    folder_id = extract_folder_id(folder_url)
    print(f"📁 Folder ID: {folder_id}")

    # Set up output directory
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = DEFAULT_OUTPUT_DIR / timestamp
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📂 Output directory: {output_dir}")

    # List videos
    videos = list_videos_in_folder(drive, folder_id)

    if not videos:
        print("⚠️  No video files found in folder")
        return [], []

    # Calculate total size
    total_size_mb = sum(v['fileSize'] for v in videos) / (1024 * 1024)
    print(f"\n📊 Total download size: {total_size_mb:.1f} MB")

    # Download all videos
    print(f"\n🚀 Starting download of {len(videos)} videos...")
    downloaded_paths = []

    for i, video in enumerate(videos, 1):
        print(f"\n[{i}/{len(videos)}] ", end="")
        try:
            path = download_video(drive, video['id'], video['title'], output_dir)
            downloaded_paths.append(path)
            video['local_path'] = str(path)
        except Exception as e:
            print(f"   ⚠️  Skipping {video['title']} due to error: {e}")

    # Save metadata
    metadata_path = output_dir / "video_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump({
            'folder_id': folder_id,
            'download_time': datetime.now().isoformat(),
            'videos': videos,
        }, f, indent=2)
    print(f"\n📝 Metadata saved to: {metadata_path}")

    print(f"\n✅ Download complete: {len(downloaded_paths)}/{len(videos)} videos")

    return downloaded_paths, videos


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Download videos from a Google Drive folder",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--folder-url",
        help="Google Drive folder URL"
    )
    parser.add_argument(
        "--folder-id",
        help="Google Drive folder ID (alternative to --folder-url)"
    )
    parser.add_argument(
        "--output-dir",
        help="Local directory for downloads"
    )
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Only list videos, don't download"
    )

    args = parser.parse_args()

    # Get folder URL/ID
    folder_url = args.folder_url or args.folder_id
    if not folder_url:
        print("❌ Please provide --folder-url or --folder-id")
        return 1

    try:
        if args.list_only:
            validate_setup()
            drive = authenticate()
            folder_id = extract_folder_id(folder_url)
            list_videos_in_folder(drive, folder_id)
        else:
            output_dir = Path(args.output_dir) if args.output_dir else None
            download_all_videos(folder_url, output_dir)

        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
