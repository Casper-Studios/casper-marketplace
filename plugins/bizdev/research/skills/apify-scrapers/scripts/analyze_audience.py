#!/usr/bin/env python3
"""
Audience Analysis Tool
Comprehensive cross-platform audience analysis with engagement metrics, quality scores,
posting time optimization, and growth trajectory analysis.

Usage:
    # Single account analysis
    python analyze_audience.py @nike --platforms instagram facebook youtube tiktok

    # Compare multiple accounts
    python analyze_audience.py @nike @adidas @puma --compare

    # With industry benchmark
    python analyze_audience.py @mybrand --benchmark sportswear

    # Export HTML report
    python analyze_audience.py @brand --format html --output audience_report.html

    # Quick profile-only scan
    python analyze_audience.py @brand --quick
"""

import os
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from statistics import mean, stdev
from typing import Dict, List, Optional, Any
from apify_client import ApifyClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
OUTPUT_DIR = Path(__file__).parent.parent / ".tmp"

# Apify Actor IDs for each platform
ACTORS = {
    "instagram": {
        "profile": "apify/instagram-profile-scraper",
        "posts": "apify/instagram-scraper",
        "comments": "apify/instagram-comment-scraper",
        "reels": "apify/instagram-reel-scraper"
    },
    "facebook": {
        "page": "apify/facebook-pages-scraper",
        "posts": "apify/facebook-posts-scraper",
        "reviews": "apify/facebook-reviews-scraper"
    },
    "youtube": {
        "channel": "streamers/youtube-channel-scraper",
        "comments": "streamers/youtube-comments-scraper"
    },
    "tiktok": {
        "scraper": "clockworks/tiktok-scraper"
    }
}

# Industry benchmarks for engagement rates (percentage)
INDUSTRY_BENCHMARKS = {
    "fashion": {"engagement": 1.5, "monthly_growth": 2.3},
    "tech": {"engagement": 0.8, "monthly_growth": 1.5},
    "food": {"engagement": 2.1, "monthly_growth": 2.8},
    "fitness": {"engagement": 1.9, "monthly_growth": 2.1},
    "beauty": {"engagement": 1.7, "monthly_growth": 2.5},
    "travel": {"engagement": 2.3, "monthly_growth": 1.9},
    "b2b": {"engagement": 0.5, "monthly_growth": 0.8},
    "sports": {"engagement": 1.2, "monthly_growth": 1.4},
    "sportswear": {"engagement": 1.3, "monthly_growth": 1.6},
    "gaming": {"engagement": 1.8, "monthly_growth": 3.2},
    "education": {"engagement": 0.9, "monthly_growth": 1.1},
    "entertainment": {"engagement": 2.0, "monthly_growth": 2.5},
    "finance": {"engagement": 0.6, "monthly_growth": 0.9},
    "healthcare": {"engagement": 0.7, "monthly_growth": 1.0},
    "retail": {"engagement": 1.1, "monthly_growth": 1.3},
    "automotive": {"engagement": 1.0, "monthly_growth": 1.2},
    "default": {"engagement": 1.0, "monthly_growth": 1.5}
}


def validate_environment():
    """Validate required environment variables."""
    if not APIFY_TOKEN:
        raise ValueError(
            "APIFY_TOKEN not found in environment. "
            "Please add it to your .env file."
        )


def normalize_handle(handle: str) -> str:
    """Remove @ prefix and clean handle."""
    return handle.lstrip("@").strip().lower()


def calculate_quality_score(engagement_rate: float) -> str:
    """
    Calculate audience quality score based on engagement rate.

    Returns letter grade A+ to F based on engagement benchmarks.
    """
    if engagement_rate > 6.0:
        return "A+"
    elif engagement_rate > 3.0:
        return "A"
    elif engagement_rate > 1.0:
        return "B"
    elif engagement_rate > 0.5:
        return "C"
    elif engagement_rate > 0.1:
        return "D"
    else:
        return "F"


def calculate_engagement_rate(likes: int, comments: int, followers: int,
                              shares: int = 0, views: int = 0,
                              platform: str = "instagram") -> float:
    """
    Calculate platform-specific engagement rate.

    Formulas:
    - Instagram: (likes + comments) / followers * 100
    - Facebook: (reactions + comments + shares) / followers * 100
    - YouTube: (likes + comments) / views * 100
    - TikTok: (likes + comments + shares) / views * 100
    """
    if platform == "instagram":
        if followers == 0:
            return 0.0
        return ((likes + comments) / followers) * 100

    elif platform == "facebook":
        if followers == 0:
            return 0.0
        return ((likes + comments + shares) / followers) * 100

    elif platform == "youtube":
        if views == 0:
            return 0.0
        return ((likes + comments) / views) * 100

    elif platform == "tiktok":
        if views == 0:
            return 0.0
        return ((likes + comments + shares) / views) * 100

    else:
        if followers == 0:
            return 0.0
        return ((likes + comments) / followers) * 100


def analyze_posting_times(posts: List[Dict]) -> Dict:
    """
    Analyze post timestamps to determine optimal posting times.

    Returns best days/hours based on engagement patterns.
    """
    if not posts:
        return {
            "weekday_best": "Unknown",
            "weekend_best": "Unknown",
            "best_hours": [],
            "timezone": "UTC",
            "confidence": 0.0
        }

    # Group posts by day of week and hour
    weekday_engagement = defaultdict(list)
    hour_engagement = defaultdict(list)

    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday",
                     "Friday", "Saturday", "Sunday"]

    for post in posts:
        timestamp = post.get("timestamp") or post.get("time")
        engagement = post.get("engagement_score", 0)

        if timestamp and engagement:
            try:
                if isinstance(timestamp, str):
                    # Try multiple date formats
                    for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S",
                               "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"]:
                        try:
                            dt = datetime.strptime(timestamp[:19], fmt[:len(timestamp[:19])])
                            break
                        except ValueError:
                            continue
                    else:
                        continue
                else:
                    dt = timestamp

                weekday = dt.weekday()
                hour = dt.hour

                weekday_engagement[weekday].append(engagement)
                hour_engagement[hour].append(engagement)
            except Exception:
                continue

    # Find best weekday and weekend day
    weekday_avgs = {day: mean(engagements) if engagements else 0
                    for day, engagements in weekday_engagement.items()}

    weekdays = {d: avg for d, avg in weekday_avgs.items() if d < 5}
    weekends = {d: avg for d, avg in weekday_avgs.items() if d >= 5}

    best_weekday = max(weekdays, key=weekdays.get) if weekdays else 2  # Default Wed
    best_weekend = max(weekends, key=weekends.get) if weekends else 5  # Default Sat

    # Find best hours
    hour_avgs = {hour: mean(engagements) if engagements else 0
                 for hour, engagements in hour_engagement.items()}

    sorted_hours = sorted(hour_avgs.items(), key=lambda x: x[1], reverse=True)
    best_hours = [f"{h}:00" for h, _ in sorted_hours[:3]]

    # Calculate confidence based on sample size
    total_posts = len(posts)
    confidence = min(1.0, total_posts / 100)

    return {
        "weekday_best": weekday_names[best_weekday],
        "weekend_best": weekday_names[best_weekend],
        "best_hours": best_hours if best_hours else ["9:00", "12:00", "18:00"],
        "timezone": "UTC",
        "confidence": round(confidence, 2)
    }


