#!/usr/bin/env python3
"""
YouTube Video Downloader - Safe, free video downloading using yt-dlp.

Security features:
- URL validation (only YouTube domains)
- Filename sanitization
- Output directory restriction (.tmp/ only by default)
- No shell injection (subprocess with list args)
- No credential storage

Usage:
    # Single video
    python download_video.py "https://youtube.com/watch?v=VIDEO_ID"

    # With quality
    python download_video.py "URL" --quality 720p

    # Audio only
    python download_video.py "URL" --audio-only

    # Playlist
    python download_video.py "PLAYLIST_URL"

    # Bulk from file
    python download_video.py --urls-file urls.txt

    # Age-restricted (requires browser cookies)
    python download_video.py "URL" --cookies-from-browser chrome
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs


# =============================================================================
# SECURITY: URL Validation
# =============================================================================

ALLOWED_DOMAINS = [
    'youtube.com',
    'www.youtube.com',
    'm.youtube.com',
    'youtu.be',
    'www.youtu.be',
    'youtube-nocookie.com',
    'www.youtube-nocookie.com',
]


def is_valid_youtube_url(url: str) -> bool:
    """
    Validate that URL is a legitimate YouTube URL.

    Security: Prevents arbitrary URL downloads and potential SSRF attacks.
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Check domain whitelist
        if domain not in ALLOWED_DOMAINS:
            return False

        # Must be http or https
        if parsed.scheme not in ('http', 'https'):
            return False

        return True
    except Exception:
        return False


def extract_video_id(url: str) -> str | None:
    """Extract video ID from YouTube URL for logging (not for security)."""
    try:
        parsed = urlparse(url)

        # youtu.be/VIDEO_ID
        if 'youtu.be' in parsed.netloc:
            return parsed.path.strip('/')

        # youtube.com/watch?v=VIDEO_ID
        if 'v' in parse_qs(parsed.query):
            return parse_qs(parsed.query)['v'][0]

        # youtube.com/shorts/VIDEO_ID
        if '/shorts/' in parsed.path:
            return parsed.path.split('/shorts/')[-1].split('/')[0]

        return None
    except Exception:
        return None


# =============================================================================
# SECURITY: Filename Sanitization
# =============================================================================

def sanitize_filename(filename: str) -> str:
    """
    Remove dangerous characters from filename.

    Security: Prevents path traversal and command injection via filenames.
    """
    # Remove path separators and null bytes
    dangerous_chars = ['/', '\\', '\x00', '..', ':', '*', '?', '"', '<', '>', '|']

    result = filename
    for char in dangerous_chars:
        result = result.replace(char, '_')

    # Limit length
    if len(result) > 200:
        result = result[:200]

    # Remove leading/trailing dots and spaces
    result = result.strip('. ')

    return result if result else 'video'


# =============================================================================
# SECURITY: Output Directory Validation
# =============================================================================

def validate_output_dir(output_dir: str, base_allowed: str = '.tmp') -> Path:
    """
    Ensure output directory is within allowed path.

    Security: Prevents writing to arbitrary filesystem locations.
    """
    output_path = Path(output_dir).resolve()

    # Default to .tmp/youtube if not specified
    if not output_dir:
        output_path = Path('.tmp/youtube/videos').resolve()

    # Ensure .tmp directory exists
    base_path = Path(base_allowed).resolve()

    # Allow .tmp and subdirectories, or explicit user override with warning
    if not str(output_path).startswith(str(base_path)):
        print(f"WARNING: Output directory '{output_path}' is outside .tmp/")
        print("For safety, files will be saved to .tmp/youtube/videos/")
        output_path = Path('.tmp/youtube/videos').resolve()

    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


# =============================================================================
# Core Download Functions
# =============================================================================

