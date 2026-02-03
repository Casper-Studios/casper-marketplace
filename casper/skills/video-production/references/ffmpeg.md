# FFmpeg Video Processing Reference

## Overview

FFmpeg is the core video processing engine for stitching multiple videos into a single output file. The `stitch_videos.py` script wraps FFmpeg to provide automated video concatenation with intelligent codec detection and optional re-encoding.

**Key Capabilities:**
- Concatenate multiple video files in sequence
- Stream copy (fast, no quality loss) when videos are compatible
- Re-encode when videos have mismatched codecs/resolutions
- Extract video metadata via FFprobe
- Generate timestamps for YouTube descriptions

**Script Location:** `~/.claude/skills/video-production/scripts/stitch_videos.py`

---

## Inputs

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `videos` | List[Path] | Ordered list of video file paths to concatenate |
| `output_path` | Path | Destination path for the stitched video |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `reencode` | bool | `false` | Force re-encoding (slower but handles incompatible videos) |
| `video_codec` | string | `libx264` | Video codec for re-encoding |
| `audio_codec` | string | `aac` | Audio codec for re-encoding |
| `crf` | int | `18` | Quality setting (lower = better quality, 18-23 recommended) |
| `preset` | string | `fast` | Encoding speed preset (ultrafast, fast, medium, slow) |

### Video Info Output

| Field | Type | Description |
|-------|------|-------------|
| `path` | string | Absolute path to video file |
| `duration` | float | Duration in seconds |
| `size_bytes` | int | File size in bytes |
| `width` | int | Video width in pixels |
| `height` | int | Video height in pixels |
| `video_codec` | string | Video codec (e.g., h264, hevc) |
| `audio_codec` | string | Audio codec (e.g., aac, mp3) |
| `fps` | float | Frames per second |
| `sample_rate` | int | Audio sample rate (Hz) |
| `audio_channels` | int | Number of audio channels |
| `start_timestamp` | float | Start time in final video (seconds) |
| `start_timestamp_formatted` | string | Formatted timestamp (HH:MM:SS or MM:SS) |

---

## CLI Usage

### Python Script

```bash
# Concatenate specific videos
python ~/.claude/skills/video-production/scripts/stitch_videos.py \
    --videos video1.mp4 video2.mp4 video3.mp4 \
    --output combined.mp4

# Concatenate all videos from directory (sorted by name)
python ~/.claude/skills/video-production/scripts/stitch_videos.py \
    --video-dir .tmp/videos \
    --output course.mp4

# Use pre-made concat file
python ~/.claude/skills/video-production/scripts/stitch_videos.py \
    --concat-file concat_list.txt \
    --output combined.mp4

# Force re-encoding with custom settings
python ~/.claude/skills/video-production/scripts/stitch_videos.py \
    --videos video1.mp4 video2.mp4 \
    --output combined.mp4 \
    --reencode \
    --video-codec libx264 \
    --crf 20 \
    --preset medium

# Get video info only
python ~/.claude/skills/video-production/scripts/stitch_videos.py \
    --info video.mp4
```

### Direct FFmpeg Commands

```bash
# Get video metadata
ffprobe -v quiet -print_format json -show_format -show_streams video.mp4

# Stream copy (fast, no re-encoding)
ffmpeg -y -f concat -safe 0 -i concat_list.txt -c copy -movflags +faststart output.mp4

# Re-encode with H.264/AAC
ffmpeg -y -f concat -safe 0 -i concat_list.txt \
    -c:v libx264 -crf 18 -preset fast \
    -c:a aac -b:a 192k \
    -pix_fmt yuv420p -movflags +faststart \
    output.mp4
```

### Concat File Format

Create `concat_list.txt`:
```
file '/absolute/path/to/video1.mp4'
file '/absolute/path/to/video2.mp4'
file '/absolute/path/to/video3.mp4'
```

---

## Error Handling

### Common Errors and Solutions

| Error | Cause | Resolution |
|-------|-------|------------|
| `FFmpeg not found` | FFmpeg not installed | Install: `brew install ffmpeg` (macOS), `sudo apt install ffmpeg` (Ubuntu) |
| `FFprobe not found` | FFprobe missing | Reinstall FFmpeg (includes FFprobe) |
| `Codec mismatch` | Videos have different codecs | Use `--reencode` flag to normalize |
| `Resolution mismatch` | Videos have different dimensions | Use `--reencode` to scale to common resolution |
| `FPS mismatch` | Videos have different frame rates | Use `--reencode` to normalize frame rate |
| `Video not found` | Invalid file path | Verify file exists and path is correct |
| `FFmpeg failed` | Various encoding errors | Check stderr output, verify input files are valid |
| `Timeout exceeded` | Large video taking too long | Allow more time, check disk I/O |

### Automatic Fallbacks

The script implements smart fallback behavior:

1. **Compatibility Check**: Before stitching, FFprobe analyzes all videos
2. **Auto Re-encode**: If videos are incompatible, automatically enables re-encoding
3. **Path Escaping**: Single quotes in file paths are properly escaped
4. **Cleanup**: Temporary concat files are removed after processing

---

## Testing Checklist

### Pre-flight Verification

```bash
# Verify FFmpeg installation
ffmpeg -version

# Verify FFprobe installation
ffprobe -version

# Check available encoders
ffmpeg -encoders | grep libx264

# Check available decoders
ffmpeg -decoders | grep h264
```

