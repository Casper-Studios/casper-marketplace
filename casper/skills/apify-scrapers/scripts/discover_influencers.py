#!/usr/bin/env python3
"""
Influencer Discovery Script
Multi-platform influencer discovery with scoring, tier classification, fake follower detection,
brand safety analysis, and contact extraction.

Supports: Instagram, TikTok, YouTube, Twitter/X

Usage:
    # Discover by hashtag
    python discover_influencers.py --hashtags fitness health --platform instagram --tier micro --min-engagement 3.0

    # Discover from competitor followers
    python discover_influencers.py --competitor @competitor --find-influencers --min-followers 10000

    # Multi-platform discovery
    python discover_influencers.py --topic "sustainable fashion" --platforms instagram tiktok youtube --max-results 100

    # With contact extraction
    python discover_influencers.py --hashtags tech --extract-contacts --output influencers_with_contacts.json

    # Export for outreach
    python discover_influencers.py --topic "AI" --tier micro mid --format csv --output outreach_list.csv

    # Search by keyword
    python discover_influencers.py --keywords "AI influencer" "tech reviewer" --platform youtube

    # Location-based discovery
    python discover_influencers.py --hashtags fashion --location "New York" --platform instagram
"""

import os
import re
import json
import csv
import argparse
import statistics
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from urllib.parse import urlparse
from apify_client import ApifyClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
OUTPUT_DIR = Path(__file__).parent.parent / ".tmp"

# Apify Actor IDs for different platforms
ACTORS = {
    "instagram": {
        "hashtag": "apify/instagram-hashtag-scraper",
        "profile": "apify/instagram-profile-scraper",
        "posts": "apify/instagram-scraper",
        "comments": "apify/instagram-comment-scraper"
    },
    "tiktok": {
        "hashtag": "clockworks/tiktok-scraper",
        "profile": "clockworks/tiktok-scraper"
    },
    "youtube": {
        "search": "streamers/youtube-scraper",
        "channel": "streamers/youtube-channel-scraper"
    },
    "twitter": {
        "search": "kaitoeasyapi/twitter-x-data-tweet-scraper",
        "profile": "kaitoeasyapi/twitter-x-data-tweet-scraper"
    }
}

# Influencer Tier Definitions
INFLUENCER_TIERS = {
    "nano": {"min": 1000, "max": 10000, "label": "Nano (1K-10K)"},
    "micro": {"min": 10000, "max": 100000, "label": "Micro (10K-100K)"},
    "mid": {"min": 100000, "max": 500000, "label": "Mid-tier (100K-500K)"},
    "macro": {"min": 500000, "max": 1000000, "label": "Macro (500K-1M)"},
    "mega": {"min": 1000000, "max": float('inf'), "label": "Mega (1M+)"}
}

# Estimated Post Rates by Tier (USD)
ESTIMATED_POST_RATES = {
    "nano": {"min": 50, "max": 250, "display": "$50-250"},
    "micro": {"min": 250, "max": 1500, "display": "$250-1.5K"},
    "mid": {"min": 1500, "max": 5000, "display": "$1.5K-5K"},
    "macro": {"min": 5000, "max": 15000, "display": "$5K-15K"},
    "mega": {"min": 15000, "max": 100000, "display": "$15K-100K+"}
}

# Scoring Weights
SCORING_WEIGHTS = {
    "engagement_rate": 0.30,       # 30% weight
    "follower_authenticity": 0.25, # 25% weight
    "content_relevance": 0.20,     # 20% weight
    "posting_consistency": 0.15,   # 15% weight
    "growth_rate": 0.10            # 10% weight
}

# Brand Safety Keywords (flagged content)
BRAND_SAFETY_RED_FLAGS = [
    "controversial", "political", "nsfw", "adult", "gambling",
    "violence", "drugs", "alcohol", "tobacco", "weapons"
]

BRAND_SAFETY_YELLOW_FLAGS = [
    "opinion", "rant", "debate", "drama", "beef", "callout"
]


def validate_environment():
    """Validate required environment variables."""
    if not APIFY_TOKEN:
        raise ValueError(
            "APIFY_TOKEN not found in environment. "
            "Please add it to your .env file."
        )


def classify_tier(followers: int) -> str:
    """
    Classify influencer tier based on follower count.

    Args:
        followers: Number of followers

    Returns:
        str: Tier name (nano, micro, mid, macro, mega)
    """
    for tier, bounds in INFLUENCER_TIERS.items():
        if bounds["min"] <= followers < bounds["max"]:
            return tier
    return "mega"  # Default for very large accounts


def calculate_engagement_rate(likes: int, comments: int, followers: int,
                              views: int = 0, shares: int = 0) -> float:
    """
    Calculate engagement rate based on available metrics.

    Args:
        likes: Number of likes
        comments: Number of comments
        followers: Number of followers
        views: Number of views (for video content)
        shares: Number of shares

    Returns:
        float: Engagement rate as percentage
    """
    if followers == 0:
        return 0.0

    # Standard engagement: (likes + comments) / followers * 100
    base_engagement = (likes + comments) / followers * 100

    # Add bonus for shares if available
    if shares > 0:
        share_bonus = (shares / followers) * 50  # shares weighted at 50%
        base_engagement += share_bonus

    # For video content, consider view rate
    if views > 0 and views > followers:
        # Viral content bonus
        viral_multiplier = min(views / followers, 3.0) / 3.0  # Cap at 3x followers
        base_engagement *= (1 + viral_multiplier * 0.2)  # Up to 20% bonus

    return round(base_engagement, 2)


