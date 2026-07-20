#!/usr/bin/env python3
"""
Title Slide Generator
Creates video title slides using PIL + FFmpeg for video course stitching.

Directive: directives/video_course_stitcher.md

Usage:
    python execution/create_title_slides.py --title "Installing Claude Code" --output slide.mp4
    python execution/create_title_slides.py --title "Your First Automation" --duration 3 --resolution 1920x1080
    python execution/create_title_slides.py --titles-file titles.json --output-dir .tmp/slides
"""

import os
import re
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# PIL for image generation (more compatible than FFmpeg drawtext)
from PIL import Image, ImageDraw, ImageFont


def check_ffmpeg() -> str:
    """Check if FFmpeg is installed and return path."""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg found: {version_line}")
            return 'ffmpeg'
    except FileNotFoundError:
        pass
    except subprocess.TimeoutExpired:
        pass

    raise RuntimeError(
        "❌ FFmpeg not found!\n\n"
        "Installation instructions:\n"
        "  macOS:   brew install ffmpeg\n"
        "  Ubuntu:  sudo apt install ffmpeg\n"
        "  Windows: Download from https://ffmpeg.org/download.html\n"
    )


def parse_resolution(resolution: str) -> Tuple[int, int]:
    """Parse resolution string like '1920x1080' into (width, height)."""
    match = re.match(r'(\d+)x(\d+)', resolution)
    if not match:
        raise ValueError(f"Invalid resolution format: {resolution}. Expected format: 1920x1080")
    return int(match.group(1)), int(match.group(2))


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color (#ffffff) to RGB tuple."""
    hex_color = hex_color.strip().lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_system_font(size: int = 72) -> ImageFont.FreeTypeFont:
    """Get a suitable system font for PIL."""
    import platform
    system = platform.system()

    font_paths = {
        'Darwin': [  # macOS
            '/System/Library/Fonts/Helvetica.ttc',
            '/Library/Fonts/Arial.ttf',
            '/System/Library/Fonts/Supplemental/Arial.ttf',
            '/System/Library/Fonts/SFNS.ttf',
        ],
        'Linux': [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
            '/usr/share/fonts/TTF/DejaVuSans-Bold.ttf',
        ],
        'Windows': [
            'C:\\Windows\\Fonts\\arial.ttf',
            'C:\\Windows\\Fonts\\segoeui.ttf',
        ]
    }

    for font_path in font_paths.get(system, []):
        if Path(font_path).exists():
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue

    # Fallback to default font
    try:
        return ImageFont.truetype("Arial", size)
    except Exception:
        return ImageFont.load_default()


def create_title_image(
    title: str,
    output_path: Path,
    width: int = 1920,
    height: int = 1080,
    bg_color: str = '#1a1a2e',
    text_color: str = '#ffffff',
    font_size: int = 72,
) -> Path:
    """
    Create a title slide image using PIL.

    Args:
        title: Text to display
        output_path: Output image path
        width: Image width
        height: Image height
        bg_color: Background color (hex)
        text_color: Text color (hex)
        font_size: Font size in pixels

    Returns:
        Path to created image
    """
    # Create image with background color
    bg_rgb = hex_to_rgb(bg_color)
    text_rgb = hex_to_rgb(text_color)

    image = Image.new('RGB', (width, height), bg_rgb)
    draw = ImageDraw.Draw(image)

    # Get font, adjusting size to fit
    font = get_system_font(font_size)

    # Calculate text size and adjust font if needed
    bbox = draw.textbbox((0, 0), title, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    max_width = width * 0.85
    if text_width > max_width:
        # Reduce font size to fit
        ratio = max_width / text_width
        new_size = int(font_size * ratio)
        font = get_system_font(max(new_size, 36))
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

    # Center text
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Draw text
    draw.text((x, y), title, font=font, fill=text_rgb)

    # Save image
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(str(output_path), 'PNG')

    return output_path


def create_title_slide(
    title: str,
    output_path: Path,
    duration: float = 3.0,
    resolution: str = '1920x1080',
    bg_color: str = '#1a1a2e',
    text_color: str = '#ffffff',
    font_size: int = 72,
    fps: int = 30,
    sample_rate: int = 44100,
) -> Path:
    """
    Create a video title slide with centered text.

    Uses PIL to create the image, then FFmpeg to convert to video.

    Args:
        title: Text to display on slide
        output_path: Output video file path
        duration: Duration in seconds
        resolution: Video resolution (e.g., '1920x1080')
        bg_color: Background color (hex)
        text_color: Text color (hex)
        font_size: Font size in pixels
        fps: Frame rate (should match source videos, typically 30)
        sample_rate: Audio sample rate (should match source, typically 44100)

    Returns:
        Path to created slide video
    """
    check_ffmpeg()

    width, height = parse_resolution(resolution)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create temporary image
    temp_image = output_path.parent / f"{output_path.stem}_temp.png"

    print(f"🎬 Creating slide: {title}")

    # Step 1: Create image with PIL
    create_title_image(
        title=title,
        output_path=temp_image,
        width=width,
        height=height,
        bg_color=bg_color,
        text_color=text_color,
        font_size=font_size,
    )

    # Step 2: Convert image to video with FFmpeg
    # IMPORTANT: fps and sample_rate must match source videos for seamless concat
    cmd = [
        'ffmpeg',
        '-y',  # Overwrite output
        '-loop', '1',  # Loop the image
        '-i', str(temp_image),  # Input image
        '-f', 'lavfi',
        '-i', f'anullsrc=r={sample_rate}:cl=stereo',  # Silent audio
        '-c:v', 'libx264',
        '-t', str(duration),
        '-r', str(fps),  # Frame rate - must match source
        '-pix_fmt', 'yuv420p',
        '-preset', 'fast',
        '-crf', '18',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-ar', str(sample_rate),  # Audio sample rate - must match source
        '-ac', '2',  # Stereo
        '-shortest',
        str(output_path)
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            print(f"   ❌ FFmpeg error: {result.stderr}")
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")

        if output_path.exists():
            size_kb = output_path.stat().st_size / 1024
            print(f"   ✅ Created: {output_path.name} ({size_kb:.1f} KB)")

            # Clean up temp image
            if temp_image.exists():
                temp_image.unlink()

            return output_path
        else:
            raise RuntimeError("Output file was not created")

    except subprocess.TimeoutExpired:
        raise RuntimeError("FFmpeg timed out")
    finally:
        # Clean up temp image on error
        if temp_image.exists():
            try:
                temp_image.unlink()
            except Exception:
                pass


def create_multiple_slides(
    titles: List[Dict],
    output_dir: Path,
    duration: float = 3.0,
    resolution: str = '1920x1080',
    bg_color: str = '#1a1a2e',
    text_color: str = '#ffffff',
    font_size: int = 72,
) -> List[Path]:
    """
    Create multiple title slides.

    Args:
        titles: List of dicts with 'title' and optionally 'filename'
        output_dir: Directory for output files
        Other args same as create_title_slide

    Returns:
        List of paths to created slides
    """
    check_ffmpeg()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"🎬 Creating {len(titles)} title slides...")
    slides = []

    for i, item in enumerate(titles, 1):
        title = item['title']
        filename = item.get('filename', f'slide_{i:03d}.mp4')
        output_path = output_dir / filename

        try:
            slide_path = create_title_slide(
                title=title,
                output_path=output_path,
                duration=duration,
                resolution=resolution,
                bg_color=bg_color,
                text_color=text_color,
                font_size=font_size,
            )
            slides.append(slide_path)
        except Exception as e:
            print(f"   ❌ Failed to create slide for '{title}': {e}")

    print(f"\n✅ Created {len(slides)}/{len(titles)} slides")
    return slides


def parse_video_title(raw_title: str) -> Tuple[Optional[int], str]:
    """
    Parse a video title to extract episode number and clean title.

    Examples:
        "[e1] Introduction to Claude Code" -> (1, "Introduction to Claude Code")
        "[e2] Installing Claude Code" -> (2, "Installing Claude Code")
        "Bonus: Tips and Tricks" -> (None, "Bonus: Tips and Tricks")

    Returns:
        Tuple of (episode_number or None, clean_title)
    """
    # Remove file extension first
    raw_title = Path(raw_title).stem if '.' in raw_title else raw_title

    # Pattern: [eN] or [EN] or [Episode N] at the start
    patterns = [
        r'^\[e(\d+)\]\s*',      # [e1], [e2], etc.
        r'^\[E(\d+)\]\s*',      # [E1], [E2], etc.
        r'^Episode\s*(\d+)[:\.\s]+',  # Episode 1:, Episode 1., Episode 1
        r'^Ep\.?\s*(\d+)[:\.\s]+',    # Ep 1, Ep. 1
        r'^(\d+)\.\s+',               # 1. Title
        r'^(\d+)\s*-\s*',             # 1 - Title
    ]

    for pattern in patterns:
        match = re.match(pattern, raw_title, re.IGNORECASE)
        if match:
            episode_num = int(match.group(1))
            clean_title = raw_title[match.end():].strip()
            return episode_num, clean_title

    # No episode pattern found
    return None, raw_title.strip()


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Create video title slides using PIL + FFmpeg",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Single slide mode
    parser.add_argument("--title", help="Title text for single slide")
    parser.add_argument("--output", help="Output file path (single slide)")

    # Batch mode
    parser.add_argument("--titles-file", help="JSON file with list of titles")
    parser.add_argument("--output-dir", help="Output directory (batch mode)")

    # Style options
    parser.add_argument("--duration", type=float, default=3.0, help="Slide duration in seconds")
    parser.add_argument("--resolution", default="1920x1080", help="Video resolution")
    parser.add_argument("--bg-color", default="#1a1a2e", help="Background color (hex)")
    parser.add_argument("--text-color", default="#ffffff", help="Text color (hex)")
    parser.add_argument("--font-size", type=int, default=72, help="Font size in pixels")

    # Utility
    parser.add_argument("--parse-title", help="Parse a title and show clean version")

    args = parser.parse_args()

    try:
        # Parse title utility
        if args.parse_title:
            ep_num, clean_title = parse_video_title(args.parse_title)
            print(f"Original: {args.parse_title}")
            print(f"Episode:  {ep_num}")
            print(f"Clean:    {clean_title}")
            return 0

        # Single slide mode
        if args.title:
            output = Path(args.output) if args.output else Path(".tmp/slides/slide.mp4")
            create_title_slide(
                title=args.title,
                output_path=output,
                duration=args.duration,
                resolution=args.resolution,
                bg_color=args.bg_color,
                text_color=args.text_color,
                font_size=args.font_size,
            )
            return 0

        # Batch mode
        if args.titles_file:
            with open(args.titles_file) as f:
                titles = json.load(f)
            output_dir = Path(args.output_dir) if args.output_dir else Path(".tmp/slides")
            create_multiple_slides(
                titles=titles,
                output_dir=output_dir,
                duration=args.duration,
                resolution=args.resolution,
                bg_color=args.bg_color,
                text_color=args.text_color,
                font_size=args.font_size,
            )
            return 0

        print("❌ Please provide --title, --titles-file, or --parse-title")
        parser.print_help()
        return 1

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
