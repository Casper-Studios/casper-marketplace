#!/usr/bin/env python3
"""
Reddit AI/Tech Trends Scraper
Scrapes trending posts from AI and tech-focused subreddits using Apify.

Usage:
    python execution/scrape_reddit_ai_tech.py [--max-posts 50] [--sort hot]
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
ACTOR_ID = "trudax/reddit-scraper-lite"  # Free tier actor
OUTPUT_DIR = Path(__file__).parent.parent / ".tmp"

# AI/Tech-focused subreddits
DEFAULT_SUBREDDITS = [
    "r/artificial",
    "r/MachineLearning",
    "r/LocalLLaMA",
    "r/ChatGPT",
    "r/OpenAI",
    "r/ClaudeAI",
    "r/singularity",
    "r/technology",
    "r/Futurology"
]

def validate_environment():
    """Validate required environment variables."""
    if not APIFY_TOKEN:
        raise ValueError(
            "APIFY_TOKEN not found in environment. "
            "Please add it to your .env file."
        )

def run_reddit_scraper(
    subreddits=None,
    search_terms=None,
    max_posts=50,
    max_comments=20,
    sort_by="hot",
    time_filter="week"
):
    """
    Run the Reddit scraper Actor.

    Args:
        subreddits (list): List of subreddit names
        search_terms (str): Search keywords
        max_posts (int): Maximum number of posts to scrape
        max_comments (int): Maximum comments per post
        sort_by (str): Sort order (hot, top, new, relevance)
        time_filter (str): Time filter (hour, day, week, month, year)

    Returns:
        dict: Scraper results with post data
    """
    if subreddits is None:
        subreddits = DEFAULT_SUBREDDITS

    print(f"🚀 Starting Reddit scraper for subreddits: {', '.join(subreddits)}")
    print(f"📊 Max posts: {max_posts}, Sort: {sort_by}, Time: {time_filter}")

    # Initialize Apify client
    client = ApifyClient(APIFY_TOKEN)

    # Prepare Actor input - use search in communities for better results
    communities = [sub.replace("r/", "") for sub in subreddits]

    run_input = {
        "maxItems": max_posts,
        "maxComments": max_comments,
        "sort": sort_by,
        "time": time_filter,
    }

    # Use search terms if provided, otherwise use start URLs
    if search_terms:
        # Build search queries for each community
        run_input["searches"] = [f"{search_terms} subreddit:{comm}" for comm in communities]
        print(f"🔍 Search: {search_terms} in communities: {', '.join(communities)}")
    else:
        # Use community URLs as startUrls
        start_urls = [{"url": f"https://www.reddit.com/{sub}/"} for sub in subreddits]
        run_input["startUrls"] = start_urls

    print("⏳ Running Actor...")

    # Run the Actor and wait for completion
    try:
        run = client.actor(ACTOR_ID).call(run_input=run_input)

        # Get run status
        print(f"✅ Actor run completed!")
        print(f"📋 Run ID: {run['id']}")
        print(f"⏱️  Duration: {run.get('duration', 'N/A')}s")

        # Fetch results from dataset
        print("📥 Fetching results...")
        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        return {
            "success": True,
            "run_id": run['id'],
            "dataset_id": run["defaultDatasetId"],
            "items": dataset_items,
            "count": len(dataset_items)
        }

    except Exception as e:
        print(f"❌ Actor run failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "items": [],
            "count": 0
        }

def process_results(results, min_score=10):
    """
    Process and structure the scraped results.

    Args:
        results (dict): Raw results from Apify
        min_score (int): Minimum upvote score filter

    Returns:
        dict: Cleaned and structured data
    """
    processed_posts = []

    print(f"🔍 Filtering for posts with {min_score}+ upvotes")

    total_scraped = len(results["items"])
    filtered_count = 0

    # Debug: Print first item structure
    if results["items"]:
        print(f"📋 Sample item keys: {list(results['items'][0].keys())[:10]}")

    for item in results["items"]:
        # The lite version returns different field names
        # Handle different possible score field names
        score = (item.get("score", 0) or item.get("ups", 0) or
                item.get("upvotes", 0) or item.get("upCount", 0) or 0)

        # If no score field, skip filtering (accept all)
        if score > 0 and score < min_score:
            continue

        # Skip comments (they have empty titles)
        title = item.get("title", "")
        if not title or len(title) < 5:
            continue

        # Extract post data (mapping lite version fields)
        post = {
            "id": item.get("id", "") or item.get("parsedId", ""),
            "title": title,
            "subreddit": item.get("subreddit", "") or item.get("communityName", "") or item.get("parsedCommunityName", ""),
            "author": item.get("author", "") or item.get("username", ""),
            "score": score,
            "upvote_ratio": item.get("upvote_ratio", 0) or item.get("upvoteRatio", 0),
            "num_comments": item.get("num_comments", 0) or item.get("numberOfComments", 0),
            "url": item.get("url", ""),
            "permalink": item.get("permalink", "") or item.get("url", ""),
            "created_utc": item.get("created_utc", "") or item.get("createdAt", ""),
            "selftext": (item.get("selftext", "") or item.get("body", ""))[:500],  # Limit text length
            "link_flair_text": item.get("link_flair_text", ""),
            "is_video": item.get("is_video", False),
            "top_comments": []
        }

        # Extract top comments
        comments = item.get("comments", [])
        for comment in comments[:5]:  # Top 5 comments
            if isinstance(comment, dict):
                post["top_comments"].append({
                    "author": comment.get("author", ""),
                    "body": comment.get("body", "")[:300],  # Limit length
                    "score": comment.get("score", 0)
                })

        processed_posts.append(post)
        filtered_count += 1

    # Sort by score descending
    processed_posts.sort(key=lambda x: x["score"], reverse=True)

    print(f"✨ Filtered {filtered_count} posts from {total_scraped} total")

    return {
        "posts": processed_posts,
        "scraped_at": datetime.now().isoformat(),
        "total_count": len(processed_posts),
        "total_scraped": total_scraped,
        "run_id": results.get("run_id", ""),
    }

def save_results(data, filename=None):
    """
    Save results to .tmp directory.

    Args:
        data (dict): Processed post data
        filename (str, optional): Custom filename
    """
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Generate filename
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reddit_ai_tech_{timestamp}.json"

    output_path = OUTPUT_DIR / filename

    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"💾 Results saved to: {output_path}")
    print(f"📊 Total posts: {data['total_count']}")

    # Print top 5 posts
    print("\n🔥 Top 5 Posts by Score:")
    for i, post in enumerate(data['posts'][:5], 1):
        print(f"\n{i}. r/{post['subreddit']} - {post['title'][:60]}...")
        print(f"   ⬆️  {post['score']} | 💬 {post['num_comments']} comments")
        print(f"   🔗 {post['permalink']}")

    return output_path

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Scrape trending AI/Tech posts from Reddit"
    )
    parser.add_argument(
        "--subreddits",
        nargs="+",
        help="List of subreddits (e.g., r/artificial r/MachineLearning)"
    )
    parser.add_argument(
        "--search",
        help="Search terms to filter posts"
    )
    parser.add_argument(
        "--max-posts",
        type=int,
        default=50,
        help="Maximum number of posts to scrape (default: 50)"
    )
    parser.add_argument(
        "--max-comments",
        type=int,
        default=20,
        help="Maximum comments per post (default: 20)"
    )
    parser.add_argument(
        "--sort",
        choices=["hot", "top", "new", "relevance"],
        default="hot",
        help="Sort order (default: hot)"
    )
    parser.add_argument(
        "--time",
        choices=["hour", "day", "week", "month", "year"],
        default="week",
        help="Time filter (default: week)"
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=10,
        help="Minimum upvote score filter (default: 10)"
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
        results = run_reddit_scraper(
            subreddits=args.subreddits,
            search_terms=args.search,
            max_posts=args.max_posts,
            max_comments=args.max_comments,
            sort_by=args.sort,
            time_filter=args.time
        )

        if not results["success"]:
            print(f"❌ Scraping failed: {results.get('error')}")
            return 1

        # Process results
        processed_data = process_results(results, min_score=args.min_score)

        # Save results
        save_results(processed_data, args.output)

        print("\n✅ Scraping completed successfully!")
        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
