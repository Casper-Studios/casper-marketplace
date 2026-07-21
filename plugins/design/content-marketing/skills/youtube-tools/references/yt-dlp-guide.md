# yt-dlp Complete Reference Guide

## Overview

yt-dlp is a feature-rich command-line video downloader supporting thousands of websites. It's a maintained fork of youtube-dl with additional features and fixes.

## Installation

```bash
# pip (recommended)
pip install yt-dlp

# Homebrew (macOS)
brew install yt-dlp

# Update to latest
pip install -U yt-dlp
```

### Optional: FFmpeg for Format Conversion

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
winget install ffmpeg
```

## youtube-tools vs Apify: When to Use Which

| Task | youtube-tools (yt-dlp) | apify-scrapers |
|------|------------------------|----------------|
| Download videos | Best choice (FREE) | Not applicable |
| Download audio | Best choice (FREE) | Not applicable |
| Get transcripts | Best choice (FREE) | Slower, costs $ |
| Get video metadata | Good (FREE) | Good for bulk |
| Search YouTube | Not supported | Use this |
| Get comments at scale | Limited | Use this |
| Channel analytics | Not supported | Use this |
| Trending discovery | Not supported | Use this |
| Cloud processing | Not supported | Use this |

**Rule of thumb:**
- Downloading content → youtube-tools (FREE)
- Searching/scraping YouTube → apify-scrapers (paid)

## Command Reference

### Basic Download

```bash
# Best quality
yt-dlp "https://youtube.com/watch?v=VIDEO_ID"

# Specific quality
yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" URL

# Audio only (MP3)
yt-dlp -x --audio-format mp3 URL

# Audio only (best quality)
yt-dlp -x --audio-format best URL
```

### Quality Selection

```bash
# List available formats
yt-dlp -F URL

# Best video + best audio (default)
yt-dlp -f "bestvideo+bestaudio/best" URL

# Specific resolution
yt-dlp -f "bestvideo[height<=1080]+bestaudio" URL

# Specific format by ID
yt-dlp -f 22 URL  # 720p mp4
```

### Quality Presets

| Preset | Format String |
|--------|---------------|
| 4K | `bestvideo[height<=2160]+bestaudio/best[height<=2160]` |
| 1080p | `bestvideo[height<=1080]+bestaudio/best[height<=1080]` |
| 720p | `bestvideo[height<=720]+bestaudio/best[height<=720]` |
| 480p | `bestvideo[height<=480]+bestaudio/best[height<=480]` |
| Smallest | `worstvideo+worstaudio/worst` |

### Output Options

```bash
# Custom filename
yt-dlp -o "%(title)s.%(ext)s" URL

# With upload date
yt-dlp -o "%(upload_date)s-%(title)s.%(ext)s" URL

# Organized by channel
yt-dlp -o "%(channel)s/%(title)s.%(ext)s" URL

# Sanitized filenames (safe for all systems)
yt-dlp --restrict-filenames URL

# Custom output directory
yt-dlp -P /path/to/output URL
```

### Output Template Variables

| Variable | Description |
|----------|-------------|
| `%(title)s` | Video title |
| `%(id)s` | Video ID |
| `%(ext)s` | File extension |
| `%(channel)s` | Channel name |
| `%(uploader)s` | Uploader name |
| `%(upload_date)s` | Upload date (YYYYMMDD) |
| `%(duration)s` | Duration in seconds |
| `%(view_count)s` | View count |
| `%(playlist_index)s` | Playlist position |

### Subtitles / Transcripts

```bash
# Download auto-generated captions
yt-dlp --write-auto-subs URL

# Download manual subtitles
yt-dlp --write-subs URL

# Both auto and manual
yt-dlp --write-subs --write-auto-subs URL

# Specific language
yt-dlp --write-subs --sub-langs en URL

# All languages
yt-dlp --all-subs URL

# Convert subtitle format
yt-dlp --write-subs --convert-subs srt URL

# List available subtitles
yt-dlp --list-subs URL

# Download only subtitles (no video)
yt-dlp --skip-download --write-auto-subs URL
```

### Playlists

```bash
# Download entire playlist
yt-dlp "https://youtube.com/playlist?list=PLAYLIST_ID"

# Download specific range
yt-dlp --playlist-start 5 --playlist-end 10 URL

# Download specific items
yt-dlp --playlist-items "1,3,5-7" URL

# Reverse order
yt-dlp --playlist-reverse URL

# Don't download playlist (single video only)
yt-dlp --no-playlist URL
```

### Metadata

```bash
# Write info JSON
yt-dlp --write-info-json URL

# Write description
yt-dlp --write-description URL

# Write thumbnail
yt-dlp --write-thumbnail URL

# Embed metadata in file
yt-dlp --embed-metadata URL

# Embed thumbnail
yt-dlp --embed-thumbnail URL

# Get info without downloading
yt-dlp --dump-json --no-download URL
```

### Authentication

```bash
# Browser cookies (safest)
yt-dlp --cookies-from-browser chrome URL
yt-dlp --cookies-from-browser firefox URL
yt-dlp --cookies-from-browser safari URL

# Cookie file (Netscape format)
yt-dlp --cookies cookies.txt URL

# Username/password (not recommended)
yt-dlp -u USERNAME -p PASSWORD URL
```

### Rate Limiting & Throttling

```bash
# Sleep between downloads
yt-dlp --sleep-interval 5 URL

