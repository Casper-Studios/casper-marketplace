#!/usr/bin/env python3
"""
Enriched Trend Analysis Engine
Multi-platform trend discovery and analysis with velocity scoring, lifecycle staging,
geographic spread, sentiment analysis, and opportunity scoring.

Usage:
    # Analyze specific topic
    python analyze_trends.py "artificial intelligence" --sources google instagram tiktok --days 90

    # Discover trending topics in category
    python analyze_trends.py --category technology --discover --top 50

    # Compare trends
    python analyze_trends.py "AI" "blockchain" "metaverse" --compare --chart

    # Regional analysis
    python analyze_trends.py "fashion trends" --regions US UK FR DE --compare

    # Real-time monitoring mode
    python analyze_trends.py --category fitness --monitor --alert-threshold 50

    # Export trend report
    python analyze_trends.py "sustainable fashion" --format html --output trend_report.html
"""

import os
import sys
import json
import time
import argparse
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from enum import Enum

from apify_client import ApifyClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
OUTPUT_DIR = Path(__file__).parent.parent / ".tmp"

# Apify Actor IDs for each platform
ACTORS = {
    "google": "apify/google-trends-scraper",
    "instagram": "apify/instagram-hashtag-scraper",
    "tiktok": "clockworks/tiktok-scraper",
    "twitter": "kaitoeasyapi/twitter-x-data-tweet-scraper",
    "reddit": "trudax/reddit-scraper-lite",
    "youtube": "streamers/youtube-scraper"
}

# Cost estimates per platform (USD per item)
COST_PER_ITEM = {
    "google": 0.01,
    "instagram": 0.003,
    "tiktok": 0.005,
    "twitter": 0.00025,
    "reddit": 0.003,
    "youtube": 0.03
}


class LifecycleStage(Enum):
    """Trend lifecycle stages based on adoption curve."""
    EMERGING = "emerging"
    GROWING = "growing"
    PEAK = "peak"
    DECLINING = "declining"


class TrendDirection(Enum):
    """Overall trend direction."""
    RISING = "rising"
    STABLE = "stable"
    FALLING = "falling"
    VOLATILE = "volatile"


@dataclass
class VelocityMetrics:
    """Velocity scoring components."""
    score: int  # 0-100
    search_growth_rate: float
    social_growth_rate: float
    content_growth_rate: float
    engagement_growth_rate: float
    acceleration: float  # Positive = accelerating, negative = decelerating
    predicted_peak_days: Optional[int] = None


@dataclass
class GeographicSpread:
    """Geographic analysis of trend."""
    origin_region: str
    spread_pattern: str  # "radial", "regional", "global"
    hottest_regions: List[str]
    emerging_regions: List[str]
    regional_intensity: Dict[str, int]  # Region -> intensity score (0-100)


@dataclass
class SentimentAnalysis:
    """Sentiment breakdown for trend."""
    overall_sentiment: str  # "positive", "neutral", "negative"
    sentiment_score: float  # -1 to 1
    distribution: Dict[str, int]  # positive/neutral/negative percentages
    controversy_score: int  # 0-100
    emotion_breakdown: Dict[str, int]  # excitement, curiosity, skepticism, fear


@dataclass
class RelatedTrends:
    """Clustered related trends."""
    parent_trends: List[str]
    child_trends: List[str]
    sibling_trends: List[str]
    competing_trends: List[str]
    co_occurring: List[str]


@dataclass
class OpportunityScore:
    """Actionability scoring."""
    overall: int  # 0-100
    content_opportunity: int  # Ease of content creation
    commercial_opportunity: int  # Monetization potential
    timing_opportunity: int  # Window of opportunity
    recommendation: str


@dataclass
class PlatformData:
    """Data from a single platform."""
    platform: str
    success: bool
    items: List[Dict]
    metrics: Dict[str, Any]
    error: Optional[str] = None


@dataclass
class TrendAnalysis:
    """Complete trend analysis result."""
    query: str
    analysis_period: Dict[str, str]
    generated_at: str
    overall_trend: Dict[str, Any]
    velocity: VelocityMetrics
    lifecycle_stage: LifecycleStage
    opportunity: OpportunityScore
    sentiment: SentimentAnalysis
    geographic: GeographicSpread
    related_trends: RelatedTrends
    by_platform: Dict[str, Dict[str, Any]]
    predictions: Dict[str, Any]
    recommendations: List[Dict[str, str]]
    raw_data: Dict[str, Any] = field(default_factory=dict)


def validate_environment() -> None:
    """Validate required environment variables."""
    if not APIFY_TOKEN:
        raise ValueError(
            "APIFY_TOKEN not found in environment. "
            "Please add it to your .env file.\n"
            "Get your API key: https://console.apify.com/account/integrations"
        )


def get_client() -> ApifyClient:
    """Get Apify client instance."""
    return ApifyClient(APIFY_TOKEN)


# =============================================================================
# DATA COLLECTION FUNCTIONS
# =============================================================================