def analyze_content_types(posts: List[Dict]) -> List[Dict]:
    """
    Categorize content by type and analyze performance.

    Returns ranked list of content types by engagement.
    """
    type_stats = defaultdict(lambda: {"count": 0, "total_engagement": 0})

    for post in posts:
        content_type = post.get("type", "Unknown")

        # Normalize content types
        if content_type in ["Video", "video", "Reel", "reel"]:
            content_type = "Reels/Video"
        elif content_type in ["Sidecar", "carousel", "Carousel"]:
            content_type = "Carousel"
        elif content_type in ["Image", "image", "Photo", "photo"]:
            content_type = "Single Image"
        elif content_type in ["Story", "story"]:
            content_type = "Story"
        else:
            content_type = "Other"

        engagement = post.get("engagement_score", 0)
        type_stats[content_type]["count"] += 1
        type_stats[content_type]["total_engagement"] += engagement

    # Calculate average engagement per type
    result = []
    for content_type, stats in type_stats.items():
        if stats["count"] > 0:
            avg_engagement = stats["total_engagement"] / stats["count"]
            result.append({
                "type": content_type,
                "count": stats["count"],
                "avg_engagement": round(avg_engagement, 2),
                "percentage": 0  # Will be calculated below
            })

    # Calculate percentages
    total_posts = sum(r["count"] for r in result)
    for r in result:
        r["percentage"] = round((r["count"] / total_posts) * 100, 1) if total_posts > 0 else 0

    # Sort by average engagement
    result.sort(key=lambda x: x["avg_engagement"], reverse=True)

    return result


def analyze_growth_trajectory(profile_data: Dict, historical_data: List[Dict] = None) -> Dict:
    """
    Analyze follower growth patterns.

    Returns growth trajectory classification and metrics.
    """
    # If we have historical data, analyze trend
    if historical_data and len(historical_data) >= 2:
        growth_rates = []
        for i in range(1, len(historical_data)):
            prev = historical_data[i-1].get("followers", 0)
            curr = historical_data[i].get("followers", 0)
            if prev > 0:
                rate = ((curr - prev) / prev) * 100
                growth_rates.append(rate)

        if growth_rates:
            avg_rate = mean(growth_rates)

            # Determine trajectory
            if len(growth_rates) >= 3:
                recent = mean(growth_rates[-2:])
                older = mean(growth_rates[:-2])

                if recent > older * 1.5:
                    trajectory = "accelerating"
                elif recent < older * 0.5:
                    trajectory = "decelerating"
                elif avg_rate < -1:
                    trajectory = "declining"
                elif avg_rate > 10:
                    trajectory = "viral"
                else:
                    trajectory = "stable"
            else:
                trajectory = "stable" if avg_rate >= 0 else "declining"

            return {
                "monthly_rate": round(avg_rate, 2),
                "trajectory": trajectory,
                "data_points": len(historical_data)
            }

    # Without historical data, estimate from engagement
    followers = profile_data.get("followers", 0) or profile_data.get("followersCount", 0)
    engagement_rate = profile_data.get("engagement_rate", 1.0)

    # Estimate growth based on engagement (higher engagement = more discovery)
    estimated_rate = engagement_rate * 0.5  # Rough estimate

    return {
        "monthly_rate": round(estimated_rate, 2),
        "trajectory": "estimated",
        "data_points": 1
    }


def extract_top_hashtags(posts: List[Dict], limit: int = 10) -> List[str]:
    """Extract most frequently used hashtags from posts."""
    hashtag_counts = defaultdict(int)

    for post in posts:
        hashtags = post.get("hashtags", [])
        if isinstance(hashtags, list):
            for tag in hashtags:
                if tag:
                    # Clean hashtag
                    clean_tag = tag.lstrip("#").lower()
                    hashtag_counts[clean_tag] += 1

    # Sort by frequency and return top N
    sorted_tags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)
    return [f"#{tag}" for tag, _ in sorted_tags[:limit]]


def analyze_sentiment(comments: List[Dict]) -> float:
    """
    Simple sentiment analysis on comments.

    Returns score from -1 (negative) to 1 (positive).
    Uses keyword-based approach for simplicity.
    """
    if not comments:
        return 0.0

    positive_words = {
        "love", "great", "amazing", "awesome", "excellent", "fantastic",
        "beautiful", "perfect", "best", "incredible", "wonderful", "fire",
        "goat", "legend", "king", "queen", "iconic", "insane", "sick"
    }

    negative_words = {
        "hate", "bad", "terrible", "awful", "horrible", "worst",
        "ugly", "disgusting", "trash", "garbage", "fake", "boring",
        "lame", "cringe", "mid", "overrated", "disappointing"
    }

    positive_count = 0
    negative_count = 0
    total_words = 0

    for comment in comments:
        text = comment.get("text", "") or comment.get("content", "") or ""
        if not text:
            continue

        words = text.lower().split()
        total_words += len(words)

        for word in words:
            clean_word = "".join(c for c in word if c.isalnum())
            if clean_word in positive_words:
                positive_count += 1
            elif clean_word in negative_words:
                negative_count += 1

    if total_words == 0:
        return 0.0

    # Calculate sentiment score
    sentiment = (positive_count - negative_count) / max(1, positive_count + negative_count)
    return round(sentiment, 2)


# =============================================================================
# PLATFORM SCRAPERS
# =============================================================================

