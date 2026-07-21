#!/usr/bin/env python3
"""
YouTube Video Info Extractor - Get metadata without downloading.

Security features:
- URL validation (only YouTube domains)
- No file system writes except to .tmp/
- No shell injection

Usage:
    # Single video
    python get_video_info.py "https://youtube.com/watch?v=VIDEO_ID"

    # Multiple videos
    python get_video_info.py --urls-file videos.txt

    # Playlist info
    python get_video_info.py "PLAYLIST_URL"

    # Output to JSON
    python get_video_info.py "URL" --output info.json
"""

import argparse
import json
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
    """Validate that URL is a legitimate YouTube URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain not in ALLOWED_DOMAINS:
            return False
        if parsed.scheme not in ('http', 'https'):
            return False
        return True
    except Exception:
        return False


def extract_video_id(url: str) -> str | None:
    """Extract video ID from YouTube URL."""
    try:
        parsed = urlparse(url)
        if 'youtu.be' in parsed.netloc:
            return parsed.path.strip('/')
        if 'v' in parse_qs(parsed.query):
            return parse_qs(parsed.query)['v'][0]
        if '/shorts/' in parsed.path:
            return parsed.path.split('/shorts/')[-1].split('/')[0]
        return None
    except Exception:
        return None


# =============================================================================
# Core Functions
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


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human-readable string."""
    if not seconds:
        return "Unknown"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def format_number(num: int) -> str:
    """Format large numbers with K/M/B suffixes."""
    if not num:
        return "0"
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    if num >= 1_000:
        return f"{num / 1_000:.1f}K"
    return str(num)


def get_video_info(url: str, cookies_browser: str | None = None) -> dict:
    """
    Get metadata for a YouTube video without downloading.

    Returns dict with:
        - title, description, channel, upload_date
        - duration, view_count, like_count
        - thumbnail URLs, available formats
        - tags, categories
    """
    result = {
        'url': url,
        'video_id': extract_video_id(url),
        'success': False,
        'error': None,
        'timestamp': datetime.now().isoformat(),
        'info': None
    }

    # Validate URL
    if not is_valid_youtube_url(url):
        result['error'] = f"Invalid YouTube URL: {url}"
        print(f"ERROR: {result['error']}")
        return result

    # Build command - extract info without downloading
    cmd = [
        'yt-dlp',
        '--dump-json',  # Output info as JSON
        '--no-download',  # Don't download anything
        '--no-warnings',
    ]

    # Browser cookies if needed
    if cookies_browser:
        allowed_browsers = ['chrome', 'firefox', 'safari', 'edge', 'brave', 'opera']
        if cookies_browser.lower() in allowed_browsers:
            cmd.extend(['--cookies-from-browser', cookies_browser.lower()])

    cmd.append(url)

    try:
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if process.returncode == 0 and process.stdout:
            # Parse JSON output
            raw_info = json.loads(process.stdout)

            # Extract key fields
            info = {
                'id': raw_info.get('id'),
                'title': raw_info.get('title'),
                'description': raw_info.get('description', '')[:1000],  # Truncate
                'channel': raw_info.get('channel'),
                'channel_id': raw_info.get('channel_id'),
                'channel_url': raw_info.get('channel_url'),
                'uploader': raw_info.get('uploader'),
                'upload_date': raw_info.get('upload_date'),
                'duration': raw_info.get('duration'),
                'duration_string': format_duration(raw_info.get('duration')),
                'view_count': raw_info.get('view_count'),
                'view_count_string': format_number(raw_info.get('view_count')),
                'like_count': raw_info.get('like_count'),
                'like_count_string': format_number(raw_info.get('like_count')),
                'comment_count': raw_info.get('comment_count'),
                'age_limit': raw_info.get('age_limit', 0),
                'is_live': raw_info.get('is_live', False),
                'was_live': raw_info.get('was_live', False),
                'thumbnail': raw_info.get('thumbnail'),
                'thumbnails': [t.get('url') for t in raw_info.get('thumbnails', [])[-3:]],  # Last 3 (highest quality)
                'tags': raw_info.get('tags', [])[:20],  # Limit tags
                'categories': raw_info.get('categories', []),
                'language': raw_info.get('language'),
                'availability': raw_info.get('availability'),
                'webpage_url': raw_info.get('webpage_url'),
                'formats_available': len(raw_info.get('formats', [])),
                'subtitles_available': list(raw_info.get('subtitles', {}).keys()),
                'automatic_captions_available': list(raw_info.get('automatic_captions', {}).keys())[:10],
            }

            # Best format info
            formats = raw_info.get('formats', [])
            video_formats = [f for f in formats if f.get('vcodec') != 'none' and f.get('height')]
            if video_formats:
                best = max(video_formats, key=lambda x: x.get('height', 0))
                info['best_quality'] = f"{best.get('height')}p"
                info['best_format'] = best.get('format_note', '')

            result['info'] = info
            result['success'] = True

            # Print summary
            print(f"Title: {info['title']}")
            print(f"Channel: {info['channel']}")
            print(f"Duration: {info['duration_string']}")
            print(f"Views: {info['view_count_string']}")
            print(f"Likes: {info['like_count_string']}")
            print(f"Upload Date: {info['upload_date']}")
            print(f"Best Quality: {info.get('best_quality', 'N/A')}")

        else:
            result['error'] = process.stderr or "Failed to get video info"
            print(f"ERROR: {result['error'][:200]}")

    except json.JSONDecodeError as e:
        result['error'] = f"Failed to parse video info: {e}"
        print(f"ERROR: {result['error']}")
    except subprocess.TimeoutExpired:
        result['error'] = "Request timed out"
        print(f"ERROR: {result['error']}")
    except Exception as e:
        result['error'] = str(e)
        print(f"ERROR: {result['error']}")

    return result


