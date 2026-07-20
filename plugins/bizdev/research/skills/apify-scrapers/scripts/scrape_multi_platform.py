#!/usr/bin/env python3
"""
Multi-Platform Content Scraper
Unified script to scrape TikTok, YouTube, and Website content using Apify actors.

Usage:
    python execution/scrape_multi_platform.py tiktok --hashtags AI ChatGPT --max-results 20
    python execution/scrape_multi_platform.py youtube --search "AI tutorial" --max-results 30
    python execution/scrape_multi_platform.py website --urls https://docs.example.com --max-pages 50
"""

import os
import json
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

# Actor IDs
ACTORS = {
    "tiktok": "clockworks/tiktok-scraper",
    "youtube": "streamers/youtube-scraper",
    "website": "apify/website-content-crawler"
}

def validate_environment():
    """Validate required environment variables."""
    if not APIFY_TOKEN:
        raise ValueError(
            "APIFY_TOKEN not found in environment. "
            "Please add it to your .env file."
        )

def scrape_tiktok(hashtags=None, max_results=50, download_videos=False):
    """Scrape TikTok content."""
    client = ApifyClient(APIFY_TOKEN)

    # Build start URLs from hashtags
    if hashtags:
        start_urls = [f"https://www.tiktok.com/tag/{tag.replace('#', '')}" for tag in hashtags]
    else:
        start_urls = [
            "https://www.tiktok.com/tag/ai",
            "https://www.tiktok.com/tag/chatgpt",
            "https://www.tiktok.com/tag/machinelearning"
        ]

    run_input = {
        "startUrls": start_urls,
        "resultsLimit": max_results,
        "shouldDownloadVideos": download_videos,
        "shouldDownloadCovers": True,
        "shouldDownloadSubtitles": True
    }

    print(f"🎵 Starting TikTok scraper for hashtags: {', '.join([url.split('/')[-1] for url in start_urls])}")
    print(f"📊 Max results: {max_results}")

    run = client.actor(ACTORS["tiktok"]).call(run_input=run_input)
    dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    return {"videos": dataset_items, "scraped_at": datetime.now().isoformat()}

def scrape_youtube(search_query=None, max_results=50, download_subtitles=True):
    """Scrape YouTube content."""
    client = ApifyClient(APIFY_TOKEN)

    run_input = {
        "maxResults": max_results,
        "downloadSubtitles": download_subtitles,
        "subtitlesLanguage": "en"
    }

    if search_query:
        run_input["searchKeywords"] = search_query
        print(f"📹 Starting YouTube scraper for query: '{search_query}'")
    else:
        run_input["searchKeywords"] = "AI tutorial"
        print(f"📹 Starting YouTube scraper with default query: 'AI tutorial'")

    print(f"📊 Max results: {max_results}")

    run = client.actor(ACTORS["youtube"]).call(run_input=run_input)
    dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    return {"videos": dataset_items, "scraped_at": datetime.now().isoformat()}

def scrape_website(urls, max_pages=100, output_format="markdown"):
    """Scrape website content for RAG/LLM."""
    client = ApifyClient(APIFY_TOKEN)

    if isinstance(urls, str):
        urls = [urls]

    start_urls = [{"url": url} for url in urls]

    run_input = {
        "startUrls": start_urls,
        "maxCrawlPages": max_pages,
        "crawlerType": "cheerio",  # Fast, no JS rendering
    }

    print(f"🌐 Starting Website Content Crawler")
    print(f"📋 URLs: {', '.join(urls)}")
    print(f"📊 Max pages: {max_pages}")

    run = client.actor(ACTORS["website"]).call(run_input=run_input)
    dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    return {"pages": dataset_items, "scraped_at": datetime.now().isoformat()}

def save_results(data, platform, filename=None):
    """Save results to .tmp directory."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{platform}_content_{timestamp}.json"

    output_path = OUTPUT_DIR / filename

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Results saved to: {output_path}")

    # Print summary stats
    if platform == "tiktok":
        print(f"📊 Total videos: {len(data.get('videos', []))}")
        for i, video in enumerate(data.get('videos', [])[:3], 1):
            print(f"\n{i}. {video.get('text', 'No caption')[:50]}...")
            print(f"   👤 @{video.get('authorMeta', {}).get('name', 'unknown')}")
            print(f"   ❤️  {video.get('diggCount', 0)} | 💬 {video.get('commentCount', 0)}")

    elif platform == "youtube":
        print(f"📊 Total videos: {len(data.get('videos', []))}")
        for i, video in enumerate(data.get('videos', [])[:3], 1):
            print(f"\n{i}. {video.get('title', 'No title')[:60]}...")
            print(f"   📺 {video.get('channelName', 'unknown')}")
            print(f"   👁️  {video.get('viewCount', 0)} views")

    elif platform == "website":
        print(f"📊 Total pages: {len(data.get('pages', []))}")
        for i, page in enumerate(data.get('pages', [])[:3], 1):
            print(f"\n{i}. {page.get('title', 'No title')[:60]}...")
            print(f"   🔗 {page.get('url', 'unknown')}")

    return output_path

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Multi-platform content scraper (TikTok, YouTube, Website)"
    )

    subparsers = parser.add_subparsers(dest="platform", help="Platform to scrape")

    # TikTok subcommand
    tiktok_parser = subparsers.add_parser("tiktok", help="Scrape TikTok content")
    tiktok_parser.add_argument("--hashtags", nargs="+", help="Hashtags to scrape")
    tiktok_parser.add_argument("--max-results", type=int, default=50)
    tiktok_parser.add_argument("--download-videos", action="store_true")
    tiktok_parser.add_argument("--output", help="Custom output filename")

    # YouTube subcommand
    youtube_parser = subparsers.add_parser("youtube", help="Scrape YouTube content")
    youtube_parser.add_argument("--search", help="Search query")
    youtube_parser.add_argument("--max-results", type=int, default=50)
    youtube_parser.add_argument("--no-subtitles", action="store_true")
    youtube_parser.add_argument("--output", help="Custom output filename")

    # Website subcommand
    website_parser = subparsers.add_parser("website", help="Crawl website content")
    website_parser.add_argument("--urls", nargs="+", required=True, help="URLs to crawl")
    website_parser.add_argument("--max-pages", type=int, default=100)
    website_parser.add_argument("--output", help="Custom output filename")

    args = parser.parse_args()

    if not args.platform:
        parser.print_help()
        return 1

    try:
        # Validate environment
        validate_environment()

        # Run appropriate scraper
        if args.platform == "tiktok":
            results = scrape_tiktok(
                hashtags=args.hashtags,
                max_results=args.max_results,
                download_videos=args.download_videos
            )
        elif args.platform == "youtube":
            results = scrape_youtube(
                search_query=args.search,
                max_results=args.max_results,
                download_subtitles=not args.no_subtitles
            )
        elif args.platform == "website":
            results = scrape_website(
                urls=args.urls,
                max_pages=args.max_pages
            )

        # Save results
        save_results(results, args.platform, getattr(args, 'output', None))

        print("\n✅ Scraping completed successfully!")
        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