def scrape_instagram(handle: str, max_posts: int = 50,
                     include_comments: bool = False) -> Dict:
    """
    Scrape Instagram profile, posts, and optionally comments.

    Returns comprehensive Instagram analytics.
    """
    client = ApifyClient(APIFY_TOKEN)
    username = normalize_handle(handle)

    print(f"  [Instagram] Scraping profile: @{username}")

    result = {
        "platform": "instagram",
        "username": username,
        "success": False,
        "error": None
    }

    try:
        # 1. Scrape profile
        profile_run = client.actor(ACTORS["instagram"]["profile"]).call(
            run_input={"usernames": [username]}
        )
        profile_items = list(client.dataset(profile_run["defaultDatasetId"]).iterate_items())

        if not profile_items:
            result["error"] = "Profile not found or private"
            return result

        profile = profile_items[0]

        # 2. Scrape posts
        print(f"  [Instagram] Fetching posts (max: {max_posts})")
        posts_run = client.actor(ACTORS["instagram"]["posts"]).call(
            run_input={
                "directUrls": [f"https://www.instagram.com/{username}/"],
                "resultsLimit": max_posts,
                "resultsType": "posts",
                "searchType": "user",
                "searchLimit": 1
            }
        )
        posts = list(client.dataset(posts_run["defaultDatasetId"]).iterate_items())

        # Process posts and calculate metrics
        processed_posts = []
        total_likes = 0
        total_comments = 0

        for post in posts:
            likes = post.get("likesCount", 0) or post.get("likes", 0)
            comments = post.get("commentsCount", 0) or post.get("comments", 0)

            processed_post = {
                "id": post.get("id", ""),
                "type": post.get("type", "Image"),
                "caption": post.get("caption", ""),
                "likes": likes,
                "comments": comments,
                "timestamp": post.get("timestamp", ""),
                "hashtags": post.get("hashtags", []),
                "engagement_score": likes + (comments * 2)
            }
            processed_posts.append(processed_post)
            total_likes += likes
            total_comments += comments

        # Calculate metrics
        followers = profile.get("followersCount", 0)
        following = profile.get("followsCount", 0)
        posts_count = profile.get("postsCount", 0)

        avg_likes = total_likes / len(processed_posts) if processed_posts else 0
        avg_comments = total_comments / len(processed_posts) if processed_posts else 0

        engagement_rate = calculate_engagement_rate(
            likes=int(avg_likes),
            comments=int(avg_comments),
            followers=followers,
            platform="instagram"
        )

        # Optional: Scrape comments for sentiment
        sentiment_score = 0.0
        if include_comments and processed_posts:
            try:
                print(f"  [Instagram] Analyzing comments for sentiment")
                sample_posts = processed_posts[:5]  # Sample first 5 posts
                all_comments = []

                for post in sample_posts:
                    post_url = f"https://www.instagram.com/p/{post.get('id', '')}/"
                    comments_run = client.actor(ACTORS["instagram"]["comments"]).call(
                        run_input={
                            "directUrls": [post_url],
                            "resultsLimit": 50
                        }
                    )
                    comments = list(client.dataset(comments_run["defaultDatasetId"]).iterate_items())
                    all_comments.extend(comments)

                sentiment_score = analyze_sentiment(all_comments)
            except Exception as e:
                print(f"  [Instagram] Warning: Could not analyze comments: {e}")

        # Build result
        result.update({
            "success": True,
            "username": profile.get("username", username),
            "full_name": profile.get("fullName", ""),
            "biography": profile.get("biography", ""),
            "followers": followers,
            "following": following,
            "posts_count": posts_count,
            "is_verified": profile.get("verified", False),
            "is_business": profile.get("isBusinessAccount", False),
            "business_category": profile.get("businessCategoryName", ""),
            "profile_url": f"https://www.instagram.com/{username}/",
            "engagement_rate": round(engagement_rate, 2),
            "quality_score": calculate_quality_score(engagement_rate),
            "follower_following_ratio": round(followers / following, 1) if following > 0 else 0,
            "avg_likes_per_post": int(avg_likes),
            "avg_comments_per_post": int(avg_comments),
            "best_posting_times": analyze_posting_times(processed_posts),
            "top_content_types": analyze_content_types(processed_posts),
            "recent_growth": analyze_growth_trajectory(profile),
            "top_hashtags": extract_top_hashtags(processed_posts),
            "sentiment_score": sentiment_score,
            "posts_analyzed": len(processed_posts)
        })

    except Exception as e:
        result["error"] = str(e)
        print(f"  [Instagram] Error: {e}")

    return result


def scrape_facebook(handle: str, max_posts: int = 50,
                    include_reviews: bool = False) -> Dict:
    """
    Scrape Facebook page and posts.

    Returns comprehensive Facebook analytics.
    """
    client = ApifyClient(APIFY_TOKEN)
    page_name = normalize_handle(handle)

    print(f"  [Facebook] Scraping page: {page_name}")

    result = {
        "platform": "facebook",
        "page_name": page_name,
        "success": False,
        "error": None
    }

    try:
        # Build URL
        page_url = f"https://www.facebook.com/{page_name}"

        # 1. Scrape page info
        page_run = client.actor(ACTORS["facebook"]["page"]).call(
            run_input={
                "startUrls": [{"url": page_url}],
                "maxPagesPerQuery": 1,
                "proxyConfiguration": {"useApifyProxy": True}
            }
        )
        page_items = list(client.dataset(page_run["defaultDatasetId"]).iterate_items())

        if not page_items:
            result["error"] = "Page not found"
            return result

        page = page_items[0]

        # 2. Scrape posts
        print(f"  [Facebook] Fetching posts (max: {max_posts})")
        posts_run = client.actor(ACTORS["facebook"]["posts"]).call(
            run_input={
                "startUrls": [{"url": page_url}],
                "maxPosts": max_posts,
                "maxPostComments": 0,
                "proxyConfiguration": {"useApifyProxy": True}
            }
        )
        posts = list(client.dataset(posts_run["defaultDatasetId"]).iterate_items())

        # Process posts
        processed_posts = []
        total_likes = 0
        total_comments = 0
        total_shares = 0

        for post in posts:
            likes = post.get("likes", 0)
            comments = post.get("comments", 0)
            shares = post.get("shares", 0)

            processed_post = {
                "id": post.get("id", ""),
                "type": "Video" if post.get("media") and "video" in str(post.get("media")).lower() else "Post",
                "text": post.get("text", ""),
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "timestamp": post.get("timestamp", ""),
                "engagement_score": likes + (comments * 2) + (shares * 3)
            }
            processed_posts.append(processed_post)
            total_likes += likes
            total_comments += comments
            total_shares += shares

        # Calculate metrics
        followers = page.get("followers", 0) or page.get("likes", 0)

        avg_likes = total_likes / len(processed_posts) if processed_posts else 0
        avg_comments = total_comments / len(processed_posts) if processed_posts else 0
        avg_shares = total_shares / len(processed_posts) if processed_posts else 0

        engagement_rate = calculate_engagement_rate(
            likes=int(avg_likes),
            comments=int(avg_comments),
            shares=int(avg_shares),
            followers=followers,
            platform="facebook"
        )

        # Optional: Analyze reviews
        review_sentiment = 0.0
        avg_rating = None
        review_count = 0

        if include_reviews:
            try:
                print(f"  [Facebook] Analyzing reviews")
                reviews_run = client.actor(ACTORS["facebook"]["reviews"]).call(
                    run_input={
                        "startUrls": [{"url": page_url}],
                        "maxReviews": 50,
                        "proxyConfiguration": {"useApifyProxy": True}
                    }
                )
                reviews = list(client.dataset(reviews_run["defaultDatasetId"]).iterate_items())

                if reviews:
                    review_count = len(reviews)
                    ratings = [r.get("rating", 0) for r in reviews if r.get("rating")]
                    avg_rating = mean(ratings) if ratings else None
                    review_sentiment = analyze_sentiment(reviews)
            except Exception as e:
                print(f"  [Facebook] Warning: Could not analyze reviews: {e}")

        # Build result
        result.update({
            "success": True,
            "page_name": page.get("name", page_name),
            "page_url": page_url,
            "category": page.get("category", ""),
            "description": page.get("description", ""),
            "followers": followers,
            "page_likes": page.get("likes", 0),
            "rating": page.get("rating"),
            "review_count": page.get("reviewCount", 0) or review_count,
            "is_verified": page.get("verified", False),
            "website": page.get("website", ""),
            "engagement_rate": round(engagement_rate, 2),
            "quality_score": calculate_quality_score(engagement_rate),
            "avg_likes_per_post": int(avg_likes),
            "avg_comments_per_post": int(avg_comments),
            "avg_shares_per_post": int(avg_shares),
            "best_posting_times": analyze_posting_times(processed_posts),
            "recent_growth": analyze_growth_trajectory({"followers": followers, "engagement_rate": engagement_rate}),
            "sentiment_score": review_sentiment,
            "avg_review_rating": avg_rating,
            "posts_analyzed": len(processed_posts)
        })

    except Exception as e:
        result["error"] = str(e)
        print(f"  [Facebook] Error: {e}")

    return result