def check_yt_dlp_installed() -> bool:
    """Check if yt-dlp is installed."""
    try:
        result = subprocess.run(
            ['yt-dlp', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def build_download_command(
    url: str,
    output_dir: Path,
    quality: str | None = None,
    audio_only: bool = False,
    cookies_browser: str | None = None,
    extra_args: list[str] | None = None
) -> list[str]:
    """
    Build yt-dlp command with safe arguments.

    Security: Uses list-based arguments to prevent shell injection.
    """
    cmd = ['yt-dlp']

    # Output template with sanitized filename
    output_template = str(output_dir / '%(title)s.%(ext)s')
    cmd.extend(['-o', output_template])

    # Restrict filename characters
    cmd.append('--restrict-filenames')

    # Progress output
    cmd.append('--progress')

    # Quality selection
    if audio_only:
        cmd.extend([
            '-x',  # Extract audio
            '--audio-format', 'mp3',
            '--audio-quality', '0',  # Best quality
        ])
    elif quality:
        quality_map = {
            '2160p': 'bestvideo[height<=2160]+bestaudio/best[height<=2160]',
            '1440p': 'bestvideo[height<=1440]+bestaudio/best[height<=1440]',
            '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            '360p': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
            'best': 'bestvideo+bestaudio/best',
            'worst': 'worstvideo+worstaudio/worst',
        }
        format_str = quality_map.get(quality.lower(), quality_map['best'])
        cmd.extend(['-f', format_str])
    else:
        # Default: best quality that merges
        cmd.extend(['-f', 'bestvideo+bestaudio/best'])

    # Merge format (requires ffmpeg)
    cmd.extend(['--merge-output-format', 'mp4'])

    # Browser cookies for age-restricted content
    if cookies_browser:
        allowed_browsers = ['chrome', 'firefox', 'safari', 'edge', 'brave', 'opera']
        if cookies_browser.lower() in allowed_browsers:
            cmd.extend(['--cookies-from-browser', cookies_browser.lower()])
        else:
            print(f"WARNING: Unknown browser '{cookies_browser}', skipping cookies")

    # No playlist by default for single URLs (safety)
    if 'playlist' not in url.lower() and 'list=' not in url.lower():
        cmd.append('--no-playlist')

    # Extra arguments (validated)
    if extra_args:
        safe_args = validate_extra_args(extra_args)
        cmd.extend(safe_args)

    # Add URL last
    cmd.append(url)

    return cmd


def validate_extra_args(args: list[str]) -> list[str]:
    """
    Validate extra arguments for safety.

    Security: Whitelist of allowed yt-dlp arguments.
    """
    # Whitelist of safe arguments
    safe_prefixes = [
        '--sleep-interval', '--max-sleep-interval',
        '--concurrent-fragments', '--retries',
        '--fragment-retries', '--skip-unavailable-fragments',
        '--keep-video', '--no-keep-video',
        '--embed-thumbnail', '--embed-metadata',
        '--write-info-json', '--write-description',
        '--write-thumbnail', '--write-comments',
        '--live-from-start', '--wait-for-video',
        '--match-title', '--reject-title',
        '--min-views', '--max-views',
        '--match-filter', '--no-match-filter',
        '--age-limit', '--download-archive',
        '--max-downloads', '--playlist-start',
        '--playlist-end', '--playlist-items',
        '--quiet', '--verbose', '--simulate',
    ]

    # Dangerous arguments to block
    blocked_args = [
        '--exec', '--exec-before-download',  # Command execution
        '--config-location',  # Config file injection
        '--cookies',  # Direct cookie file (use --cookies-from-browser)
        '--batch-file',  # We handle this ourselves
        '-a',  # Alias for batch-file
    ]

    safe = []
    i = 0
    while i < len(args):
        arg = args[i]

        # Check if blocked
        if any(arg.startswith(blocked) for blocked in blocked_args):
            print(f"WARNING: Blocked unsafe argument: {arg}")
            i += 1
            continue

        # Check if allowed
        if any(arg.startswith(prefix) for prefix in safe_prefixes):
            safe.append(arg)
            # If it's a flag that takes a value
            if '=' not in arg and i + 1 < len(args) and not args[i + 1].startswith('-'):
                safe.append(args[i + 1])
                i += 1

        i += 1

    return safe


def download_video(
    url: str,
    output_dir: Path,
    quality: str | None = None,
    audio_only: bool = False,
    cookies_browser: str | None = None,
    extra_args: list[str] | None = None,
    verbose: bool = False
) -> dict:
    """Download a single video and return result info."""

    result = {
        'url': url,
        'video_id': extract_video_id(url),
        'success': False,
        'output_dir': str(output_dir),
        'error': None,
        'timestamp': datetime.now().isoformat(),
    }

    # Validate URL
    if not is_valid_youtube_url(url):
        result['error'] = f"Invalid YouTube URL: {url}"
        print(f"ERROR: {result['error']}")
        return result

    # Build command
    cmd = build_download_command(
        url=url,
        output_dir=output_dir,
        quality=quality,
        audio_only=audio_only,
        cookies_browser=cookies_browser,
        extra_args=extra_args
    )

    if verbose:
        print(f"Command: {' '.join(cmd)}")

    try:
        # Run download
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )

        if process.returncode == 0:
            result['success'] = True
            result['stdout'] = process.stdout
            print(f"SUCCESS: Downloaded {url}")
        else:
            result['error'] = process.stderr or "Download failed"
            print(f"ERROR: {result['error'][:200]}")

    except subprocess.TimeoutExpired:
        result['error'] = "Download timed out (1 hour limit)"
        print(f"ERROR: {result['error']}")
    except Exception as e:
        result['error'] = str(e)
        print(f"ERROR: {result['error']}")

    return result


def download_from_file(
    urls_file: str,
    output_dir: Path,
    quality: str | None = None,
    audio_only: bool = False,
    cookies_browser: str | None = None,
    sleep_interval: int = 5
) -> list[dict]:
    """Download multiple videos from a file of URLs."""

    results = []

    # Read and validate URLs file
    try:
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except Exception as e:
        print(f"ERROR: Could not read URLs file: {e}")
        return results

    print(f"Found {len(urls)} URLs to download")

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url[:80]}...")

        result = download_video(
            url=url,
            output_dir=output_dir,
            quality=quality,
            audio_only=audio_only,
            cookies_browser=cookies_browser,
            extra_args=[f'--sleep-interval={sleep_interval}'] if sleep_interval > 0 else None
        )
        results.append(result)

    return results


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Safe YouTube video downloader using yt-dlp',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://youtube.com/watch?v=VIDEO_ID"
  %(prog)s "URL" --quality 720p
  %(prog)s "URL" --audio-only
  %(prog)s "PLAYLIST_URL" --output-dir ./videos
  %(prog)s --urls-file urls.txt
  %(prog)s "URL" --cookies-from-browser chrome  # For age-restricted
        """
    )

    parser.add_argument('url', nargs='?', help='YouTube video or playlist URL')
    parser.add_argument('--urls-file', help='File containing URLs (one per line)')
    parser.add_argument('--output-dir', '-o', default='.tmp/youtube/videos',
                        help='Output directory (default: .tmp/youtube/videos)')
    parser.add_argument('--quality', '-q',
                        choices=['2160p', '1440p', '1080p', '720p', '480p', '360p', 'best', 'worst'],
                        help='Video quality (default: best)')
    parser.add_argument('--audio-only', '-a', action='store_true',
                        help='Extract audio only (MP3)')
    parser.add_argument('--cookies-from-browser', '-c',
                        choices=['chrome', 'firefox', 'safari', 'edge', 'brave', 'opera'],
                        help='Use cookies from browser (for age-restricted content)')
    parser.add_argument('--sleep-interval', type=int, default=5,
                        help='Seconds to sleep between downloads in bulk mode (default: 5)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show verbose output')
    parser.add_argument('--output-json', help='Save results to JSON file')

    args = parser.parse_args()

    # Check yt-dlp is installed
    if not check_yt_dlp_installed():
        print("ERROR: yt-dlp is not installed. Run: pip install yt-dlp")
        sys.exit(1)

    # Validate we have input
    if not args.url and not args.urls_file:
        parser.print_help()
        sys.exit(1)

    # Validate and create output directory
    output_dir = validate_output_dir(args.output_dir)

    # Adjust for audio-only
    if args.audio_only:
        output_dir = output_dir.parent / 'audio'
        output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Output directory: {output_dir}")
    print("=" * 60)

    # Download
    if args.urls_file:
        results = download_from_file(
            urls_file=args.urls_file,
            output_dir=output_dir,
            quality=args.quality,
            audio_only=args.audio_only,
            cookies_browser=args.cookies_from_browser,
            sleep_interval=args.sleep_interval
        )
    else:
        results = [download_video(
            url=args.url,
            output_dir=output_dir,
            quality=args.quality,
            audio_only=args.audio_only,
            cookies_browser=args.cookies_from_browser,
            verbose=args.verbose
        )]

    # Summary
    print("\n" + "=" * 60)
    success_count = sum(1 for r in results if r['success'])
    print(f"Results: {success_count}/{len(results)} successful")

    # Save results to JSON if requested
    if args.output_json:
        with open(args.output_json, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to: {args.output_json}")

    # Return appropriate exit code
    sys.exit(0 if success_count == len(results) else 1)


if __name__ == '__main__':
    main()
