#!/usr/bin/env python3
"""
Video Stitcher
Concatenates multiple video files using FFmpeg with optional re-encoding.

Directive: directives/video_course_stitcher.md

Usage:
    python execution/stitch_videos.py --videos video1.mp4 video2.mp4 video3.mp4 --output combined.mp4
    python execution/stitch_videos.py --video-dir .tmp/videos --output course.mp4
    python execution/stitch_videos.py --concat-file concat_list.txt --output combined.mp4 --reencode
"""

import os
import re
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import timedelta


def check_ffmpeg() -> Tuple[str, str]:
    """Check if FFmpeg and FFprobe are installed."""
    for cmd in ['ffmpeg', 'ffprobe']:
        try:
            result = subprocess.run(
                [cmd, '-version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                raise RuntimeError(f"{cmd} returned non-zero exit code")
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            raise RuntimeError(
                f"❌ {cmd} not found!\n\n"
                "Installation instructions:\n"
                "  macOS:   brew install ffmpeg\n"
                "  Ubuntu:  sudo apt install ffmpeg\n"
                "  Windows: Download from https://ffmpeg.org/download.html\n"
            )
    return 'ffmpeg', 'ffprobe'


def get_video_info(video_path: Path) -> Dict:
    """
    Get video metadata using FFprobe.

    Returns dict with: duration, width, height, video_codec, audio_codec, fps
    """
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        str(video_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if result.returncode != 0:
        raise RuntimeError(f"FFprobe failed for {video_path}: {result.stderr}")

    data = json.loads(result.stdout)

    info = {
        'path': str(video_path),
        'duration': float(data.get('format', {}).get('duration', 0)),
        'size_bytes': int(data.get('format', {}).get('size', 0)),
    }

    # Get video stream info
    for stream in data.get('streams', []):
        if stream.get('codec_type') == 'video':
            info['width'] = stream.get('width', 0)
            info['height'] = stream.get('height', 0)
            info['video_codec'] = stream.get('codec_name', 'unknown')
            # Parse fps from avg_frame_rate (e.g., "30/1")
            fps_str = stream.get('avg_frame_rate', '0/1')
            if '/' in fps_str:
                num, den = fps_str.split('/')
                info['fps'] = float(num) / float(den) if float(den) > 0 else 0
            else:
                info['fps'] = float(fps_str)
        elif stream.get('codec_type') == 'audio':
            info['audio_codec'] = stream.get('codec_name', 'unknown')
            info['sample_rate'] = int(stream.get('sample_rate', 0))
            info['audio_channels'] = stream.get('channels', 0)

    return info


def format_duration(seconds: float) -> str:
    """Format seconds as HH:MM:SS or MM:SS."""
    td = timedelta(seconds=int(seconds))
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def create_concat_file(videos: List[Path], concat_file: Path) -> Path:
    """
    Create FFmpeg concat demuxer file.

    Format:
        file 'path/to/video1.mp4'
        file 'path/to/video2.mp4'
    """
    concat_file = Path(concat_file)
    concat_file.parent.mkdir(parents=True, exist_ok=True)

    with open(concat_file, 'w') as f:
        for video in videos:
            # Use absolute paths and escape single quotes
            abs_path = str(Path(video).resolve())
            escaped_path = abs_path.replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")

    print(f"📝 Created concat file: {concat_file}")
    return concat_file


def check_videos_compatible(video_infos: List[Dict]) -> Tuple[bool, str]:
    """
    Check if videos are compatible for stream copy (no re-encoding).

    Returns (compatible, reason)
    """
    if not video_infos:
        return False, "No videos provided"

    first = video_infos[0]
    base_codec = first.get('video_codec')
    base_width = first.get('width')
    base_height = first.get('height')
    base_fps = first.get('fps')

    for i, info in enumerate(video_infos[1:], 2):
        if info.get('video_codec') != base_codec:
            return False, f"Video {i} has codec {info.get('video_codec')}, expected {base_codec}"
        if info.get('width') != base_width or info.get('height') != base_height:
            return False, f"Video {i} has resolution {info.get('width')}x{info.get('height')}, expected {base_width}x{base_height}"
        if abs(info.get('fps', 0) - base_fps) > 0.1:
            return False, f"Video {i} has fps {info.get('fps')}, expected {base_fps}"

    return True, "All videos compatible"


def stitch_videos(
    videos: List[Path],
    output_path: Path,
    reencode: bool = False,
    video_codec: str = 'libx264',
    audio_codec: str = 'aac',
    crf: int = 18,
    preset: str = 'fast',
) -> Tuple[Path, List[Dict]]:
    """
    Concatenate multiple videos into one.

    Args:
        videos: List of video file paths (in order)
        output_path: Output file path
        reencode: Force re-encoding (slower but handles incompatible videos)
        video_codec: Video codec for re-encoding
        audio_codec: Audio codec for re-encoding
        crf: Quality setting (lower = better, 18-23 recommended)
        preset: Encoding speed preset (ultrafast, fast, medium, slow)

    Returns:
        Tuple of (output_path, list of video metadata including timestamps)
    """
    check_ffmpeg()

    if not videos:
        raise ValueError("No videos provided")

    videos = [Path(v) for v in videos]
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get info for all videos
    print(f"📊 Analyzing {len(videos)} videos...")
    video_infos = []
    total_duration = 0

    for video in videos:
        if not video.exists():
            raise FileNotFoundError(f"Video not found: {video}")
        info = get_video_info(video)
        video_infos.append(info)
        total_duration += info['duration']
        print(f"   • {video.name}: {format_duration(info['duration'])} ({info.get('video_codec', 'unknown')})")

    print(f"   Total duration: {format_duration(total_duration)}")

    # Calculate timestamps for each video
    current_timestamp = 0
    for info in video_infos:
        info['start_timestamp'] = current_timestamp
        info['start_timestamp_formatted'] = format_duration(current_timestamp)
        current_timestamp += info['duration']

    # Check compatibility
    compatible, reason = check_videos_compatible(video_infos)
    if not compatible and not reencode:
        print(f"⚠️  Videos not compatible for stream copy: {reason}")
        print("   Will re-encode (this takes longer)")
        reencode = True

    # Create concat demuxer file
    concat_file = output_path.parent / "concat_list.txt"
    create_concat_file(videos, concat_file)

    # Build FFmpeg command
    if reencode:
        print(f"🔄 Re-encoding with {video_codec} / {audio_codec} (CRF {crf}, preset {preset})...")
        cmd = [
            'ffmpeg',
            '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c:v', video_codec,
            '-crf', str(crf),
            '-preset', preset,
            '-c:a', audio_codec,
            '-b:a', '192k',
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            str(output_path)
        ]
    else:
        print("📎 Stream copying (fast mode)...")
        cmd = [
            'ffmpeg',
            '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c', 'copy',
            '-movflags', '+faststart',
            str(output_path)
        ]

    print(f"🎬 Stitching videos...")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout for large videos
        )

        if result.returncode != 0:
            print(f"❌ FFmpeg error: {result.stderr}")
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")

        if output_path.exists():
            final_info = get_video_info(output_path)
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"✅ Created: {output_path}")
            print(f"   Duration: {format_duration(final_info['duration'])}")
            print(f"   Size: {size_mb:.1f} MB")
            return output_path, video_infos
        else:
            raise RuntimeError("Output file was not created")

    except subprocess.TimeoutExpired:
        raise RuntimeError("FFmpeg timed out (exceeded 1 hour)")
    finally:
        # Clean up concat file
        if concat_file.exists():
            concat_file.unlink()


def stitch_with_slides(
    videos: List[Path],
    slides: List[Optional[Path]],
    output_path: Path,
    **kwargs
) -> Tuple[Path, List[Dict]]:
    """
    Stitch videos with title slides between them.

    Args:
        videos: List of main video files
        slides: List of slide videos (same length as videos, None for no slide)
        output_path: Output file path
        **kwargs: Passed to stitch_videos

    Returns:
        Tuple of (output_path, list of segment metadata)
    """
    if len(videos) != len(slides):
        raise ValueError(f"Videos ({len(videos)}) and slides ({len(slides)}) must have same length")

    # Build interleaved list: [slide1, video1, slide2, video2, ...]
    # But slide1 might be None for the intro video
    segments = []
    segment_types = []

    for i, (video, slide) in enumerate(zip(videos, slides)):
        if slide is not None and Path(slide).exists():
            segments.append(Path(slide))
            segment_types.append('slide')
        segments.append(Path(video))
        segment_types.append('video')

    print(f"📋 Stitching {len(segments)} segments ({len(videos)} videos, {sum(1 for s in slides if s)} slides)")

    result_path, segment_infos = stitch_videos(segments, output_path, **kwargs)

    # Add type info to segment metadata
    for info, seg_type in zip(segment_infos, segment_types):
        info['segment_type'] = seg_type

    return result_path, segment_infos


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Concatenate multiple videos using FFmpeg",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Input options
    parser.add_argument("--videos", nargs="+", help="Video files to concatenate (in order)")
    parser.add_argument("--video-dir", help="Directory containing videos (sorted by name)")
    parser.add_argument("--concat-file", help="Pre-made FFmpeg concat file")

    # Output
    parser.add_argument("--output", "-o", required=True, help="Output file path")

    # Encoding options
    parser.add_argument("--reencode", action="store_true", help="Force re-encoding")
    parser.add_argument("--video-codec", default="libx264", help="Video codec")
    parser.add_argument("--audio-codec", default="aac", help="Audio codec")
    parser.add_argument("--crf", type=int, default=18, help="Quality (lower=better)")
    parser.add_argument("--preset", default="fast", help="Encoding speed preset")

    # Utility
    parser.add_argument("--info", help="Just show info for a video file")

    args = parser.parse_args()

    try:
        check_ffmpeg()

        # Info mode
        if args.info:
            info = get_video_info(Path(args.info))
            print(json.dumps(info, indent=2))
            return 0

        # Get video list
        videos = []
        if args.videos:
            videos = [Path(v) for v in args.videos]
        elif args.video_dir:
            video_dir = Path(args.video_dir)
            videos = sorted(video_dir.glob("*.mp4")) + sorted(video_dir.glob("*.mov"))
        elif args.concat_file:
            # Read paths from concat file
            with open(args.concat_file) as f:
                for line in f:
                    if line.strip().startswith("file "):
                        path = line.strip()[5:].strip("'\"")
                        videos.append(Path(path))

        if not videos:
            print("❌ No videos specified. Use --videos, --video-dir, or --concat-file")
            return 1

        print(f"📹 Found {len(videos)} videos")

        stitch_videos(
            videos=videos,
            output_path=Path(args.output),
            reencode=args.reencode,
            video_codec=args.video_codec,
            audio_codec=args.audio_codec,
            crf=args.crf,
            preset=args.preset,
        )

        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