def scrape_youtube(handle: str, max_videos: int = 50,
                   include_comments: bool = False) -> Dict:
    """
    Scrape YouTube channel and videos.

    Returns comprehensive YouTube analytics.
    """
    client = ApifyClient(APIFY_TOKEN)
    channel_name = normalize_handle(handle)

    print(f"  [YouTube] Scraping channel: {channel_name}")

    result = {
        "platform": "youtube",
        "channel_name": channel_name,
        "success": False,
        "error": None
    }

    try:
        # Build search for channel
        channel_run = client.actor(ACTORS["youtube"]["channel"]).call(
            run_input={
                "searchKeywords": channel_name,
                "maxResults": max_videos,
                "downloadSubtitles": False
            }
        )
        items = list(client.dataset(channel_run["defaultDatasetId"]).iterate_items())

        if not items:
            result["error"] = "Channel not found"
            return result

        # Filter to find channel and videos
        channel_info = None
        videos = []

        for item in items:
            if item.get("type") == "channel":
                channel_info = item
            elif item.get("type") == "video" or item.get("title"):
                videos.append(item)

        # If no explicit channel info, derive from videos
        if not channel_info and videos:
            channel_info = {
                "channelName": videos[0].get("channelName", channel_name),
                "subscriberCount": videos[0].get("channelSubscribers", 0)
            }

        # Process videos
        processed_videos = []
        total_views = 0
        total_likes = 0
        total_comments = 0

        for video in videos[:max_videos]:
            views = video.get("viewCount", 0) or video.get("views", 0)
            likes = video.get("likeCount", 0) or video.get("likes", 0)
            comments = video.get("commentCount", 0) or video.get("comments", 0)

            processed_video = {
                "id": video.get("id", ""),
                "title": video.get("title", ""),
                "views": views,
                "likes": likes,
                "comments": comments,
                "duration": video.get("duration", ""),
                "timestamp": video.get("uploadDate", "") or video.get("date", ""),
                "engagement_score": likes + (comments * 2)
            }
            processed_videos.append(processed_video)
            total_views += views
            total_likes += likes
            total_comments += comments

        # Calculate metrics
        subscribers = channel_info.get("subscriberCount", 0) or channel_info.get("subscribers", 0)

        avg_views = total_views / len(processed_videos) if processed_videos else 0
        avg_likes = total_likes / len(processed_videos) if processed_videos else 0
        avg_comments = total_comments / len(processed_videos) if processed_videos else 0

        engagement_rate = calculate_engagement_rate(
            likes=int(avg_likes),
            comments=int(avg_comments),
            followers=subscribers,
            views=int(avg_views),
            platform="youtube"
        )

        # View-to-subscriber ratio
        view_sub_ratio = avg_views / subscribers if subscribers > 0 else 0

        # Optional: Comment sentiment
        sentiment_score = 0.0
        if include_comments and processed_videos:
            # Would need to scrape comments - simplified for now
            pass

        # Build result
        result.update({
            "success": True,
            "channel_name": channel_info.get("channelName", channel_name),
            "channel_url": f"https://www.youtube.com/@{channel_name}",
            "subscribers": subscribers,
            "total_views": total_views,
            "video_count": len(processed_videos),
            "engagement_rate": round(engagement_rate, 2),
            "quality_score": calculate_quality_score(engagement_rate),
            "view_to_subscriber_ratio": round(view_sub_ratio, 2),
            "avg_views_per_video": int(avg_views),
            "avg_likes_per_video": int(avg_likes),
            "avg_comments_per_video": int(avg_comments),
            "best_posting_times": analyze_posting_times(processed_videos),
            "recent_growth": analyze_growth_trajectory({"followers": subscribers, "engagement_rate": engagement_rate}),
            "sentiment_score": sentiment_score,
            "videos_analyzed": len(processed_videos)
        })

    except Exception as e:
        result["error"] = str(e)
        print(f"  [YouTube] Error: {e}")

    return result