def calculate_authenticity_score(engagement_rate: float, followers: int,
                                  avg_comments_length: float = 0,
                                  comment_diversity: float = 0) -> int:
    """
    Estimate follower authenticity using heuristics.

    Fake follower indicators:
    - Very low engagement rate for high follower count
    - Short, generic comments
    - Low comment diversity (same users commenting)

    Args:
        engagement_rate: Calculated engagement rate
        followers: Number of followers
        avg_comments_length: Average comment length in characters
        comment_diversity: Ratio of unique commenters to total comments

    Returns:
        int: Authenticity score (0-100)
    """
    score = 100

    # Engagement rate baseline check
    tier = classify_tier(followers)

    # Expected engagement by tier (higher followers usually means lower engagement)
    expected_engagement = {
        "nano": 5.0,
        "micro": 3.0,
        "mid": 2.0,
        "macro": 1.5,
        "mega": 1.0
    }

    expected = expected_engagement.get(tier, 2.0)

    # Penalize if engagement is suspiciously low
    if engagement_rate < expected * 0.3:
        score -= 40  # Major red flag
    elif engagement_rate < expected * 0.5:
        score -= 25
    elif engagement_rate < expected * 0.7:
        score -= 10

    # Penalize if engagement is suspiciously high (possible fake engagement)
    if engagement_rate > expected * 5:
        score -= 30  # Unusual, possibly fake
    elif engagement_rate > expected * 3:
        score -= 15

    # Bonus for quality comments (if data available)
    if avg_comments_length > 50:  # Longer comments suggest real engagement
        score += 5
    elif avg_comments_length < 10:  # Very short comments suspicious
        score -= 10

    # Comment diversity bonus
    if comment_diversity > 0.8:  # Many unique commenters
        score += 10
    elif comment_diversity < 0.3:  # Same people commenting
        score -= 15

    return max(0, min(100, score))


def analyze_brand_safety(content_texts: List[str]) -> Dict[str, Any]:
    """
    Analyze content for brand safety concerns.

    Args:
        content_texts: List of post captions/descriptions

    Returns:
        dict: Brand safety analysis with status and flags
    """
    red_count = 0
    yellow_count = 0
    flagged_terms = []

    combined_text = " ".join(content_texts).lower()

    for term in BRAND_SAFETY_RED_FLAGS:
        if term in combined_text:
            red_count += 1
            flagged_terms.append({"term": term, "severity": "red"})

    for term in BRAND_SAFETY_YELLOW_FLAGS:
        if term in combined_text:
            yellow_count += 1
            flagged_terms.append({"term": term, "severity": "yellow"})

    # Determine overall status
    if red_count >= 2:
        status = "red"
        description = "Multiple high-risk content flags"
    elif red_count == 1:
        status = "yellow"
        description = "Some potentially risky content"
    elif yellow_count >= 3:
        status = "yellow"
        description = "Multiple moderate-risk content flags"
    else:
        status = "green"
        description = "No significant brand safety concerns"

    return {
        "status": status,
        "description": description,
        "red_flags": red_count,
        "yellow_flags": yellow_count,
        "flagged_terms": flagged_terms[:5]  # Top 5 flagged terms
    }


def extract_contact_info(bio: str, website: str = "") -> Dict[str, Any]:
    """
    Extract contact information from bio and website.

    Args:
        bio: Profile biography text
        website: Profile website URL

    Returns:
        dict: Extracted contact information
    """
    contact = {
        "email": None,
        "phone": None,
        "website": None,
        "business_inquiry_link": None,
        "linktree": None,
        "other_links": []
    }

    if not bio:
        bio = ""

    # Email extraction
    email_pattern = r'[\w.+-]+@[\w-]+\.[\w.-]+'
    emails = re.findall(email_pattern, bio)
    if emails:
        # Filter out common non-email patterns
        valid_emails = [e for e in emails if not e.endswith('.com.')]
        if valid_emails:
            contact["email"] = valid_emails[0]

    # Business email indicators in bio
    business_patterns = [
        r'business[\s:]+([^\s]+@[\w-]+\.[\w.-]+)',
        r'collab[\s:]+([^\s]+@[\w-]+\.[\w.-]+)',
        r'inquiry[\s:]+([^\s]+@[\w-]+\.[\w.-]+)',
        r'contact[\s:]+([^\s]+@[\w-]+\.[\w.-]+)'
    ]
    for pattern in business_patterns:
        match = re.search(pattern, bio, re.IGNORECASE)
        if match:
            contact["email"] = match.group(1)
            break

    # Website
    if website:
        contact["website"] = website

    # Linktree detection
    linktree_pattern = r'linktr\.ee/[\w.-]+'
    linktree_match = re.search(linktree_pattern, bio, re.IGNORECASE)
    if linktree_match:
        contact["linktree"] = f"https://{linktree_match.group()}"

    # Other common link patterns
    link_patterns = [
        (r'beacons\.ai/[\w.-]+', 'beacons'),
        (r'bio\.link/[\w.-]+', 'biolink'),
        (r'stan\.store/[\w.-]+', 'stan_store'),
        (r'tap\.bio/[\w.-]+', 'tapbio')
    ]

    for pattern, link_type in link_patterns:
        match = re.search(pattern, bio, re.IGNORECASE)
        if match:
            contact["other_links"].append({
                "type": link_type,
                "url": f"https://{match.group()}"
            })

    return contact


