# Video Course Stitcher Workflow

## Overview
Download videos from Google Drive, stitch with title slides, generate YouTube description.

## Inputs

### Required
| Parameter | Type | Description |
|-----------|------|-------------|
| `folder_url` | string | Google Drive folder URL |
| `output_name` | string | Final video filename |

### Optional
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `slide_duration` | float | 3.0 | Title slide duration (seconds) |
| `slide_bg_color` | string | #1a1a2e | Background hex color |
| `slide_text_color` | string | #ffffff | Text hex color |
| `skip_first_slide` | bool | true | Skip title for intro video |
| `upload_to_drive` | bool | true | Upload result to Drive |

## Pipeline

```
1. AUTHENTICATE with Google Drive
   └── Load credentials from mycreds.txt

2. PARSE FOLDER URL
   └── List all video files (mp4, mov, mkv)
   └── Sort by name (episode order)

3. DOWNLOAD VIDEOS
   └── Create .tmp/video_course_stitcher/TIMESTAMP/downloads/
   └── Download each file

4. PARSE VIDEO TITLES
   └── "[e2] Installing Claude Code" → "Installing Claude Code"

5. GET VIDEO METADATA
   └── FFprobe for duration, resolution, codec

6. GENERATE TITLE SLIDES
   └── For each video (except first if skip_first_slide):
       ├── Create PNG with title text
       └── Convert to video clip

7. BUILD CONCAT LIST
   └── video1 → slide2 → video2 → slide3 → video3...

8. STITCH WITH FFMPEG
   └── ffmpeg -f concat -safe 0 -i concat_list.txt -c copy output.mp4

9. CALCULATE TIMESTAMPS
   └── Track cumulative duration
   └── Format as HH:MM:SS

10. GENERATE YOUTUBE DESCRIPTION
    └── 0:00 - Introduction
    └── 5:23 - Installing Claude Code
    └── 12:45 - Your First Automation

11. UPLOAD TO GOOGLE DRIVE
    └── Upload final video + description
```

## FFmpeg Commands

### Get Video Info
```bash
ffprobe -v quiet -print_format json -show_format -show_streams video.mp4
```

### Create Title Slide
```bash
ffmpeg -f lavfi -i color=c=0x1a1a2e:s=1920x1080:d=3 \
  -vf "drawtext=text='Installing Claude Code':fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2" \
  -c:v libx264 -t 3 slide.mp4

# Add silent audio
ffmpeg -i slide.mp4 -f lavfi -i anullsrc=r=48000:cl=stereo -c:v copy -c:a aac -shortest slide_with_audio.mp4
```

### Concatenate Videos
```bash
# concat_list.txt:
# file 'video1.mp4'
# file 'slide2.mp4'
# file 'video2.mp4'

ffmpeg -f concat -safe 0 -i concat_list.txt -c copy output.mp4
```

## Output Structure

```
.tmp/video_course_stitcher/{timestamp}/
├── downloads/         # Downloaded source videos
├── slides/            # Generated title slides
├── concat_list.txt    # FFmpeg input file
├── output.mp4         # Final stitched video
├── youtube_description.md  # Timestamped description
└── metadata.json      # Processing info
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `Invalid credentials` | OAuth token expired | Delete `mycreds.txt`, re-authenticate |
| `Folder not found` | Invalid Drive folder URL | Verify folder ID and permissions |
| `No videos found` | Folder empty or wrong file types | Check folder contains mp4/mov/mkv files |
| `Video download failed` | Network error or file access | Retry up to 3 times with backoff |
| `FFmpeg not found` | FFmpeg not installed | Install: `brew install ffmpeg` (mac) or `apt install ffmpeg` |
| `FFprobe not found` | FFprobe missing (part of FFmpeg) | Reinstall FFmpeg with all components |
| `Codec mismatch` | Videos have different codecs | Re-encode all to H.264 before concat |
| `Resolution mismatch` | Videos have different sizes | Scale all to common resolution |
| `Audio track missing` | Silent video in sequence | Add silent audio track with `anullsrc` |
| `Disk space error` | Not enough space for videos | Free up space, videos can be large |
| `Title slide render failed` | Font or color issue | Check hex color format, use default font |
| `Upload failed` | Drive quota or permissions | Check quota, verify folder access |

### Recovery Strategies

1. **Automatic retry**: Retry failed downloads 3 times with exponential backoff
2. **Codec normalization**: If concat fails, re-encode all videos to H.264/AAC
3. **Resolution normalization**: Scale all videos to match the first video's resolution
4. **Audio fallback**: If video lacks audio, add silent track automatically
5. **Partial processing**: Save progress to allow resume after failures
6. **Cleanup on failure**: Remove partial files to prevent disk fill
7. **Pre-flight checks**: Verify FFmpeg, disk space, and credentials before starting

## Use Cases

1. **Course compilation** - Combine tutorials for YouTube
2. **Webinar series** - Merge weekly webinars
3. **Training materials** - Single onboarding video
4. **Conference talks** - Combine session recordings

## Testing Checklist

### Pre-flight
- [ ] FFmpeg installed and in PATH (`ffmpeg -version`)
- [ ] FFprobe available (`ffprobe -version`)
- [ ] Google Drive OAuth credentials available (`mycreds.txt`)
- [ ] Dependencies installed (`pip install pydrive2 pillow python-dotenv`)
- [ ] Sufficient disk space for video downloads

### Smoke Test
```bash
# Test with a small Drive folder (2-3 short videos)
python scripts/video_course_stitcher.py \
    --folder-url "https://drive.google.com/drive/folders/FOLDER_ID" \
    --output-name "test_course"

# Test with custom slide settings
python scripts/video_course_stitcher.py \
    --folder-url "https://drive.google.com/drive/folders/FOLDER_ID" \
    --output-name "styled_course" \
    --slide-duration 2.0 \
    --slide-bg-color "#000000" \
    --slide-text-color "#00ff00"

# Test without uploading to Drive (local only)
python scripts/video_course_stitcher.py \
    --folder-url "https://drive.google.com/drive/folders/FOLDER_ID" \
    --output-name "local_test" \
    --no-upload
```

### Validation
- [ ] Videos downloaded to `.tmp/video_course_stitcher/{timestamp}/downloads/`
- [ ] Videos sorted in correct episode order (by filename)
- [ ] Title slides generated for each video (except first if `skip_first_slide`)
- [ ] Slide colors match specified hex values
- [ ] Slide duration matches specified seconds
- [ ] `concat_list.txt` lists videos and slides in correct order
- [ ] Final `output.mp4` plays without errors
- [ ] Video has correct resolution (matches source videos)
- [ ] Audio tracks present and synced
- [ ] `youtube_description.md` has correct timestamps
- [ ] Timestamp format is `HH:MM:SS` for long videos
- [ ] Final video uploaded to Drive (if `upload_to_drive=true`)
- [ ] Codec compatibility: all source videos should have matching codecs

### FFmpeg Verification
```bash
# Verify FFmpeg installation
ffmpeg -version

# Test video info extraction
ffprobe -v quiet -print_format json -show_format test_video.mp4

# Test simple concat (manual)
ffmpeg -f concat -safe 0 -i concat_list.txt -c copy test_output.mp4
```

### Common Issues
- [ ] If concat fails with codec error, source videos have mismatched codecs
- [ ] If title slides have no audio, ensure `anullsrc` filter is applied
- [ ] If timestamps are wrong, verify FFprobe duration extraction
- [ ] If upload fails, check Drive quota and folder permissions