### Smoke Tests

```bash
# Test video info extraction
python ~/.claude/skills/video-production/scripts/stitch_videos.py --info test.mp4

# Test simple concat (2 videos)
python ~/.claude/skills/video-production/scripts/stitch_videos.py \
    --videos short1.mp4 short2.mp4 \
    --output test_concat.mp4

# Test with re-encoding
python ~/.claude/skills/video-production/scripts/stitch_videos.py \
    --videos video1.mp4 video2.mp4 \
    --output test_reencode.mp4 \
    --reencode
```

### Validation Checks

- [ ] FFmpeg and FFprobe return version info
- [ ] `--info` returns valid JSON metadata
- [ ] Stream copy works for compatible videos
- [ ] Re-encoding produces playable output
- [ ] Timestamps are correctly calculated
- [ ] Output file has `+faststart` for web streaming

---

## Performance Tips

### Speed Optimization

| Tip | Impact | Use When |
|-----|--------|----------|
| Use stream copy (`-c copy`) | 10-100x faster | All videos have same codec/resolution/fps |
| Use `ultrafast` preset | 2-3x faster encoding | Speed matters more than file size |
| Use `fast` preset | Balanced speed/quality | General use (default) |
| Use hardware acceleration | 5-10x faster | GPU available (see below) |
| Lower CRF value | Faster encoding | Quality is paramount (CRF 15-18) |

### Hardware Acceleration

```bash
# Check for NVIDIA GPU encoder
ffmpeg -encoders | grep nvenc

# Use NVIDIA hardware encoding
ffmpeg -i input.mp4 -c:v h264_nvenc -preset fast output.mp4

# Check for Apple VideoToolbox (macOS)
ffmpeg -encoders | grep videotoolbox

# Use Apple hardware encoding
ffmpeg -i input.mp4 -c:v h264_videotoolbox -q:v 65 output.mp4
```

### Codec Selection Guide

| Codec | Pros | Cons | Use Case |
|-------|------|------|----------|
| `libx264` | Universal compatibility, good quality | CPU-intensive | General distribution |
| `libx265` | Better compression, smaller files | Slower encoding, less compatible | Long-term storage |
| `h264_nvenc` | Very fast, GPU-based | Requires NVIDIA GPU | Quick exports |
| `h264_videotoolbox` | Fast on macOS | macOS only | Local macOS processing |

### Quality Settings

| CRF Value | Quality | File Size | Use Case |
|-----------|---------|-----------|----------|
| 15-17 | Excellent | Large | Archival, source material |
| 18-20 | Very good | Medium | YouTube, general distribution |
| 21-23 | Good | Smaller | Web streaming, mobile |
| 24+ | Acceptable | Small | Low bandwidth, previews |

---

## Troubleshooting

### Video Won't Play After Stitching

```bash
# Check output file integrity
ffprobe -v error output.mp4

# Re-encode with web-safe settings
ffmpeg -i output.mp4 -c:v libx264 -profile:v baseline -level 3.0 \
    -c:a aac -b:a 128k -movflags +faststart safe_output.mp4
```

### Audio Out of Sync

```bash
# Re-encode with audio sync
ffmpeg -y -f concat -safe 0 -i concat_list.txt \
    -c:v libx264 -c:a aac \
    -async 1 -vsync cfr \
    output.mp4
```

### Concat Fails with "Discarding Extra" Warnings

Videos have different numbers of streams. Solutions:

```bash
# Option 1: Map only video and first audio stream
ffmpeg -y -f concat -safe 0 -i concat_list.txt \
    -map 0:v:0 -map 0:a:0 -c copy output.mp4

# Option 2: Re-encode everything
ffmpeg -y -f concat -safe 0 -i concat_list.txt \
    -c:v libx264 -c:a aac output.mp4
```

### Large File Size

```bash
# Use higher CRF for smaller files
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium \
    -c:a aac -b:a 128k output.mp4

# Use two-pass encoding for precise file size
ffmpeg -i input.mp4 -c:v libx264 -b:v 2M -pass 1 -f null /dev/null
ffmpeg -i input.mp4 -c:v libx264 -b:v 2M -pass 2 output.mp4
```

---

## Integration Patterns

### With Title Slides

```python
from stitch_videos import stitch_with_slides

# Interleave videos with title slides
result_path, metadata = stitch_with_slides(
    videos=[Path("intro.mp4"), Path("lesson1.mp4"), Path("lesson2.mp4")],
    slides=[None, Path("slide1.mp4"), Path("slide2.mp4")],  # None = no slide before intro
    output_path=Path(".tmp/course.mp4"),
    reencode=True  # Recommended when mixing generated slides with source videos
)
```

### With YouTube Description

```python
from stitch_videos import stitch_videos
from generate_youtube_description import generate_youtube_description

# Stitch videos
output_path, video_infos = stitch_videos(
    videos=video_list,
    output_path=Path(".tmp/course.mp4")
)

# Generate description with timestamps
description = generate_youtube_description(
    video_segments=video_infos,
    course_title="Claude Code Course"
)
```

---

## Related Skills

- **title-slides** - Generate title slide videos to interleave with content
- **youtube-description** - Generate timestamped YouTube descriptions
- **google-workspace** - Upload final videos to Google Drive