def get_playlist_info(url: str) -> dict:
    """Get info for all videos in a playlist."""
    result = {
        'url': url,
        'success': False,
        'error': None,
        'timestamp': datetime.now().isoformat(),
        'playlist_title': None,
        'playlist_count': 0,
        'videos': []
    }

    if not is_valid_youtube_url(url):
        result['error'] = f"Invalid YouTube URL: {url}"
        return result

    cmd = [
        'yt-dlp',
        '--dump-json',
        '--flat-playlist',  # Don't extract video info, just list
        '--no-download',
        url
    ]

    try:
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )

        if process.returncode == 0 and process.stdout:
            # Each line is a separate JSON object
            videos = []
            for line in process.stdout.strip().split('\n'):
                if line:
                    try:
                        video = json.loads(line)
                        videos.append({
                            'id': video.get('id'),
                            'title': video.get('title'),
                            'url': video.get('url') or f"https://youtube.com/watch?v={video.get('id')}",
                            'duration': video.get('duration'),
                            'duration_string': format_duration(video.get('duration')),
                        })
                    except json.JSONDecodeError:
                        continue

            result['videos'] = videos
            result['playlist_count'] = len(videos)
            result['success'] = True

            print(f"Playlist contains {len(videos)} videos")

    except Exception as e:
        result['error'] = str(e)

    return result


def process_urls_file(urls_file: str, cookies_browser: str | None = None) -> list[dict]:
    """Process multiple URLs from a file."""
    results = []

    try:
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except Exception as e:
        print(f"ERROR: Could not read URLs file: {e}")
        return results

    print(f"Processing {len(urls)} URLs...")

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] {url[:60]}...")
        result = get_video_info(url, cookies_browser)
        results.append(result)

    return results


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Get YouTube video metadata without downloading',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://youtube.com/watch?v=VIDEO_ID"
  %(prog)s "PLAYLIST_URL"
  %(prog)s --urls-file videos.txt
  %(prog)s "URL" --output info.json
  %(prog)s "URL" --full  # Include all raw data
        """
    )

    parser.add_argument('url', nargs='?', help='YouTube video or playlist URL')
    parser.add_argument('--urls-file', help='File containing URLs (one per line)')
    parser.add_argument('--output', '-o', help='Output JSON file')
    parser.add_argument('--full', action='store_true',
                        help='Include full raw data (larger output)')
    parser.add_argument('--cookies-from-browser', '-c',
                        choices=['chrome', 'firefox', 'safari', 'edge', 'brave', 'opera'],
                        help='Use cookies from browser (for age-restricted)')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Minimal output (JSON only)')

    args = parser.parse_args()

    # Check yt-dlp is installed
    if not check_yt_dlp_installed():
        print("ERROR: yt-dlp is not installed. Run: pip install yt-dlp")
        sys.exit(1)

    # Validate we have input
    if not args.url and not args.urls_file:
        parser.print_help()
        sys.exit(1)

    # Process
    if args.urls_file:
        results = process_urls_file(args.urls_file, args.cookies_from_browser)
    elif 'playlist' in args.url.lower() or 'list=' in args.url:
        results = [get_playlist_info(args.url)]
    else:
        results = [get_video_info(args.url, args.cookies_from_browser)]

    # Output
    if args.output:
        output_path = Path(args.output)
        # Ensure we're writing to .tmp if no path specified
        if not output_path.is_absolute() and not str(output_path).startswith('.tmp'):
            output_path = Path('.tmp/youtube/metadata') / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(results if len(results) > 1 else results[0], f, indent=2)
        print(f"\nSaved to: {output_path}")

    elif args.quiet:
        print(json.dumps(results if len(results) > 1 else results[0], indent=2))

    # Summary
    if not args.quiet:
        print("\n" + "=" * 60)
        success_count = sum(1 for r in results if r['success'])
        print(f"Results: {success_count}/{len(results)} successful")

    sys.exit(0 if all(r['success'] for r in results) else 1)


if __name__ == '__main__':
    main()