def extract_hashtags_from_content(posts: List[Dict]) -> List[Tuple[str, int]]:
    """
    Extract and count hashtags from posts.

    Args:
        posts: List of post data

    Returns:
        List of (hashtag, count) tuples sorted by frequency
    """
    hashtag_counts = {}

    for post in posts:
        caption = post.get("caption", "") or post.get("text", "") or ""
        hashtags = re.findall(r'#(\w+)', caption)
        for tag in hashtags:
            tag_lower = tag.lower()
            hashtag_counts[tag_lower] = hashtag_counts.get(tag_lower, 0) + 1

    # Sort by count, return top hashtags
    sorted_tags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_tags[:20]


def categorize_content(posts: List[Dict], hashtags: List[Tuple[str, int]]) -> List[str]:
    """
    Categorize influencer content based on hashtags and captions.

    Args:
        posts: List of post data
        hashtags: List of (hashtag, count) tuples

    Returns:
        List of content category strings
    """
    # Category keywords mapping
    categories = {
        "fitness": ["fitness", "workout", "gym", "exercise", "training", "gains", "fitfam"],
        "fashion": ["fashion", "style", "outfit", "ootd", "clothing", "wear", "streetwear"],
        "beauty": ["beauty", "makeup", "skincare", "cosmetics", "glam", "mua"],
        "food": ["food", "recipe", "cooking", "foodie", "chef", "restaurant", "cuisine"],
        "travel": ["travel", "wanderlust", "vacation", "trip", "explore", "adventure"],
        "tech": ["tech", "technology", "gadget", "software", "coding", "ai", "startup"],
        "gaming": ["gaming", "gamer", "esports", "twitch", "streamer", "playstation", "xbox"],
        "lifestyle": ["lifestyle", "life", "daily", "routine", "vlog", "day"],
        "business": ["business", "entrepreneur", "marketing", "money", "investing", "finance"],
        "parenting": ["parenting", "mom", "dad", "kids", "family", "baby", "mother"],
        "entertainment": ["entertainment", "comedy", "funny", "humor", "dance", "music"],
        "health": ["health", "wellness", "mindfulness", "meditation", "mental", "nutrition"],
        "education": ["education", "learn", "tutorial", "tips", "howto", "course"]
    }

    # Get all hashtag texts
    hashtag_texts = [h[0] for h in hashtags]

    # Score each category
    category_scores = {}
    for category, keywords in categories.items():
        score = sum(1 for h in hashtag_texts if any(k in h for k in keywords))
        if score > 0:
            category_scores[category] = score

    # Also check captions
    all_text = " ".join(
        (p.get("caption", "") or p.get("text", "") or "").lower()
        for p in posts
    )

    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in all_text:
                category_scores[category] = category_scores.get(category, 0) + 0.5

    # Return top categories
    sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    return [c[0] for c in sorted_categories[:5]]


def calculate_influencer_score(
    engagement_rate: float,
    authenticity_score: int,
    content_relevance: float,
    posting_frequency: float,
    growth_rate: float = 0
) -> int:
    """
    Calculate overall influencer score using weighted algorithm.

    Weights:
    - Engagement rate: 30%
    - Follower authenticity: 25%
    - Content relevance: 20%
    - Posting consistency: 15%
    - Growth rate: 10%

    Args:
        engagement_rate: Engagement rate percentage
        authenticity_score: Authenticity score (0-100)
        content_relevance: Content relevance score (0-100)
        posting_frequency: Posts per week (normalized to 0-100)
        growth_rate: Growth rate percentage (normalized to 0-100)

    Returns:
        int: Overall influencer score (0-100)
    """
    # Normalize engagement rate (5% = 100 score)
    engagement_normalized = min(100, (engagement_rate / 5) * 100)

    # Normalize posting frequency (7 posts/week = 100)
    posting_normalized = min(100, (posting_frequency / 7) * 100)

    # Normalize growth rate (10% monthly = 100)
    growth_normalized = min(100, (growth_rate / 10) * 100)

    # Calculate weighted score
    score = (
        engagement_normalized * SCORING_WEIGHTS["engagement_rate"] +
        authenticity_score * SCORING_WEIGHTS["follower_authenticity"] +
        content_relevance * SCORING_WEIGHTS["content_relevance"] +
        posting_normalized * SCORING_WEIGHTS["posting_consistency"] +
        growth_normalized * SCORING_WEIGHTS["growth_rate"]
    )

    return int(min(100, max(0, score)))


