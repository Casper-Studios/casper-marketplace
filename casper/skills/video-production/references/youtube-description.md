# YouTube Description Generation Reference

## Overview

Generate comprehensive YouTube descriptions with timestamps for video courses. Creates structured descriptions including course outline with clickable timestamps, learning objectives, target audience, and resources.

**Key Capabilities:**
- Generate clickable timestamp chapters from video metadata
- Extract learning topics from lesson titles
- Create structured description with multiple sections
- Support both metadata file input and direct title/duration lists
- Parse clean titles from episode-formatted filenames

**Script Location:** `~/.claude/skills/video-production/scripts/generate_youtube_description.py`

---

## Inputs

### Metadata File Format

```json
{
    "segments": [
        {
            "path": "/path/to/[e1] Introduction.mp4",
            "start_timestamp": 0,
            "duration": 300,
            "segment_type": "video"
        },
        {
            "path": "/path/to/slide.mp4",
            "start_timestamp": 300,
            "duration": 3,
            "segment_type": "slide"
        },
        {
            "path": "/path/to/[e2] Setup.mp4",
            "start_timestamp": 303,
            "duration": 450,
            "segment_type": "video"
        }
    ]
}
```

### Required Parameters (Metadata Mode)

| Parameter | Type | Description |
|-----------|------|-------------|
| `metadata` | Path | Path to video metadata JSON file |

### Required Parameters (Direct Mode)

| Parameter | Type | Description |
|-----------|------|-------------|
| `titles` | List[str] | Video titles in order |
| `durations` | List[float] | Video durations in seconds |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `title` | string | `"Video Course"` | Course title for description |
| `tagline` | string | `""` | Custom hook/tagline (auto-generated if empty) |
| `slide_duration` | float | `3.0` | Duration of title slides between videos |
| `no_skip_first` | bool | `false` | Include slide before first video in calculations |

---

## CLI Usage

### From Metadata File

```bash
# Generate from stitcher metadata output
python ~/.claude/skills/video-production/scripts/generate_youtube_description.py \
    --metadata video_metadata.json \
    --output description.md

# With custom course title
python ~/.claude/skills/video-production/scripts/generate_youtube_description.py \
    --metadata video_metadata.json \
    --title "Claude Code Masterclass" \
    --output description.md

# With custom tagline
python ~/.claude/skills/video-production/scripts/generate_youtube_description.py \
    --metadata video_metadata.json \
    --title "AI Automation Course" \
    --tagline "Go from zero to automating your entire workflow in 2 hours!" \
    --output description.md
```

### From Title and Duration Lists

```bash
# Generate from direct input
python ~/.claude/skills/video-production/scripts/generate_youtube_description.py \
    --titles "Introduction" "Setup" "First Project" "Advanced Topics" \
    --durations 300 450 600 480 \
    --title "Claude Code Course" \
    --output description.md

# With custom slide duration
python ~/.claude/skills/video-production/scripts/generate_youtube_description.py \
    --titles "Lesson 1" "Lesson 2" "Lesson 3" \
    --durations 600 900 750 \
    --slide-duration 2.0 \
    --output description.md

# Print to stdout (no file output)
python ~/.claude/skills/video-production/scripts/generate_youtube_description.py \
    --titles "Part 1" "Part 2" \
    --durations 1800 2400 \
    --title "Complete Workshop"
```

---

## Output Structure

### Generated Description Format

```markdown
Master Claude Code Course in this comprehensive 2.5 hours course - no coding experience required.

This 2.5 hours course takes you from complete beginner to confidently using the tools for real-world tasks. Perfect for non-technical professionals, founders, marketers, and anyone looking to leverage AI for automation.

---

## What You'll Learn

- Getting started and understanding the fundamentals
- Installation and setup process
- Building automated workflows
- Integrating with Google Workspace (Drive, Sheets, Docs)
- Real-world projects you can apply immediately

---

## Course Outline

0:00 - Introduction
5:00 - Installing Claude Code
12:30 - Your First Automation
25:45 - Google Workspace Integration
42:00 - Advanced Workflows

---

## Who This Is For

- Non-technical professionals who want to leverage AI
- Founders and operators looking to automate repetitive tasks
- Marketers who want to scale content and outreach
- Anyone curious about AI automation

No programming experience needed. If you can write an email, you can follow this course.

---

## Resources

- Claude Code: https://claude.ai/claude-code
- Anthropic: https://anthropic.com

---

If you found this helpful, please like and subscribe for more AI automation content!

---

#AI #Automation #NoCode #Tutorial #Productivity #Claude #Anthropic
```

### Timestamp Format

| Duration | Format | Example |
|----------|--------|---------|
| Under 1 hour | `M:SS` | `5:23` |
| 1+ hours | `H:MM:SS` | `1:05:23` |

---

## Error Handling

### Common Errors and Solutions

| Error | Cause | Resolution |
|-------|-------|------------|
| `Number of titles must match durations` | Mismatched input lists | Ensure same number of titles and durations |
| `No segments provided` | Empty or invalid metadata | Verify metadata JSON has `segments` or `videos` array |
| `File not found` | Invalid metadata path | Check file path exists |
| `JSON decode error` | Malformed JSON | Validate JSON syntax |
| `Invalid timestamp` | Negative or invalid duration | Verify all durations are positive numbers |

### Title Parsing Edge Cases

| Input | Parsed Title |
|-------|--------------|
| `[e1] Introduction.mp4` | Introduction |
| `[E2] Setup Guide.mp4` | Setup Guide |
| `Episode 3: Automation.mp4` | Automation |
| `Ep. 4 Workflows.mp4` | Workflows |
| `5. Advanced Topics.mp4` | Advanced Topics |
| `6 - Final Project.mp4` | Final Project |
| `Bonus Tips.mp4` | Bonus Tips |
| `video.mp4` | video |