# Random sleep range
yt-dlp --min-sleep-interval 3 --max-sleep-interval 10 URL

# Limit download rate
yt-dlp --limit-rate 1M URL

# Concurrent fragments
yt-dlp --concurrent-fragments 4 URL
```

### Filtering

```bash
# Match title
yt-dlp --match-title "tutorial" URL

# Reject title
yt-dlp --reject-title "advertisement" URL

# Date filtering
yt-dlp --dateafter 20230101 URL
yt-dlp --datebefore 20231231 URL

# View count filtering
yt-dlp --min-views 1000 URL
yt-dlp --max-views 1000000 URL

# Duration filtering (seconds)
yt-dlp --match-filter "duration > 60 & duration < 600" URL
```

### Live Streams

```bash
# Download live stream (wait for it to end)
yt-dlp URL

# Download from start
yt-dlp --live-from-start URL

# Wait for stream to go live
yt-dlp --wait-for-video 30 URL  # Check every 30 seconds
```

### Advanced Options

```bash
# Archive (don't re-download)
yt-dlp --download-archive downloaded.txt URL

# Max downloads
yt-dlp --max-downloads 10 URL

# Retries
yt-dlp --retries 10 URL

# Ignore errors (continue on failure)
yt-dlp --ignore-errors URL

# Quiet mode
yt-dlp -q URL

# Verbose mode
yt-dlp -v URL

# Simulate (don't download)
yt-dlp --simulate URL
```

## Common Use Cases

### Download Course Playlist

```bash
yt-dlp \
  -f "bestvideo[height<=720]+bestaudio" \
  --merge-output-format mp4 \
  -o "%(playlist_index)s-%(title)s.%(ext)s" \
  --restrict-filenames \
  --sleep-interval 5 \
  "PLAYLIST_URL"
```

### Extract All Transcripts from Playlist

```bash
yt-dlp \
  --skip-download \
  --write-auto-subs \
  --sub-langs en \
  --convert-subs srt \
  -o "%(playlist_index)s-%(title)s.%(ext)s" \
  "PLAYLIST_URL"
```

### Download Audio Podcast

```bash
yt-dlp \
  -x \
  --audio-format mp3 \
  --audio-quality 0 \
  --embed-thumbnail \
  --embed-metadata \
  -o "%(title)s.%(ext)s" \
  URL
```

### Archive Channel

```bash
yt-dlp \
  --download-archive channel_archive.txt \
  -f "bestvideo[height<=1080]+bestaudio" \
  --merge-output-format mp4 \
  -o "%(upload_date)s-%(title)s.%(ext)s" \
  --sleep-interval 10 \
  "https://youtube.com/@CHANNEL/videos"
```

### Get All Metadata (No Download)

```bash
yt-dlp \
  --dump-json \
  --no-download \
  --flat-playlist \
  "PLAYLIST_URL" > playlist_info.json
```

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Video unavailable` | Private/deleted/region-locked | Use VPN or cookies |
| `Sign in to confirm age` | Age-restricted | `--cookies-from-browser chrome` |
| `Unable to extract video data` | YouTube changed API | Update: `pip install -U yt-dlp` |
| `HTTP Error 429` | Rate limited | Add `--sleep-interval 10` |
| `Incomplete data` | Network issue | Add `--retries 10` |
| `Requested format not available` | Format doesn't exist | Use `-F` to list formats |

### Retry Strategy

```bash
yt-dlp \
  --retries 10 \
  --fragment-retries 10 \
  --skip-unavailable-fragments \
  URL
```

## Security Considerations

### Safe Practices
- Only download from trusted URLs
- Validate URLs before processing
- Use `--restrict-filenames` to sanitize output
- Avoid `--exec` for untrusted content
- Don't store cookies/credentials in scripts

### Privacy
- yt-dlp doesn't track or phone home
- No data sent to third parties
- Browser cookie access requires explicit flag
- Downloaded files are local only

## Performance Tips

### Speed Up Downloads
```bash
# Use concurrent fragments
yt-dlp --concurrent-fragments 4 URL

# Use external downloader
yt-dlp --downloader aria2c URL
```

### Reduce Bandwidth
```bash
# Lower quality
yt-dlp -f "bestvideo[height<=480]+bestaudio" URL

# Audio only
yt-dlp -x URL
```

### Batch Processing
```bash
# From file
yt-dlp -a urls.txt

# With archive (skip already downloaded)
yt-dlp --download-archive archive.txt -a urls.txt
```

## Integration with Other Tools

### FFmpeg (included when converting)
```bash
# Merge formats
yt-dlp --merge-output-format mp4 URL

# Post-process audio
yt-dlp -x --audio-format mp3 --postprocessor-args "-ar 44100" URL
```

### jq (JSON processing)
```bash
# Extract specific fields
yt-dlp --dump-json URL | jq '{title, duration, view_count}'
```

### aria2c (faster downloads)
```bash
# Use aria2c for downloading
yt-dlp --downloader aria2c --downloader-args "-x 16 -s 16" URL
```

## Resources

- GitHub: https://github.com/yt-dlp/yt-dlp
- Documentation: https://github.com/yt-dlp/yt-dlp#readme
- Supported sites: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md
- Options reference: `yt-dlp --help`