def estimate_cpm(tier: str, platform: str) -> Dict[str, Any]:
    """
    Estimate CPM (cost per thousand impressions) by tier and platform.

    Args:
        tier: Influencer tier
        platform: Social platform

    Returns:
        dict: CPM estimates
    """
    # Platform multipliers
    platform_multipliers = {
        "instagram": 1.0,
        "tiktok": 0.8,  # Generally cheaper
        "youtube": 1.5,  # Generally more expensive
        "twitter": 0.7
    }

    base_cpm = {
        "nano": {"min": 2, "max": 5},
        "micro": {"min": 5, "max": 15},
        "mid": {"min": 15, "max": 30},
        "macro": {"min": 30, "max": 50},
        "mega": {"min": 50, "max": 100}
    }

    multiplier = platform_multipliers.get(platform, 1.0)
    tier_cpm = base_cpm.get(tier, base_cpm["micro"])

    return {
        "cpm_min": round(tier_cpm["min"] * multiplier, 2),
        "cpm_max": round(tier_cpm["max"] * multiplier, 2),
        "display": f"${round(tier_cpm['min'] * multiplier)}-${round(tier_cpm['max'] * multiplier)}"
    }


# ============================================================================
# Platform-Specific Scrapers
# ============================================================================

def scrape_instagram_by_hashtag(hashtags: List[str], max_results: int = 100) -> Dict:
    """Scrape Instagram posts by hashtag."""
    print(f"Scraping Instagram for hashtags: {hashtags}")

    client = ApifyClient(APIFY_TOKEN)
    clean_hashtags = [h.lstrip('#') for h in hashtags]

    run_input = {
        "hashtags": clean_hashtags,
        "resultsLimit": max_results,
        "resultsType": "posts"
    }

    run = client.actor(ACTORS["instagram"]["hashtag"]).call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    return {"platform": "instagram", "items": items, "run_id": run["id"]}


def scrape_instagram_profiles(usernames: List[str]) -> Dict:
    """Scrape Instagram profile details."""
    print(f"Scraping Instagram profiles: {usernames}")

    client = ApifyClient(APIFY_TOKEN)
    clean_usernames = [u.lstrip('@') for u in usernames]

    run_input = {"usernames": clean_usernames}

    run = client.actor(ACTORS["instagram"]["profile"]).call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    return {"platform": "instagram", "items": items, "run_id": run["id"]}


def scrape_tiktok_by_hashtag(hashtags: List[str], max_results: int = 100) -> Dict:
    """Scrape TikTok videos by hashtag."""
    print(f"Scraping TikTok for hashtags: {hashtags}")

    client = ApifyClient(APIFY_TOKEN)

    start_urls = [
        f"https://www.tiktok.com/tag/{h.lstrip('#')}"
        for h in hashtags
    ]

    run_input = {
        "startUrls": start_urls,
        "resultsLimit": max_results,
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False
    }

    run = client.actor(ACTORS["tiktok"]["hashtag"]).call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    return {"platform": "tiktok", "items": items, "run_id": run["id"]}


def scrape_youtube_by_search(keywords: List[str], max_results: int = 50) -> Dict:
    """Scrape YouTube videos by search keywords."""
    print(f"Scraping YouTube for: {keywords}")

    client = ApifyClient(APIFY_TOKEN)

    search_query = " ".join(keywords)

    run_input = {
        "searchKeywords": search_query,
        "maxResults": max_results,
        "downloadSubtitles": False
    }

    run = client.actor(ACTORS["youtube"]["search"]).call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    return {"platform": "youtube", "items": items, "run_id": run["id"]}


def scrape_twitter_by_search(keywords: List[str], max_results: int = 100) -> Dict:
    """Scrape Twitter/X posts by search."""
    print(f"Scraping Twitter for: {keywords}")

    client = ApifyClient(APIFY_TOKEN)

    search_query = " ".join(keywords)

    run_input = {
        "searchTerms": [search_query],
        "maxTweets": max_results,
        "tweetLanguage": "en"
    }

    run = client.actor(ACTORS["twitter"]["search"]).call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    return {"platform": "twitter", "items": items, "run_id": run["id"]}


# ============================================================================
# Result Processing
# ============================================================================

def extract_influencers_from_instagram_posts(posts: List[Dict]) -> Dict[str, Dict]:
    """Extract unique influencers from Instagram posts."""
    influencers = {}

    for post in posts:
        username = post.get("ownerUsername") or post.get("owner", {}).get("username", "")
        if not username:
            continue

        if username not in influencers:
            influencers[username] = {
                "username": username,
                "platform": "instagram",
                "posts": [],
                "total_likes": 0,
                "total_comments": 0,
                "post_count": 0
            }

        likes = post.get("likesCount", 0) or post.get("likes", 0) or 0
        comments = post.get("commentsCount", 0) or post.get("comments", 0) or 0

        influencers[username]["posts"].append({
            "caption": post.get("caption", ""),
            "likes": likes,
            "comments": comments,
            "timestamp": post.get("timestamp", ""),
            "url": post.get("url", "")
        })
        influencers[username]["total_likes"] += likes
        influencers[username]["total_comments"] += comments
        influencers[username]["post_count"] += 1

    return influencers


