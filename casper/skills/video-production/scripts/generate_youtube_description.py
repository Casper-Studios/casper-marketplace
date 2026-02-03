#!/usr/bin/env python3
"""
YouTube Description Generator
Creates comprehensive YouTube descriptions with timestamps for course videos.

Directive: directives/video_course_stitcher.md

Usage:
    python execution/generate_youtube_description.py --metadata video_metadata.json --output description.md
    python execution/generate_youtube_description.py --metadata video_metadata.json --title "Claude Code Course" --output description.md
"""

import json
import argparse
from pathlib import Path
from datetime import timedelta
from typing import Dict, List, Optional


def format_timestamp(seconds: float) -> str:
    """
    Format seconds as timestamp for YouTube.

    YouTube accepts: H:MM:SS, HH:MM:SS, M:SS, MM:SS
    """
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def format_duration_human(seconds: float) -> str:
    """Format duration as human-readable string (e.g., '2.5 hours')."""
    hours = seconds / 3600
    if hours >= 1:
        return f"{hours:.1f} hours" if hours != int(hours) else f"{int(hours)} hours"
    else:
        minutes = seconds / 60
        return f"{int(minutes)} minutes"


def parse_clean_title(raw_title: str) -> str:
    """
    Extract clean title from video filename.

    Examples:
        "[e1] Introduction to Claude Code.mp4" -> "Introduction to Claude Code"
        "[e2] Installing Claude Code.mp4" -> "Installing Claude Code"
        "Bonus Tips.mp4" -> "Bonus Tips"
    """
    import re

    # Remove file extension
    title = Path(raw_title).stem

    # Remove episode prefixes
    patterns = [
        r'^\[e\d+\]\s*',        # [e1], [e2], etc.
        r'^\[E\d+\]\s*',        # [E1], [E2], etc.
        r'^Episode\s*\d+[:\.\s]+',  # Episode 1:, Episode 1.
        r'^Ep\.?\s*\d+[:\.\s]+',    # Ep 1, Ep. 1
        r'^\d+\.\s+',               # 1. Title
        r'^\d+\s*-\s*',             # 1 - Title
    ]

    for pattern in patterns:
        title = re.sub(pattern, '', title, flags=re.IGNORECASE)

    return title.strip()


def extract_lesson_topics(clean_titles: List[str]) -> List[str]:
    """Extract key learning topics from lesson titles."""
    topics = []
    for title in clean_titles:
        # Convert title to a "what you'll learn" bullet point
        title_lower = title.lower()
        if 'introduction' in title_lower or 'intro' in title_lower:
            topics.append("Getting started and understanding the fundamentals")
        elif 'install' in title_lower or 'setup' in title_lower:
            topics.append("Installation and setup process")
        elif 'google' in title_lower:
            topics.append("Integrating with Google Workspace (Drive, Sheets, Docs)")
        elif 'workflow' in title_lower or 'automat' in title_lower:
            topics.append("Building automated workflows")
        elif 'website' in title_lower or 'web' in title_lower:
            topics.append("Creating websites with AI assistance")
        elif 'context' in title_lower or 'tool' in title_lower:
            topics.append("Understanding context and available tools")
        elif 'outreach' in title_lower:
            topics.append("AI-powered outreach and communication")
        elif 'project' in title_lower:
            topics.append("Hands-on project work")
        else:
            # Generic topic extraction
            topics.append(title)

    # Remove duplicates while preserving order
    seen = set()
    unique_topics = []
    for topic in topics:
        if topic not in seen:
            seen.add(topic)
            unique_topics.append(topic)

    return unique_topics[:6]  # Limit to 6 topics


