# Title Slide Generation Reference

## Overview

Generate professional video title slides for course content using PIL (Python Imaging Library) and FFmpeg. Title slides are short video clips with centered text on a solid background, designed to be interleaved with main video content.

**Key Capabilities:**
- Create title slide videos with customizable colors and fonts
- Auto-scale text to fit within frame
- Generate silent audio track for seamless concatenation
- Batch generation from JSON configuration
- Parse episode numbers from filenames

**Script Location:** `~/.claude/skills/video-production/scripts/create_title_slides.py`

---

## Inputs

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `title` | string | Text to display on the slide |
| `output_path` | Path | Destination path for the video file |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `duration` | float | `3.0` | Slide duration in seconds |
| `resolution` | string | `1920x1080` | Video resolution (WxH format) |
| `bg_color` | string | `#1a1a2e` | Background color (hex) |
| `text_color` | string | `#ffffff` | Text color (hex) |
| `font_size` | int | `72` | Font size in pixels |
| `fps` | int | `30` | Frame rate (should match source videos) |
| `sample_rate` | int | `44100` | Audio sample rate (should match source videos) |

### Batch Mode Input (JSON)

```json
[
    {"title": "Introduction to Claude Code", "filename": "slide_001.mp4"},
    {"title": "Installing Claude Code", "filename": "slide_002.mp4"},
    {"title": "Your First Automation", "filename": "slide_003.mp4"}
]
```

---

## CLI Usage

### Single Slide Generation

```bash
# Basic title slide
python ~/.claude/skills/video-production/scripts/create_title_slides.py \
    --title "Installing Claude Code" \
    --output slide.mp4

# Custom duration and resolution
python ~/.claude/skills/video-production/scripts/create_title_slides.py \
    --title "Your First Automation" \
    --duration 3 \
    --resolution 1920x1080 \
    --output slide.mp4

# Custom colors
python ~/.claude/skills/video-production/scripts/create_title_slides.py \
    --title "Advanced Workflows" \
    --bg-color "#000000" \
    --text-color "#00ff00" \
    --output slide.mp4

# Custom font size
python ~/.claude/skills/video-production/scripts/create_title_slides.py \
    --title "Lesson 1" \
    --font-size 96 \
    --output large_text_slide.mp4
```

### Batch Generation

```bash
# Generate multiple slides from JSON file
python ~/.claude/skills/video-production/scripts/create_title_slides.py \
    --titles-file titles.json \
    --output-dir .tmp/slides

# Batch with custom styling
python ~/.claude/skills/video-production/scripts/create_title_slides.py \
    --titles-file titles.json \
    --output-dir .tmp/slides \
    --duration 2.0 \
    --bg-color "#1a1a2e" \
    --text-color "#ffffff"
```

### Title Parsing Utility

```bash
# Parse episode number and clean title from filename
python ~/.claude/skills/video-production/scripts/create_title_slides.py \
    --parse-title "[e2] Installing Claude Code.mp4"
# Output:
# Original: [e2] Installing Claude Code.mp4
# Episode:  2
# Clean:    Installing Claude Code
```

---

## Output Structure

### Single Slide Output

```
output_path.mp4  # Final slide video
```

### Batch Output

```
.tmp/slides/
    slide_001.mp4
    slide_002.mp4
    slide_003.mp4
    ...
```

### Video Specifications

| Property | Value |
|----------|-------|
| Format | MP4 (H.264 + AAC) |
| Video Codec | libx264 |
| CRF | 18 (high quality) |
| Preset | fast |
| Pixel Format | yuv420p |
| Audio | Silent AAC stereo |
| Audio Bitrate | 128k |

---

## Error Handling

### Common Errors and Solutions

| Error | Cause | Resolution |
|-------|-------|------------|
| `FFmpeg not found` | FFmpeg not installed | Install: `brew install ffmpeg` (macOS), `sudo apt install ffmpeg` (Ubuntu) |
| `Invalid resolution format` | Wrong format string | Use format: `WIDTHxHEIGHT` (e.g., `1920x1080`) |
| `Invalid hex color` | Malformed color code | Use format: `#RRGGBB` (e.g., `#ffffff`) |
| `Font not found` | System font unavailable | Script auto-falls back to default font |
| `FFmpeg failed` | Various encoding errors | Check stderr, verify PIL generated valid PNG |
| `Output not created` | Permission or path error | Verify output directory is writable |
| `Timeout expired` | FFmpeg hung | Check system resources, try smaller resolution |

### Font Fallback Order

The script searches for fonts in this order:

**macOS:**
1. `/System/Library/Fonts/Helvetica.ttc`
2. `/Library/Fonts/Arial.ttf`
3. `/System/Library/Fonts/Supplemental/Arial.ttf`
4. `/System/Library/Fonts/SFNS.ttf`

**Linux:**
1. `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`
2. `/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf`
3. `/usr/share/fonts/TTF/DejaVuSans-Bold.ttf`

**Windows:**
1. `C:\Windows\Fonts\arial.ttf`
2. `C:\Windows\Fonts\segoeui.ttf`

If none found, falls back to PIL default bitmap font.

---

## Testing Checklist

### Pre-flight Verification

```bash
# Verify FFmpeg installation
ffmpeg -version

# Verify PIL installation
python -c "from PIL import Image, ImageDraw, ImageFont; print('PIL OK')"

# Check for system fonts
ls /System/Library/Fonts/Helvetica.ttc  # macOS
ls /usr/share/fonts/truetype/dejavu/    # Linux
```

### Smoke Tests