def extract_influencers_from_tiktok_posts(posts: List[Dict]) -> Dict[str, Dict]:
    """Extract unique influencers from TikTok posts."""
    influencers = {}

    for post in posts:
        author = post.get("authorMeta", {})
        username = author.get("name", "") or post.get("author", "")
        if not username:
            continue

        if username not in influencers:
            influencers[username] = {
                "username": username,
                "platform": "tiktok",
                "followers": author.get("fans", 0),
                "posts": [],
                "total_likes": 0,
                "total_comments": 0,
                "total_views": 0,
                "total_shares": 0,
                "post_count": 0
            }

        likes = post.get("diggCount", 0) or post.get("likes", 0) or 0
        comments = post.get("commentCount", 0) or post.get("comments", 0) or 0
        views = post.get("playCount", 0) or post.get("views", 0) or 0
        shares = post.get("shareCount", 0) or 0

        influencers[username]["posts"].append({
            "caption": post.get("text", ""),
            "likes": likes,
            "comments": comments,
            "views": views,
            "shares": shares,
            "url": post.get("webVideoUrl", "")
        })
        influencers[username]["total_likes"] += likes
        influencers[username]["total_comments"] += comments
        influencers[username]["total_views"] += views
        influencers[username]["total_shares"] += shares
        influencers[username]["post_count"] += 1

        # Update followers if higher (might get updated data)
        if author.get("fans", 0) > influencers[username].get("followers", 0):
            influencers[username]["followers"] = author.get("fans", 0)

    return influencers


def extract_influencers_from_youtube(videos: List[Dict]) -> Dict[str, Dict]:
    """Extract unique channels from YouTube videos."""
    influencers = {}

    for video in videos:
        channel_name = video.get("channelName", "") or video.get("channel", "")
        channel_id = video.get("channelId", "")
        if not channel_name:
            continue

        key = channel_id or channel_name

        if key not in influencers:
            influencers[key] = {
                "username": channel_name,
                "channel_id": channel_id,
                "platform": "youtube",
                "subscribers": video.get("subscriberCount", 0),
                "posts": [],
                "total_views": 0,
                "total_likes": 0,
                "total_comments": 0,
                "post_count": 0
            }

        views = video.get("viewCount", 0) or 0
        likes = video.get("likeCount", 0) or 0
        comments = video.get("commentCount", 0) or 0

        influencers[key]["posts"].append({
            "title": video.get("title", ""),
            "views": views,
            "likes": likes,
            "comments": comments,
            "url": video.get("url", "")
        })
        influencers[key]["total_views"] += views
        influencers[key]["total_likes"] += likes
        influencers[key]["total_comments"] += comments
        influencers[key]["post_count"] += 1

    return influencers


def extract_influencers_from_twitter(tweets: List[Dict]) -> Dict[str, Dict]:
    """Extract unique users from Twitter posts."""
    influencers = {}

    for tweet in tweets:
        user = tweet.get("author", {}) or tweet.get("user", {})
        username = user.get("userName", "") or user.get("screen_name", "")
        if not username:
            continue

        if username not in influencers:
            influencers[username] = {
                "username": username,
                "platform": "twitter",
                "followers": user.get("followers", 0) or user.get("followers_count", 0),
                "display_name": user.get("name", ""),
                "verified": user.get("isBlueVerified", False) or user.get("verified", False),
                "posts": [],
                "total_likes": 0,
                "total_retweets": 0,
                "total_replies": 0,
                "post_count": 0
            }

        likes = tweet.get("likeCount", 0) or tweet.get("favorite_count", 0) or 0
        retweets = tweet.get("retweetCount", 0) or tweet.get("retweet_count", 0) or 0
        replies = tweet.get("replyCount", 0) or 0

        influencers[username]["posts"].append({
            "text": tweet.get("text", ""),
            "likes": likes,
            "retweets": retweets,
            "replies": replies,
            "url": tweet.get("url", "")
        })
        influencers[username]["total_likes"] += likes
        influencers[username]["total_retweets"] += retweets
        influencers[username]["total_replies"] += replies
        influencers[username]["post_count"] += 1

    return influencers


