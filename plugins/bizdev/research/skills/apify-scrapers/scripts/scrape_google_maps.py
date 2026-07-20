#!/usr/bin/env python3
"""
Google Maps Scraper
Scrapes businesses, place details, and reviews from Google Maps using Apify actors.

Usage:
    # Search for businesses
    python scrape_google_maps.py search "coffee shops" --location "San Francisco, CA" --max-results 50 --output coffee.json

    # Get place details by URL
    python scrape_google_maps.py place "https://maps.google.com/..." --output place.json

    # Get reviews for a place
    python scrape_google_maps.py reviews "https://maps.google.com/..." --max-reviews 100 --output reviews.json

    # Search with filters
    python scrape_google_maps.py search "restaurants" --location "NYC" --min-rating 4.0 --max-results 100 --output restaurants.json
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

# Actor IDs for Google Maps
ACTORS = {
    "search": "compass/crawler-google-places",
    "place": "compass/google-maps-extractor",
    "reviews": "compass/google-maps-reviews-scraper"
}


def validate_environment():
    """Validate required environment variables."""
    if not APIFY_TOKEN:
        raise ValueError(
            "APIFY_TOKEN not found in environment. "
            "Please add it to your .env file."
        )


def scrape_search(query, location=None, max_results=50, min_rating=None, language="en", zoom=14):
    """
    Search for businesses on Google Maps.

    Args:
        query (str): Search query (e.g., "coffee shops", "restaurants")
        location (str): Location to search in (e.g., "San Francisco, CA")
        max_results (int): Maximum number of results to return
        min_rating (float): Minimum rating filter (1.0-5.0)
        language (str): Language code for results
        zoom (int): Zoom level for search area (10-21)

    Returns:
        dict: Search results with business data
    """
    client = ApifyClient(APIFY_TOKEN)

    # Build search query with location
    search_terms = query
    if location:
        search_terms = f"{query} in {location}"

    run_input = {
        "searchStringsArray": [search_terms],
        "maxCrawledPlacesPerSearch": max_results,
        "language": language,
        "deeperCityScrape": False,
        "onlyDataFromSearchPage": False,
        "includeWebResults": False,
        "skipClosedPlaces": False,
    }

    # Add zoom level if specified
    if zoom:
        run_input["zoom"] = zoom

    print(f"Searching Google Maps for: '{search_terms}'")
    print(f"Max results: {max_results}")
    if min_rating:
        print(f"Min rating filter: {min_rating}")

    print("Running Actor...")

    try:
        run = client.actor(ACTORS["search"]).call(run_input=run_input)

        print(f"Actor run completed!")
        print(f"Run ID: {run['id']}")
        print(f"Duration: {run.get('stats', {}).get('runTimeSecs', 'N/A')}s")

        # Fetch results
        print("Fetching results...")
        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        # Apply min_rating filter if specified
        if min_rating:
            original_count = len(dataset_items)
            dataset_items = [
                item for item in dataset_items
                if item.get("totalScore", 0) and item.get("totalScore", 0) >= min_rating
            ]
            print(f"Filtered {original_count} results to {len(dataset_items)} with rating >= {min_rating}")

        return {
            "success": True,
            "run_id": run['id'],
            "dataset_id": run["defaultDatasetId"],
            "items": dataset_items,
            "count": len(dataset_items),
            "query": query,
            "location": location
        }

    except Exception as e:
        print(f"Actor run failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "items": [],
            "count": 0,
            "query": query,
            "location": location
        }


def scrape_place(place_url, language="en"):
    """
    Get detailed information about a specific place.

    Args:
        place_url (str): Google Maps URL for the place
        language (str): Language code for results

    Returns:
        dict: Place details
    """
    client = ApifyClient(APIFY_TOKEN)

    run_input = {
        "startUrls": [{"url": place_url}],
        "language": language,
        "maxImages": 10,
        "maxReviews": 0,  # Just details, not reviews
        "onlyDataFromSearchPage": False,
    }

    print(f"Fetching place details for: {place_url}")
    print("Running Actor...")

    try:
        run = client.actor(ACTORS["place"]).call(run_input=run_input)

        print(f"Actor run completed!")
        print(f"Run ID: {run['id']}")

        # Fetch results
        print("Fetching results...")
        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        return {
            "success": True,
            "run_id": run['id'],
            "dataset_id": run["defaultDatasetId"],
            "items": dataset_items,
            "count": len(dataset_items),
            "url": place_url
        }

    except Exception as e:
        print(f"Actor run failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "items": [],
            "count": 0,
            "url": place_url
        }


def scrape_reviews(place_url, max_reviews=100, language="en", sort_by="newest"):
    """
    Scrape reviews for a specific place.

    Args:
        place_url (str): Google Maps URL for the place
        max_reviews (int): Maximum number of reviews to scrape
        language (str): Language code for results
        sort_by (str): Sort order - "newest", "highest", "lowest", "relevant"

    Returns:
        dict: Review data
    """
    client = ApifyClient(APIFY_TOKEN)

    # Map sort options
    sort_mapping = {
        "newest": "newestFirst",
        "highest": "highestRating",
        "lowest": "lowestRating",
        "relevant": "mostRelevant"
    }

    run_input = {
        "startUrls": [{"url": place_url}],
        "maxReviews": max_reviews,
        "language": language,
        "reviewsSort": sort_mapping.get(sort_by, "newestFirst"),
        "personalDataOptions": "SKIP_PERSONAL_DATA",  # Privacy-conscious default
    }

    print(f"Scraping reviews for: {place_url}")
    print(f"Max reviews: {max_reviews}")
    print(f"Sort by: {sort_by}")
    print("Running Actor...")

    try:
        run = client.actor(ACTORS["reviews"]).call(run_input=run_input)

        print(f"Actor run completed!")
        print(f"Run ID: {run['id']}")
        print(f"Duration: {run.get('stats', {}).get('runTimeSecs', 'N/A')}s")

        # Fetch results
        print("Fetching results...")
        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        return {
            "success": True,
            "run_id": run['id'],
            "dataset_id": run["defaultDatasetId"],
            "items": dataset_items,
            "count": len(dataset_items),
            "url": place_url
        }

    except Exception as e:
        print(f"Actor run failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "items": [],
            "count": 0,
            "url": place_url
        }


def process_search_results(results):
    """
    Process and normalize search results.

    Args:
        results (dict): Raw results from Apify

    Returns:
        dict: Normalized data structure
    """
    processed_places = []

    for item in results["items"]:
        place = {
            "name": item.get("title", ""),
            "address": item.get("address", ""),
            "rating": item.get("totalScore"),
            "reviews_count": item.get("reviewsCount", 0),
            "phone": item.get("phone", ""),
            "website": item.get("website", ""),
            "place_id": item.get("placeId", ""),
            "coordinates": {
                "lat": item.get("location", {}).get("lat"),
                "lng": item.get("location", {}).get("lng")
            },
            "category": item.get("categoryName", ""),
            "price_level": item.get("price", ""),
            "hours": item.get("openingHours", []),
            "url": item.get("url", ""),
            "image_url": item.get("imageUrl", ""),
            "claimed": item.get("claimThisBusiness", False),
        }
        processed_places.append(place)

    # Sort by rating descending (places with reviews first)
    processed_places.sort(
        key=lambda x: (x["rating"] or 0, x["reviews_count"] or 0),
        reverse=True
    )

    return {
        "scraped_at": datetime.now().isoformat(),
        "platform": "google_maps",
        "mode": "search",
        "query": results.get("query", ""),
        "location": results.get("location", ""),
        "total_count": len(processed_places),
        "run_id": results.get("run_id", ""),
        "data": processed_places
    }


def process_place_results(results):
    """
    Process place details results.

    Args:
        results (dict): Raw results from Apify

    Returns:
        dict: Normalized data structure
    """
    processed_places = []

    for item in results["items"]:
        place = {
            "name": item.get("title", ""),
            "address": item.get("address", ""),
            "rating": item.get("totalScore"),
            "reviews_count": item.get("reviewsCount", 0),
            "phone": item.get("phone", ""),
            "website": item.get("website", ""),
            "place_id": item.get("placeId", ""),
            "coordinates": {
                "lat": item.get("location", {}).get("lat"),
                "lng": item.get("location", {}).get("lng")
            },
            "category": item.get("categoryName", ""),
            "categories": item.get("categories", []),
            "price_level": item.get("price", ""),
            "hours": item.get("openingHours", []),
            "url": item.get("url", ""),
            "image_url": item.get("imageUrl", ""),
            "images": item.get("imageUrls", []),
            "description": item.get("description", ""),
            "additional_info": item.get("additionalInfo", {}),
            "popular_times": item.get("popularTimesHistogram", {}),
            "reviews_distribution": item.get("reviewsDistribution", {}),
        }
        processed_places.append(place)

    return {
        "scraped_at": datetime.now().isoformat(),
        "platform": "google_maps",
        "mode": "place",
        "url": results.get("url", ""),
        "total_count": len(processed_places),
        "run_id": results.get("run_id", ""),
        "data": processed_places
    }


def process_review_results(results):
    """
    Process review results.

    Args:
        results (dict): Raw results from Apify

    Returns:
        dict: Normalized data structure
    """
    processed_reviews = []
    place_info = None

    for item in results["items"]:
        # Extract place info from first item
        if not place_info:
            place_info = {
                "name": item.get("title", ""),
                "address": item.get("address", ""),
                "rating": item.get("totalScore"),
                "reviews_count": item.get("reviewsCount", 0),
                "place_id": item.get("placeId", ""),
                "url": item.get("url", ""),
            }

        # Extract reviews
        reviews = item.get("reviews", [])
        for review in reviews:
            processed_review = {
                "review_id": review.get("reviewId", ""),
                "author": review.get("name", ""),
                "rating": review.get("stars"),
                "text": review.get("text", ""),
                "published_at": review.get("publishedAtDate", ""),
                "response_from_owner": review.get("responseFromOwnerText", ""),
                "likes_count": review.get("likesCount", 0),
                "review_url": review.get("reviewUrl", ""),
            }
            processed_reviews.append(processed_review)

    # Sort reviews by date (newest first)
    processed_reviews.sort(
        key=lambda x: x.get("published_at", ""),
        reverse=True
    )

    return {
        "scraped_at": datetime.now().isoformat(),
        "platform": "google_maps",
        "mode": "reviews",
        "url": results.get("url", ""),
        "place_info": place_info,
        "total_count": len(processed_reviews),
        "run_id": results.get("run_id", ""),
        "data": processed_reviews
    }


def save_results(data, filename=None):
    """
    Save results to .tmp directory.

    Args:
        data (dict): Processed data
        filename (str, optional): Custom filename

    Returns:
        Path: Output file path
    """
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Generate filename
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        mode = data.get("mode", "unknown")
        filename = f"google_maps_{mode}_{timestamp}.json"

    output_path = OUTPUT_DIR / filename

    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_path}")
    print(f"Total items: {data['total_count']}")

    # Print summary based on mode
    mode = data.get("mode", "")

    if mode == "search":
        print(f"\nTop 5 Places by Rating:")
        for i, place in enumerate(data['data'][:5], 1):
            rating = place.get('rating') or 'N/A'
            reviews = place.get('reviews_count') or 0
            print(f"\n{i}. {place['name']}")
            print(f"   Rating: {rating} ({reviews} reviews)")
            print(f"   Address: {place['address']}")
            if place.get('phone'):
                print(f"   Phone: {place['phone']}")
            if place.get('website'):
                print(f"   Website: {place['website']}")

    elif mode == "place":
        for place in data['data'][:1]:
            print(f"\nPlace Details:")
            print(f"   Name: {place['name']}")
            print(f"   Rating: {place.get('rating') or 'N/A'} ({place.get('reviews_count') or 0} reviews)")
            print(f"   Address: {place['address']}")
            print(f"   Category: {place.get('category', 'N/A')}")
            if place.get('phone'):
                print(f"   Phone: {place['phone']}")
            if place.get('website'):
                print(f"   Website: {place['website']}")
            if place.get('description'):
                print(f"   Description: {place['description'][:200]}...")

    elif mode == "reviews":
        place = data.get('place_info', {})
        print(f"\nReviews for: {place.get('name', 'Unknown')}")
        print(f"Overall Rating: {place.get('rating') or 'N/A'}")
        print(f"\nTop 3 Recent Reviews:")
        for i, review in enumerate(data['data'][:3], 1):
            print(f"\n{i}. {review.get('author', 'Anonymous')} - {review.get('rating', 'N/A')} stars")
            text = review.get('text', 'No text')
            print(f"   {text[:150]}{'...' if len(text) > 150 else ''}")
            if review.get('published_at'):
                print(f"   Posted: {review['published_at']}")

    return output_path


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Google Maps Scraper - Search businesses, get place details, and extract reviews"
    )

    subparsers = parser.add_subparsers(dest="mode", help="Scraping mode")

    # Search subcommand
    search_parser = subparsers.add_parser("search", help="Search for businesses")
    search_parser.add_argument("query", help="Search query (e.g., 'coffee shops', 'restaurants')")
    search_parser.add_argument("--location", help="Location to search in (e.g., 'San Francisco, CA')")
    search_parser.add_argument("--max-results", type=int, default=50, help="Maximum results (default: 50)")
    search_parser.add_argument("--min-rating", type=float, help="Minimum rating filter (1.0-5.0)")
    search_parser.add_argument("--language", default="en", help="Language code (default: en)")
    search_parser.add_argument("--zoom", type=int, default=14, help="Zoom level 10-21 (default: 14)")
    search_parser.add_argument("--output", help="Custom output filename")

    # Place subcommand
    place_parser = subparsers.add_parser("place", help="Get place details by URL")
    place_parser.add_argument("url", help="Google Maps place URL")
    place_parser.add_argument("--language", default="en", help="Language code (default: en)")
    place_parser.add_argument("--output", help="Custom output filename")

    # Reviews subcommand
    reviews_parser = subparsers.add_parser("reviews", help="Get reviews for a place")
    reviews_parser.add_argument("url", help="Google Maps place URL")
    reviews_parser.add_argument("--max-reviews", type=int, default=100, help="Maximum reviews (default: 100)")
    reviews_parser.add_argument("--language", default="en", help="Language code (default: en)")
    reviews_parser.add_argument("--sort-by", choices=["newest", "highest", "lowest", "relevant"],
                               default="newest", help="Sort order (default: newest)")
    reviews_parser.add_argument("--output", help="Custom output filename")

    args = parser.parse_args()

    if not args.mode:
        parser.print_help()
        return 1

    try:
        # Validate environment
        validate_environment()

        # Run appropriate scraper
        if args.mode == "search":
            results = scrape_search(
                query=args.query,
                location=args.location,
                max_results=args.max_results,
                min_rating=args.min_rating,
                language=args.language,
                zoom=args.zoom
            )

            if not results["success"]:
                print(f"Scraping failed: {results.get('error')}")
                return 1

            processed_data = process_search_results(results)

        elif args.mode == "place":
            results = scrape_place(
                place_url=args.url,
                language=args.language
            )

            if not results["success"]:
                print(f"Scraping failed: {results.get('error')}")
                return 1

            processed_data = process_place_results(results)

        elif args.mode == "reviews":
            results = scrape_reviews(
                place_url=args.url,
                max_reviews=args.max_reviews,
                language=args.language,
                sort_by=args.sort_by
            )

            if not results["success"]:
                print(f"Scraping failed: {results.get('error')}")
                return 1

            processed_data = process_review_results(results)

        # Save results
        save_results(processed_data, getattr(args, 'output', None))

        print("\nScraping completed successfully!")
        return 0

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