---

## Testing Checklist

### Pre-flight Verification

```bash
# Verify script runs
python ~/.claude/skills/video-production/scripts/generate_youtube_description.py --help

# Check JSON parsing
python -c "import json; print(json.load(open('metadata.json')))"
```

### Smoke Tests

```bash
# Test with direct input
python ~/.claude/skills/video-production/scripts/generate_youtube_description.py \
    --titles "Intro" "Lesson 1" "Lesson 2" \
    --durations 60 120 180

# Test with metadata file
echo '{"segments":[{"path":"test.mp4","start_timestamp":0,"duration":300}]}' > test_meta.json
python ~/.claude/skills/video-production/scripts/generate_youtube_description.py \
    --metadata test_meta.json

# Test file output
python ~/.claude/skills/video-production/scripts/generate_youtube_description.py \
    --titles "Test" --durations 100 \
    --output .tmp/test_description.md
cat .tmp/test_description.md
```

### Validation Checks

- [ ] Timestamps are in correct format (M:SS or H:MM:SS)
- [ ] Timestamps match expected start times
- [ ] Episode prefixes are stripped from titles
- [ ] Learning topics are extracted correctly
- [ ] Total duration is calculated accurately
- [ ] Output file is valid markdown
- [ ] All sections are present
- [ ] Hashtags are included
- [ ] Resource links are correct

### Timestamp Accuracy Test

```bash
# Compare with FFprobe durations
for video in video1.mp4 video2.mp4; do
    ffprobe -v error -show_entries format=duration \
        -of csv=p=0 "$video"
done

# Generate description and verify timestamps
python generate_youtube_description.py \
    --titles "Video 1" "Video 2" \
    --durations 300 450 \
    --slide-duration 3.0
```

---

## Integration Patterns

### With Video Stitcher Workflow

```python
from pathlib import Path
import json
from stitch_videos import stitch_videos
from generate_youtube_description import generate_youtube_description

# Step 1: Stitch videos
output_path, segment_infos = stitch_videos(
    videos=[Path("intro.mp4"), Path("lesson1.mp4"), Path("lesson2.mp4")],
    output_path=Path(".tmp/course.mp4")
)

# Step 2: Generate description
description = generate_youtube_description(
    video_segments=segment_infos,
    course_title="Claude Code Masterclass",
    course_tagline="Master AI automation in under 3 hours!"
)

# Step 3: Save description
with open(".tmp/youtube_description.md", "w") as f:
    f.write(description)

# Step 4: Save metadata for later use
metadata = {
    "output_video": str(output_path),
    "segments": segment_infos,
    "description": description
}
with open(".tmp/course_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)
```

### With Title Slides Workflow

```python
from pathlib import Path
from create_title_slides import create_title_slide, parse_video_title
from stitch_videos import stitch_with_slides
from generate_youtube_description import generate_youtube_description

# Step 1: Parse video titles
videos = [
    Path("[e1] Introduction.mp4"),
    Path("[e2] Setup.mp4"),
    Path("[e3] Automation.mp4")
]

# Step 2: Generate slides
slides = []
for i, video in enumerate(videos):
    if i == 0:
        slides.append(None)  # No slide before intro
    else:
        _, clean_title = parse_video_title(video.name)
        slide_path = Path(f".tmp/slides/slide_{i}.mp4")
        create_title_slide(clean_title, slide_path)
        slides.append(slide_path)

# Step 3: Stitch with slides
output_path, segment_infos = stitch_with_slides(
    videos=videos,
    slides=slides,
    output_path=Path(".tmp/course.mp4")
)

# Step 4: Generate description (excludes slide timestamps by default)
description = generate_youtube_description(
    video_segments=segment_infos,
    course_title="Complete Claude Code Course",
    include_slide_timestamps=False  # Only show video start times
)
```

### Learning Topic Extraction

The script automatically extracts learning topics from lesson titles:

| Title Contains | Generated Topic |
|----------------|-----------------|
| introduction, intro | Getting started and understanding the fundamentals |
| install, setup | Installation and setup process |
| google | Integrating with Google Workspace (Drive, Sheets, Docs) |
| workflow, automat | Building automated workflows |
| website, web | Creating websites with AI assistance |
| context, tool | Understanding context and available tools |
| outreach | AI-powered outreach and communication |
| project | Hands-on project work |
| (other) | Title used as-is |

---

## Customization

### Custom Description Template

```python
from generate_youtube_description import format_timestamp

def custom_description(segments, course_title):
    lines = []

    # Custom intro
    lines.append(f"Welcome to {course_title}!")
    lines.append("")

    # Custom timestamp section
    lines.append("CHAPTERS:")
    for seg in segments:
        if seg.get('segment_type') != 'slide':
            ts = format_timestamp(seg['start_timestamp'])
            title = Path(seg['path']).stem
            lines.append(f"{ts} {title}")

    # Custom CTA
    lines.append("")
    lines.append("SUBSCRIBE for more content!")

    return "\n".join(lines)
```

### Duration Formatting

```python
from generate_youtube_description import format_timestamp, format_duration_human

# Timestamp for chapters
format_timestamp(3600)  # "1:00:00"
format_timestamp(65)    # "1:05"

# Human-readable duration
format_duration_human(3600)   # "1 hours"
format_duration_human(5400)   # "1.5 hours"
format_duration_human(1800)   # "30 minutes"
```

---

## Related Skills

- **ffmpeg** - Video stitching that generates segment metadata
- **title-slides** - Generate title slides for video courses
- **content-generation** - Additional content generation patterns
- **google-workspace** - Upload descriptions alongside videos