def enrich_influencer_data(
    influencer: Dict,
    profile_data: Optional[Dict] = None,
    target_hashtags: List[str] = None
) -> Dict:
    """
    Enrich influencer data with scores and analysis.

    Args:
        influencer: Basic influencer data
        profile_data: Additional profile data if available
        target_hashtags: Hashtags used for discovery (for relevance scoring)

    Returns:
        dict: Enriched influencer data
    """
    platform = influencer.get("platform", "instagram")
    posts = influencer.get("posts", [])

    # Get follower count
    if profile_data:
        followers = profile_data.get("followersCount", 0) or profile_data.get("followers", 0)
        bio = profile_data.get("biography", "") or profile_data.get("bio", "")
        website = profile_data.get("externalUrl", "") or profile_data.get("website", "")
        full_name = profile_data.get("fullName", "") or profile_data.get("name", "")
        verified = profile_data.get("verified", False) or profile_data.get("isVerified", False)
        profile_pic = profile_data.get("profilePicUrl", "") or profile_data.get("avatar", "")
    else:
        followers = influencer.get("followers", 0)
        bio = ""
        website = ""
        full_name = ""
        verified = influencer.get("verified", False)
        profile_pic = ""

    # Calculate engagement metrics
    total_likes = influencer.get("total_likes", 0)
    total_comments = influencer.get("total_comments", 0)
    total_views = influencer.get("total_views", 0)
    total_shares = influencer.get("total_shares", 0) or influencer.get("total_retweets", 0)
    post_count = influencer.get("post_count", 1)

    avg_likes = total_likes / max(post_count, 1)
    avg_comments = total_comments / max(post_count, 1)

    # Engagement rate
    engagement_rate = calculate_engagement_rate(
        int(avg_likes), int(avg_comments), followers,
        views=total_views // max(post_count, 1),
        shares=total_shares // max(post_count, 1)
    )

    # Tier classification
    tier = classify_tier(followers)

    # Authenticity score
    authenticity = calculate_authenticity_score(engagement_rate, followers)

    # Extract hashtags and categories
    hashtags = extract_hashtags_from_content(posts)
    categories = categorize_content(posts, hashtags)

    # Content relevance (if target hashtags provided)
    if target_hashtags:
        matching = sum(1 for h, _ in hashtags if any(t.lower() in h for t in target_hashtags))
        relevance = min(100, (matching / len(target_hashtags)) * 100) if target_hashtags else 50
    else:
        relevance = 50  # Default

    # Posting frequency (estimate from sample)
    posting_frequency = min(7, post_count / 2)  # Rough estimate

    # Brand safety
    captions = [p.get("caption", "") or p.get("text", "") or p.get("title", "") for p in posts]
    brand_safety = analyze_brand_safety(captions)

    # Contact extraction
    contact = extract_contact_info(bio, website)

    # Overall influencer score
    influencer_score = calculate_influencer_score(
        engagement_rate,
        authenticity,
        relevance,
        posting_frequency
    )

    # Estimated rates
    post_rate = ESTIMATED_POST_RATES.get(tier, ESTIMATED_POST_RATES["micro"])
    cpm = estimate_cpm(tier, platform)

    # Build enriched profile
    enriched = {
        "username": f"@{influencer['username']}",
        "platform": platform,
        "full_name": full_name,
        "followers": followers,
        "engagement_rate": engagement_rate,
        "influencer_score": influencer_score,
        "tier": tier,
        "tier_label": INFLUENCER_TIERS[tier]["label"],
        "authenticity_score": authenticity,
        "verified": verified,
        "estimated_post_rate": post_rate["display"],
        "cpm_estimate": cpm["display"],
        "contact": contact,
        "top_hashtags": [h[0] for h in hashtags[:10]],
        "content_categories": categories,
        "brand_safety": brand_safety["status"],
        "brand_safety_detail": brand_safety,
        "profile_url": _build_profile_url(influencer["username"], platform),
        "profile_pic": profile_pic,
        "bio": bio[:200] if bio else "",
        "sample_posts_analyzed": post_count,
        "avg_likes": int(avg_likes),
        "avg_comments": int(avg_comments)
    }

    if platform in ["tiktok", "youtube"]:
        enriched["avg_views"] = total_views // max(post_count, 1)

    return enriched


def _build_profile_url(username: str, platform: str) -> str:
    """Build profile URL for a given platform."""
    username = username.lstrip('@')
    urls = {
        "instagram": f"https://www.instagram.com/{username}/",
        "tiktok": f"https://www.tiktok.com/@{username}",
        "youtube": f"https://www.youtube.com/@{username}",
        "twitter": f"https://twitter.com/{username}"
    }
    return urls.get(platform, "")


def filter_by_tier(influencers: List[Dict], tiers: List[str]) -> List[Dict]:
    """Filter influencers by tier."""
    if not tiers:
        return influencers
    return [i for i in influencers if i.get("tier") in tiers]


def filter_by_engagement(influencers: List[Dict], min_rate: float) -> List[Dict]:
    """Filter influencers by minimum engagement rate."""
    return [i for i in influencers if i.get("engagement_rate", 0) >= min_rate]


def filter_by_followers(influencers: List[Dict], min_followers: int, max_followers: int = None) -> List[Dict]:
    """Filter influencers by follower count."""
    filtered = [i for i in influencers if i.get("followers", 0) >= min_followers]
    if max_followers:
        filtered = [i for i in filtered if i.get("followers", 0) <= max_followers]
    return filtered


def calculate_tier_distribution(influencers: List[Dict]) -> Dict[str, int]:
    """Calculate distribution of influencers by tier."""
    distribution = {tier: 0 for tier in INFLUENCER_TIERS}
    for inf in influencers:
        tier = inf.get("tier", "unknown")
        if tier in distribution:
            distribution[tier] += 1
    return distribution


def calculate_platform_breakdown(influencers: List[Dict]) -> Dict[str, int]:
    """Calculate distribution of influencers by platform."""
    breakdown = {}
    for inf in influencers:
        platform = inf.get("platform", "unknown")
        breakdown[platform] = breakdown.get(platform, 0) + 1
    return breakdown


# ============================================================================
# Main Discovery Function
# ============================================================================