def generate_youtube_description(
    video_segments: List[Dict],
    course_title: str = "Video Course",
    course_tagline: str = "",
    total_duration: float = 0,
    include_slide_timestamps: bool = False,
) -> str:
    """
    Generate a comprehensive YouTube description with timestamps.

    Args:
        video_segments: List of segment metadata (from stitch_videos output)
        course_title: Title for the course
        course_tagline: Short tagline/hook for the course
        total_duration: Total duration in seconds (calculated if not provided)
        include_slide_timestamps: Whether to show slide timestamps (usually False)

    Returns:
        Formatted YouTube description
    """
    lines = []

    # Collect lesson info
    lessons = []
    for segment in video_segments:
        if segment.get('segment_type') == 'slide' and not include_slide_timestamps:
            continue

        timestamp = format_timestamp(segment.get('start_timestamp', 0))
        raw_title = segment.get('path', 'Untitled')
        clean_title = parse_clean_title(Path(raw_title).name)
        duration = segment.get('duration', 0)

        lessons.append({
            'timestamp': timestamp,
            'title': clean_title,
            'duration': duration,
        })

    # Calculate total duration if not provided
    if total_duration == 0 and lessons:
        total_duration = sum(l['duration'] for l in lessons)

    duration_str = format_duration_human(total_duration)
    clean_titles = [l['title'] for l in lessons]
    learning_topics = extract_lesson_topics(clean_titles)

    # === HOOK / INTRO ===
    if course_tagline:
        lines.append(course_tagline)
    else:
        lines.append(f"Master {course_title} in this comprehensive {duration_str} course - no coding experience required.")
    lines.append("")
    lines.append(f"This {duration_str} course takes you from complete beginner to confidently using the tools for real-world tasks. Perfect for non-technical professionals, founders, marketers, and anyone looking to leverage AI for automation.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # === WHAT YOU'LL LEARN ===
    lines.append("## What You'll Learn")
    lines.append("")
    for topic in learning_topics:
        lines.append(f"- {topic}")
    lines.append("- Real-world projects you can apply immediately")
    lines.append("")
    lines.append("---")
    lines.append("")

    # === COURSE OUTLINE (TIMESTAMPS) ===
    lines.append("## Course Outline")
    lines.append("")
    for lesson in lessons:
        lines.append(f"{lesson['timestamp']} - {lesson['title']}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # === WHO THIS IS FOR ===
    lines.append("## Who This Is For")
    lines.append("")
    lines.append("- Non-technical professionals who want to leverage AI")
    lines.append("- Founders and operators looking to automate repetitive tasks")
    lines.append("- Marketers who want to scale content and outreach")
    lines.append("- Anyone curious about AI automation")
    lines.append("")
    lines.append("No programming experience needed. If you can write an email, you can follow this course.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # === RESOURCES ===
    lines.append("## Resources")
    lines.append("")
    lines.append("- Claude Code: https://claude.ai/claude-code")
    lines.append("- Anthropic: https://anthropic.com")
    lines.append("")
    lines.append("---")
    lines.append("")

    # === CTA ===
    lines.append("If you found this helpful, please like and subscribe for more AI automation content!")
    lines.append("")
    lines.append("---")
    lines.append("")

    # === HASHTAGS ===
    lines.append("#AI #Automation #NoCode #Tutorial #Productivity #Claude #Anthropic")

    return "\n".join(lines)


def generate_from_metadata_file(
    metadata_path: Path,
    course_title: str = "Video Course",
    course_tagline: str = "",
) -> str:
    """
    Generate description from a metadata JSON file.

    Expected format:
    {
        "segments": [
            {
                "path": "/path/to/video.mp4",
                "start_timestamp": 0,
                "duration": 300,
                "segment_type": "video"  # or "slide"
            },
            ...
        ]
    }
    """
    with open(metadata_path) as f:
        data = json.load(f)

    segments = data.get('segments', data.get('videos', []))

    return generate_youtube_description(
        video_segments=segments,
        course_title=course_title,
        course_tagline=course_tagline,
    )


def generate_simple_description(
    video_titles: List[str],
    video_durations: List[float],
    course_title: str = "Video Course",
    course_tagline: str = "",
    slide_duration: float = 3.0,
    skip_first_slide: bool = True,
) -> str:
    """
    Generate description from simple lists of titles and durations.

    This is useful when you have the raw data before stitching.

    Args:
        video_titles: List of video titles (in order)
        video_durations: List of video durations in seconds
        course_title: Title for the course
        course_tagline: Short tagline for the course
        slide_duration: Duration of title slides between videos
        skip_first_slide: Whether first video has no preceding slide

    Returns:
        Formatted YouTube description
    """
    # Build segments list
    segments = []
    current_time = 0

    for i, (title, duration) in enumerate(zip(video_titles, video_durations)):
        # Add slide duration (except for first video if skip_first_slide)
        if i > 0:
            current_time += slide_duration

        segments.append({
            'path': title,
            'start_timestamp': current_time,
            'duration': duration,
            'segment_type': 'video',
        })

        current_time += duration

    return generate_youtube_description(
        video_segments=segments,
        course_title=course_title,
        course_tagline=course_tagline,
        total_duration=current_time,
    )


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive YouTube description with timestamps",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Input options
    parser.add_argument("--metadata", help="Path to video metadata JSON file")
    parser.add_argument("--titles", nargs="+", help="Video titles (in order)")
    parser.add_argument("--durations", nargs="+", type=float, help="Video durations in seconds")

    # Course info
    parser.add_argument("--title", default="Video Course", help="Course title")
    parser.add_argument("--tagline", default="", help="Course tagline/hook")

    # Options
    parser.add_argument("--slide-duration", type=float, default=3.0, help="Slide duration")
    parser.add_argument("--no-skip-first", action="store_true", help="Include slide before first video")

    # Output
    parser.add_argument("--output", "-o", help="Output file path (prints to stdout if not specified)")

    args = parser.parse_args()

    try:
        description = None

        if args.metadata:
            # Generate from metadata file
            description = generate_from_metadata_file(
                metadata_path=Path(args.metadata),
                course_title=args.title,
                course_tagline=args.tagline,
            )
        elif args.titles and args.durations:
            # Generate from titles and durations
            if len(args.titles) != len(args.durations):
                print("❌ Number of titles must match number of durations")
                return 1

            description = generate_simple_description(
                video_titles=args.titles,
                video_durations=args.durations,
                course_title=args.title,
                course_tagline=args.tagline,
                slide_duration=args.slide_duration,
                skip_first_slide=not args.no_skip_first,
            )
        else:
            print("❌ Please provide --metadata or both --titles and --durations")
            parser.print_help()
            return 1

        # Output
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(description)
            print(f"✅ Description saved to: {output_path}")
        else:
            print(description)

        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