def scrape_tiktok(handle: str, max_videos: int = 50) -> Dict:
    """
    Scrape TikTok profile and videos.

    Returns comprehensive TikTok analytics.
    """
    client = ApifyClient(APIFY_TOKEN)
    username = normalize_handle(handle)

    print(f"  [TikTok] Scraping profile: @{username}")

    result = {
        "platform": "tiktok",
        "username": username,
        "success": False,
        "error": None
    }

    try:
        # Scrape profile and videos
        profile_url = f"https://www.tiktok.com/@{username}"

        run = client.actor(ACTORS["tiktok"]["scraper"]).call(
            run_input={
                "startUrls": [profile_url],
                "resultsLimit": max_videos,
                "shouldDownloadVideos": False,
                "shouldDownloadCovers": False
            }
        )
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        if not items:
            result["error"] = "Profile not found or private"
            return result

        # Process videos
        processed_videos = []
        total_views = 0
        total_likes = 0
        total_comments = 0
        total_shares = 0

        profile_info = None

        for item in items:
            # Extract profile info from first item
            if not profile_info:
                author = item.get("authorMeta", {})
                if author:
                    profile_info = {
                        "username": author.get("name", username),
                        "nickname": author.get("nickName", ""),
                        "followers": author.get("fans", 0),
                        "following": author.get("following", 0),
                        "likes": author.get("heart", 0),
                        "videos": author.get("video", 0),
                        "verified": author.get("verified", False)
                    }

            views = item.get("playCount", 0)
            likes = item.get("diggCount", 0)
            comments = item.get("commentCount", 0)
            shares = item.get("shareCount", 0)

            processed_video = {
                "id": item.get("id", ""),
                "text": item.get("text", ""),
                "views": views,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "timestamp": item.get("createTime", ""),
                "hashtags": [tag.get("name", "") for tag in item.get("hashtags", [])],
                "engagement_score": likes + (comments * 2) + (shares * 3)
            }
            processed_videos.append(processed_video)
            total_views += views
            total_likes += likes
            total_comments += comments
            total_shares += shares

        if not profile_info:
            profile_info = {"followers": 0, "following": 0, "likes": 0, "videos": 0, "verified": False}

        # Calculate metrics
        followers = profile_info.get("followers", 0)

        avg_views = total_views / len(processed_videos) if processed_videos else 0
        avg_likes = total_likes / len(processed_videos) if processed_videos else 0
        avg_comments = total_comments / len(processed_videos) if processed_videos else 0
        avg_shares = total_shares / len(processed_videos) if processed_videos else 0

        engagement_rate = calculate_engagement_rate(
            likes=int(avg_likes),
            comments=int(avg_comments),
            shares=int(avg_shares),
            followers=followers,
            views=int(avg_views),
            platform="tiktok"
        )

        # Build result
        result.update({
            "success": True,
            "username": profile_info.get("username", username),
            "nickname": profile_info.get("nickname", ""),
            "profile_url": profile_url,
            "followers": followers,
            "following": profile_info.get("following", 0),
            "total_likes": profile_info.get("likes", 0),
            "video_count": profile_info.get("videos", 0),
            "is_verified": profile_info.get("verified", False),
            "engagement_rate": round(engagement_rate, 2),
            "quality_score": calculate_quality_score(engagement_rate),
            "follower_following_ratio": round(followers / profile_info.get("following", 1), 1) if profile_info.get("following", 0) > 0 else 0,
            "avg_views_per_video": int(avg_views),
            "avg_likes_per_video": int(avg_likes),
            "avg_comments_per_video": int(avg_comments),
            "avg_shares_per_video": int(avg_shares),
            "best_posting_times": analyze_posting_times(processed_videos),
            "top_content_types": [{"type": "Short Video", "count": len(processed_videos), "avg_engagement": round(mean([v["engagement_score"] for v in processed_videos]) if processed_videos else 0, 2)}],
            "recent_growth": analyze_growth_trajectory({"followers": followers, "engagement_rate": engagement_rate}),
            "top_hashtags": extract_top_hashtags(processed_videos),
            "videos_analyzed": len(processed_videos)
        })

    except Exception as e:
        result["error"] = str(e)
        print(f"  [TikTok] Error: {e}")

    return result


# =============================================================================
# ANALYSIS & REPORTING
# =============================================================================

def analyze_account(handle: str, platforms: List[str],
                    benchmark: str = None, max_posts: int = 50,
                    include_comments: bool = False,
                    quick: bool = False) -> Dict:
    """
    Analyze a single account across specified platforms.

    Returns comprehensive cross-platform analysis.
    """
    print(f"\nAnalyzing: {handle}")
    print(f"Platforms: {', '.join(platforms)}")
    print("-" * 50)

    results = {
        "analysis_timestamp": datetime.now().isoformat(),
        "account": handle,
        "platforms": {},
        "cross_platform_summary": {},
        "benchmark_comparison": None,
        "recommendations": []
    }

    # Scrape each platform
    platform_scrapers = {
        "instagram": lambda: scrape_instagram(handle, max_posts if not quick else 10, include_comments),
        "facebook": lambda: scrape_facebook(handle, max_posts if not quick else 10, include_comments),
        "youtube": lambda: scrape_youtube(handle, max_posts if not quick else 10, include_comments),
        "tiktok": lambda: scrape_tiktok(handle, max_posts if not quick else 10)
    }

    for platform in platforms:
        if platform in platform_scrapers:
            platform_data = platform_scrapers[platform]()
            if platform_data["success"]:
                results["platforms"][platform] = platform_data
            else:
                print(f"  [{platform.capitalize()}] Skipped: {platform_data.get('error', 'Unknown error')}")

    # Generate cross-platform summary
    if results["platforms"]:
        results["cross_platform_summary"] = generate_cross_platform_summary(results["platforms"])

    # Compare with benchmark
    if benchmark:
        results["benchmark_comparison"] = compare_with_benchmark(
            results["cross_platform_summary"],
            benchmark
        )

    # Generate recommendations
    results["recommendations"] = generate_recommendations(results)

    return results


def generate_cross_platform_summary(platforms: Dict) -> Dict:
    """
    Generate summary metrics across all platforms.
    """
    total_reach = 0
    engagement_rates = []
    quality_scores = []

    strongest_platform = None
    strongest_engagement = 0
    weakest_platform = None
    weakest_engagement = float('inf')

    for platform_name, data in platforms.items():
        followers = data.get("followers", 0) or data.get("subscribers", 0)
        total_reach += followers

        er = data.get("engagement_rate", 0)
        engagement_rates.append(er)

        qs = data.get("quality_score", "C")
        quality_scores.append(qs)

        if er > strongest_engagement:
            strongest_engagement = er
            strongest_platform = platform_name

        if er < weakest_engagement and er > 0:
            weakest_engagement = er
            weakest_platform = platform_name

    # Average quality score
    score_values = {"A+": 6, "A": 5, "B": 4, "C": 3, "D": 2, "F": 1}
    avg_score_val = mean([score_values.get(qs, 3) for qs in quality_scores])

    if avg_score_val >= 5.5:
        overall_quality = "A+"
    elif avg_score_val >= 4.5:
        overall_quality = "A"
    elif avg_score_val >= 3.5:
        overall_quality = "B+"
    elif avg_score_val >= 2.5:
        overall_quality = "B"
    elif avg_score_val >= 1.5:
        overall_quality = "C"
    else:
        overall_quality = "D"

    # Estimate audience overlap (rough estimate based on typical social media patterns)
    # Accounts with large followings typically have 20-40% overlap
    estimated_overlap = 0.25 if total_reach > 1000000 else 0.15

    # Determine growth trend
    growth_rates = [data.get("recent_growth", {}).get("monthly_rate", 0)
                    for data in platforms.values()]
    avg_growth = mean(growth_rates) if growth_rates else 0

    if avg_growth > 3:
        growth_trend = "accelerating"
    elif avg_growth > 1:
        growth_trend = "growing"
    elif avg_growth > 0:
        growth_trend = "stable"
    else:
        growth_trend = "declining"

    return {
        "total_reach": total_reach,
        "unique_reach_estimate": int(total_reach * (1 - estimated_overlap)),
        "avg_engagement_rate": round(mean(engagement_rates), 2) if engagement_rates else 0,
        "strongest_platform": strongest_platform,
        "weakest_platform": weakest_platform,
        "overall_quality_score": overall_quality,
        "growth_trend": growth_trend,
        "estimated_audience_overlap": estimated_overlap,
        "platforms_analyzed": len(platforms)
    }