def discover_influencers(
    hashtags: List[str] = None,
    keywords: List[str] = None,
    topic: str = None,
    platforms: List[str] = None,
    tiers: List[str] = None,
    min_engagement: float = 0,
    min_followers: int = 1000,
    max_followers: int = None,
    max_results: int = 100,
    extract_contacts: bool = False,
    fetch_profiles: bool = False
) -> Dict:
    """
    Main discovery function that orchestrates the entire process.

    Args:
        hashtags: List of hashtags to search
        keywords: List of keywords to search
        topic: Topic string (converted to hashtags/keywords)
        platforms: List of platforms to search
        tiers: List of tiers to filter
        min_engagement: Minimum engagement rate
        min_followers: Minimum follower count
        max_followers: Maximum follower count
        max_results: Max results per platform
        extract_contacts: Whether to extract contact info
        fetch_profiles: Whether to fetch full profile data

    Returns:
        dict: Complete discovery results
    """
    # Default platforms
    if not platforms:
        platforms = ["instagram"]

    # Convert topic to hashtags if provided
    if topic and not hashtags:
        hashtags = topic.lower().replace(",", " ").split()

    if not hashtags and not keywords:
        raise ValueError("Must provide hashtags, keywords, or topic")

    search_terms = hashtags or keywords or []

    print(f"Starting influencer discovery...")
    print(f"Platforms: {platforms}")
    print(f"Search terms: {search_terms}")
    print(f"Max results per platform: {max_results}")

    all_influencers = []
    platform_raw_data = {}

    # Scrape each platform
    for platform in platforms:
        print(f"\nProcessing {platform}...")

        try:
            if platform == "instagram":
                raw = scrape_instagram_by_hashtag(search_terms, max_results)
                influencer_map = extract_influencers_from_instagram_posts(raw["items"])

            elif platform == "tiktok":
                raw = scrape_tiktok_by_hashtag(search_terms, max_results)
                influencer_map = extract_influencers_from_tiktok_posts(raw["items"])

            elif platform == "youtube":
                raw = scrape_youtube_by_search(search_terms, max_results)
                influencer_map = extract_influencers_from_youtube(raw["items"])

            elif platform == "twitter":
                raw = scrape_twitter_by_search(search_terms, max_results)
                influencer_map = extract_influencers_from_twitter(raw["items"])

            else:
                print(f"Unknown platform: {platform}, skipping")
                continue

            platform_raw_data[platform] = raw

            # Enrich each influencer
            print(f"Found {len(influencer_map)} unique creators on {platform}")

            for username, data in influencer_map.items():
                try:
                    enriched = enrich_influencer_data(data, target_hashtags=search_terms)
                    all_influencers.append(enriched)
                except Exception as e:
                    print(f"Error enriching {username}: {e}")
                    continue

        except Exception as e:
            print(f"Error scraping {platform}: {e}")
            continue

    # Fetch profile details if requested (for Instagram)
    if fetch_profiles and "instagram" in platforms:
        print("\nFetching detailed profile data...")
        ig_usernames = [
            i["username"].lstrip("@")
            for i in all_influencers
            if i["platform"] == "instagram"
        ][:50]  # Limit to 50 profiles

        if ig_usernames:
            try:
                profiles = scrape_instagram_profiles(ig_usernames)
                profile_map = {p["username"]: p for p in profiles.get("items", [])}

                # Re-enrich with profile data
                for i, inf in enumerate(all_influencers):
                    if inf["platform"] == "instagram":
                        username = inf["username"].lstrip("@")
                        if username in profile_map:
                            original_data = {
                                "username": username,
                                "platform": "instagram",
                                "posts": [],  # Would need to re-fetch
                                "total_likes": inf["avg_likes"] * inf["sample_posts_analyzed"],
                                "total_comments": inf["avg_comments"] * inf["sample_posts_analyzed"],
                                "post_count": inf["sample_posts_analyzed"]
                            }
                            enriched = enrich_influencer_data(
                                original_data,
                                profile_map[username],
                                target_hashtags=search_terms
                            )
                            all_influencers[i] = enriched
            except Exception as e:
                print(f"Error fetching profiles: {e}")

    # Apply filters
    print(f"\nTotal influencers found: {len(all_influencers)}")

    # Filter by followers
    all_influencers = filter_by_followers(all_influencers, min_followers, max_followers)
    print(f"After follower filter ({min_followers}+): {len(all_influencers)}")

    # Filter by tier
    if tiers:
        all_influencers = filter_by_tier(all_influencers, tiers)
        print(f"After tier filter ({tiers}): {len(all_influencers)}")

    # Filter by engagement
    if min_engagement > 0:
        all_influencers = filter_by_engagement(all_influencers, min_engagement)
        print(f"After engagement filter ({min_engagement}%+): {len(all_influencers)}")

    # Sort by influencer score
    all_influencers.sort(key=lambda x: x.get("influencer_score", 0), reverse=True)

    # Build response
    result = {
        "query": {
            "hashtags": hashtags,
            "keywords": keywords,
            "topic": topic,
            "platforms": platforms,
            "tiers": tiers,
            "min_engagement": min_engagement,
            "min_followers": min_followers,
            "max_followers": max_followers
        },
        "discovered_at": datetime.now().isoformat(),
        "total_found": len(all_influencers),
        "influencers": all_influencers,
        "tier_distribution": calculate_tier_distribution(all_influencers),
        "platform_breakdown": calculate_platform_breakdown(all_influencers),
        "scoring_weights": SCORING_WEIGHTS
    }

    return result


