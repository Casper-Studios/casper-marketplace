#!/usr/bin/env python3
"""
Scrape Content by URL
Scrapes content from individual URLs (Twitter, YouTube, Reddit, websites).
Uses Apify for Twitter/YouTube/Reddit, and Firecrawl for websites.

Usage:
    python execution/scrape_content_by_url.py "https://x.com/elonmusk/status/123456"
    python execution/scrape_content_by_url.py "https://youtube.com/watch?v=abc123"
    python execution/scrape_content_by_url.py "https://reddit.com/r/MachineLearning/comments/..."
    python execution/scrape_content_by_url.py "https://example.com/article" --type website
    python execution/scrape_content_by_url.py "https://wsj.com/article" --proxy stealth
"""

import os
import re
import json
import time
from datetime import datetime
from pathlib import Path
from apify_client import ApifyClient
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

# Configuration
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
OUTPUT_DIR = Path(__file__).parent.parent / ".tmp"

# Actor IDs (Apify)
ACTORS = {
    "twitter": "kaitoeasyapi/twitter-x-data-tweet-scraper-pay-per-result-cheapest",
    "youtube": "streamers/youtube-scraper",
    "reddit": "trudax/reddit-scraper-lite"
}


def validate_environment(url_type=None):
    """Validate required environment variables based on URL type."""
    if url_type in ["twitter", "youtube", "reddit"]:
        if not APIFY_TOKEN:
            raise ValueError(
                "APIFY_TOKEN not found in environment. "
                "Please add it to your .env file."
            )
    elif url_type == "website":
        if not FIRECRAWL_API_KEY:
            raise ValueError(
                "FIRECRAWL_API_KEY not found in environment. "
                "Please add it to your .env file."
            )
    else:
        # Check both for auto-detection
        if not APIFY_TOKEN and not FIRECRAWL_API_KEY:
            raise ValueError(
                "Neither APIFY_TOKEN nor FIRECRAWL_API_KEY found. "
                "Please add at least one to your .env file."
            )


def detect_url_type(url):
    """
    Detect the type of URL.

    Args:
        url: URL string

    Returns:
        str: One of 'twitter', 'youtube', 'reddit', 'website'
    """
    url_lower = url.lower()

    if "twitter.com" in url_lower or "x.com" in url_lower:
        return "twitter"
    elif "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "youtube"
    elif "reddit.com" in url_lower:
        return "reddit"
    else:
        return "website"


def extract_tweet_id(url):
    """
    Extract tweet ID from Twitter/X URL.

    Args:
        url: Twitter URL like https://x.com/user/status/1234567890

    Returns:
        str: Tweet ID or None
    """
    # Pattern: twitter.com/*/status/{id} or x.com/*/status/{id}
    pattern = r'(?:twitter\.com|x\.com)/\w+/status/(\d+)'
    match = re.search(pattern, url)
    return match.group(1) if match else None


def extract_youtube_id(url):
    """
    Extract video ID from YouTube URL.

    Args:
        url: YouTube URL

    Returns:
        str: Video ID or None
    """
    # Pattern 1: youtube.com/watch?v=VIDEO_ID
    pattern1 = r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)'
    match = re.search(pattern1, url)
    if match:
        return match.group(1)

    # Pattern 2: youtu.be/VIDEO_ID
    pattern2 = r'youtu\.be/([a-zA-Z0-9_-]+)'
    match = re.search(pattern2, url)
    if match:
        return match.group(1)

    return None