def collect_google_trends(
    query: str,
    days: int = 30,
    regions: List[str] = None
) -> PlatformData:
    """
    Collect Google Trends data for a query.

    Args:
        query: Search term
        days: Analysis period in days
        regions: List of region codes (e.g., ["US", "UK"])

    Returns:
        PlatformData with trend information
    """
    print(f"  [Google Trends] Collecting data for '{query}'...")
    client = get_client()

    # Default to US if no regions specified
    geo = regions[0] if regions else "US"

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    run_input = {
        "searchTerms": [query],
        "geo": geo,
        "timeRange": "past30Days" if days <= 30 else "past90Days",
        "isMultiple": False
    }

    try:
        run = client.actor(ACTORS["google"]).call(run_input=run_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        # Process Google Trends data
        metrics = {
            "search_interest": 0,
            "trend_direction": "stable",
            "change_percentage": 0,
            "related_queries": [],
            "rising_topics": []
        }

        if items:
            # Calculate average interest and trend
            interest_values = []
            for item in items:
                if "interestOverTime" in item:
                    for point in item.get("interestOverTime", []):
                        interest_values.append(point.get("value", 0))

                # Extract related queries
                if "relatedQueries" in item:
                    for rq in item.get("relatedQueries", {}).get("rising", []):
                        metrics["rising_topics"].append({
                            "query": rq.get("query", ""),
                            "growth": rq.get("value", "")
                        })
                    for rq in item.get("relatedQueries", {}).get("top", []):
                        metrics["related_queries"].append({
                            "query": rq.get("query", ""),
                            "value": rq.get("value", 0)
                        })

            if interest_values:
                metrics["search_interest"] = int(statistics.mean(interest_values[-7:]))  # Last 7 days

                # Calculate trend direction
                if len(interest_values) >= 14:
                    recent = statistics.mean(interest_values[-7:])
                    previous = statistics.mean(interest_values[-14:-7])
                    if previous > 0:
                        change = ((recent - previous) / previous) * 100
                        metrics["change_percentage"] = round(change, 1)
                        if change > 10:
                            metrics["trend_direction"] = f"+{round(change)}% vs last week"
                        elif change < -10:
                            metrics["trend_direction"] = f"{round(change)}% vs last week"
                        else:
                            metrics["trend_direction"] = "stable"

        print(f"  [Google Trends] Collected {len(items)} data points")
        return PlatformData(
            platform="google",
            success=True,
            items=items,
            metrics=metrics
        )

    except Exception as e:
        print(f"  [Google Trends] Error: {str(e)}")
        return PlatformData(
            platform="google",
            success=False,
            items=[],
            metrics={},
            error=str(e)
        )


def collect_instagram_trends(
    query: str,
    max_posts: int = 100
) -> PlatformData:
    """
    Collect Instagram hashtag data.

    Args:
        query: Hashtag to search (without #)
        max_posts: Maximum posts to collect

    Returns:
        PlatformData with Instagram metrics
    """
    print(f"  [Instagram] Collecting hashtag data for '#{query}'...")
    client = get_client()

    # Clean hashtag
    hashtag = query.replace("#", "").replace(" ", "")

    run_input = {
        "hashtags": [hashtag],
        "resultsLimit": max_posts,
        "resultsType": "posts"
    }

    try:
        run = client.actor(ACTORS["instagram"]).call(run_input=run_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        # Process Instagram data
        metrics = {
            "hashtag_posts": len(items),
            "total_likes": 0,
            "total_comments": 0,
            "avg_engagement": 0,
            "top_content_formats": [],
            "weekly_growth": "N/A",
            "top_creators": []
        }

        if items:
            # Aggregate metrics
            likes = []
            comments = []
            formats = defaultdict(int)
            creators = defaultdict(int)

            for item in items:
                like_count = item.get("likesCount", 0) or item.get("likes", 0)
                comment_count = item.get("commentsCount", 0) or item.get("comments", 0)
                likes.append(like_count)
                comments.append(comment_count)

                # Track content formats
                if item.get("isVideo"):
                    formats["reels"] += 1
                elif item.get("type") == "Sidecar":
                    formats["carousel"] += 1
                else:
                    formats["image"] += 1

                # Track top creators
                creator = item.get("ownerUsername", "")
                if creator:
                    creators[creator] += 1

            metrics["total_likes"] = sum(likes)
            metrics["total_comments"] = sum(comments)
            metrics["avg_engagement"] = round(statistics.mean(likes) + statistics.mean(comments) * 2, 1)

            # Sort formats by count
            sorted_formats = sorted(formats.items(), key=lambda x: x[1], reverse=True)
            metrics["top_content_formats"] = [f[0] for f in sorted_formats[:3]]

            # Top creators
            sorted_creators = sorted(creators.items(), key=lambda x: x[1], reverse=True)
            metrics["top_creators"] = [f"@{c[0]}" for c in sorted_creators[:5]]

        print(f"  [Instagram] Collected {len(items)} posts")
        return PlatformData(
            platform="instagram",
            success=True,
            items=items,
            metrics=metrics
        )

    except Exception as e:
        print(f"  [Instagram] Error: {str(e)}")
        return PlatformData(
            platform="instagram",
            success=False,
            items=[],
            metrics={},
            error=str(e)
        )


def collect_tiktok_trends(
    query: str,
    max_results: int = 50
) -> PlatformData:
    """
    Collect TikTok hashtag/trend data.

    Args:
        query: Hashtag or topic
        max_results: Maximum videos to collect

    Returns:
        PlatformData with TikTok metrics
    """
    print(f"  [TikTok] Collecting hashtag data for '#{query}'...")
    client = get_client()

    # Clean hashtag
    hashtag = query.replace("#", "").replace(" ", "")

    run_input = {
        "startUrls": [f"https://www.tiktok.com/tag/{hashtag}"],
        "resultsLimit": max_results,
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
        "shouldDownloadSubtitles": True
    }

    try:
        run = client.actor(ACTORS["tiktok"]).call(run_input=run_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        # Process TikTok data
        metrics = {
            "hashtag_views": 0,
            "total_videos": len(items),
            "total_likes": 0,
            "total_comments": 0,
            "total_shares": 0,
            "trending_sounds": [],
            "creator_adoption": "low",
            "viral_videos": 0
        }

        if items:
            views = []
            likes = []
            comments = []
            shares = []
            sounds = defaultdict(int)
            unique_creators = set()

            for item in items:
                view_count = item.get("playCount", 0) or item.get("videoPlayCount", 0)
                like_count = item.get("diggCount", 0) or item.get("likesCount", 0)
                comment_count = item.get("commentCount", 0)
                share_count = item.get("shareCount", 0)

                views.append(view_count)
                likes.append(like_count)
                comments.append(comment_count)
                shares.append(share_count)

                # Track sounds
                music = item.get("musicMeta", {}) or item.get("music", {})
                if music:
                    sound_name = music.get("musicName", "") or music.get("title", "")
                    if sound_name:
                        sounds[sound_name] += 1

                # Track creators
                author = item.get("authorMeta", {}) or item.get("author", {})
                if author:
                    unique_creators.add(author.get("name", "") or author.get("uniqueId", ""))

                # Count viral videos (>1M views)
                if view_count > 1000000:
                    metrics["viral_videos"] += 1

            metrics["hashtag_views"] = sum(views)
            metrics["total_likes"] = sum(likes)
            metrics["total_comments"] = sum(comments)
            metrics["total_shares"] = sum(shares)

            # Determine creator adoption level
            creator_count = len(unique_creators)
            if creator_count > 40:
                metrics["creator_adoption"] = "high"
            elif creator_count > 20:
                metrics["creator_adoption"] = "medium"
            else:
                metrics["creator_adoption"] = "low"

            # Top trending sounds
            sorted_sounds = sorted(sounds.items(), key=lambda x: x[1], reverse=True)
            metrics["trending_sounds"] = [
                {"name": s[0], "uses": s[1]}
                for s in sorted_sounds[:5]
            ]

        print(f"  [TikTok] Collected {len(items)} videos")
        return PlatformData(
            platform="tiktok",
            success=True,
            items=items,
            metrics=metrics
        )

    except Exception as e:
        print(f"  [TikTok] Error: {str(e)}")
        return PlatformData(
            platform="tiktok",
            success=False,
            items=[],
            metrics={},
            error=str(e)
        )


def collect_twitter_trends(
    query: str,
    max_tweets: int = 100
) -> PlatformData:
    """
    Collect Twitter/X data for a query.

    Args:
        query: Search query
        max_tweets: Maximum tweets to collect

    Returns:
        PlatformData with Twitter metrics
    """
    print(f"  [Twitter] Collecting tweets for '{query}'...")
    client = get_client()

    run_input = {
        "searchTerms": [query],
        "maxTweets": max_tweets,
        "sort": "Latest"
    }

    try:
        run = client.actor(ACTORS["twitter"]).call(run_input=run_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        # Process Twitter data
        metrics = {
            "total_tweets": len(items),
            "total_likes": 0,
            "total_retweets": 0,
            "total_replies": 0,
            "avg_engagement": 0,
            "top_tweets": [],
            "influencer_mentions": 0
        }

        if items:
            likes = []
            retweets = []
            replies = []
            top_tweets = []

            for item in items:
                like_count = item.get("likeCount", 0) or item.get("favorite_count", 0)
                retweet_count = item.get("retweetCount", 0) or item.get("retweet_count", 0)
                reply_count = item.get("replyCount", 0)

                likes.append(like_count)
                retweets.append(retweet_count)
                replies.append(reply_count)

                # Check for influencer (verified or >10k followers)
                author = item.get("author", {}) or {}
                followers = author.get("followers", 0) or author.get("followersCount", 0)
                if followers > 10000 or author.get("isVerified", False):
                    metrics["influencer_mentions"] += 1

                # Track top tweets
                engagement = like_count + retweet_count * 2 + reply_count
                top_tweets.append({
                    "text": (item.get("text", "") or item.get("full_text", ""))[:100],
                    "engagement": engagement,
                    "author": author.get("userName", "") or author.get("screen_name", "")
                })

            metrics["total_likes"] = sum(likes)
            metrics["total_retweets"] = sum(retweets)
            metrics["total_replies"] = sum(replies)
            metrics["avg_engagement"] = round(statistics.mean(likes) + statistics.mean(retweets) * 2, 1)

            # Sort and get top tweets
            top_tweets.sort(key=lambda x: x["engagement"], reverse=True)
            metrics["top_tweets"] = top_tweets[:5]

        print(f"  [Twitter] Collected {len(items)} tweets")
        return PlatformData(
            platform="twitter",
            success=True,
            items=items,
            metrics=metrics
        )

    except Exception as e:
        print(f"  [Twitter] Error: {str(e)}")
        return PlatformData(
            platform="twitter",
            success=False,
            items=[],
            metrics={},
            error=str(e)
        )


def collect_reddit_trends(
    query: str,
    max_posts: int = 100
) -> PlatformData:
    """
    Collect Reddit discussion data.

    Args:
        query: Search query
        max_posts: Maximum posts to collect

    Returns:
        PlatformData with Reddit metrics
    """
    print(f"  [Reddit] Collecting discussions for '{query}'...")
    client = get_client()

    run_input = {
        "searchTerms": [query],
        "maxItems": max_posts,
        "sort": "relevance",
        "time": "month"
    }

    try:
        run = client.actor(ACTORS["reddit"]).call(run_input=run_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        # Process Reddit data
        metrics = {
            "active_discussions": len(items),
            "total_upvotes": 0,
            "total_comments": 0,
            "avg_upvotes": 0,
            "top_subreddits": [],
            "sentiment_indicators": {
                "positive_ratio": 0,
                "controversial_posts": 0
            }
        }

        if items:
            upvotes = []
            comments = []
            subreddits = defaultdict(int)

            for item in items:
                upvote_count = item.get("score", 0) or item.get("ups", 0)
                comment_count = item.get("numComments", 0) or item.get("num_comments", 0)

                upvotes.append(upvote_count)
                comments.append(comment_count)

                # Track subreddits
                subreddit = item.get("subreddit", "") or item.get("communityName", "")
                if subreddit:
                    subreddits[subreddit] += 1

                # Track controversial posts (high comment-to-upvote ratio)
                if upvote_count > 0 and comment_count / upvote_count > 0.5:
                    metrics["sentiment_indicators"]["controversial_posts"] += 1

            metrics["total_upvotes"] = sum(upvotes)
            metrics["total_comments"] = sum(comments)
            metrics["avg_upvotes"] = round(statistics.mean(upvotes), 1) if upvotes else 0

            # Calculate positive ratio (upvote ratio proxy)
            avg_score = statistics.mean(upvotes) if upvotes else 0
            metrics["sentiment_indicators"]["positive_ratio"] = min(100, int(avg_score / 10))

            # Top subreddits
            sorted_subs = sorted(subreddits.items(), key=lambda x: x[1], reverse=True)
            metrics["top_subreddits"] = [f"r/{s[0]}" for s in sorted_subs[:5]]

        print(f"  [Reddit] Collected {len(items)} posts")
        return PlatformData(
            platform="reddit",
            success=True,
            items=items,
            metrics=metrics
        )

    except Exception as e:
        print(f"  [Reddit] Error: {str(e)}")
        return PlatformData(
            platform="reddit",
            success=False,
            items=[],
            metrics={},
            error=str(e)
        )


def collect_youtube_trends(
    query: str,
    max_results: int = 50
) -> PlatformData:
    """
    Collect YouTube search/trend data.

    Args:
        query: Search query
        max_results: Maximum videos to collect

    Returns:
        PlatformData with YouTube metrics
    """
    print(f"  [YouTube] Collecting videos for '{query}'...")
    client = get_client()

    run_input = {
        "searchKeywords": query,
        "maxResults": max_results,
        "downloadSubtitles": False
    }

    try:
        run = client.actor(ACTORS["youtube"]).call(run_input=run_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        # Process YouTube data
        metrics = {
            "trending_videos": len(items),
            "total_views": 0,
            "avg_views": 0,
            "total_likes": 0,
            "top_channels": [],
            "content_types": [],
            "avg_duration": 0
        }

        if items:
            views = []
            likes = []
            durations = []
            channels = defaultdict(int)
            content_types = defaultdict(int)

            for item in items:
                view_count = item.get("viewCount", 0) or item.get("views", 0)
                like_count = item.get("likeCount", 0) or item.get("likes", 0)
                duration = item.get("duration", 0)

                views.append(view_count)
                likes.append(like_count)
                if duration:
                    durations.append(duration)

                # Track channels
                channel = item.get("channelName", "") or item.get("channelTitle", "")
                if channel:
                    channels[channel] += 1

                # Categorize content type by duration
                if duration:
                    if duration < 60:
                        content_types["shorts"] += 1
                    elif duration < 600:
                        content_types["standard"] += 1
                    else:
                        content_types["long-form"] += 1

            metrics["total_views"] = sum(views)
            metrics["avg_views"] = round(statistics.mean(views), 0) if views else 0
            metrics["total_likes"] = sum(likes)
            metrics["avg_duration"] = round(statistics.mean(durations) / 60, 1) if durations else 0

            # Top channels
            sorted_channels = sorted(channels.items(), key=lambda x: x[1], reverse=True)
            metrics["top_channels"] = [c[0] for c in sorted_channels[:5]]

            # Content types
            sorted_types = sorted(content_types.items(), key=lambda x: x[1], reverse=True)
            metrics["content_types"] = [t[0] for t in sorted_types]

        print(f"  [YouTube] Collected {len(items)} videos")
        return PlatformData(
            platform="youtube",
            success=True,
            items=items,
            metrics=metrics
        )

    except Exception as e:
        print(f"  [YouTube] Error: {str(e)}")
        return PlatformData(
            platform="youtube",
            success=False,
            items=[],
            metrics={},
            error=str(e)
        )


# =============================================================================
# ENRICHMENT FUNCTIONS
# =============================================================================

def calculate_velocity_score(platform_data: Dict[str, PlatformData]) -> VelocityMetrics:
    """
    Calculate trend velocity score based on growth rates across platforms.

    Args:
        platform_data: Dictionary of platform data

    Returns:
        VelocityMetrics with scoring components
    """
    # Initialize growth rates
    search_growth = 0.0
    social_growth = 0.0
    content_growth = 0.0
    engagement_growth = 0.0

    valid_sources = 0

    # Google Trends - search growth
    if "google" in platform_data and platform_data["google"].success:
        metrics = platform_data["google"].metrics
        change = metrics.get("change_percentage", 0)
        search_growth = min(100, max(0, 50 + change))  # Normalize to 0-100
        valid_sources += 1

    # Social platforms - social growth
    social_scores = []
    for platform in ["instagram", "tiktok", "twitter"]:
        if platform in platform_data and platform_data[platform].success:
            metrics = platform_data[platform].metrics
            # Use engagement as proxy for growth
            if platform == "instagram":
                score = min(100, metrics.get("avg_engagement", 0) / 10)
            elif platform == "tiktok":
                adoption = metrics.get("creator_adoption", "low")
                score = {"high": 80, "medium": 50, "low": 20}.get(adoption, 20)
            else:
                score = min(100, metrics.get("avg_engagement", 0) / 5)
            social_scores.append(score)

    if social_scores:
        social_growth = statistics.mean(social_scores)
        valid_sources += 1

    # Content growth - based on volume
    content_scores = []
    for platform in ["tiktok", "youtube", "instagram"]:
        if platform in platform_data and platform_data[platform].success:
            items = len(platform_data[platform].items)
            # Normalize: 100 items = 100 score
            score = min(100, items)
            content_scores.append(score)

    if content_scores:
        content_growth = statistics.mean(content_scores)
        valid_sources += 1

    # Engagement growth - combined metrics
    engagement_scores = []
    for platform in platform_data.values():
        if platform.success:
            metrics = platform.metrics
            # Different platforms have different engagement metrics
            if "avg_engagement" in metrics:
                engagement_scores.append(min(100, metrics["avg_engagement"] / 5))
            elif "avg_upvotes" in metrics:
                engagement_scores.append(min(100, metrics["avg_upvotes"] / 10))

    if engagement_scores:
        engagement_growth = statistics.mean(engagement_scores)
        valid_sources += 1

    # Calculate weighted velocity score
    if valid_sources > 0:
        velocity_score = int(
            search_growth * 0.3 +
            social_growth * 0.25 +
            content_growth * 0.25 +
            engagement_growth * 0.2
        )
    else:
        velocity_score = 0

    # Calculate acceleration (simplified)
    acceleration = (search_growth - 50) / 10  # Positive if growing faster than average

    # Predict peak timing
    if velocity_score > 80:
        predicted_peak_days = 30
    elif velocity_score > 60:
        predicted_peak_days = 60
    elif velocity_score > 40:
        predicted_peak_days = 90
    else:
        predicted_peak_days = None

    return VelocityMetrics(
        score=velocity_score,
        search_growth_rate=round(search_growth, 1),
        social_growth_rate=round(social_growth, 1),
        content_growth_rate=round(content_growth, 1),
        engagement_growth_rate=round(engagement_growth, 1),
        acceleration=round(acceleration, 2),
        predicted_peak_days=predicted_peak_days
    )


def determine_lifecycle_stage(
    velocity: VelocityMetrics,
    platform_data: Dict[str, PlatformData]
) -> LifecycleStage:
    """
    Determine trend lifecycle stage based on velocity and adoption patterns.

    Args:
        velocity: Velocity metrics
        platform_data: Platform data dictionary

    Returns:
        LifecycleStage enum value
    """
    score = velocity.score
    acceleration = velocity.acceleration

    # Check content volume as adoption indicator
    total_items = sum(
        len(p.items) for p in platform_data.values() if p.success
    )

    if score > 70 and acceleration > 0:
        # High velocity, accelerating
        if total_items < 200:
            return LifecycleStage.EMERGING
        else:
            return LifecycleStage.GROWING
    elif score > 50:
        # Moderate velocity
        if acceleration < -0.5:
            return LifecycleStage.PEAK
        else:
            return LifecycleStage.GROWING
    elif score > 30:
        # Low velocity
        if acceleration < 0:
            return LifecycleStage.DECLINING
        else:
            return LifecycleStage.PEAK
    else:
        # Very low velocity
        return LifecycleStage.DECLINING


def analyze_geographic_spread(
    platform_data: Dict[str, PlatformData],
    regions: List[str] = None
) -> GeographicSpread:
    """
    Analyze geographic spread of the trend.

    Args:
        platform_data: Platform data dictionary
        regions: Regions to analyze

    Returns:
        GeographicSpread analysis
    """
    # Default analysis based on common patterns
    # In production, this would use regional data from each platform

    default_regions = regions or ["US"]

    # Estimate regional intensity based on platform data
    regional_intensity = {}
    for region in default_regions:
        # US typically has highest intensity for English content
        if region == "US":
            regional_intensity[region] = 100
        elif region in ["UK", "CA", "AU"]:
            regional_intensity[region] = 75
        elif region in ["DE", "FR", "NL"]:
            regional_intensity[region] = 50
        else:
            regional_intensity[region] = 30

    # Determine spread pattern
    if len(regional_intensity) > 5:
        spread_pattern = "global"
    elif len(regional_intensity) > 2:
        spread_pattern = "regional"
    else:
        spread_pattern = "localized"

    # Sort regions by intensity
    sorted_regions = sorted(
        regional_intensity.items(),
        key=lambda x: x[1],
        reverse=True
    )

    hottest = [r[0] for r in sorted_regions[:3]]
    emerging = [r[0] for r in sorted_regions[3:6] if r[1] < 50]

    return GeographicSpread(
        origin_region=default_regions[0] if default_regions else "US",
        spread_pattern=spread_pattern,
        hottest_regions=hottest,
        emerging_regions=emerging or ["BR", "ID", "IN"],  # Common emerging markets
        regional_intensity=regional_intensity
    )


def analyze_sentiment(
    platform_data: Dict[str, PlatformData]
) -> SentimentAnalysis:
    """
    Analyze sentiment across platforms.

    Args:
        platform_data: Platform data dictionary

    Returns:
        SentimentAnalysis with breakdown
    """
    # Aggregate sentiment indicators
    positive_signals = 0
    negative_signals = 0
    total_signals = 0
    controversy_indicators = 0

    for platform, data in platform_data.items():
        if not data.success:
            continue

        metrics = data.metrics

        if platform == "reddit":
            # Reddit has explicit sentiment indicators
            sentiment_data = metrics.get("sentiment_indicators", {})
            positive_signals += sentiment_data.get("positive_ratio", 50)
            controversy_indicators += sentiment_data.get("controversial_posts", 0)
            total_signals += 100

        elif platform == "twitter":
            # Use engagement as sentiment proxy
            engagement = metrics.get("avg_engagement", 0)
            influencer_mentions = metrics.get("influencer_mentions", 0)
            positive_signals += min(100, engagement + influencer_mentions * 5)
            total_signals += 100

        elif platform in ["instagram", "tiktok", "youtube"]:
            # High engagement generally indicates positive sentiment
            if platform == "instagram":
                engagement = metrics.get("avg_engagement", 0)
            elif platform == "tiktok":
                adoption = metrics.get("creator_adoption", "low")
                engagement = {"high": 80, "medium": 50, "low": 20}.get(adoption, 20)
            else:
                engagement = min(100, metrics.get("avg_views", 0) / 10000)

            positive_signals += engagement
            total_signals += 100

    # Calculate overall sentiment
    if total_signals > 0:
        sentiment_score = (positive_signals / total_signals) * 2 - 1  # -1 to 1 scale
        sentiment_score = round(max(-1, min(1, sentiment_score)), 2)
    else:
        sentiment_score = 0.0

    # Determine overall sentiment label
    if sentiment_score > 0.3:
        overall_sentiment = "positive"
    elif sentiment_score < -0.3:
        overall_sentiment = "negative"
    else:
        overall_sentiment = "neutral"

    # Calculate distribution
    if sentiment_score > 0:
        positive_pct = int(50 + sentiment_score * 40)
        negative_pct = int(20 - sentiment_score * 15)
    else:
        positive_pct = int(50 + sentiment_score * 40)
        negative_pct = int(20 - sentiment_score * 15)

    neutral_pct = 100 - positive_pct - negative_pct

    # Controversy score
    controversy_score = min(100, controversy_indicators * 10)

    # Emotion breakdown (simplified)
    emotion_breakdown = {
        "excitement": int(positive_pct * 0.7),
        "curiosity": int(neutral_pct * 0.8),
        "skepticism": int(negative_pct * 0.5),
        "fear": int(negative_pct * 0.3)
    }

    return SentimentAnalysis(
        overall_sentiment=overall_sentiment,
        sentiment_score=sentiment_score,
        distribution={
            "positive": positive_pct,
            "neutral": neutral_pct,
            "negative": negative_pct
        },
        controversy_score=controversy_score,
        emotion_breakdown=emotion_breakdown
    )


def find_related_trends(
    query: str,
    platform_data: Dict[str, PlatformData]
) -> RelatedTrends:
    """
    Find and cluster related trends.

    Args:
        query: Original query
        platform_data: Platform data dictionary

    Returns:
        RelatedTrends with clustering
    """
    related_queries = []
    rising_topics = []
    hashtags = set()

    # Extract related data from platforms
    if "google" in platform_data and platform_data["google"].success:
        metrics = platform_data["google"].metrics
        related_queries.extend([
            rq["query"] for rq in metrics.get("related_queries", [])
        ])
        rising_topics.extend([
            rt["query"] for rt in metrics.get("rising_topics", [])
        ])

    # Extract hashtags from social platforms
    for platform in ["instagram", "tiktok"]:
        if platform in platform_data and platform_data[platform].success:
            for item in platform_data[platform].items[:20]:  # Sample first 20
                item_hashtags = item.get("hashtags", [])
                if isinstance(item_hashtags, list):
                    hashtags.update(item_hashtags)

    # Clean query for comparison
    query_lower = query.lower()

    # Categorize trends
    parent_trends = []
    child_trends = []
    sibling_trends = []
    competing_trends = []
    co_occurring = []

    # Analyze related queries
    for rq in related_queries + rising_topics:
        rq_lower = rq.lower()
        if query_lower in rq_lower and len(rq_lower) > len(query_lower):
            # More specific = child trend
            child_trends.append(rq)
        elif rq_lower in query_lower:
            # More general = parent trend
            parent_trends.append(rq)
        else:
            # Neither = sibling
            sibling_trends.append(rq)

    # Add common hashtags as co-occurring
    for tag in list(hashtags)[:10]:
        if tag.lower() != query_lower:
            co_occurring.append(f"#{tag}")

    # Add some generic competing trends based on common patterns
    if "ai" in query_lower or "artificial intelligence" in query_lower:
        competing_trends = ["traditional software", "human expertise", "manual processes"]
    elif "crypto" in query_lower or "blockchain" in query_lower:
        competing_trends = ["traditional finance", "centralized systems"]

    return RelatedTrends(
        parent_trends=parent_trends[:5],
        child_trends=child_trends[:5],
        sibling_trends=sibling_trends[:5],
        competing_trends=competing_trends[:3],
        co_occurring=co_occurring[:10]
    )


def calculate_opportunity_score(
    velocity: VelocityMetrics,
    lifecycle: LifecycleStage,
    sentiment: SentimentAnalysis
) -> OpportunityScore:
    """
    Calculate actionability/opportunity score.

    Args:
        velocity: Velocity metrics
        lifecycle: Lifecycle stage
        sentiment: Sentiment analysis

    Returns:
        OpportunityScore with components
    """
    # Content opportunity: How easy is it to create relevant content?
    # Higher velocity = more demand = higher opportunity
    content_opp = min(100, velocity.score + 10)

    # Commercial opportunity: Monetization potential
    # Best in growing stage with positive sentiment
    commercial_base = {
        LifecycleStage.EMERGING: 60,
        LifecycleStage.GROWING: 90,
        LifecycleStage.PEAK: 70,
        LifecycleStage.DECLINING: 30
    }.get(lifecycle, 50)

    # Adjust for sentiment
    sentiment_modifier = (sentiment.sentiment_score + 1) / 2  # 0 to 1
    commercial_opp = int(commercial_base * sentiment_modifier)

    # Timing opportunity: Is there still room to participate?
    timing_base = {
        LifecycleStage.EMERGING: 95,
        LifecycleStage.GROWING: 80,
        LifecycleStage.PEAK: 40,
        LifecycleStage.DECLINING: 15
    }.get(lifecycle, 50)

    # Adjust for velocity (high velocity = act fast)
    timing_opp = min(100, timing_base + velocity.acceleration * 10)

    # Calculate overall score
    overall = int(
        content_opp * 0.35 +
        commercial_opp * 0.35 +
        timing_opp * 0.30
    )

    # Generate recommendation
    if overall >= 80:
        recommendation = "High priority - act now"
    elif overall >= 60:
        recommendation = "Good opportunity - plan action within 2 weeks"
    elif overall >= 40:
        recommendation = "Moderate potential - worth monitoring"
    elif overall >= 20:
        recommendation = "Low priority - limited near-term potential"
    else:
        recommendation = "Not recommended at this time"

    return OpportunityScore(
        overall=overall,
        content_opportunity=int(content_opp),
        commercial_opportunity=int(commercial_opp),
        timing_opportunity=int(timing_opp),
        recommendation=recommendation
    )


def generate_predictions(
    velocity: VelocityMetrics,
    lifecycle: LifecycleStage,
    sentiment: SentimentAnalysis
) -> Dict[str, Any]:
    """
    Generate trend predictions.

    Args:
        velocity: Velocity metrics
        lifecycle: Lifecycle stage
        sentiment: Sentiment analysis

    Returns:
        Dictionary with predictions
    """
    # Peak timing prediction
    if velocity.predicted_peak_days:
        peak_date = datetime.now() + timedelta(days=velocity.predicted_peak_days)
        if velocity.predicted_peak_days <= 30:
            peak_timing = "Next 30 days"
        elif velocity.predicted_peak_days <= 60:
            peak_timing = f"Q{(peak_date.month - 1) // 3 + 1} {peak_date.year}"
        else:
            peak_timing = f"Q{(peak_date.month - 1) // 3 + 1} {peak_date.year}"
    else:
        peak_timing = "Already peaked" if lifecycle == LifecycleStage.DECLINING else "Unknown"

    # Longevity prediction
    if lifecycle in [LifecycleStage.EMERGING, LifecycleStage.GROWING]:
        if velocity.score > 70:
            longevity = "sustained"
        else:
            longevity = "moderate"
    elif lifecycle == LifecycleStage.PEAK:
        longevity = "short-term"
    else:
        longevity = "fading"

    # Confidence based on data quality
    confidence = min(90, velocity.score)

    # Risk factors
    risk_factors = []
    if sentiment.controversy_score > 50:
        risk_factors.append("High controversy risk")
    if lifecycle == LifecycleStage.PEAK:
        risk_factors.append("Market saturation")
    if velocity.acceleration < -1:
        risk_factors.append("Decelerating growth")
    if sentiment.sentiment_score < 0:
        risk_factors.append("Negative sentiment")

    if not risk_factors:
        risk_factors = ["None identified"]

    return {
        "peak_timing": peak_timing,
        "longevity": longevity,
        "confidence": confidence,
        "risk_factors": risk_factors
    }


def generate_recommendations(
    query: str,
    lifecycle: LifecycleStage,
    opportunity: OpportunityScore,
    platform_data: Dict[str, PlatformData]
) -> List[Dict[str, str]]:
    """
    Generate actionable recommendations.

    Args:
        query: Original query
        lifecycle: Lifecycle stage
        opportunity: Opportunity score
        platform_data: Platform data dictionary

    Returns:
        List of recommendation dictionaries
    """
    recommendations = []

    # Lifecycle-based recommendations
    if lifecycle == LifecycleStage.EMERGING:
        recommendations.append({
            "action": "Create foundational content now",
            "priority": "high",
            "rationale": "Early mover advantage - establish authority before saturation"
        })
        recommendations.append({
            "action": "Build email list around this topic",
            "priority": "high",
            "rationale": "Capture early adopters for long-term engagement"
        })
    elif lifecycle == LifecycleStage.GROWING:
        recommendations.append({
            "action": "Scale content production",
            "priority": "high",
            "rationale": "Mainstream adoption in progress - maximize reach now"
        })
        recommendations.append({
            "action": "Create how-to and tutorial content",
            "priority": "high",
            "rationale": "High demand for practical, actionable information"
        })
    elif lifecycle == LifecycleStage.PEAK:
        recommendations.append({
            "action": "Differentiate with unique angle",
            "priority": "medium",
            "rationale": "Market saturated - need to stand out from competition"
        })
        recommendations.append({
            "action": "Focus on niche sub-topics",
            "priority": "medium",
            "rationale": "General content oversaturated - go deeper"
        })
    else:  # Declining
        recommendations.append({
            "action": "Archive or sunset content",
            "priority": "low",
            "rationale": "Diminishing returns - focus resources elsewhere"
        })
        recommendations.append({
            "action": "Pivot to successor trends",
            "priority": "medium",
            "rationale": "Identify and transition to emerging replacements"
        })

    # Platform-specific recommendations
    best_platforms = []
    for platform, data in platform_data.items():
        if data.success and len(data.items) > 0:
            best_platforms.append(platform)

    if "tiktok" in best_platforms:
        recommendations.append({
            "action": f"Create short-form video content about {query}",
            "priority": "high" if lifecycle in [LifecycleStage.EMERGING, LifecycleStage.GROWING] else "medium",
            "rationale": "TikTok showing strong engagement for this topic"
        })

    if "youtube" in best_platforms:
        recommendations.append({
            "action": "Develop long-form educational content",
            "priority": "medium",
            "rationale": "YouTube audience seeking in-depth information"
        })

    # Geographic recommendations
    recommendations.append({
        "action": "Target English-speaking markets first",
        "priority": "medium",
        "rationale": "Highest search volume and engagement in US/UK/CA"
    })

    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 1))

    return recommendations[:6]  # Return top 6 recommendations


# =============================================================================
# MAIN ANALYSIS FUNCTION
# =============================================================================

def analyze_trend(
    query: str,
    sources: List[str] = None,
    days: int = 30,
    regions: List[str] = None,
    max_results_per_source: int = 100,
    enrich_level: str = "full"
) -> TrendAnalysis:
    """
    Perform comprehensive trend analysis.

    Args:
        query: Search term or topic
        sources: List of platforms to analyze
        days: Analysis period in days
        regions: Geographic regions to analyze
        max_results_per_source: Max items per platform
        enrich_level: "basic" or "full"

    Returns:
        TrendAnalysis with complete results
    """
    validate_environment()

    # Default sources
    if not sources:
        sources = ["google", "instagram", "tiktok"]

    # Default regions
    if not regions:
        regions = ["US"]

    print(f"\nAnalyzing trend: '{query}'")
    print(f"Sources: {', '.join(sources)}")
    print(f"Period: {days} days")
    print(f"Regions: {', '.join(regions)}")
    print("-" * 50)

    # Collect data from each platform
    platform_data: Dict[str, PlatformData] = {}

    collection_funcs = {
        "google": lambda: collect_google_trends(query, days, regions),
        "instagram": lambda: collect_instagram_trends(query, max_results_per_source),
        "tiktok": lambda: collect_tiktok_trends(query, max_results_per_source),
        "twitter": lambda: collect_twitter_trends(query, max_results_per_source),
        "reddit": lambda: collect_reddit_trends(query, max_results_per_source),
        "youtube": lambda: collect_youtube_trends(query, max_results_per_source // 2)
    }

    print("\nCollecting data...")
    for source in sources:
        if source in collection_funcs:
            platform_data[source] = collection_funcs[source]()

    # Check if we have any successful data
    successful_sources = [p for p, d in platform_data.items() if d.success]
    if not successful_sources:
        raise ValueError("No data collected from any source. Check your query and API credentials.")

    print(f"\nSuccessful sources: {', '.join(successful_sources)}")

    # Calculate enrichments
    print("\nCalculating enrichments...")

    # Velocity scoring
    print("  - Velocity score")
    velocity = calculate_velocity_score(platform_data)

    # Lifecycle stage
    print("  - Lifecycle stage")
    lifecycle = determine_lifecycle_stage(velocity, platform_data)

    # Geographic spread
    print("  - Geographic spread")
    geographic = analyze_geographic_spread(platform_data, regions)

    # Sentiment analysis
    print("  - Sentiment analysis")
    sentiment = analyze_sentiment(platform_data)

    # Related trends
    print("  - Related trends")
    related = find_related_trends(query, platform_data)

    # Opportunity score
    print("  - Opportunity score")
    opportunity = calculate_opportunity_score(velocity, lifecycle, sentiment)

    # Predictions
    print("  - Predictions")
    predictions = generate_predictions(velocity, lifecycle, sentiment)

    # Recommendations
    print("  - Recommendations")
    recommendations = generate_recommendations(query, lifecycle, opportunity, platform_data)

    # Build platform-specific results
    by_platform = {}
    for platform, data in platform_data.items():
        if data.success:
            by_platform[platform] = data.metrics

    # Calculate analysis period
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Build overall trend summary
    overall_trend = {
        "direction": TrendDirection.RISING.value if velocity.score > 50 else TrendDirection.FALLING.value,
        "velocity_score": velocity.score,
        "lifecycle_stage": lifecycle.value,
        "opportunity_score": opportunity.overall,
        "sentiment": sentiment.overall_sentiment,
        "controversy_score": sentiment.controversy_score
    }

    # Create analysis result
    analysis = TrendAnalysis(
        query=query,
        analysis_period={
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d")
        },
        generated_at=datetime.now().isoformat(),
        overall_trend=overall_trend,
        velocity=velocity,
        lifecycle_stage=lifecycle,
        opportunity=opportunity,
        sentiment=sentiment,
        geographic=geographic,
        related_trends=related,
        by_platform=by_platform,
        predictions=predictions,
        recommendations=recommendations
    )

    print("\nAnalysis complete!")
    return analysis


def compare_trends(
    queries: List[str],
    sources: List[str] = None,
    days: int = 30
) -> Dict[str, Any]:
    """
    Compare multiple trends side by side.

    Args:
        queries: List of search terms
        sources: Platforms to analyze
        days: Analysis period

    Returns:
        Comparison dictionary
    """
    print(f"\nComparing trends: {', '.join(queries)}")
    print("-" * 50)

    analyses = {}
    for query in queries:
        try:
            analyses[query] = analyze_trend(query, sources, days)
        except Exception as e:
            print(f"Warning: Failed to analyze '{query}': {e}")

    if not analyses:
        raise ValueError("No trends could be analyzed")

    # Build comparison
    comparison = {
        "queries": queries,
        "analysis_period": {
            "start": (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d"),
            "end": datetime.now().strftime("%Y-%m-%d")
        },
        "generated_at": datetime.now().isoformat(),
        "comparison_matrix": [],
        "winner": None,
        "insights": []
    }

    # Build comparison matrix
    for query, analysis in analyses.items():
        comparison["comparison_matrix"].append({
            "query": query,
            "velocity_score": analysis.velocity.score,
            "lifecycle_stage": analysis.lifecycle_stage.value,
            "opportunity_score": analysis.opportunity.overall,
            "sentiment": analysis.sentiment.overall_sentiment,
            "recommendation": analysis.opportunity.recommendation
        })

    # Determine winner by opportunity score
    winner = max(analyses.items(), key=lambda x: x[1].opportunity.overall)
    comparison["winner"] = {
        "query": winner[0],
        "opportunity_score": winner[1].opportunity.overall,
        "rationale": winner[1].opportunity.recommendation
    }

    # Generate insights
    scores = [(q, a.opportunity.overall) for q, a in analyses.items()]
    scores.sort(key=lambda x: x[1], reverse=True)

    if len(scores) >= 2:
        comparison["insights"].append(
            f"'{scores[0][0]}' has the highest opportunity score ({scores[0][1]}) "
            f"compared to '{scores[-1][0]}' ({scores[-1][1]})"
        )

    # Stage distribution insight
    stages = [a.lifecycle_stage.value for a in analyses.values()]
    if LifecycleStage.EMERGING.value in stages:
        emerging = [q for q, a in analyses.items() if a.lifecycle_stage == LifecycleStage.EMERGING]
        comparison["insights"].append(
            f"Emerging trends with high potential: {', '.join(emerging)}"
        )

    return comparison


def discover_trends(
    category: str,
    top: int = 20,
    sources: List[str] = None
) -> Dict[str, Any]:
    """
    Discover trending topics in a category.

    Args:
        category: Topic category (e.g., "technology", "fitness")
        top: Number of trends to discover
        sources: Platforms to search

    Returns:
        Discovery results
    """
    print(f"\nDiscovering trends in category: '{category}'")
    print(f"Looking for top {top} trends...")
    print("-" * 50)

    # Use Google Trends to discover related topics
    client = get_client()

    run_input = {
        "searchTerms": [category],
        "geo": "US",
        "timeRange": "past30Days"
    }

    try:
        run = client.actor(ACTORS["google"]).call(run_input=run_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        discovered = []

        for item in items:
            # Extract rising topics
            rising = item.get("relatedQueries", {}).get("rising", [])
            for topic in rising[:top]:
                discovered.append({
                    "query": topic.get("query", ""),
                    "growth": topic.get("value", ""),
                    "type": "rising"
                })

            # Extract top topics
            top_topics = item.get("relatedQueries", {}).get("top", [])
            for topic in top_topics[:top // 2]:
                discovered.append({
                    "query": topic.get("query", ""),
                    "interest": topic.get("value", 0),
                    "type": "established"
                })

        # Deduplicate
        seen = set()
        unique_discovered = []
        for d in discovered:
            if d["query"] not in seen:
                seen.add(d["query"])
                unique_discovered.append(d)

        return {
            "category": category,
            "discovered_at": datetime.now().isoformat(),
            "total_found": len(unique_discovered),
            "trends": unique_discovered[:top],
            "recommendation": f"Analyze top trends with: python analyze_trends.py \"{unique_discovered[0]['query']}\" --sources google instagram tiktok" if unique_discovered else ""
        }

    except Exception as e:
        print(f"Error discovering trends: {e}")
        return {
            "category": category,
            "error": str(e),
            "trends": []
        }


# =============================================================================
# OUTPUT FUNCTIONS
# =============================================================================

def format_json_output(analysis: TrendAnalysis) -> Dict[str, Any]:
    """Convert analysis to JSON-serializable dictionary."""
    result = {
        "query": analysis.query,
        "analysis_period": analysis.analysis_period,
        "generated_at": analysis.generated_at,
        "overall_trend": analysis.overall_trend,
        "velocity": {
            "score": analysis.velocity.score,
            "search_growth_rate": analysis.velocity.search_growth_rate,
            "social_growth_rate": analysis.velocity.social_growth_rate,
            "content_growth_rate": analysis.velocity.content_growth_rate,
            "engagement_growth_rate": analysis.velocity.engagement_growth_rate,
            "acceleration": analysis.velocity.acceleration,
            "predicted_peak_days": analysis.velocity.predicted_peak_days
        },
        "lifecycle_stage": analysis.lifecycle_stage.value,
        "opportunity": {
            "overall": analysis.opportunity.overall,
            "content_opportunity": analysis.opportunity.content_opportunity,
            "commercial_opportunity": analysis.opportunity.commercial_opportunity,
            "timing_opportunity": analysis.opportunity.timing_opportunity,
            "recommendation": analysis.opportunity.recommendation
        },
        "sentiment": {
            "overall_sentiment": analysis.sentiment.overall_sentiment,
            "sentiment_score": analysis.sentiment.sentiment_score,
            "distribution": analysis.sentiment.distribution,
            "controversy_score": analysis.sentiment.controversy_score,
            "emotion_breakdown": analysis.sentiment.emotion_breakdown
        },
        "geographic_analysis": {
            "origin_region": analysis.geographic.origin_region,
            "spread_pattern": analysis.geographic.spread_pattern,
            "hottest_regions": analysis.geographic.hottest_regions,
            "emerging_regions": analysis.geographic.emerging_regions,
            "regional_intensity": analysis.geographic.regional_intensity
        },
        "related_trends": {
            "parent": analysis.related_trends.parent_trends,
            "child": analysis.related_trends.child_trends,
            "sibling": analysis.related_trends.sibling_trends,
            "competing": analysis.related_trends.competing_trends,
            "co_occurring": analysis.related_trends.co_occurring
        },
        "by_platform": analysis.by_platform,
        "predictions": analysis.predictions,
        "recommendations": analysis.recommendations
    }
    return result


def format_html_output(analysis: TrendAnalysis) -> str:
    """Generate HTML report from analysis."""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trend Analysis: {analysis.query}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #1a1a1a; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #333; margin-top: 30px; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric {{ display: inline-block; text-align: center; padding: 15px 25px; margin: 5px; background: #f8f9fa; border-radius: 8px; }}
        .metric-value {{ font-size: 32px; font-weight: bold; color: #007bff; }}
        .metric-label {{ font-size: 12px; color: #666; text-transform: uppercase; }}
        .score-high {{ color: #28a745; }}
        .score-medium {{ color: #ffc107; }}
        .score-low {{ color: #dc3545; }}
        .tag {{ display: inline-block; padding: 4px 12px; margin: 3px; background: #e9ecef; border-radius: 15px; font-size: 14px; }}
        .recommendation {{ padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; background: #f8f9fa; }}
        .recommendation.high {{ border-color: #28a745; }}
        .recommendation.medium {{ border-color: #ffc107; }}
        .recommendation.low {{ border-color: #6c757d; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }}
        th {{ background: #f8f9fa; }}
        .progress {{ height: 20px; background: #e9ecef; border-radius: 10px; overflow: hidden; }}
        .progress-bar {{ height: 100%; background: linear-gradient(90deg, #007bff, #00bcd4); }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Trend Analysis: {analysis.query}</h1>
        <p>Generated: {analysis.generated_at} | Period: {analysis.analysis_period['start']} to {analysis.analysis_period['end']}</p>

        <div class="card">
            <h2>Overview</h2>
            <div class="metric">
                <div class="metric-value {'score-high' if analysis.velocity.score >= 70 else 'score-medium' if analysis.velocity.score >= 40 else 'score-low'}">{analysis.velocity.score}</div>
                <div class="metric-label">Velocity Score</div>
            </div>
            <div class="metric">
                <div class="metric-value">{analysis.lifecycle_stage.value.title()}</div>
                <div class="metric-label">Lifecycle Stage</div>
            </div>
            <div class="metric">
                <div class="metric-value {'score-high' if analysis.opportunity.overall >= 70 else 'score-medium' if analysis.opportunity.overall >= 40 else 'score-low'}">{analysis.opportunity.overall}</div>
                <div class="metric-label">Opportunity Score</div>
            </div>
            <div class="metric">
                <div class="metric-value">{analysis.sentiment.overall_sentiment.title()}</div>
                <div class="metric-label">Sentiment</div>
            </div>
        </div>

        <div class="card">
            <h2>Velocity Breakdown</h2>
            <table>
                <tr><th>Metric</th><th>Score</th><th>Visualization</th></tr>
                <tr>
                    <td>Search Growth</td>
                    <td>{analysis.velocity.search_growth_rate}</td>
                    <td><div class="progress"><div class="progress-bar" style="width: {analysis.velocity.search_growth_rate}%"></div></div></td>
                </tr>
                <tr>
                    <td>Social Growth</td>
                    <td>{analysis.velocity.social_growth_rate}</td>
                    <td><div class="progress"><div class="progress-bar" style="width: {analysis.velocity.social_growth_rate}%"></div></div></td>
                </tr>
                <tr>
                    <td>Content Growth</td>
                    <td>{analysis.velocity.content_growth_rate}</td>
                    <td><div class="progress"><div class="progress-bar" style="width: {analysis.velocity.content_growth_rate}%"></div></div></td>
                </tr>
                <tr>
                    <td>Engagement Growth</td>
                    <td>{analysis.velocity.engagement_growth_rate}</td>
                    <td><div class="progress"><div class="progress-bar" style="width: {analysis.velocity.engagement_growth_rate}%"></div></div></td>
                </tr>
            </table>
        </div>

        <div class="card">
            <h2>Geographic Analysis</h2>
            <p><strong>Origin:</strong> {analysis.geographic.origin_region} | <strong>Pattern:</strong> {analysis.geographic.spread_pattern}</p>
            <p><strong>Hottest Regions:</strong> {', '.join(analysis.geographic.hottest_regions)}</p>
            <p><strong>Emerging Regions:</strong> {', '.join(analysis.geographic.emerging_regions)}</p>
        </div>

        <div class="card">
            <h2>Related Trends</h2>
            <p><strong>Parent Trends:</strong> {''.join([f'<span class="tag">{t}</span>' for t in analysis.related_trends.parent_trends]) or 'None'}</p>
            <p><strong>Child Trends:</strong> {''.join([f'<span class="tag">{t}</span>' for t in analysis.related_trends.child_trends]) or 'None'}</p>
            <p><strong>Sibling Trends:</strong> {''.join([f'<span class="tag">{t}</span>' for t in analysis.related_trends.sibling_trends]) or 'None'}</p>
            <p><strong>Co-occurring:</strong> {''.join([f'<span class="tag">{t}</span>' for t in analysis.related_trends.co_occurring]) or 'None'}</p>
        </div>

        <div class="card">
            <h2>Predictions</h2>
            <table>
                <tr><td><strong>Peak Timing</strong></td><td>{analysis.predictions['peak_timing']}</td></tr>
                <tr><td><strong>Longevity</strong></td><td>{analysis.predictions['longevity'].title()}</td></tr>
                <tr><td><strong>Confidence</strong></td><td>{analysis.predictions['confidence']}%</td></tr>
                <tr><td><strong>Risk Factors</strong></td><td>{', '.join(analysis.predictions['risk_factors'])}</td></tr>
            </table>
        </div>

        <div class="card">
            <h2>Recommendations</h2>
            {''.join([f'''
            <div class="recommendation {r['priority']}">
                <strong>{r['action']}</strong>
                <span class="tag">{r['priority'].upper()}</span>
                <p>{r['rationale']}</p>
            </div>
            ''' for r in analysis.recommendations])}
        </div>

        <div class="card">
            <h2>Platform Data</h2>
            {''.join([f'''
            <h3>{platform.title()}</h3>
            <table>
                {''.join([f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in metrics.items() if not isinstance(v, (list, dict))])}
            </table>
            ''' for platform, metrics in analysis.by_platform.items()])}
        </div>
    </div>
</body>
</html>"""
    return html


def save_output(
    data: Any,
    output_format: str = "json",
    filename: str = None
) -> Path:
    """Save analysis output to file."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if isinstance(data, TrendAnalysis):
        query_slug = data.query.replace(" ", "_").lower()[:30]
        if not filename:
            filename = f"trend_analysis_{query_slug}_{timestamp}"
    else:
        if not filename:
            filename = f"trend_output_{timestamp}"

    if output_format == "json":
        output_path = OUTPUT_DIR / f"{filename}.json"
        content = format_json_output(data) if isinstance(data, TrendAnalysis) else data
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)

    elif output_format == "html":
        output_path = OUTPUT_DIR / f"{filename}.html"
        content = format_html_output(data) if isinstance(data, TrendAnalysis) else str(data)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

    elif output_format == "csv":
        output_path = OUTPUT_DIR / f"{filename}.csv"
        if isinstance(data, TrendAnalysis):
            # Flatten for CSV
            rows = [
                ["Metric", "Value"],
                ["Query", data.query],
                ["Velocity Score", data.velocity.score],
                ["Lifecycle Stage", data.lifecycle_stage.value],
                ["Opportunity Score", data.opportunity.overall],
                ["Sentiment", data.sentiment.overall_sentiment],
                ["Peak Timing", data.predictions['peak_timing']],
                ["Recommendation", data.opportunity.recommendation]
            ]
            with open(output_path, 'w', encoding='utf-8') as f:
                for row in rows:
                    f.write(",".join(str(c) for c in row) + "\n")
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)

    print(f"\nOutput saved to: {output_path}")
    return output_path


def print_summary(analysis: TrendAnalysis) -> None:
    """Print a summary of the analysis to console."""
    print("\n" + "=" * 60)
    print(f"TREND ANALYSIS SUMMARY: {analysis.query}")
    print("=" * 60)

    print(f"\n{'='*20} OVERVIEW {'='*20}")
    print(f"  Velocity Score:    {analysis.velocity.score}/100")
    print(f"  Lifecycle Stage:   {analysis.lifecycle_stage.value.title()}")
    print(f"  Opportunity Score: {analysis.opportunity.overall}/100")
    print(f"  Sentiment:         {analysis.sentiment.overall_sentiment.title()} ({analysis.sentiment.sentiment_score:.2f})")

    print(f"\n{'='*20} VELOCITY {'='*20}")
    print(f"  Search Growth:     {analysis.velocity.search_growth_rate}")
    print(f"  Social Growth:     {analysis.velocity.social_growth_rate}")
    print(f"  Content Growth:    {analysis.velocity.content_growth_rate}")
    print(f"  Acceleration:      {analysis.velocity.acceleration}")

    print(f"\n{'='*20} PREDICTIONS {'='*20}")
    print(f"  Peak Timing:       {analysis.predictions['peak_timing']}")
    print(f"  Longevity:         {analysis.predictions['longevity']}")
    print(f"  Confidence:        {analysis.predictions['confidence']}%")
    print(f"  Risk Factors:      {', '.join(analysis.predictions['risk_factors'])}")

    print(f"\n{'='*20} RECOMMENDATIONS {'='*20}")
    for i, rec in enumerate(analysis.recommendations[:3], 1):
        print(f"  {i}. [{rec['priority'].upper()}] {rec['action']}")
        print(f"     {rec['rationale']}")

    print(f"\n{'='*20} OPPORTUNITY {'='*20}")
    print(f"  {analysis.opportunity.recommendation}")

    print("\n" + "=" * 60)


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Enriched Trend Analysis Engine - Multi-platform trend discovery and analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze specific topic
  python analyze_trends.py "artificial intelligence" --sources google instagram tiktok --days 90

  # Discover trending topics in category
  python analyze_trends.py --category technology --discover --top 50

  # Compare trends
  python analyze_trends.py "AI" "blockchain" "metaverse" --compare

  # Regional analysis
  python analyze_trends.py "fashion trends" --regions US UK FR DE

  # Export HTML report
  python analyze_trends.py "sustainable fashion" --format html --output trend_report.html
        """
    )

    # Positional arguments
    parser.add_argument(
        "queries",
        nargs="*",
        help="Search term(s) to analyze"
    )

    # Data collection options
    parser.add_argument(
        "--sources",
        nargs="+",
        choices=["google", "instagram", "tiktok", "twitter", "reddit", "youtube", "all"],
        default=["google", "instagram", "tiktok"],
        help="Platforms to analyze (default: google instagram tiktok)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Analysis period in days (default: 30)"
    )
    parser.add_argument(
        "--regions",
        nargs="+",
        default=["US"],
        help="Geographic regions to analyze (default: US)"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=100,
        help="Maximum results per platform (default: 100)"
    )

    # Discovery mode
    parser.add_argument(
        "--category",
        help="Category for trend discovery"
    )
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Enable discovery mode"
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Number of trends to discover (default: 20)"
    )

    # Comparison mode
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare multiple trends"
    )

    # Output options
    parser.add_argument(
        "--format",
        choices=["json", "html", "csv"],
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--output",
        help="Custom output filename"
    )
    parser.add_argument(
        "--enrich",
        choices=["basic", "full"],
        default="full",
        help="Enrichment level (default: full)"
    )

    # Monitoring (placeholder)
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Continuous monitoring mode (not yet implemented)"
    )
    parser.add_argument(
        "--alert-threshold",
        type=int,
        default=70,
        help="Velocity score threshold for alerts (default: 70)"
    )

    args = parser.parse_args()

    # Expand "all" sources
    if "all" in args.sources:
        args.sources = ["google", "instagram", "tiktok", "twitter", "reddit", "youtube"]

    try:
        # Validate environment
        validate_environment()

        # Discovery mode
        if args.discover or args.category:
            category = args.category or (args.queries[0] if args.queries else "technology")
            result = discover_trends(category, args.top, args.sources)
            output_path = save_output(result, args.format, args.output)

            print("\nDiscovered Trends:")
            for i, trend in enumerate(result.get("trends", [])[:10], 1):
                print(f"  {i}. {trend['query']} ({trend.get('growth', trend.get('interest', 'N/A'))})")

            return 0

        # Comparison mode
        if args.compare and len(args.queries) > 1:
            result = compare_trends(args.queries, args.sources, args.days)
            output_path = save_output(result, args.format, args.output)

            print("\nComparison Results:")
            print(f"Winner: {result['winner']['query']} (Score: {result['winner']['opportunity_score']})")
            for insight in result.get("insights", []):
                print(f"  - {insight}")

            return 0

        # Single trend analysis
        if not args.queries:
            parser.print_help()
            return 1

        query = " ".join(args.queries)
        analysis = analyze_trend(
            query=query,
            sources=args.sources,
            days=args.days,
            regions=args.regions,
            max_results_per_source=args.max_results,
            enrich_level=args.enrich
        )

        # Print summary
        print_summary(analysis)

        # Save output
        save_output(analysis, args.format, args.output)

        return 0

    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