def compare_with_benchmark(summary: Dict, industry: str) -> Dict:
    """
    Compare metrics against industry benchmarks.
    """
    benchmark = INDUSTRY_BENCHMARKS.get(industry.lower(), INDUSTRY_BENCHMARKS["default"])

    engagement_diff = ((summary.get("avg_engagement_rate", 0) - benchmark["engagement"])
                       / benchmark["engagement"]) * 100

    # Determine position
    if engagement_diff > 20:
        position = "significantly above average"
    elif engagement_diff > 5:
        position = "above average"
    elif engagement_diff > -5:
        position = "average"
    elif engagement_diff > -20:
        position = "below average"
    else:
        position = "significantly below average"

    return {
        "industry": industry,
        "benchmark_engagement": benchmark["engagement"],
        "benchmark_growth": benchmark["monthly_growth"],
        "engagement_vs_benchmark": f"{'+' if engagement_diff >= 0 else ''}{round(engagement_diff)}%",
        "position": position
    }


def generate_recommendations(analysis: Dict) -> List[str]:
    """
    Generate actionable recommendations based on analysis.
    """
    recommendations = []

    platforms = analysis.get("platforms", {})
    summary = analysis.get("cross_platform_summary", {})
    benchmark = analysis.get("benchmark_comparison")

    # Platform-specific recommendations
    for platform_name, data in platforms.items():
        er = data.get("engagement_rate", 0)
        qs = data.get("quality_score", "C")

        if qs in ["D", "F"]:
            recommendations.append(
                f"[{platform_name.capitalize()}] Low engagement rate ({er}%) suggests audience quality issues. "
                "Consider audience audit and content refresh."
            )

        # Posting time optimization
        best_times = data.get("best_posting_times", {})
        if best_times.get("confidence", 0) > 0.5:
            recommendations.append(
                f"[{platform_name.capitalize()}] Best posting times: {best_times.get('weekday_best')} at "
                f"{', '.join(best_times.get('best_hours', [])[:2])}"
            )

        # Content type recommendations
        content_types = data.get("top_content_types", [])
        if content_types and len(content_types) > 1:
            top_type = content_types[0]
            if top_type.get("avg_engagement", 0) > er * 1.5:
                recommendations.append(
                    f"[{platform_name.capitalize()}] {top_type['type']} content performs {round((top_type['avg_engagement']/er - 1) * 100)}% "
                    "better than average - prioritize this format."
                )

    # Cross-platform recommendations
    if summary.get("weakest_platform") and summary.get("strongest_platform"):
        if summary["weakest_platform"] != summary["strongest_platform"]:
            recommendations.append(
                f"Cross-platform: {summary['strongest_platform'].capitalize()} is your strongest platform. "
                f"Consider replicating successful strategies on {summary['weakest_platform'].capitalize()}."
            )

    # Benchmark recommendations
    if benchmark:
        if "below" in benchmark.get("position", ""):
            recommendations.append(
                f"Engagement is {benchmark['engagement_vs_benchmark']} vs {benchmark['industry']} benchmark. "
                "Focus on community engagement and content quality."
            )

    return recommendations[:10]  # Limit to top 10 recommendations


def compare_accounts(accounts: List[Dict]) -> Dict:
    """
    Generate comparison report for multiple accounts.
    """
    comparison = {
        "comparison_timestamp": datetime.now().isoformat(),
        "accounts_compared": len(accounts),
        "accounts": [],
        "rankings": {},
        "insights": []
    }

    # Collect metrics for ranking
    metrics = {
        "total_reach": [],
        "avg_engagement": [],
        "quality_score": [],
        "growth_rate": []
    }

    for account in accounts:
        summary = account.get("cross_platform_summary", {})
        account_summary = {
            "handle": account.get("account", "Unknown"),
            "total_reach": summary.get("total_reach", 0),
            "avg_engagement_rate": summary.get("avg_engagement_rate", 0),
            "quality_score": summary.get("overall_quality_score", "C"),
            "strongest_platform": summary.get("strongest_platform", "N/A"),
            "growth_trend": summary.get("growth_trend", "unknown")
        }
        comparison["accounts"].append(account_summary)

        metrics["total_reach"].append((account_summary["handle"], account_summary["total_reach"]))
        metrics["avg_engagement"].append((account_summary["handle"], account_summary["avg_engagement_rate"]))

    # Generate rankings
    for metric_name, values in metrics.items():
        if values:
            sorted_values = sorted(values, key=lambda x: x[1], reverse=True)
            comparison["rankings"][metric_name] = [
                {"rank": i+1, "account": v[0], "value": v[1]}
                for i, v in enumerate(sorted_values)
            ]

    # Generate insights
    if len(accounts) >= 2:
        # Find leader in engagement
        eng_leader = max(comparison["accounts"], key=lambda x: x["avg_engagement_rate"])
        comparison["insights"].append(
            f"{eng_leader['handle']} leads in engagement rate ({eng_leader['avg_engagement_rate']}%)"
        )

        # Find leader in reach
        reach_leader = max(comparison["accounts"], key=lambda x: x["total_reach"])
        comparison["insights"].append(
            f"{reach_leader['handle']} has the largest audience ({reach_leader['total_reach']:,} total reach)"
        )

    return comparison


# =============================================================================
# OUTPUT GENERATION
# =============================================================================

