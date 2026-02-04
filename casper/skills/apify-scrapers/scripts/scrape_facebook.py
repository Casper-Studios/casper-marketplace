#!/usr/bin/env python3
"""
Facebook Scraper
Comprehensive Facebook scraper supporting pages, posts, reviews, groups, and marketplace using Apify.

Usage:
    # Scrape page info
    python scrape_facebook.py page "https://facebook.com/pagename" --output page.json

    # Scrape posts from a page
    python scrape_facebook.py posts "https://facebook.com/pagename" --max-posts 50 --output posts.json

    # Scrape reviews
    python scrape_facebook.py reviews "https://facebook.com/pagename" --max-reviews 100 --output reviews.json

    # Scrape group posts
    python scrape_facebook.py groups "https://facebook.com/groups/groupname" --max-posts 50 --output groups.json

    # Scrape marketplace
    python scrape_facebook.py marketplace "laptops" --location "New York" --max-items 50 --output marketplace.json
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from apify_client import ApifyClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
OUTPUT_DIR = Path(__file__).parent.parent / ".tmp"

# Apify Actor IDs for different Facebook scraping modes
ACTORS = {
    "page": "apify/facebook-pages-scraper",
    "posts": "apify/facebook-posts-scraper",
    "reviews": "apify/facebook-reviews-scraper",
    "groups": "apify/facebook-groups-scraper",
    "marketplace": "apify/facebook-marketplace-scraper",
}


def validate_environment():
    """Validate required environment variables."""
    if not APIFY_TOKEN:
        raise ValueError(
            "APIFY_TOKEN not found in environment. "
            "Please add it to your .env file."
        )


def run_facebook_scraper(mode, target, **kwargs):
    """
    Run the appropriate Facebook scraper Actor based on mode.

    Args:
        mode (str): Scraping mode (page, posts, reviews, groups, marketplace)
        target (str): URL or search query depending on mode
        **kwargs: Additional parameters specific to each mode

    Returns:
        dict: Scraper results with data
    """
    actor_id = ACTORS.get(mode)
    if not actor_id:
        raise ValueError(f"Unknown mode: {mode}. Available modes: {list(ACTORS.keys())}")

    print(f"Starting Facebook {mode} scraper")
    print(f"Target: {target}")
    print(f"Actor: {actor_id}")

    # Initialize Apify client
    client = ApifyClient(APIFY_TOKEN)

    # Build input based on mode
    run_input = build_actor_input(mode, target, **kwargs)

    print(f"Running Actor with input: {json.dumps(run_input, indent=2)}")

    try:
        run = client.actor(actor_id).call(run_input=run_input)

        print(f"Actor run completed!")
        print(f"Run ID: {run['id']}")
        print(f"Duration: {run.get('stats', {}).get('runTimeSecs', 'N/A')}s")

        # Fetch results from dataset
        print("Fetching results...")
        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        return {
            "success": True,
            "run_id": run['id'],
            "dataset_id": run["defaultDatasetId"],
            "items": dataset_items,
            "count": len(dataset_items),
            "mode": mode,
            "target": target
        }

    except Exception as e:
        print(f"Actor run failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "items": [],
            "count": 0,
            "mode": mode,
            "target": target
        }


def build_actor_input(mode, target, **kwargs):
    """
    Build the appropriate input for each Apify actor.

    Args:
        mode (str): Scraping mode
        target (str): URL or search query
        **kwargs: Additional parameters

    Returns:
        dict: Actor input configuration
    """
    if mode == "page":
        return {
            "startUrls": [{"url": target}],
            "maxPagesPerQuery": kwargs.get("max_pages", 1),
            "proxyConfiguration": {"useApifyProxy": True},
        }

    elif mode == "posts":
        return {
            "startUrls": [{"url": target}],
            "maxPosts": kwargs.get("max_posts", 50),
            "maxPostComments": kwargs.get("max_comments", 0),
            "maxCommentReplies": kwargs.get("max_replies", 0),
            "proxyConfiguration": {"useApifyProxy": True},
        }

    elif mode == "reviews":
        return {
            "startUrls": [{"url": target}],
            "maxReviews": kwargs.get("max_reviews", 100),
            "proxyConfiguration": {"useApifyProxy": True},
        }

    elif mode == "groups":
        return {
            "startUrls": [{"url": target}],
            "maxPosts": kwargs.get("max_posts", 50),
            "maxPostComments": kwargs.get("max_comments", 0),
            "proxyConfiguration": {"useApifyProxy": True},
        }

    elif mode == "marketplace":
        input_config = {
            "searchQuery": target,
            "maxItems": kwargs.get("max_items", 50),
            "proxyConfiguration": {"useApifyProxy": True},
        }
        if kwargs.get("location"):
            input_config["location"] = kwargs["location"]
        if kwargs.get("min_price"):
            input_config["minPrice"] = kwargs["min_price"]
        if kwargs.get("max_price"):
            input_config["maxPrice"] = kwargs["max_price"]
        if kwargs.get("category"):
            input_config["category"] = kwargs["category"]
        return input_config

    else:
        raise ValueError(f"Unknown mode: {mode}")


def process_results(results):
    """
    Process and structure the scraped results based on mode.

    Args:
        results (dict): Raw results from Apify

    Returns:
        dict: Cleaned and structured data
    """
    mode = results.get("mode", "unknown")
    items = results.get("items", [])

    processors = {
        "page": process_page_data,
        "posts": process_posts_data,
        "reviews": process_reviews_data,
        "groups": process_groups_data,
        "marketplace": process_marketplace_data,
    }

    processor = processors.get(mode, lambda x: x)
    processed_data = processor(items)

    return {
        "scraped_at": datetime.now().isoformat(),
        "platform": "facebook",
        "mode": mode,
        "target": results.get("target", ""),
        "total_count": len(processed_data),
        "run_id": results.get("run_id", ""),
        "data": processed_data
    }


def process_page_data(items):
    """Process Facebook page data."""
    processed = []
    for item in items:
        page = {
            "id": item.get("id", ""),
            "name": item.get("name", ""),
            "username": item.get("username", ""),
            "url": item.get("url", ""),
            "category": item.get("category", ""),
            "description": item.get("description", ""),
            "likes": item.get("likes", 0),
            "followers": item.get("followers", 0),
            "rating": item.get("rating", None),
            "review_count": item.get("reviewCount", 0),
            "address": item.get("address", ""),
            "phone": item.get("phone", ""),
            "website": item.get("website", ""),
            "email": item.get("email", ""),
            "hours": item.get("hours", {}),
            "cover_photo": item.get("coverPhoto", ""),
            "profile_photo": item.get("profilePhoto", ""),
            "verified": item.get("verified", False),
            "raw": item  # Keep raw data for debugging
        }
        processed.append(page)
    return processed


def process_posts_data(items):
    """Process Facebook posts data."""
    processed = []
    for item in items:
        post = {
            "id": item.get("id", ""),
            "url": item.get("url", ""),
            "text": item.get("text", ""),
            "time": item.get("time", ""),
            "timestamp": item.get("timestamp", ""),
            "likes": item.get("likes", 0),
            "comments": item.get("comments", 0),
            "shares": item.get("shares", 0),
            "reactions": item.get("reactions", {}),
            "media": item.get("media", []),
            "author": {
                "name": item.get("authorName", ""),
                "id": item.get("authorId", ""),
                "url": item.get("authorUrl", ""),
            },
            "is_shared": item.get("isShared", False),
            "shared_post": item.get("sharedPost", None),
            "engagement_score": (
                item.get("likes", 0) +
                item.get("comments", 0) * 2 +
                item.get("shares", 0) * 3
            ),
        }
        processed.append(post)

    # Sort by engagement score
    processed.sort(key=lambda x: x["engagement_score"], reverse=True)
    return processed


def process_reviews_data(items):
    """Process Facebook reviews data."""
    processed = []
    for item in items:
        review = {
            "id": item.get("id", ""),
            "rating": item.get("rating", None),
            "text": item.get("text", ""),
            "time": item.get("time", ""),
            "timestamp": item.get("timestamp", ""),
            "author": {
                "name": item.get("authorName", ""),
                "id": item.get("authorId", ""),
                "url": item.get("authorUrl", ""),
                "profile_photo": item.get("authorProfilePhoto", ""),
            },
            "helpful_count": item.get("helpfulCount", 0),
            "response": item.get("response", None),
        }
        processed.append(review)

    # Sort by timestamp (newest first) if available
    processed.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return processed


def process_groups_data(items):
    """Process Facebook group posts data."""
    processed = []
    for item in items:
        post = {
            "id": item.get("id", ""),
            "url": item.get("url", ""),
            "text": item.get("text", ""),
            "time": item.get("time", ""),
            "timestamp": item.get("timestamp", ""),
            "likes": item.get("likes", 0),
            "comments": item.get("comments", 0),
            "shares": item.get("shares", 0),
            "reactions": item.get("reactions", {}),
            "media": item.get("media", []),
            "author": {
                "name": item.get("authorName", ""),
                "id": item.get("authorId", ""),
                "url": item.get("authorUrl", ""),
            },
            "group": {
                "name": item.get("groupName", ""),
                "id": item.get("groupId", ""),
                "url": item.get("groupUrl", ""),
            },
            "engagement_score": (
                item.get("likes", 0) +
                item.get("comments", 0) * 2 +
                item.get("shares", 0) * 3
            ),
        }
        processed.append(post)

    # Sort by engagement score
    processed.sort(key=lambda x: x["engagement_score"], reverse=True)
    return processed


def process_marketplace_data(items):
    """Process Facebook marketplace listings data."""
    processed = []
    for item in items:
        listing = {
            "id": item.get("id", ""),
            "url": item.get("url", ""),
            "title": item.get("title", ""),
            "price": item.get("price", ""),
            "price_amount": item.get("priceAmount", None),
            "currency": item.get("currency", "USD"),
            "description": item.get("description", ""),
            "condition": item.get("condition", ""),
            "location": item.get("location", ""),
            "images": item.get("images", []),
            "seller": {
                "name": item.get("sellerName", ""),
                "id": item.get("sellerId", ""),
                "url": item.get("sellerUrl", ""),
                "profile_photo": item.get("sellerProfilePhoto", ""),
            },
            "category": item.get("category", ""),
            "listed_time": item.get("listedTime", ""),
            "availability": item.get("availability", ""),
        }
        processed.append(listing)
    return processed


def save_results(data, filename=None, mode="facebook"):
    """
    Save results to .tmp directory.

    Args:
        data (dict): Processed data
        filename (str, optional): Custom filename
        mode (str): Scraping mode for default filename

    Returns:
        Path: Path to saved file
    """
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate filename
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"facebook_{mode}_{timestamp}.json"

    output_path = OUTPUT_DIR / filename

    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {output_path}")
    print(f"Total items: {data['total_count']}")

    return output_path


def print_summary(data):
    """Print a summary of the scraped data."""
    mode = data.get("mode", "unknown")
    items = data.get("data", [])

    print(f"\n--- Facebook {mode.upper()} Summary ---")
    print(f"Total items: {len(items)}")

    if mode == "page" and items:
        for page in items[:3]:
            print(f"\n  Page: {page.get('name', 'N/A')}")
            print(f"  Followers: {page.get('followers', 'N/A')}")
            print(f"  Rating: {page.get('rating', 'N/A')}")
            print(f"  URL: {page.get('url', 'N/A')}")

    elif mode == "posts" and items:
        print("\nTop 5 Most Engaged Posts:")
        for i, post in enumerate(items[:5], 1):
            print(f"\n  {i}. {post.get('text', 'N/A')[:100]}...")
            print(f"     Likes: {post.get('likes', 0)} | Comments: {post.get('comments', 0)} | Shares: {post.get('shares', 0)}")
            print(f"     URL: {post.get('url', 'N/A')}")

    elif mode == "reviews" and items:
        print("\nRecent Reviews:")
        for i, review in enumerate(items[:5], 1):
            rating = review.get('rating', 'N/A')
            text = review.get('text', 'N/A')[:100]
            author = review.get('author', {}).get('name', 'Anonymous')
            print(f"\n  {i}. Rating: {rating}/5 by {author}")
            print(f"     {text}...")

    elif mode == "groups" and items:
        print("\nTop 5 Most Engaged Group Posts:")
        for i, post in enumerate(items[:5], 1):
            print(f"\n  {i}. {post.get('text', 'N/A')[:100]}...")
            print(f"     Likes: {post.get('likes', 0)} | Comments: {post.get('comments', 0)}")
            print(f"     Group: {post.get('group', {}).get('name', 'N/A')}")

    elif mode == "marketplace" and items:
        print("\nMarketplace Listings:")
        for i, listing in enumerate(items[:5], 1):
            print(f"\n  {i}. {listing.get('title', 'N/A')}")
            print(f"     Price: {listing.get('price', 'N/A')}")
            print(f"     Location: {listing.get('location', 'N/A')}")
            print(f"     Condition: {listing.get('condition', 'N/A')}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Facebook scraper supporting multiple modes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape page info
  python scrape_facebook.py page "https://facebook.com/pagename"

  # Scrape posts from a page
  python scrape_facebook.py posts "https://facebook.com/pagename" --max-posts 50

  # Scrape reviews
  python scrape_facebook.py reviews "https://facebook.com/pagename" --max-reviews 100

  # Scrape group posts
  python scrape_facebook.py groups "https://facebook.com/groups/groupname" --max-posts 50

  # Scrape marketplace
  python scrape_facebook.py marketplace "laptops" --location "New York" --max-items 50
        """
    )

    subparsers = parser.add_subparsers(dest="mode", help="Scraping mode")

    # Page scraper
    page_parser = subparsers.add_parser("page", help="Scrape Facebook page information")
    page_parser.add_argument("url", help="Facebook page URL")
    page_parser.add_argument("--max-pages", type=int, default=1, help="Max pages to scrape (default: 1)")
    page_parser.add_argument("--output", help="Custom output filename")

    # Posts scraper
    posts_parser = subparsers.add_parser("posts", help="Scrape posts from a Facebook page")
    posts_parser.add_argument("url", help="Facebook page URL")
    posts_parser.add_argument("--max-posts", type=int, default=50, help="Max posts to scrape (default: 50)")
    posts_parser.add_argument("--max-comments", type=int, default=0, help="Max comments per post (default: 0)")
    posts_parser.add_argument("--max-replies", type=int, default=0, help="Max replies per comment (default: 0)")
    posts_parser.add_argument("--output", help="Custom output filename")

    # Reviews scraper
    reviews_parser = subparsers.add_parser("reviews", help="Scrape reviews from a Facebook page")
    reviews_parser.add_argument("url", help="Facebook page URL")
    reviews_parser.add_argument("--max-reviews", type=int, default=100, help="Max reviews to scrape (default: 100)")
    reviews_parser.add_argument("--output", help="Custom output filename")

    # Groups scraper
    groups_parser = subparsers.add_parser("groups", help="Scrape posts from a Facebook group")
    groups_parser.add_argument("url", help="Facebook group URL")
    groups_parser.add_argument("--max-posts", type=int, default=50, help="Max posts to scrape (default: 50)")
    groups_parser.add_argument("--max-comments", type=int, default=0, help="Max comments per post (default: 0)")
    groups_parser.add_argument("--output", help="Custom output filename")

    # Marketplace scraper
    marketplace_parser = subparsers.add_parser("marketplace", help="Scrape Facebook Marketplace listings")
    marketplace_parser.add_argument("query", help="Search query for marketplace")
    marketplace_parser.add_argument("--location", help="Location for marketplace search")
    marketplace_parser.add_argument("--max-items", type=int, default=50, help="Max items to scrape (default: 50)")
    marketplace_parser.add_argument("--min-price", type=float, help="Minimum price filter")
    marketplace_parser.add_argument("--max-price", type=float, help="Maximum price filter")
    marketplace_parser.add_argument("--category", help="Category filter")
    marketplace_parser.add_argument("--output", help="Custom output filename")

    args = parser.parse_args()

    if not args.mode:
        parser.print_help()
        return 1

    try:
        # Validate environment
        validate_environment()

        # Build kwargs based on mode
        kwargs = {}
        if args.mode == "page":
            target = args.url
            kwargs["max_pages"] = args.max_pages
        elif args.mode == "posts":
            target = args.url
            kwargs["max_posts"] = args.max_posts
            kwargs["max_comments"] = args.max_comments
            kwargs["max_replies"] = args.max_replies
        elif args.mode == "reviews":
            target = args.url
            kwargs["max_reviews"] = args.max_reviews
        elif args.mode == "groups":
            target = args.url
            kwargs["max_posts"] = args.max_posts
            kwargs["max_comments"] = args.max_comments
        elif args.mode == "marketplace":
            target = args.query
            kwargs["max_items"] = args.max_items
            kwargs["location"] = args.location
            kwargs["min_price"] = args.min_price
            kwargs["max_price"] = args.max_price
            kwargs["category"] = args.category

        # Run scraper
        results = run_facebook_scraper(args.mode, target, **kwargs)

        if not results["success"]:
            print(f"Scraping failed: {results.get('error')}")
            return 1

        # Process results
        processed_data = process_results(results)

        # Save results
        save_results(processed_data, args.output, args.mode)

        # Print summary
        print_summary(processed_data)

        print("\nScraping completed successfully!")
        return 0

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