```bash
# Test single slide generation
python ~/.claude/skills/video-production/scripts/create_title_slides.py \
    --title "Test Slide" \
    --output .tmp/test_slide.mp4

# Test custom resolution
python ~/.claude/skills/video-production/scripts/create_title_slides.py \
    --title "4K Test" \
    --resolution 3840x2160 \
    --output .tmp/test_4k.mp4

# Test title parsing
python ~/.claude/skills/video-production/scripts/create_title_slides.py \
    --parse-title "[e1] Introduction.mp4"
```

### Validation Checks

- [ ] FFmpeg returns version info
- [ ] PIL imports without errors
- [ ] Single slide generates valid MP4
- [ ] Video plays without errors
- [ ] Audio track present (silent)
- [ ] Text is centered and readable
- [ ] Custom colors render correctly
- [ ] Long titles auto-scale to fit
- [ ] Resolution matches specification
- [ ] Duration matches specification

---

## Performance Tips

### Pre-generate Slides

For large courses, batch generate all slides upfront:

```python
from pathlib import Path
from create_title_slides import create_multiple_slides

titles = [
    {"title": "Lesson 1: Introduction", "filename": "slide_01.mp4"},
    {"title": "Lesson 2: Setup", "filename": "slide_02.mp4"},
    {"title": "Lesson 3: First Project", "filename": "slide_03.mp4"},
]

slides = create_multiple_slides(
    titles=titles,
    output_dir=Path(".tmp/slides"),
    duration=3.0,
    resolution="1920x1080"
)
```

### Caching Recommendations

| Strategy | Implementation |
|----------|----------------|
| Pre-generate all slides | Generate during build, not runtime |
| Cache by title hash | Store slides with hash-based filenames |
| Reuse identical slides | Check for existing file before generating |
| Template-based generation | Create base templates, swap text only |

### Resolution Matching

Always match slide resolution to your source videos:

```bash
# Check source video resolution
ffprobe -v error -select_streams v:0 \
    -show_entries stream=width,height \
    -of csv=p=0 source_video.mp4
# Output: 1920,1080

# Generate matching slides
python create_title_slides.py \
    --title "Lesson 1" \
    --resolution 1920x1080 \
    --output slide.mp4
```

### Frame Rate Matching

Match FPS and sample rate to source videos for seamless concatenation:

```bash
# Check source video fps
ffprobe -v error -select_streams v:0 \
    -show_entries stream=r_frame_rate \
    -of csv=p=0 source_video.mp4
# Output: 30/1

# Check source audio sample rate
ffprobe -v error -select_streams a:0 \
    -show_entries stream=sample_rate \
    -of csv=p=0 source_video.mp4
# Output: 44100
```

---

## Troubleshooting

### Text Not Visible

```bash
# Check color contrast
# Ensure bg_color and text_color have sufficient contrast
# Bad: bg_color="#ffffff", text_color="#eeeeee"
# Good: bg_color="#1a1a2e", text_color="#ffffff"
```

### Text Too Small

```bash
# Increase font size
python create_title_slides.py \
    --title "My Title" \
    --font-size 96 \
    --output slide.mp4
```

### Text Cropped at Edges

The script auto-scales text to fit within 85% of frame width. For very long titles:

1. Use shorter title text
2. Reduce font size manually
3. Split into multiple lines (not supported yet)

### Slides Don't Concatenate Smoothly

Ensure matching specifications:

```bash
# Generate slides with exact specs of source videos
python create_title_slides.py \
    --title "Lesson 1" \
    --resolution 1920x1080 \
    --duration 3.0 \
    --output slide.mp4
```

If still having issues, use `--reencode` when stitching.

### No Audio Track

The script generates silent audio automatically. If missing:

```bash
# Manually add silent audio
ffmpeg -i slide_no_audio.mp4 \
    -f lavfi -i anullsrc=r=44100:cl=stereo \
    -c:v copy -c:a aac -shortest \
    slide_with_audio.mp4
```

---

## Integration Patterns

### With Video Stitcher

```python
from pathlib import Path
from create_title_slides import create_title_slide, parse_video_title
from stitch_videos import stitch_with_slides

# Parse video titles to generate slides
videos = [Path("intro.mp4"), Path("[e1] Setup.mp4"), Path("[e2] First Project.mp4")]
slides = []

for i, video in enumerate(videos):
    if i == 0:
        slides.append(None)  # No slide before intro
    else:
        _, clean_title = parse_video_title(video.name)
        slide_path = Path(f".tmp/slides/slide_{i:03d}.mp4")
        create_title_slide(
            title=clean_title,
            output_path=slide_path,
            duration=3.0,
            resolution="1920x1080"
        )
        slides.append(slide_path)

# Stitch everything together
output, metadata = stitch_with_slides(
    videos=videos,
    slides=slides,
    output_path=Path(".tmp/course.mp4")
)
```

### Title Parsing Patterns

Supported episode formats:

| Pattern | Example | Parsed Episode | Clean Title |
|---------|---------|----------------|-------------|
| `[eN]` | `[e1] Introduction` | 1 | Introduction |
| `[EN]` | `[E2] Setup` | 2 | Setup |
| `Episode N:` | `Episode 3: Automation` | 3 | Automation |
| `Ep N` | `Ep 4 Workflows` | 4 | Workflows |
| `N.` | `5. Advanced` | 5 | Advanced |
| `N -` | `6 - Final` | 6 | Final |
| None | `Bonus Tips` | None | Bonus Tips |

---

## Related Skills

- **ffmpeg** - Video concatenation and processing
- **youtube-description** - Generate descriptions with timestamps
- **google-workspace** - Upload slides and videos to Google Drive