def scrape_twitter(url):
    """
    Scrape a single tweet by URL.

    Args:
        url: Twitter/X URL

    Returns:
        dict: Scraped tweet data
    """
    tweet_id = extract_tweet_id(url)
    if not tweet_id:
        return {"error": f"Could not extract tweet ID from URL: {url}"}

    print(f"   Scraping tweet ID: {tweet_id}")

    client = ApifyClient(APIFY_TOKEN)

    run_input = {
        "tweetIDs": [tweet_id]
    }

    try:
        run = client.actor(ACTORS["twitter"]).call(run_input=run_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        if not items:
            return {"error": "No tweet data returned"}

        tweet = items[0]
        return {
            "id": tweet.get("id", tweet_id),
            "text": tweet.get("text", ""),
            "author": tweet.get("author", {}).get("userName", ""),
            "author_name": tweet.get("author", {}).get("name", ""),
            "created_at": tweet.get("createdAt", ""),
            "likes": tweet.get("likeCount", 0),
            "retweets": tweet.get("retweetCount", 0),
            "replies": tweet.get("replyCount", 0),
            "views": tweet.get("viewCount", 0),
            "url": url
        }

    except Exception as e:
        return {"error": str(e)}


def scrape_youtube(url):
    """
    Scrape a single YouTube video by URL.

    Args:
        url: YouTube URL

    Returns:
        dict: Scraped video data
    """
    video_id = extract_youtube_id(url)
    if not video_id:
        return {"error": f"Could not extract video ID from URL: {url}"}

    print(f"   Scraping YouTube video ID: {video_id}")

    # Normalize URL
    normalized_url = f"https://www.youtube.com/watch?v={video_id}"

    client = ApifyClient(APIFY_TOKEN)

    run_input = {
        "startUrls": [{"url": normalized_url}],
        "maxResults": 1,
        "downloadSubtitles": True,
        "subtitlesLanguage": "en"
    }

    try:
        run = client.actor(ACTORS["youtube"]).call(run_input=run_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        if not items:
            return {"error": "No video data returned"}

        video = items[0]
        return {
            "id": video.get("id", video_id),
            "title": video.get("title", ""),
            "description": video.get("description", ""),
            "channel": video.get("channelName", ""),
            "channel_url": video.get("channelUrl", ""),
            "published_at": video.get("date", ""),
            "views": video.get("viewCount", 0),
            "likes": video.get("likes", 0),
            "comments": video.get("commentsCount", 0),
            "duration": video.get("duration", ""),
            "subtitles": video.get("subtitles", ""),
            "url": normalized_url
        }

    except Exception as e:
        return {"error": str(e)}


def scrape_reddit(url):
    """
    Scrape a single Reddit post by URL.

    Args:
        url: Reddit URL

    Returns:
        dict: Scraped post data
    """
    print(f"   Scraping Reddit post: {url}")

    client = ApifyClient(APIFY_TOKEN)

    run_input = {
        "startUrls": [{"url": url}],
        "maxItems": 1,
        "maxComments": 10
    }

    try:
        run = client.actor(ACTORS["reddit"]).call(run_input=run_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        if not items:
            return {"error": "No Reddit data returned"}

        post = items[0]
        return {
            "id": post.get("id", ""),
            "title": post.get("title", ""),
            "body": post.get("body", post.get("selftext", "")),
            "author": post.get("author", ""),
            "subreddit": post.get("subreddit", ""),
            "score": post.get("score", 0),
            "upvote_ratio": post.get("upvoteRatio", 0),
            "comments_count": post.get("numberOfComments", 0),
            "created_at": post.get("createdAt", ""),
            "url": url
        }

    except Exception as e:
        return {"error": str(e)}


def scrape_website(url, proxy="auto", timeout=30000, retry_with_stealth=True):
    """
    Scrape a single webpage by URL using Firecrawl.

    Args:
        url: Website URL
        proxy: Proxy mode (basic, stealth, auto)
        timeout: Timeout in milliseconds
        retry_with_stealth: If True, retry with stealth proxy on failure

    Returns:
        dict: Scraped page data
    """
    print(f"   Scraping website: {url}")
    print(f"   Using Firecrawl (proxy={proxy})")

    if not FIRECRAWL_API_KEY:
        return {"error": "FIRECRAWL_API_KEY not set"}

    # Try SDK first, fall back to requests
    try:
        from firecrawl import Firecrawl
        use_sdk = True
    except ImportError:
        use_sdk = False

    try:
        if use_sdk:
            client = Firecrawl(api_key=FIRECRAWL_API_KEY)
            response = client.scrape(
                url,
                formats=["markdown"],
                only_main_content=True,
                timeout=timeout,
                proxy=proxy
            )
            # SDK returns a Document object, not a dict
            # Convert to dict-like access
            if hasattr(response, 'markdown'):
                # It's a Document object
                data = {
                    "markdown": response.markdown or "",
                    "metadata": {
                        "title": getattr(response, 'title', '') or (response.metadata.title if hasattr(response, 'metadata') and hasattr(response.metadata, 'title') else ''),
                        "description": getattr(response, 'description', '') or (response.metadata.description if hasattr(response, 'metadata') and hasattr(response.metadata, 'description') else ''),
                        "language": response.metadata.language if hasattr(response, 'metadata') and hasattr(response.metadata, 'language') else '',
                        "sourceURL": response.metadata.sourceURL if hasattr(response, 'metadata') and hasattr(response.metadata, 'sourceURL') else url,
                    }
                }
            elif isinstance(response, dict):
                data = response
            else:
                data = {}
        else:
            # Use requests directly
            import requests
            api_url = "https://api.firecrawl.dev/v2/scrape"
            response = requests.post(
                api_url,
                headers={
                    "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "url": url,
                    "formats": ["markdown"],
                    "onlyMainContent": True,
                    "timeout": timeout,
                    "proxy": proxy
                },
                timeout=timeout / 1000 + 30
            )

            if response.status_code != 200:
                error_msg = response.text
                try:
                    error_json = response.json()
                    error_msg = error_json.get("error", error_msg)
                except:
                    pass
                return {"error": f"Firecrawl error ({response.status_code}): {error_msg}"}

            result = response.json()
            if not result.get("success"):
                return {"error": result.get("error", "Unknown error")}

            data = result.get("data", {})

        # Extract metadata
        metadata = data.get("metadata", {})

        result = {
            "title": metadata.get("title", ""),
            "text": data.get("markdown", ""),
            "url": metadata.get("sourceURL", url),
            "description": metadata.get("description", ""),
            "language": metadata.get("language", ""),
            "metadata": metadata
        }

        # Check if we got empty content and should retry with stealth
        if not result.get("text") and retry_with_stealth and proxy != "stealth":
            print(f"   ⚠️  Empty content, retrying with stealth proxy...")
            return scrape_website(url, proxy="stealth", timeout=timeout, retry_with_stealth=False)

        return result

    except Exception as e:
        # Retry with stealth on error if not already using it
        if retry_with_stealth and proxy != "stealth":
            print(f"   ⚠️  Error with {proxy} proxy, retrying with stealth...")
            return scrape_website(url, proxy="stealth", timeout=timeout, retry_with_stealth=False)
        return {"error": str(e)}


def clean_url(url):
    """
    Clean URL by removing common trailing characters from Slack formatting.

    Args:
        url: Raw URL string

    Returns:
        str: Cleaned URL
    """
    if not url:
        return url

    # Remove trailing > (common in Slack message links)
    url = url.rstrip('>')

    # Remove trailing | and anything after (Slack link text)
    if '|' in url:
        url = url.split('|')[0]

    # Remove trailing punctuation that's not part of URL
    url = url.rstrip('.,;:!?')

    return url.strip()


def scrape_url(url, url_type=None, proxy="auto", timeout=30000):
    """
    Scrape content from a URL.

    Args:
        url: URL to scrape
        url_type: Optional type override ('twitter', 'youtube', 'reddit', 'website')
        proxy: Proxy mode for websites (basic, stealth, auto)
        timeout: Timeout in milliseconds for websites

    Returns:
        dict: Scraped content with metadata
    """
    # Clean URL first (remove Slack formatting artifacts)
    url = clean_url(url)

    # Detect type if not provided
    if not url_type:
        url_type = detect_url_type(url)

    print(f"   Detected type: {url_type}")

    # Scrape based on type
    if url_type == "twitter":
        content = scrape_twitter(url)
    elif url_type == "youtube":
        content = scrape_youtube(url)
    elif url_type == "reddit":
        content = scrape_reddit(url)
    else:
        content = scrape_website(url, proxy=proxy, timeout=timeout)

    return {
        "url": url,
        "type": url_type,
        "scraped_at": datetime.now().isoformat(),
        "content": content
    }


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Scrape content from individual URLs"
    )
    parser.add_argument(
        "url",
        help="URL to scrape"
    )
    parser.add_argument(
        "--type",
        choices=["twitter", "youtube", "reddit", "website"],
        help="Force URL type (auto-detected if not provided)"
    )
    parser.add_argument(
        "--proxy",
        choices=["basic", "stealth", "auto"],
        default="auto",
        help="Proxy mode for websites (default: auto, use stealth for premium content)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30000,
        help="Timeout in milliseconds for websites (default: 30000)"
    )
    parser.add_argument(
        "--output",
        help="Custom output filename"
    )

    args = parser.parse_args()

    # Detect type first for environment validation
    url_type = args.type if args.type else detect_url_type(args.url)

    try:
        # Validate environment based on URL type
        validate_environment(url_type)

        print(f"🔗 Scraping URL: {args.url}")

        # Scrape URL
        result = scrape_url(args.url, args.type, proxy=args.proxy, timeout=args.timeout)

        if "error" in result.get("content", {}):
            print(f"❌ Error: {result['content']['error']}")
            return 1

        # Save results
        OUTPUT_DIR.mkdir(exist_ok=True)

        if args.output:
            filename = args.output
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraped_{result['type']}_{timestamp}.json"

        output_path = OUTPUT_DIR / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Saved to: {output_path}")
        print(f"📋 Type: {result['type']}")

        # Print preview
        content = result['content']
        if result['type'] == 'twitter':
            print(f"\n🐦 Tweet by @{content.get('author', 'unknown')}:")
            print(f"   {content.get('text', '')[:200]}...")
            print(f"   ❤️  {content.get('likes', 0)} | 🔄 {content.get('retweets', 0)}")
        elif result['type'] == 'youtube':
            print(f"\n📹 Video: {content.get('title', 'unknown')[:60]}...")
            print(f"   📺 {content.get('channel', 'unknown')}")
            print(f"   👁️  {content.get('views', 0)} views")
            if content.get('subtitles'):
                print(f"   📝 Subtitles: {len(content['subtitles'])} chars")
        elif result['type'] == 'reddit':
            print(f"\n📱 Reddit: {content.get('title', 'unknown')[:60]}...")
            print(f"   r/{content.get('subreddit', 'unknown')} by u/{content.get('author', 'unknown')}")
            print(f"   ⬆️  {content.get('score', 0)} | 💬 {content.get('comments_count', 0)}")
        else:
            print(f"\n🌐 Website: {content.get('title', 'unknown')[:60]}...")
            print(f"   📄 {len(content.get('text', ''))} chars of content")

        print("\n✅ Scraping completed!")
        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