def generate_html_report(analysis: Dict, comparison: Dict = None) -> str:
    """
    Generate styled HTML report.
    """
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audience Analysis Report</title>
    <style>
        :root {
            --primary: #2563eb;
            --secondary: #64748b;
            --success: #22c55e;
            --warning: #f59e0b;
            --danger: #ef4444;
            --bg: #f8fafc;
            --card: #ffffff;
            --text: #1e293b;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 2rem;
        }

        .container { max-width: 1200px; margin: 0 auto; }

        h1 { font-size: 2rem; margin-bottom: 0.5rem; }
        h2 { font-size: 1.5rem; margin: 2rem 0 1rem; color: var(--primary); }
        h3 { font-size: 1.2rem; margin: 1rem 0 0.5rem; }

        .header {
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, var(--primary), #7c3aed);
            color: white;
            border-radius: 1rem;
            margin-bottom: 2rem;
        }

        .header .subtitle { opacity: 0.9; }

        .card {
            background: var(--card);
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .metric {
            text-align: center;
            padding: 1.5rem;
            background: var(--card);
            border-radius: 0.75rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .metric .value {
            font-size: 2rem;
            font-weight: bold;
            color: var(--primary);
        }

        .metric .label {
            font-size: 0.875rem;
            color: var(--secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .grade {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 0.5rem;
            font-weight: bold;
        }

        .grade-a { background: #dcfce7; color: #15803d; }
        .grade-b { background: #dbeafe; color: #1d4ed8; }
        .grade-c { background: #fef3c7; color: #b45309; }
        .grade-d { background: #fee2e2; color: #dc2626; }

        .platform-card {
            border-left: 4px solid var(--primary);
        }

        .platform-instagram { border-left-color: #e1306c; }
        .platform-facebook { border-left-color: #1877f2; }
        .platform-youtube { border-left-color: #ff0000; }
        .platform-tiktok { border-left-color: #000000; }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }

        th, td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }

        th {
            background: var(--bg);
            font-weight: 600;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--secondary);
        }

        .recommendations {
            background: #f0f9ff;
            border-radius: 0.75rem;
            padding: 1.5rem;
        }

        .recommendations li {
            margin-bottom: 0.75rem;
            padding-left: 1.5rem;
            position: relative;
        }

        .recommendations li::before {
            content: ">";
            position: absolute;
            left: 0;
            color: var(--primary);
            font-weight: bold;
        }

        .footer {
            text-align: center;
            margin-top: 3rem;
            padding: 1rem;
            color: var(--secondary);
            font-size: 0.875rem;
        }
    </style>
</head>
<body>
    <div class="container">
"""

    # Header
    account = analysis.get("account", "Unknown")
    timestamp = analysis.get("analysis_timestamp", datetime.now().isoformat())

    html += f"""
        <div class="header">
            <h1>Audience Analysis Report</h1>
            <p class="subtitle">{account}</p>
            <p class="subtitle">Generated: {timestamp[:10]}</p>
        </div>
"""

    # Cross-platform summary
    summary = analysis.get("cross_platform_summary", {})
    if summary:
        quality = summary.get("overall_quality_score", "C")
        grade_class = f"grade-{quality[0].lower()}"

        html += f"""
        <h2>Executive Summary</h2>
        <div class="metrics-grid">
            <div class="metric">
                <div class="value">{summary.get('total_reach', 0):,}</div>
                <div class="label">Total Reach</div>
            </div>
            <div class="metric">
                <div class="value">{summary.get('avg_engagement_rate', 0)}%</div>
                <div class="label">Avg Engagement</div>
            </div>
            <div class="metric">
                <div class="value"><span class="grade {grade_class}">{quality}</span></div>
                <div class="label">Quality Score</div>
            </div>
            <div class="metric">
                <div class="value">{summary.get('platforms_analyzed', 0)}</div>
                <div class="label">Platforms</div>
            </div>
        </div>

        <div class="card">
            <p><strong>Strongest Platform:</strong> {summary.get('strongest_platform', 'N/A').capitalize()}</p>
            <p><strong>Growth Trend:</strong> {summary.get('growth_trend', 'Unknown').capitalize()}</p>
            <p><strong>Estimated Unique Reach:</strong> {summary.get('unique_reach_estimate', 0):,}</p>
        </div>
"""

    # Platform breakdowns
    platforms = analysis.get("platforms", {})
    if platforms:
        html += "<h2>Platform Breakdown</h2>"

        for platform_name, data in platforms.items():
            quality = data.get("quality_score", "C")
            grade_class = f"grade-{quality[0].lower()}"

            followers = data.get("followers", 0) or data.get("subscribers", 0)

            html += f"""
        <div class="card platform-card platform-{platform_name}">
            <h3>{platform_name.capitalize()}</h3>
            <table>
                <tr>
                    <td><strong>Followers/Subscribers</strong></td>
                    <td>{followers:,}</td>
                    <td><strong>Engagement Rate</strong></td>
                    <td>{data.get('engagement_rate', 0)}%</td>
                </tr>
                <tr>
                    <td><strong>Quality Score</strong></td>
                    <td><span class="grade {grade_class}">{quality}</span></td>
                    <td><strong>Posts Analyzed</strong></td>
                    <td>{data.get('posts_analyzed', 0) or data.get('videos_analyzed', 0)}</td>
                </tr>
            </table>
"""

            # Best posting times
            best_times = data.get("best_posting_times", {})
            if best_times.get("best_hours"):
                html += f"""
            <p><strong>Best Posting Times:</strong> {best_times.get('weekday_best', 'N/A')} at {', '.join(best_times.get('best_hours', [])[:3])}</p>
"""

            # Top hashtags (if available)
            hashtags = data.get("top_hashtags", [])
            if hashtags:
                html += f"""
            <p><strong>Top Hashtags:</strong> {' '.join(hashtags[:5])}</p>
"""

            html += "</div>"

    # Benchmark comparison
    benchmark = analysis.get("benchmark_comparison")
    if benchmark:
        html += f"""
        <h2>Industry Benchmark Comparison</h2>
        <div class="card">
            <table>
                <tr>
                    <th>Industry</th>
                    <th>Benchmark Engagement</th>
                    <th>Your Performance</th>
                    <th>Position</th>
                </tr>
                <tr>
                    <td>{benchmark.get('industry', 'N/A').capitalize()}</td>
                    <td>{benchmark.get('benchmark_engagement', 0)}%</td>
                    <td>{benchmark.get('engagement_vs_benchmark', 'N/A')}</td>
                    <td>{benchmark.get('position', 'N/A').capitalize()}</td>
                </tr>
            </table>
        </div>
"""

    # Recommendations
    recommendations = analysis.get("recommendations", [])
    if recommendations:
        html += """
        <h2>Recommendations</h2>
        <div class="recommendations">
            <ul>
"""
        for rec in recommendations:
            html += f"                <li>{rec}</li>\n"

        html += """
            </ul>
        </div>
"""

    # Comparison section (if provided)
    if comparison and comparison.get("accounts"):
        html += """
        <h2>Account Comparison</h2>
        <div class="card">
            <table>
                <tr>
                    <th>Account</th>
                    <th>Total Reach</th>
                    <th>Engagement Rate</th>
                    <th>Quality Score</th>
                    <th>Strongest Platform</th>
                </tr>
"""
        for acc in comparison["accounts"]:
            quality = acc.get("quality_score", "C")
            grade_class = f"grade-{quality[0].lower()}"
            html += f"""
                <tr>
                    <td>{acc.get('handle', 'N/A')}</td>
                    <td>{acc.get('total_reach', 0):,}</td>
                    <td>{acc.get('avg_engagement_rate', 0)}%</td>
                    <td><span class="grade {grade_class}">{quality}</span></td>
                    <td>{acc.get('strongest_platform', 'N/A').capitalize()}</td>
                </tr>
"""
        html += """
            </table>
        </div>
"""

    # Footer
    html += """
        <div class="footer">
            <p>Generated by Audience Analysis Tool</p>
            <p>Powered by Apify</p>
        </div>
    </div>
</body>
</html>
"""

    return html


def generate_csv(analysis: Dict, comparison: Dict = None) -> str:
    """
    Generate CSV output.
    """
    lines = ["account,platform,followers,engagement_rate,quality_score,growth_rate,posts_analyzed"]

    account = analysis.get("account", "Unknown")

    for platform_name, data in analysis.get("platforms", {}).items():
        followers = data.get("followers", 0) or data.get("subscribers", 0)
        engagement = data.get("engagement_rate", 0)
        quality = data.get("quality_score", "N/A")
        growth = data.get("recent_growth", {}).get("monthly_rate", 0)
        posts = data.get("posts_analyzed", 0) or data.get("videos_analyzed", 0)

        lines.append(f"{account},{platform_name},{followers},{engagement},{quality},{growth},{posts}")

    return "\n".join(lines)


def save_results(data: Any, output_path: str, format_type: str = "json") -> Path:
    """
    Save results in specified format.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = format_type if format_type != "json" else "json"
        output_path = f"audience_analysis_{timestamp}.{ext}"

    full_path = OUTPUT_DIR / output_path

    if format_type == "json":
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    elif format_type == "html":
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(data)
    elif format_type == "csv":
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(data)

    print(f"\nResults saved to: {full_path}")
    return full_path


def print_summary(analysis: Dict):
    """
    Print analysis summary to console.
    """
    print("\n" + "=" * 60)
    print("AUDIENCE ANALYSIS SUMMARY")
    print("=" * 60)

    print(f"\nAccount: {analysis.get('account', 'Unknown')}")

    summary = analysis.get("cross_platform_summary", {})
    if summary:
        print(f"\nCross-Platform Metrics:")
        print(f"  Total Reach: {summary.get('total_reach', 0):,}")
        print(f"  Avg Engagement: {summary.get('avg_engagement_rate', 0)}%")
        print(f"  Quality Score: {summary.get('overall_quality_score', 'N/A')}")
        print(f"  Growth Trend: {summary.get('growth_trend', 'Unknown')}")
        print(f"  Strongest Platform: {summary.get('strongest_platform', 'N/A')}")

    platforms = analysis.get("platforms", {})
    if platforms:
        print("\nPlatform Breakdown:")
        for platform_name, data in platforms.items():
            followers = data.get("followers", 0) or data.get("subscribers", 0)
            print(f"\n  [{platform_name.capitalize()}]")
            print(f"    Followers: {followers:,}")
            print(f"    Engagement: {data.get('engagement_rate', 0)}%")
            print(f"    Quality: {data.get('quality_score', 'N/A')}")

    recommendations = analysis.get("recommendations", [])
    if recommendations:
        print("\nTop Recommendations:")
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"  {i}. {rec}")

    print("\n" + "=" * 60)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Comprehensive cross-platform audience analysis tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single account analysis
  python analyze_audience.py @nike --platforms instagram facebook youtube

  # Compare multiple accounts
  python analyze_audience.py @nike @adidas @puma --compare

  # With industry benchmark
  python analyze_audience.py @mybrand --benchmark sportswear

  # Export HTML report
  python analyze_audience.py @brand --format html --output report.html

  # Quick profile-only scan
  python analyze_audience.py @brand --quick
        """
    )

    parser.add_argument(
        "accounts",
        nargs="+",
        help="Account handle(s) to analyze (e.g., @nike or nike)"
    )

    parser.add_argument(
        "--platforms",
        nargs="+",
        choices=["instagram", "facebook", "youtube", "tiktok"],
        default=["instagram", "facebook", "youtube", "tiktok"],
        help="Platforms to analyze (default: all)"
    )

    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare multiple accounts side-by-side"
    )

    parser.add_argument(
        "--benchmark",
        choices=list(INDUSTRY_BENCHMARKS.keys()),
        help="Industry to benchmark against"
    )

    parser.add_argument(
        "--max-posts",
        type=int,
        default=50,
        help="Maximum posts to analyze per platform (default: 50)"
    )

    parser.add_argument(
        "--include-comments",
        action="store_true",
        help="Include comment analysis for sentiment (slower)"
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick profile-only analysis (faster, less detail)"
    )

    parser.add_argument(
        "--format",
        choices=["json", "html", "csv"],
        default="json",
        help="Output format (default: json)"
    )

    parser.add_argument(
        "--output",
        help="Output filename (saved to .tmp directory)"
    )

    args = parser.parse_args()

    try:
        # Validate environment
        validate_environment()

        # Analyze each account
        all_analyses = []

        for account in args.accounts:
            analysis = analyze_account(
                handle=account,
                platforms=args.platforms,
                benchmark=args.benchmark,
                max_posts=args.max_posts,
                include_comments=args.include_comments,
                quick=args.quick
            )
            all_analyses.append(analysis)
            print_summary(analysis)

        # Generate comparison if requested
        comparison = None
        if args.compare and len(all_analyses) > 1:
            comparison = compare_accounts(all_analyses)
            print("\nComparison Rankings:")
            for metric, rankings in comparison.get("rankings", {}).items():
                print(f"\n  {metric.replace('_', ' ').title()}:")
                for r in rankings[:3]:
                    print(f"    {r['rank']}. {r['account']}: {r['value']:,}" if isinstance(r['value'], int) else f"    {r['rank']}. {r['account']}: {r['value']}")

        # Generate output
        if args.format == "json":
            if args.compare and comparison:
                output_data = {
                    "analyses": all_analyses,
                    "comparison": comparison
                }
            else:
                output_data = all_analyses[0] if len(all_analyses) == 1 else all_analyses

            save_results(output_data, args.output, "json")

        elif args.format == "html":
            # Use first analysis for single report, include comparison if available
            html_content = generate_html_report(all_analyses[0], comparison)
            save_results(html_content, args.output, "html")

        elif args.format == "csv":
            csv_content = generate_csv(all_analyses[0], comparison)
            save_results(csv_content, args.output, "csv")

        print("\nAudience analysis completed successfully!")
        return 0

    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
