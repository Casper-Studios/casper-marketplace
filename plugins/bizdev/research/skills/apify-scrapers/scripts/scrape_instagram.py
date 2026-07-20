#!/usr/bin/env python3
"""
Instagram Scraper
Comprehensive Instagram scraper supporting multiple modes using Apify actors.

Usage:
    # Scrape profile data
    python scrape_instagram.py profile username1 username2 --output profile.json

    # Scrape posts from profiles
    python scrape_instagram.py posts username1 --max-posts 50 --output posts.json

    # Scrape hashtag posts
    python scrape_instagram.py hashtag ai machinelearning --max-posts 100 --output hashtag.json

    # Scrape reels from profile
    python scrape_instagram.py reels username --max-reels 20 --output reels.json

    # Scrape comments on a post
    python scrape_instagram.py comments https://www.instagram.com/p/ABC123/ --max-comments 100 --output comments.json
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from apify_client import ApifyClient
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

# Configuration
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
OUTPUT_DIR = Path(__file__).parent.parent / ".tmp"

# Apify Actor IDs for different Instagram scraping modes
ACTORS = {
    "profile": "apify/instagram-profile-scraper",
    "posts": "apify/instagram-scraper",
    "hashtag": "apify/instagram-hashtag-scraper",
    "reels": "apify/instagram-reel-scraper",
    "comments": "apify/instagram-comment-scraper"
}


def validate_environment():
    """Validate required environment variables."""
    if not APIFY_TOKEN:
        raise ValueError(
            "APIFY_TOKEN not found in environment. "
            "Please add it to your .env file."
        )


def validate_instagram_url(url: str) -> bool:
    """
    Validate Instagram post/reel URL format.

    Args:
        url: URL to validate

    Returns:
        bool: True if valid Instagram URL
    """
    pattern = r'^https?://(www\.)?instagram\.com/(p|reel|reels)/[\w-]+/?'
    return bool(re.match(pattern, url))


def normalize_username(username: str) -> str:
    """
    Normalize Instagram username (remove @ prefix if present).

    Args:
        username: Instagram username

    Returns:
        str: Normalized username
    """
    return username.lstrip('@')


def build_profile_url(username: str) -> str:
    """Build Instagram profile URL from username."""
    return f"https://www.instagram.com/{normalize_username(username)}/"


def run_profile_scraper(usernames: list) -> dict:
    """
    Scrape Instagram profile data.

    Args:
        usernames: List of Instagram usernames

    Returns:
        dict: Scraper results with profile data
    """
    print(f"Starting Instagram profile scraper")
    print(f"Profiles: {usernames}")

    client = ApifyClient(APIFY_TOKEN)

    # Build profile URLs
    profile_urls = [build_profile_url(u) for u in usernames]

    run_input = {
        "usernames": [normalize_username(u) for u in usernames]
    }

    print(f"Running Actor: {ACTORS['profile']}")

    try:
        run = client.actor(ACTORS['profile']).call(run_input=run_input)

        print(f"Actor run completed!")
        print(f"Run ID: {run['id']}")

        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        return {
            "success": True,
            "run_id": run['id'],
            "dataset_id": run["defaultDatasetId"],
            "items": dataset_items,
            "count": len(dataset_items),
            "mode": "profile",
            "query": usernames
        }

    except Exception as e:
        print(f"Actor run failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "items": [],
            "count": 0,
            "mode": "profile",
            "query": usernames
        }


def run_posts_scraper(usernames: list, max_posts: int = 50) -> dict:
    """
    Scrape Instagram posts from profiles.

    Args:
        usernames: List of Instagram usernames
        max_posts: Maximum posts to scrape per profile

    Returns:
        dict: Scraper results with post data
    """
    print(f"Starting Instagram posts scraper")
    print(f"Profiles: {usernames}")
    print(f"Max posts per profile: {max_posts}")

    client = ApifyClient(APIFY_TOKEN)

    # Build profile URLs for direct URLs input
    direct_urls = [build_profile_url(u) for u in usernames]

    run_input = {
        "directUrls": direct_urls,
        "resultsLimit": max_posts,
        "resultsType": "posts",
        "searchType": "user",
        "searchLimit": 1
    }

    print(f"Running Actor: {ACTORS['posts']}")

    try:
        run = client.actor(ACTORS['posts']).call(run_input=run_input)

        print(f"Actor run completed!")
        print(f"Run ID: {run['id']}")

        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        return {
            "success": True,
            "run_id": run['id'],
            "dataset_id": run["defaultDatasetId"],
            "items": dataset_items,
            "count": len(dataset_items),
            "mode": "posts",
            "query": usernames
        }

    except Exception as e:
        print(f"Actor run failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "items": [],
            "count": 0,
            "mode": "posts",
            "query": usernames
        }


def run_hashtag_scraper(hashtags: list, max_posts: int = 100) -> dict:
    """
    Scrape Instagram posts by hashtag.

    Args:
        hashtags: List of hashtags to search (without #)
        max_posts: Maximum posts to scrape per hashtag

    Returns:
        dict: Scraper results with post data
    """
    print(f"Starting Instagram hashtag scraper")
    print(f"Hashtags: {hashtags}")
    print(f"Max posts per hashtag: {max_posts}")

    client = ApifyClient(APIFY_TOKEN)

    # Clean hashtags (remove # if present)
    clean_hashtags = [h.lstrip('#') for h in hashtags]

    run_input = {
        "hashtags": clean_hashtags,
        "resultsLimit": max_posts,
        "resultsType": "posts"
    }

    print(f"Running Actor: {ACTORS['hashtag']}")

    try:
        run = client.actor(ACTORS['hashtag']).call(run_input=run_input)

        print(f"Actor run completed!")
        print(f"Run ID: {run['id']}")

        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        return {
            "success": True,
            "run_id": run['id'],
            "dataset_id": run["defaultDatasetId"],
            "items": dataset_items,
            "count": len(dataset_items),
            "mode": "hashtag",
            "query": clean_hashtags
        }

    except Exception as e:
        print(f"Actor run failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "items": [],
            "count": 0,
            "mode": "hashtag",
            "query": clean_hashtags
        }


def run_reels_scraper(usernames: list, max_reels: int = 20) -> dict:
    """
    Scrape Instagram reels from profiles.

    Args:
        usernames: List of Instagram usernames
        max_reels: Maximum reels to scrape per profile

    Returns:
        dict: Scraper results with reel data
    """
    print(f"Starting Instagram reels scraper")
    print(f"Profiles: {usernames}")
    print(f"Max reels per profile: {max_reels}")

    client = ApifyClient(APIFY_TOKEN)

    # Build profile URLs
    profile_urls = [build_profile_url(u) for u in usernames]

    run_input = {
        "usernames": [normalize_username(u) for u in usernames],
        "resultsLimit": max_reels
    }

    print(f"Running Actor: {ACTORS['reels']}")

    try:
        run = client.actor(ACTORS['reels']).call(run_input=run_input)

        print(f"Actor run completed!")
        print(f"Run ID: {run['id']}")

        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        return {
            "success": True,
            "run_id": run['id'],
            "dataset_id": run["defaultDatasetId"],
            "items": dataset_items,
            "count": len(dataset_items),
            "mode": "reels",
            "query": usernames
        }

    except Exception as e:
        print(f"Actor run failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "items": [],
            "count": 0,
            "mode": "reels",
            "query": usernames
        }


def run_comments_scraper(post_urls: list, max_comments: int = 100) -> dict:
    """
    Scrape comments from Instagram posts.

    Args:
        post_urls: List of Instagram post URLs
        max_comments: Maximum comments to scrape per post

    Returns:
        dict: Scraper results with comment data
    """
    print(f"Starting Instagram comments scraper")
    print(f"Posts: {post_urls}")
    print(f"Max comments per post: {max_comments}")

    client = ApifyClient(APIFY_TOKEN)

    # Validate URLs
    for url in post_urls:
        if not validate_instagram_url(url):
            print(f"Warning: '{url}' may not be a valid Instagram post URL")

    run_input = {
        "directUrls": post_urls,
        "resultsLimit": max_comments
    }

    print(f"Running Actor: {ACTORS['comments']}")

    try:
        run = client.actor(ACTORS['comments']).call(run_input=run_input)

        print(f"Actor run completed!")
        print(f"Run ID: {run['id']}")

        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        return {
            "success": True,
            "run_id": run['id'],
            "dataset_id": run["defaultDatasetId"],
            "items": dataset_items,
            "count": len(dataset_items),
            "mode": "comments",
            "query": post_urls
        }

    except Exception as e:
        print(f"Actor run failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "items": [],
            "count": 0,
            "mode": "comments",
            "query": post_urls
        }


def process_profile_results(results: dict) -> dict:
    """Process profile scraper results."""
    processed_profiles = []

    for item in results["items"]:
        profile = {
            "username": item.get("username", ""),
            "full_name": item.get("fullName", ""),
            "biography": item.get("biography", ""),
            "external_url": item.get("externalUrl", ""),
            "followers_count": item.get("followersCount", 0),
            "following_count": item.get("followsCount", 0),
            "posts_count": item.get("postsCount", 0),
            "is_verified": item.get("verified", False),
            "is_private": item.get("private", False),
            "is_business": item.get("isBusinessAccount", False),
            "business_category": item.get("businessCategoryName", ""),
            "profile_pic_url": item.get("profilePicUrl", ""),
            "profile_pic_url_hd": item.get("profilePicUrlHD", ""),
            "profile_url": f"https://www.instagram.com/{item.get('username', '')}/",
            "id": item.get("id", "")
        }
        processed_profiles.append(profile)

    return {
        "scraped_at": datetime.now().isoformat(),
        "platform": "instagram",
        "mode": "profile",
        "total_count": len(processed_profiles),
        "query": results.get("query", []),
        "run_id": results.get("run_id", ""),
        "data": processed_profiles
    }


def process_posts_results(results: dict) -> dict:
    """Process posts scraper results."""
    processed_posts = []

    for item in results["items"]:
        # Handle different response structures
        owner = item.get("ownerUsername") or item.get("owner", {}).get("username", "")

        post = {
            "id": item.get("id", ""),
            "shortcode": item.get("shortCode", "") or item.get("shortcode", ""),
            "caption": item.get("caption", ""),
            "owner_username": owner,
            "timestamp": item.get("timestamp", ""),
            "likes_count": item.get("likesCount", 0) or item.get("likes", 0),
            "comments_count": item.get("commentsCount", 0) or item.get("comments", 0),
            "video_view_count": item.get("videoViewCount", 0),
            "video_play_count": item.get("videoPlayCount", 0),
            "is_video": item.get("isVideo", False) or item.get("type") == "Video",
            "type": item.get("type", "Image"),
            "display_url": item.get("displayUrl", "") or item.get("url", ""),
            "video_url": item.get("videoUrl", ""),
            "post_url": item.get("url", "") or f"https://www.instagram.com/p/{item.get('shortCode', '')}/",
            "location": item.get("locationName", ""),
            "hashtags": item.get("hashtags", []),
            "mentions": item.get("mentions", []),
            "engagement_score": (item.get("likesCount", 0) or item.get("likes", 0)) +
                               (item.get("commentsCount", 0) or item.get("comments", 0)) * 2
        }
        processed_posts.append(post)

    # Sort by engagement
    processed_posts.sort(key=lambda x: x["engagement_score"], reverse=True)

    return {
        "scraped_at": datetime.now().isoformat(),
        "platform": "instagram",
        "mode": "posts",
        "total_count": len(processed_posts),
        "query": results.get("query", []),
        "run_id": results.get("run_id", ""),
        "data": processed_posts
    }


def process_hashtag_results(results: dict) -> dict:
    """Process hashtag scraper results."""
    processed_posts = []

    for item in results["items"]:
        owner = item.get("ownerUsername") or item.get("owner", {}).get("username", "")

        post = {
            "id": item.get("id", ""),
            "shortcode": item.get("shortCode", "") or item.get("shortcode", ""),
            "caption": item.get("caption", ""),
            "owner_username": owner,
            "timestamp": item.get("timestamp", ""),
            "likes_count": item.get("likesCount", 0) or item.get("likes", 0),
            "comments_count": item.get("commentsCount", 0) or item.get("comments", 0),
            "video_view_count": item.get("videoViewCount", 0),
            "is_video": item.get("isVideo", False) or item.get("type") == "Video",
            "type": item.get("type", "Image"),
            "display_url": item.get("displayUrl", "") or item.get("url", ""),
            "video_url": item.get("videoUrl", ""),
            "post_url": item.get("url", "") or f"https://www.instagram.com/p/{item.get('shortCode', '')}/",
            "hashtags": item.get("hashtags", []),
            "source_hashtag": item.get("hashtag", ""),
            "engagement_score": (item.get("likesCount", 0) or item.get("likes", 0)) +
                               (item.get("commentsCount", 0) or item.get("comments", 0)) * 2
        }
        processed_posts.append(post)

    # Sort by engagement
    processed_posts.sort(key=lambda x: x["engagement_score"], reverse=True)

    return {
        "scraped_at": datetime.now().isoformat(),
        "platform": "instagram",
        "mode": "hashtag",
        "total_count": len(processed_posts),
        "query": results.get("query", []),
        "run_id": results.get("run_id", ""),
        "data": processed_posts
    }


def process_reels_results(results: dict) -> dict:
    """Process reels scraper results."""
    processed_reels = []

    for item in results["items"]:
        owner = item.get("ownerUsername") or item.get("owner", {}).get("username", "")

        reel = {
            "id": item.get("id", ""),
            "shortcode": item.get("shortCode", "") or item.get("shortcode", ""),
            "caption": item.get("caption", ""),
            "owner_username": owner,
            "timestamp": item.get("timestamp", ""),
            "likes_count": item.get("likesCount", 0) or item.get("likes", 0),
            "comments_count": item.get("commentsCount", 0) or item.get("comments", 0),
            "play_count": item.get("videoPlayCount", 0) or item.get("playCount", 0),
            "view_count": item.get("videoViewCount", 0) or item.get("viewCount", 0),
            "duration": item.get("videoDuration", 0) or item.get("duration", 0),
            "video_url": item.get("videoUrl", ""),
            "thumbnail_url": item.get("displayUrl", "") or item.get("thumbnailUrl", ""),
            "reel_url": item.get("url", "") or f"https://www.instagram.com/reel/{item.get('shortCode', '')}/",
            "audio_title": item.get("musicInfo", {}).get("song_name", "") if item.get("musicInfo") else "",
            "audio_artist": item.get("musicInfo", {}).get("artist_name", "") if item.get("musicInfo") else "",
            "hashtags": item.get("hashtags", []),
            "engagement_score": (item.get("likesCount", 0) or item.get("likes", 0)) +
                               (item.get("commentsCount", 0) or item.get("comments", 0)) * 2 +
                               (item.get("videoPlayCount", 0) or item.get("playCount", 0)) // 100
        }
        processed_reels.append(reel)

    # Sort by engagement
    processed_reels.sort(key=lambda x: x["engagement_score"], reverse=True)

    return {
        "scraped_at": datetime.now().isoformat(),
        "platform": "instagram",
        "mode": "reels",
        "total_count": len(processed_reels),
        "query": results.get("query", []),
        "run_id": results.get("run_id", ""),
        "data": processed_reels
    }


def process_comments_results(results: dict) -> dict:
    """Process comments scraper results."""
    processed_comments = []

    for item in results["items"]:
        comment = {
            "id": item.get("id", ""),
            "text": item.get("text", ""),
            "owner_username": item.get("ownerUsername", "") or item.get("owner", {}).get("username", ""),
            "owner_profile_pic": item.get("ownerProfilePicUrl", ""),
            "timestamp": item.get("timestamp", ""),
            "likes_count": item.get("likesCount", 0) or item.get("likes", 0),
            "replies_count": item.get("repliesCount", 0),
            "post_shortcode": item.get("postShortCode", "") or item.get("shortcode", ""),
            "post_url": item.get("postUrl", ""),
            "is_reply": item.get("isReply", False),
            "parent_comment_id": item.get("parentCommentId", "")
        }
        processed_comments.append(comment)

    # Sort by likes
    processed_comments.sort(key=lambda x: x["likes_count"], reverse=True)

    return {
        "scraped_at": datetime.now().isoformat(),
        "platform": "instagram",
        "mode": "comments",
        "total_count": len(processed_comments),
        "query": results.get("query", []),
        "run_id": results.get("run_id", ""),
        "data": processed_comments
    }


def process_results(results: dict) -> dict:
    """
    Route to appropriate processor based on mode.

    Args:
        results: Raw results from Apify

    Returns:
        dict: Processed data
    """
    mode = results.get("mode", "")

    processors = {
        "profile": process_profile_results,
        "posts": process_posts_results,
        "hashtag": process_hashtag_results,
        "reels": process_reels_results,
        "comments": process_comments_results
    }

    processor = processors.get(mode)
    if processor:
        return processor(results)
    else:
        # Generic fallback
        return {
            "scraped_at": datetime.now().isoformat(),
            "platform": "instagram",
            "mode": mode,
            "total_count": len(results.get("items", [])),
            "query": results.get("query", []),
            "run_id": results.get("run_id", ""),
            "data": results.get("items", [])
        }


def save_results(data: dict, filename: str = None) -> Path:
    """
    Save results to .tmp directory.

    Args:
        data: Processed data
        filename: Custom filename (optional)

    Returns:
        Path: Output file path
    """
    OUTPUT_DIR.mkdir(exist_ok=True)

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        mode = data.get("mode", "instagram")
        filename = f"instagram_{mode}_{timestamp}.json"

    output_path = OUTPUT_DIR / filename

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_path}")
    print(f"Total items: {data['total_count']}")

    # Print preview based on mode
    mode = data.get("mode", "")
    items = data.get("data", [])

    if mode == "profile" and items:
        print("\nProfile Summary:")
        for profile in items[:5]:
            print(f"\n  @{profile['username']} ({profile['full_name']})")
            print(f"  Followers: {profile['followers_count']:,} | Following: {profile['following_count']:,}")
            print(f"  Posts: {profile['posts_count']:,} | Verified: {profile['is_verified']}")

    elif mode == "posts" and items:
        print("\nTop Posts by Engagement:")
        for i, post in enumerate(items[:5], 1):
            caption_preview = (post['caption'][:80] + "...") if post['caption'] and len(post['caption']) > 80 else (post['caption'] or "(no caption)")
            caption_preview = caption_preview.replace('\n', ' ')
            print(f"\n  {i}. @{post['owner_username']}")
            print(f"     {caption_preview}")
            print(f"     Likes: {post['likes_count']:,} | Comments: {post['comments_count']:,}")

    elif mode == "hashtag" and items:
        print("\nTop Hashtag Posts:")
        for i, post in enumerate(items[:5], 1):
            caption_preview = (post['caption'][:80] + "...") if post['caption'] and len(post['caption']) > 80 else (post['caption'] or "(no caption)")
            caption_preview = caption_preview.replace('\n', ' ')
            print(f"\n  {i}. #{post.get('source_hashtag', '')} - @{post['owner_username']}")
            print(f"     {caption_preview}")
            print(f"     Likes: {post['likes_count']:,} | Comments: {post['comments_count']:,}")

    elif mode == "reels" and items:
        print("\nTop Reels by Engagement:")
        for i, reel in enumerate(items[:5], 1):
            caption_preview = (reel['caption'][:80] + "...") if reel['caption'] and len(reel['caption']) > 80 else (reel['caption'] or "(no caption)")
            caption_preview = caption_preview.replace('\n', ' ')
            print(f"\n  {i}. @{reel['owner_username']}")
            print(f"     {caption_preview}")
            print(f"     Plays: {reel['play_count']:,} | Likes: {reel['likes_count']:,}")

    elif mode == "comments" and items:
        print("\nTop Comments by Likes:")
        for i, comment in enumerate(items[:5], 1):
            text_preview = (comment['text'][:80] + "...") if len(comment['text']) > 80 else comment['text']
            text_preview = text_preview.replace('\n', ' ')
            print(f"\n  {i}. @{comment['owner_username']}")
            print(f"     {text_preview}")
            print(f"     Likes: {comment['likes_count']:,}")

    return output_path


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Scrape Instagram profiles, posts, hashtags, reels, and comments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape profile data
  python scrape_instagram.py profile cristiano messi --output profiles.json

  # Scrape posts from a profile
  python scrape_instagram.py posts natgeo --max-posts 50

  # Scrape hashtag posts
  python scrape_instagram.py hashtag travel photography --max-posts 100

  # Scrape reels
  python scrape_instagram.py reels redbull --max-reels 20

  # Scrape comments from a post
  python scrape_instagram.py comments "https://www.instagram.com/p/ABC123/" --max-comments 100
        """
    )

    subparsers = parser.add_subparsers(dest="mode", help="Scraping mode")

    # Profile mode
    profile_parser = subparsers.add_parser("profile", help="Scrape profile data")
    profile_parser.add_argument(
        "usernames",
        nargs="+",
        help="Instagram usernames to scrape"
    )
    profile_parser.add_argument(
        "--output",
        help="Custom output filename"
    )

    # Posts mode
    posts_parser = subparsers.add_parser("posts", help="Scrape posts from profiles")
    posts_parser.add_argument(
        "usernames",
        nargs="+",
        help="Instagram usernames to scrape posts from"
    )
    posts_parser.add_argument(
        "--max-posts",
        type=int,
        default=50,
        help="Maximum posts to scrape per profile (default: 50)"
    )
    posts_parser.add_argument(
        "--output",
        help="Custom output filename"
    )

    # Hashtag mode
    hashtag_parser = subparsers.add_parser("hashtag", help="Scrape posts by hashtag")
    hashtag_parser.add_argument(
        "hashtags",
        nargs="+",
        help="Hashtags to search (without #)"
    )
    hashtag_parser.add_argument(
        "--max-posts",
        type=int,
        default=100,
        help="Maximum posts to scrape per hashtag (default: 100)"
    )
    hashtag_parser.add_argument(
        "--output",
        help="Custom output filename"
    )

    # Reels mode
    reels_parser = subparsers.add_parser("reels", help="Scrape reels from profiles")
    reels_parser.add_argument(
        "usernames",
        nargs="+",
        help="Instagram usernames to scrape reels from"
    )
    reels_parser.add_argument(
        "--max-reels",
        type=int,
        default=20,
        help="Maximum reels to scrape per profile (default: 20)"
    )
    reels_parser.add_argument(
        "--output",
        help="Custom output filename"
    )

    # Comments mode
    comments_parser = subparsers.add_parser("comments", help="Scrape comments from posts")
    comments_parser.add_argument(
        "post_urls",
        nargs="+",
        help="Instagram post URLs to scrape comments from"
    )
    comments_parser.add_argument(
        "--max-comments",
        type=int,
        default=100,
        help="Maximum comments to scrape per post (default: 100)"
    )
    comments_parser.add_argument(
        "--output",
        help="Custom output filename"
    )

    args = parser.parse_args()

    if not args.mode:
        parser.print_help()
        return 1

    try:
        # Validate environment
        validate_environment()

        # Run appropriate scraper based on mode
        if args.mode == "profile":
            results = run_profile_scraper(args.usernames)
        elif args.mode == "posts":
            results = run_posts_scraper(args.usernames, args.max_posts)
        elif args.mode == "hashtag":
            results = run_hashtag_scraper(args.hashtags, args.max_posts)
        elif args.mode == "reels":
            results = run_reels_scraper(args.usernames, args.max_reels)
        elif args.mode == "comments":
            results = run_comments_scraper(args.post_urls, args.max_comments)
        else:
            print(f"Unknown mode: {args.mode}")
            return 1

        if not results["success"]:
            print(f"Scraping failed: {results.get('error')}")
            return 1

        if results["count"] == 0:
            print("No results found for the given input")
            return 0

        # Process results
        processed_data = process_results(results)

        # Save results
        save_results(processed_data, args.output)

        print("\nInstagram scraping completed successfully!")
        return 0

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
