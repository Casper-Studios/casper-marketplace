#!/usr/bin/env python3
"""
LinkedIn Post Scraper
Scrapes LinkedIn posts by author URL or search query using Apify.

Usage:
    # Scrape posts from a specific profile
    python execution/scrape_linkedin_posts.py author "https://www.linkedin.com/in/example-user/"

    # Scrape posts from multiple profiles
    python execution/scrape_linkedin_posts.py author "https://www.linkedin.com/in/user1/" "https://www.linkedin.com/in/user2/"

    # Search for posts by keyword
    python execution/scrape_linkedin_posts.py search "AI agents" "automation tools"

    # Customize max posts
    python execution/scrape_linkedin_posts.py author "https://www.linkedin.com/in/example-user/" --max-posts 50

    # Include comments and reactions
    python execution/scrape_linkedin_posts.py author "https://www.linkedin.com/in/example-user/" --scrape-comments --scrape-reactions
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
ACTOR_ID = "harvestapi/linkedin-post-search"
OUTPUT_DIR = Path(__file__).parent.parent / ".tmp"


def validate_environment():
    """Validate required environment variables."""
    if not APIFY_TOKEN:
        raise ValueError(
            "APIFY_TOKEN not found in environment. "
            "Please add it to your .env file."
        )


def validate_linkedin_url(url: str) -> bool:
    """
    Validate LinkedIn profile URL format.

    Args:
        url: URL to validate

    Returns:
        bool: True if valid LinkedIn profile URL
    """
    pattern = r'^https?://(www\.)?linkedin\.com/in/[\w-]+/?$'
    return bool(re.match(pattern, url))


def run_linkedin_scraper(
    mode: str,
    inputs: list,
    max_posts: int = 30,
    scrape_comments: bool = False,
    scrape_reactions: bool = False,
    max_reactions: int = 5
) -> dict:
    """
    Run the LinkedIn scraper Actor.

    Args:
        mode: 'author' or 'search'
        inputs: List of author URLs or search queries
        max_posts: Maximum posts to retrieve
        scrape_comments: Whether to scrape post comments
        scrape_reactions: Whether to scrape reaction details
        max_reactions: Max reactions to scrape per post

    Returns:
        dict: Scraper results with post data
    """
    print(f"🚀 Starting LinkedIn scraper in {mode} mode")
    print(f"📊 Max posts: {max_posts}")
    print(f"📝 Input: {inputs}")

    # Initialize Apify client
    client = ApifyClient(APIFY_TOKEN)

    # Build Actor input based on mode
    run_input = {
        "maxPosts": max_posts,
        "scrapeComments": scrape_comments,
        "scrapeReactions": scrape_reactions,
        "maxReactions": max_reactions
    }

    if mode == "author":
        # Validate URLs
        for url in inputs:
            if not validate_linkedin_url(url):
                print(f"⚠️  Warning: '{url}' may not be a valid LinkedIn profile URL")
        run_input["authorUrls"] = inputs
    elif mode == "search":
        run_input["searchQueries"] = inputs
    else:
        raise ValueError(f"Invalid mode: {mode}. Use 'author' or 'search'")

    print(f"⏳ Running Actor with input: {json.dumps(run_input, indent=2)}")

    try:
        run = client.actor(ACTOR_ID).call(run_input=run_input)

        print(f"✅ Actor run completed!")
        print(f"📋 Run ID: {run['id']}")
        print(f"⏱️  Duration: {run.get('stats', {}).get('runTimeSecs', 'N/A')}s")

        # Fetch results from dataset
        print("📥 Fetching results...")
        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        return {
            "success": True,
            "run_id": run['id'],
            "dataset_id": run["defaultDatasetId"],
            "items": dataset_items,
            "count": len(dataset_items),
            "mode": mode,
            "query": inputs
        }

    except Exception as e:
        print(f"❌ Actor run failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "items": [],
            "count": 0,
            "mode": mode,
            "query": inputs
        }


def process_results(results: dict) -> dict:
    """
    Process and structure the scraped results.

    Args:
        results: Raw results from Apify

    Returns:
        dict: Cleaned and structured data
    """
    processed_posts = []

    for item in results["items"]:
        # Extract engagement metrics from nested 'engagement' object
        engagement = item.get("engagement", {})
        likes = engagement.get("likes", 0)
        comments_count = engagement.get("comments", 0)
        shares = engagement.get("shares", 0)

        # Extract author info from nested 'author' object
        author = item.get("author", {})

        # Extract posted time from nested 'postedAt' object
        posted_at = item.get("postedAt", {})

        # Extract image URLs from 'postImages' array
        post_images = item.get("postImages", [])
        media_urls = [img.get("url") for img in post_images if img.get("url")]

        post = {
            "id": item.get("id", ""),
            "text": item.get("content", ""),
            "author_name": author.get("name", ""),
            "author_url": author.get("linkedinUrl", ""),
            "author_headline": author.get("info", ""),
            "author_avatar": author.get("avatar", {}).get("url", ""),
            "posted_at": posted_at.get("date", ""),
            "posted_ago": posted_at.get("postedAgoText", ""),
            "likes": likes,
            "comments": comments_count,
            "reposts": shares,
            "post_url": item.get("linkedinUrl", ""),
            "media_urls": media_urls,
            "hashtags": item.get("hashtags", []),
            "engagement_score": likes + (comments_count * 2) + (shares * 3),
            "reactions_breakdown": engagement.get("reactions", [])
        }

        # Include comments if scraped
        if item.get("comments"):
            post["comment_data"] = item["comments"]

        # Include reactions if scraped
        if item.get("reactions"):
            post["reaction_data"] = item["reactions"]

        processed_posts.append(post)

    # Sort by engagement score descending
    processed_posts.sort(key=lambda x: x["engagement_score"], reverse=True)

    return {
        "posts": processed_posts,
        "scraped_at": datetime.now().isoformat(),
        "total_count": len(processed_posts),
        "mode": results.get("mode", "unknown"),
        "query": results.get("query", []),
        "run_id": results.get("run_id", "")
    }


def save_results(data: dict, filename: str = None) -> Path:
    """
    Save results to .tmp directory.

    Args:
        data: Processed post data
        filename: Custom filename (optional)

    Returns:
        Path: Output file path
    """
    OUTPUT_DIR.mkdir(exist_ok=True)

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"linkedin_posts_{timestamp}.json"

    output_path = OUTPUT_DIR / filename

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Results saved to: {output_path}")
    print(f"📊 Total posts: {data['total_count']}")

    # Print top posts
    if data['posts']:
        print("\n🔥 Top Posts by Engagement:")
        for i, post in enumerate(data['posts'][:5], 1):
            text_preview = post['text'][:100] + "..." if len(post['text']) > 100 else post['text']
            text_preview = text_preview.replace('\n', ' ')
            print(f"\n{i}. {post['author_name']}")
            print(f"   {text_preview}")
            print(f"   👍 {post['likes']} | 💬 {post['comments']} | 🔄 {post['reposts']}")
            if post['post_url']:
                print(f"   🔗 {post['post_url']}")

    return output_path


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Scrape LinkedIn posts by author or search query",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape from a profile
  python execution/scrape_linkedin_posts.py author "https://www.linkedin.com/in/example-user/"

  # Search for posts
  python execution/scrape_linkedin_posts.py search "AI automation" "LLM agents"

  # With options
  python execution/scrape_linkedin_posts.py author "https://www.linkedin.com/in/user/" --max-posts 50 --scrape-comments
        """
    )

    parser.add_argument(
        "mode",
        choices=["author", "search"],
        help="Scraping mode: 'author' for profile URLs, 'search' for keywords"
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="LinkedIn profile URLs (author mode) or search queries (search mode)"
    )
    parser.add_argument(
        "--max-posts",
        type=int,
        default=30,
        help="Maximum posts to scrape (default: 30)"
    )
    parser.add_argument(
        "--scrape-comments",
        action="store_true",
        help="Include post comments (increases cost)"
    )
    parser.add_argument(
        "--scrape-reactions",
        action="store_true",
        help="Include reaction details (increases cost)"
    )
    parser.add_argument(
        "--max-reactions",
        type=int,
        default=5,
        help="Max reactions to scrape per post (default: 5)"
    )
    parser.add_argument(
        "--output",
        help="Custom output filename"
    )

    args = parser.parse_args()

    try:
        # Validate environment
        validate_environment()

        # Run scraper
        results = run_linkedin_scraper(
            mode=args.mode,
            inputs=args.inputs,
            max_posts=args.max_posts,
            scrape_comments=args.scrape_comments,
            scrape_reactions=args.scrape_reactions,
            max_reactions=args.max_reactions
        )

        if not results["success"]:
            print(f"❌ Scraping failed: {results.get('error')}")
            return 1

        if results["count"] == 0:
            print("⚠️  No posts found for the given input")
            return 0

        # Process results
        processed_data = process_results(results)

        # Save results
        save_results(processed_data, args.output)

        print("\n✅ LinkedIn scraping completed successfully!")
        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