def save_results(data: Dict, filename: str = None, format: str = "json") -> Path:
    """
    Save results to file.

    Args:
        data: Discovery results
        filename: Output filename
        format: Output format (json or csv)

    Returns:
        Path: Output file path
    """
    OUTPUT_DIR.mkdir(exist_ok=True)

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = "csv" if format == "csv" else "json"
        filename = f"influencers_{timestamp}.{extension}"

    output_path = OUTPUT_DIR / filename

    if format == "csv":
        # Flatten influencer data for CSV
        rows = []
        for inf in data.get("influencers", []):
            row = {
                "username": inf.get("username", ""),
                "platform": inf.get("platform", ""),
                "full_name": inf.get("full_name", ""),
                "followers": inf.get("followers", 0),
                "engagement_rate": inf.get("engagement_rate", 0),
                "influencer_score": inf.get("influencer_score", 0),
                "tier": inf.get("tier", ""),
                "authenticity_score": inf.get("authenticity_score", 0),
                "verified": inf.get("verified", False),
                "estimated_post_rate": inf.get("estimated_post_rate", ""),
                "email": inf.get("contact", {}).get("email", ""),
                "website": inf.get("contact", {}).get("website", ""),
                "categories": ", ".join(inf.get("content_categories", [])),
                "top_hashtags": ", ".join(inf.get("top_hashtags", [])[:5]),
                "brand_safety": inf.get("brand_safety", ""),
                "profile_url": inf.get("profile_url", ""),
                "bio": inf.get("bio", "").replace("\n", " ")[:100]
            }
            rows.append(row)

        if rows:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
    else:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_path}")
    return output_path


def print_summary(data: Dict):
    """Print discovery summary to console."""
    print("\n" + "="*60)
    print("INFLUENCER DISCOVERY SUMMARY")
    print("="*60)

    print(f"\nTotal influencers found: {data['total_found']}")

    print("\nTier Distribution:")
    for tier, count in data.get("tier_distribution", {}).items():
        if count > 0:
            label = INFLUENCER_TIERS.get(tier, {}).get("label", tier)
            print(f"  {label}: {count}")

    print("\nPlatform Breakdown:")
    for platform, count in data.get("platform_breakdown", {}).items():
        print(f"  {platform.capitalize()}: {count}")

    print("\nTop 10 Influencers by Score:")
    for i, inf in enumerate(data.get("influencers", [])[:10], 1):
        print(f"\n  {i}. {inf['username']} ({inf['platform']})")
        print(f"     Followers: {inf['followers']:,} | Engagement: {inf['engagement_rate']}%")
        print(f"     Score: {inf['influencer_score']} | Tier: {inf['tier_label']}")
        print(f"     Authenticity: {inf['authenticity_score']}% | Safety: {inf['brand_safety']}")
        if inf.get("contact", {}).get("email"):
            print(f"     Email: {inf['contact']['email']}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Discover and analyze influencers across social platforms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Discover fitness influencers on Instagram
  python discover_influencers.py --hashtags fitness health --platform instagram --tier micro

  # Multi-platform discovery
  python discover_influencers.py --topic "sustainable fashion" --platforms instagram tiktok youtube

  # Filter by engagement
  python discover_influencers.py --hashtags tech AI --min-engagement 3.0 --min-followers 10000

  # Export to CSV for outreach
  python discover_influencers.py --topic "AI" --tier micro mid --format csv --output outreach.csv

  # With profile fetching for more data
  python discover_influencers.py --hashtags beauty --platform instagram --fetch-profiles
        """
    )

    # Discovery inputs
    parser.add_argument("--hashtags", nargs="+", help="Hashtags to search (without #)")
    parser.add_argument("--keywords", nargs="+", help="Keywords to search")
    parser.add_argument("--topic", help="Topic to discover influencers for")
    parser.add_argument("--competitor", help="Competitor account to analyze")

    # Platform options
    parser.add_argument(
        "--platform", "--platforms",
        nargs="+",
        dest="platforms",
        choices=["instagram", "tiktok", "youtube", "twitter"],
        default=["instagram"],
        help="Platforms to search (default: instagram)"
    )

    # Filtering options
    parser.add_argument(
        "--tier",
        nargs="+",
        choices=["nano", "micro", "mid", "macro", "mega"],
        help="Filter by influencer tier"
    )
    parser.add_argument(
        "--min-engagement",
        type=float,
        default=0,
        help="Minimum engagement rate percentage"
    )
    parser.add_argument(
        "--min-followers",
        type=int,
        default=1000,
        help="Minimum follower count (default: 1000)"
    )
    parser.add_argument(
        "--max-followers",
        type=int,
        help="Maximum follower count"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=100,
        help="Maximum results per platform (default: 100)"
    )

    # Enrichment options
    parser.add_argument(
        "--extract-contacts",
        action="store_true",
        help="Extract contact information from bios"
    )
    parser.add_argument(
        "--fetch-profiles",
        action="store_true",
        help="Fetch detailed profile data (slower, more accurate)"
    )
    parser.add_argument(
        "--find-influencers",
        action="store_true",
        help="Find influencers from competitor followers"
    )
    parser.add_argument("--location", help="Filter by location (when available)")

    # Output options
    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--output",
        help="Output filename"
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.hashtags and not args.keywords and not args.topic and not args.competitor:
        print("Error: Must provide --hashtags, --keywords, --topic, or --competitor")
        parser.print_help()
        return 1

    try:
        # Validate environment
        validate_environment()

        # Run discovery
        results = discover_influencers(
            hashtags=args.hashtags,
            keywords=args.keywords,
            topic=args.topic,
            platforms=args.platforms,
            tiers=args.tier,
            min_engagement=args.min_engagement,
            min_followers=args.min_followers,
            max_followers=args.max_followers,
            max_results=args.max_results,
            extract_contacts=args.extract_contacts,
            fetch_profiles=args.fetch_profiles
        )

        # Print summary
        print_summary(results)

        # Save results
        save_results(results, args.output, args.format)

        print("\nInfluencer discovery completed successfully!")
        return 0

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
