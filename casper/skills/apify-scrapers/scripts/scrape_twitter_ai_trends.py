#!/usr/bin/env python3
"""
Twitter AI Trends Scraper
Scrapes trending AI-related posts from Twitter/X using Apify.

Usage:
    python execution/scrape_twitter_ai_trends.py [--max-tweets 100] [--query "AI"]
"""

import os
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
ACTOR_ID = "kaitoeasyapi/twitter-x-data-tweet-scraper-pay-per-result-cheapest"
OUTPUT_DIR = Path(__file__).parent.parent / ".tmp"

def validate_environment():
    """Validate required environment variables."""
    if not APIFY_TOKEN:
        raise ValueError(
            "APIFY_TOKEN not found in environment. "
            "Please add it to your .env file."
        )

def run_twitter_scraper(query="AI", max_tweets=50):
    """
    Run the Twitter scraper Actor.

    Args:
        query (str): Search query for tweets
        max_tweets (int): Maximum number of tweets to scrape

    Returns:
        dict: Scraper results with tweet data
    """
    print(f"🚀 Starting Twitter scraper for query: '{query}'")
    print(f"📊 Max tweets: {max_tweets}")

    # Initialize Apify client
    client = ApifyClient(APIFY_TOKEN)

    # Prepare Actor input using correct API parameters
    run_input = {
        "twitterContent": query,  # Search for tweets containing this term
        "maxItems": max_tweets,   # Maximum number of tweets to return
        "lang": "en",             # English tweets only
        "queryType": "Latest",    # Get latest tweets
        "include:nativeretweets": False,  # Exclude retweets
        "filter:replies": False,  # Exclude replies
    }

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

def process_results(results, min_likes=10, min_retweets=5):
    """
    Process and structure the scraped results, filtering for trending tweets.

    Args:
        results (dict): Raw results from Apify
        min_likes (int): Minimum likes for trending filter
        min_retweets (int): Minimum retweets for trending filter

    Returns:
        dict: Cleaned and structured data with only trending tweets
    """
    from dateutil import parser

    processed_tweets = []
    now = datetime.now()
    cutoff_time = now.replace(hour=0, minute=0, second=0, microsecond=0)  # Today at midnight

    print(f"🔍 Filtering for tweets since: {cutoff_time.isoformat()}")
    print(f"📊 Engagement threshold: {min_likes}+ likes OR {min_retweets}+ retweets")

    total_scraped = len(results["items"])
    filtered_count = 0

    for item in results["items"]:
        # Skip retweets - we want original content only
        if item.get("isRetweet", False):
            continue

        likes = item.get("likeCount", 0)
        retweets = item.get("retweetCount", 0)

        # Filter by engagement threshold
        if likes < min_likes and retweets < min_retweets:
            continue

        # Parse and check date (but don't filter strictly - data quality issues)
        created_at_str = item.get("createdAt", "")

        tweet = {
            "id": item.get("id", ""),
            "text": item.get("text", ""),
            "author": item.get("author", {}).get("userName", ""),
            "author_name": item.get("author", {}).get("name", ""),
            "created_at": created_at_str,
            "likes": likes,
            "retweets": retweets,
            "replies": item.get("replyCount", 0),
            "views": item.get("viewCount", 0),
            "url": item.get("url", ""),
            "engagement_score": likes + retweets,
        }
        processed_tweets.append(tweet)
        filtered_count += 1

    # Sort by engagement score (likes + retweets) descending
    processed_tweets.sort(
        key=lambda x: x["engagement_score"],
        reverse=True
    )

    print(f"✨ Filtered {filtered_count} trending tweets from {total_scraped} total")

    return {
        "tweets": processed_tweets,
        "scraped_at": datetime.now().isoformat(),
        "total_count": len(processed_tweets),
        "total_scraped": total_scraped,
        "query_used": results.get("query", "AI"),
        "run_id": results.get("run_id", ""),
        "filter_applied": {
            "min_likes": min_likes,
            "min_retweets": min_retweets,
            "date_cutoff": cutoff_time.isoformat(),
            "retweets_excluded": True
        }
    }

def save_results(data, filename=None):
    """
    Save results to .tmp directory.

    Args:
        data (dict): Processed tweet data
        filename (str, optional): Custom filename
    """
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Generate filename
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"twitter_ai_trends_{timestamp}.json"

    output_path = OUTPUT_DIR / filename

    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"💾 Results saved to: {output_path}")
    print(f"📊 Total tweets: {data['total_count']}")

    # Print top 5 tweets
    print("\n🔥 Top 5 Most Engaged Tweets:")
    for i, tweet in enumerate(data['tweets'][:5], 1):
        print(f"\n{i}. @{tweet['author']}")
        print(f"   {tweet['text'][:100]}...")
        print(f"   ❤️  {tweet['likes']} | 🔄 {tweet['retweets']} | 👁️  {tweet['views']}")
        print(f"   🔗 {tweet['url']}")

    return output_path

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Scrape trending AI tweets from Twitter/X"
    )
    parser.add_argument(
        "--query",
        default="AI OR ChatGPT OR LLM OR GPT OR Claude OR 'artificial intelligence' OR OpenAI OR Anthropic",
        help="Search query for tweets"
    )
    parser.add_argument(
        "--max-tweets",
        type=int,
        default=50,
        help="Maximum number of tweets to scrape"
    )
    parser.add_argument(
        "--output",
        help="Custom output filename"
    )
    parser.add_argument(
        "--min-likes",
        type=int,
        default=10,
        help="Minimum likes for trending filter (default: 10)"
    )
    parser.add_argument(
        "--min-retweets",
        type=int,
        default=5,
        help="Minimum retweets for trending filter (default: 5)"
    )

    args = parser.parse_args()

    try:
        # Validate environment
        validate_environment()

        # Run scraper
        results = run_twitter_scraper(
            query=args.query,
            max_tweets=args.max_tweets
        )

        if not results["success"]:
            print(f"❌ Scraping failed: {results.get('error')}")
            return 1

        # Process results with trending filters
        results["query"] = args.query
        processed_data = process_results(
            results,
            min_likes=args.min_likes,
            min_retweets=args.min_retweets
        )

        # Save results
        save_results(processed_data, args.output)

        print("\n✅ Scraping completed successfully!")
        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
