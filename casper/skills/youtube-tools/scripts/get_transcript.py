#!/usr/bin/env python3
"""
YouTube Transcript Extractor - Safe subtitle/caption extraction using yt-dlp.

Security features:
- URL validation (only YouTube domains)
- Output directory restriction (.tmp/ only by default)
- No shell injection (subprocess with list args)

Usage:
    # Get auto-generated captions
    python get_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

    # Get specific language
    python get_transcript.py "URL" --lang es

    # Get manual subtitles only (higher quality)
    python get_transcript.py "URL" --manual-only

    # List available subtitles
    python get_transcript.py "URL" --list-subs

    # Bulk extraction
    python get_transcript.py --urls-file videos.txt
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
# SECURITY: URL Validation (same as download_video.py)
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


def validate_output_dir(output_dir: str, base_allowed: str = '.tmp') -> Path:
    """Ensure output directory is within allowed path."""
    output_path = Path(output_dir).resolve()
    if not output_dir:
        output_path = Path('.tmp/youtube/transcripts').resolve()
    base_path = Path(base_allowed).resolve()
    if not str(output_path).startswith(str(base_path)):
        print(f"WARNING: Output directory '{output_path}' is outside .tmp/")
        output_path = Path('.tmp/youtube/transcripts').resolve()
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def sanitize_filename(filename: str) -> str:
    """Remove dangerous characters from filename."""
    dangerous_chars = ['/', '\\', '\x00', '..', ':', '*', '?', '"', '<', '>', '|']
    result = filename
    for char in dangerous_chars:
        result = result.replace(char, '_')
    if len(result) > 200:
        result = result[:200]
    result = result.strip('. ')
    return result if result else 'transcript'


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


def list_available_subtitles(url: str) -> dict | None:
    """List available subtitles for a video."""
    if not is_valid_youtube_url(url):
        print(f"ERROR: Invalid YouTube URL: {url}")
        return None

    cmd = ['yt-dlp', '--list-subs', '--skip-download', url]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return {
            'url': url,
            'video_id': extract_video_id(url),
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        }
    except Exception as e:
        return {'url': url, 'error': str(e)}


def get_transcript(
    url: str,
    output_dir: Path,
    lang: str = 'en',
    manual_only: bool = False,
    auto_only: bool = False,
    all_langs: bool = False,
    format: str = 'vtt',
    cookies_browser: str | None = None
) -> dict:
    """
    Extract transcript/subtitles from a YouTube video.

    Args:
        url: YouTube video URL
        output_dir: Where to save the transcript
        lang: Language code (default: en)
        manual_only: Only get manually uploaded subtitles
        auto_only: Only get auto-generated captions
        all_langs: Download all available languages
        format: Output format (vtt, srt, ass, json3)
        cookies_browser: Browser to get cookies from (for age-restricted)

    Returns:
        dict with success status and file info
    """
    result = {
        'url': url,
        'video_id': extract_video_id(url),
        'success': False,
        'output_dir': str(output_dir),
        'files': [],
        'error': None,
        'timestamp': datetime.now().isoformat(),
    }

    # Validate URL
    if not is_valid_youtube_url(url):
        result['error'] = f"Invalid YouTube URL: {url}"
        print(f"ERROR: {result['error']}")
        return result

    # Build command
    cmd = ['yt-dlp', '--skip-download']  # Don't download video

    # Output template
    output_template = str(output_dir / '%(title)s.%(ext)s')
    cmd.extend(['-o', output_template])
    cmd.append('--restrict-filenames')

    # Subtitle selection
    if all_langs:
        cmd.append('--all-subs')
    else:
        if manual_only:
            cmd.extend(['--sub-langs', lang])
            cmd.append('--write-subs')
        elif auto_only:
            cmd.extend(['--sub-langs', lang])
            cmd.append('--write-auto-subs')
        else:
            # Try manual first, fall back to auto
            cmd.extend(['--sub-langs', lang])
            cmd.append('--write-subs')
            cmd.append('--write-auto-subs')

    # Convert to specified format
    if format != 'vtt':
        cmd.extend(['--convert-subs', format])

    # Browser cookies if needed
    if cookies_browser:
        allowed_browsers = ['chrome', 'firefox', 'safari', 'edge', 'brave', 'opera']
        if cookies_browser.lower() in allowed_browsers:
            cmd.extend(['--cookies-from-browser', cookies_browser.lower()])

    # Also write video info for context
    cmd.append('--write-info-json')

    cmd.append(url)

    try:
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )

        # Check for subtitle files
        subtitle_extensions = ['.vtt', '.srt', '.ass', '.json3', '.ttml']
        for file in output_dir.iterdir():
            if any(file.name.endswith(ext) for ext in subtitle_extensions):
                result['files'].append(str(file))

        if result['files']:
            result['success'] = True
            print(f"SUCCESS: Extracted {len(result['files'])} transcript file(s)")
            for f in result['files']:
                print(f"  - {f}")
        else:
            result['error'] = "No subtitles found for this video"
            if process.stderr:
                result['error'] += f"\n{process.stderr[:500]}"
            print(f"WARNING: {result['error']}")

    except subprocess.TimeoutExpired:
        result['error'] = "Transcript extraction timed out"
        print(f"ERROR: {result['error']}")
    except Exception as e:
        result['error'] = str(e)
        print(f"ERROR: {result['error']}")

    return result


def convert_vtt_to_text(vtt_file: Path) -> str:
    """
    Convert VTT subtitle file to plain text.

    Removes timestamps and formatting for easy reading/processing.
    """
    try:
        content = vtt_file.read_text(encoding='utf-8')
        lines = content.split('\n')

        text_lines = []
        prev_line = None

        for line in lines:
            # Skip header
            if line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'):
                continue
            # Skip timestamps (00:00:00.000 --> 00:00:00.000)
            if '-->' in line:
                continue
            # Skip empty lines and line numbers
            if not line.strip() or line.strip().isdigit():
                continue
            # Skip position/alignment cues
            if line.startswith('align:') or line.startswith('position:'):
                continue

            # Remove HTML tags
            clean_line = re.sub(r'<[^>]+>', '', line)
            clean_line = clean_line.strip()

            # Deduplicate (YouTube auto-captions often repeat)
            if clean_line and clean_line != prev_line:
                text_lines.append(clean_line)
                prev_line = clean_line

        return ' '.join(text_lines)
    except Exception as e:
        return f"Error converting VTT: {e}"


def extract_from_file(
    urls_file: str,
    output_dir: Path,
    lang: str = 'en',
    manual_only: bool = False,
    sleep_interval: int = 3
) -> list[dict]:
    """Extract transcripts from multiple videos."""
    results = []

    try:
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except Exception as e:
        print(f"ERROR: Could not read URLs file: {e}")
        return results

    print(f"Found {len(urls)} URLs to process")

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url[:60]}...")

        result = get_transcript(
            url=url,
            output_dir=output_dir,
            lang=lang,
            manual_only=manual_only
        )
        results.append(result)

        # Sleep between requests
        if i < len(urls) and sleep_interval > 0:
            import time
            time.sleep(sleep_interval)

    return results


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Extract transcripts/subtitles from YouTube videos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://youtube.com/watch?v=VIDEO_ID"
  %(prog)s "URL" --lang es
  %(prog)s "URL" --manual-only
  %(prog)s "URL" --list-subs
  %(prog)s "URL" --format srt
  %(prog)s --urls-file videos.txt
  %(prog)s "URL" --to-text  # Convert to plain text
        """
    )

    parser.add_argument('url', nargs='?', help='YouTube video URL')
    parser.add_argument('--urls-file', help='File containing URLs (one per line)')
    parser.add_argument('--output-dir', '-o', default='.tmp/youtube/transcripts',
                        help='Output directory (default: .tmp/youtube/transcripts)')
    parser.add_argument('--output', help='Specific output file path')
    parser.add_argument('--lang', '-l', default='en',
                        help='Language code (default: en)')
    parser.add_argument('--manual-only', action='store_true',
                        help='Only get manually uploaded subtitles')
    parser.add_argument('--auto-only', action='store_true',
                        help='Only get auto-generated captions')
    parser.add_argument('--all-langs', action='store_true',
                        help='Download all available languages')
    parser.add_argument('--list-subs', action='store_true',
                        help='List available subtitles without downloading')
    parser.add_argument('--format', '-f', default='vtt',
                        choices=['vtt', 'srt', 'ass', 'json3'],
                        help='Subtitle format (default: vtt)')
    parser.add_argument('--to-text', action='store_true',
                        help='Convert transcript to plain text')
    parser.add_argument('--cookies-from-browser', '-c',
                        choices=['chrome', 'firefox', 'safari', 'edge', 'brave', 'opera'],
                        help='Use cookies from browser (for age-restricted)')
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

    # List subtitles mode
    if args.list_subs:
        if not args.url:
            print("ERROR: URL required for --list-subs")
            sys.exit(1)
        result = list_available_subtitles(args.url)
        if result:
            print(result.get('output', 'No output'))
            if result.get('error'):
                print(f"Error: {result['error']}")
        sys.exit(0)

    # Validate and create output directory
    output_dir = validate_output_dir(args.output_dir)
    print(f"Output directory: {output_dir}")
    print("=" * 60)

    # Extract transcripts
    if args.urls_file:
        results = extract_from_file(
            urls_file=args.urls_file,
            output_dir=output_dir,
            lang=args.lang,
            manual_only=args.manual_only
        )
    else:
        results = [get_transcript(
            url=args.url,
            output_dir=output_dir,
            lang=args.lang,
            manual_only=args.manual_only,
            auto_only=args.auto_only,
            all_langs=args.all_langs,
            format=args.format,
            cookies_browser=args.cookies_from_browser
        )]

    # Convert to plain text if requested
    if args.to_text:
        for result in results:
            for file_path in result.get('files', []):
                if file_path.endswith('.vtt'):
                    vtt_path = Path(file_path)
                    text = convert_vtt_to_text(vtt_path)
                    text_path = vtt_path.with_suffix('.txt')
                    text_path.write_text(text, encoding='utf-8')
                    print(f"Converted to text: {text_path}")
                    result['files'].append(str(text_path))

    # Summary
    print("\n" + "=" * 60)
    success_count = sum(1 for r in results if r['success'])
    print(f"Results: {success_count}/{len(results)} successful")

    # Save to specific output file if requested
    if args.output and len(results) == 1 and results[0]['success']:
        for file_path in results[0].get('files', []):
            if file_path.endswith('.vtt') or file_path.endswith('.srt'):
                content = Path(file_path).read_text(encoding='utf-8')
                Path(args.output).write_text(content, encoding='utf-8')
                print(f"Saved to: {args.output}")
                break

    # Save results JSON if requested
    if args.output_json:
        with open(args.output_json, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to: {args.output_json}")

    sys.exit(0 if success_count == len(results) else 1)


if __name__ == '__main__':
    main()
