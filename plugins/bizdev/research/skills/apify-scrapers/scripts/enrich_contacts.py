#!/usr/bin/env python3
"""
Contact Enrichment Scraper
Extracts contact information (emails, phones, social links) from websites using Apify.

Usage:
    # Enrich single website
    python enrich_contacts.py "https://example.com" --output contacts.json

    # Enrich multiple websites
    python enrich_contacts.py "https://site1.com" "https://site2.com" --output contacts.json

    # From file (one URL per line)
    python enrich_contacts.py --from-file urls.txt --output contacts.json

    # Limit pages crawled per site
    python enrich_contacts.py "https://example.com" --max-pages 10 --output contacts.json

    # Include social media links
    python enrich_contacts.py "https://example.com" --include-social --output contacts.json
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
ACTOR_ID = "vdrmota/contact-info-scraper"
OUTPUT_DIR = Path(__file__).parent.parent / ".tmp"


def validate_environment():
    """Validate required environment variables."""
    if not APIFY_TOKEN:
        raise ValueError(
            "APIFY_TOKEN not found in environment. "
            "Please add it to your .env file."
        )


def normalize_url(url: str) -> str:
    """
    Normalize a URL or domain to a full URL.

    Args:
        url: URL or domain string

    Returns:
        Normalized URL with protocol
    """
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    return url


def load_urls_from_file(filepath: str) -> list:
    """
    Load URLs from a file (one per line).

    Args:
        filepath: Path to file containing URLs

    Returns:
        List of normalized URLs
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"URL file not found: {filepath}")

    urls = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):  # Skip empty lines and comments
                urls.append(normalize_url(line))

    return urls


def run_contact_scraper(urls: list, max_pages: int = 5, include_social: bool = True):
    """
    Run the Contact Info Scraper Actor.

    Args:
        urls: List of website URLs to scrape
        max_pages: Maximum pages to crawl per site
        include_social: Whether to extract social media links

    Returns:
        dict: Scraper results with contact data
    """
    print(f"Starting contact enrichment for {len(urls)} website(s)")
    print(f"Max pages per site: {max_pages}")
    print(f"Include social links: {include_social}")

    # Initialize Apify client
    client = ApifyClient(APIFY_TOKEN)

    # Prepare Actor input
    # The contact-info-scraper expects startUrls as an array of objects
    start_urls = [{"url": url} for url in urls]

    run_input = {
        "startUrls": start_urls,
        "maxDepth": max_pages,
        "maxPagesPerStartUrl": max_pages,
        "sameDomain": True,  # Stay on the same domain
        "considerChildFrames": True,  # Check iframes too
    }

    print("Running Actor...")

    try:
        run = client.actor(ACTOR_ID).call(run_input=run_input)

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
            "count": len(dataset_items)
        }

    except Exception as e:
        print(f"Actor run failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "items": [],
            "count": 0
        }


def process_results(results: dict, include_social: bool = True) -> dict:
    """
    Process and structure the scraped contact results.

    Args:
        results: Raw results from Apify
        include_social: Whether to include social media links

    Returns:
        dict: Cleaned and structured contact data
    """
    processed_sites = []
    total_emails = 0
    total_phones = 0

    # Group results by domain/URL
    site_data = {}

    for item in results["items"]:
        url = item.get("url", "")

        # Extract domain for grouping
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        if domain not in site_data:
            site_data[domain] = {
                "url": domain,
                "emails": set(),
                "phones": set(),
                "social": {}
            }

        # Collect emails
        emails = item.get("emails", [])
        if emails:
            site_data[domain]["emails"].update(emails)

        # Collect phones
        phones = item.get("phones", [])
        if phones:
            site_data[domain]["phones"].update(phones)

        # Collect social links if requested
        if include_social:
            social = item.get("socialLinks", {})
            if social:
                for platform, link in social.items():
                    if link and platform not in site_data[domain]["social"]:
                        site_data[domain]["social"][platform] = link

    # Convert sets to lists and count totals
    for domain, data in site_data.items():
        emails_list = sorted(list(data["emails"]))
        phones_list = sorted(list(data["phones"]))

        processed_site = {
            "url": data["url"],
            "emails": emails_list,
            "phones": phones_list,
        }

        if include_social:
            processed_site["social"] = data["social"]

        processed_sites.append(processed_site)
        total_emails += len(emails_list)
        total_phones += len(phones_list)

    # Sort by URL for consistent output
    processed_sites.sort(key=lambda x: x["url"])

    print(f"Processed {len(processed_sites)} site(s)")
    print(f"Total emails found: {total_emails}")
    print(f"Total phones found: {total_phones}")

    return {
        "scraped_at": datetime.now().isoformat(),
        "platform": "contact_enrichment",
        "total_sites": len(processed_sites),
        "total_emails_found": total_emails,
        "total_phones_found": total_phones,
        "run_id": results.get("run_id", ""),
        "data": processed_sites
    }


def save_results(data: dict, filename: str = None) -> Path:
    """
    Save results to .tmp directory or specified path.

    Args:
        data: Processed contact data
        filename: Custom filename or path

    Returns:
        Path to saved file
    """
    # Determine output path
    if filename:
        output_path = Path(filename)
        # If it's a relative path without directory, put in .tmp
        if not output_path.is_absolute() and output_path.parent == Path('.'):
            OUTPUT_DIR.mkdir(exist_ok=True)
            output_path = OUTPUT_DIR / filename
        else:
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        OUTPUT_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"contacts_{timestamp}.json"

    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {output_path}")
    print(f"Total sites: {data['total_sites']}")
    print(f"Total emails: {data['total_emails_found']}")
    print(f"Total phones: {data['total_phones_found']}")

    # Print summary for each site
    print("\nContact Summary:")
    for site in data['data']:
        print(f"\n  {site['url']}")
        if site['emails']:
            print(f"    Emails: {', '.join(site['emails'][:3])}" +
                  (f" (+{len(site['emails'])-3} more)" if len(site['emails']) > 3 else ""))
        if site['phones']:
            print(f"    Phones: {', '.join(site['phones'][:3])}" +
                  (f" (+{len(site['phones'])-3} more)" if len(site['phones']) > 3 else ""))
        if site.get('social'):
            platforms = list(site['social'].keys())
            print(f"    Social: {', '.join(platforms)}")

    return output_path


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Extract contact information from websites using Apify"
    )
    parser.add_argument(
        "urls",
        nargs="*",
        help="Website URLs or domains to scrape"
    )
    parser.add_argument(
        "--from-file",
        dest="from_file",
        help="Load URLs from a file (one per line)"
    )
    parser.add_argument(
        "--output",
        help="Output filename (saved to .tmp/ directory)"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=5,
        dest="max_pages",
        help="Maximum pages to crawl per site (default: 5)"
    )
    parser.add_argument(
        "--include-social",
        action="store_true",
        dest="include_social",
        default=True,
        help="Include social media links (default: True)"
    )
    parser.add_argument(
        "--no-social",
        action="store_false",
        dest="include_social",
        help="Exclude social media links"
    )

    args = parser.parse_args()

    # Collect URLs
    urls = []

    if args.from_file:
        try:
            urls.extend(load_urls_from_file(args.from_file))
            print(f"Loaded {len(urls)} URL(s) from {args.from_file}")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            return 1

    if args.urls:
        urls.extend([normalize_url(u) for u in args.urls])

    if not urls:
        print("Error: No URLs provided. Use positional arguments or --from-file")
        parser.print_help()
        return 1

    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    urls = unique_urls

    print(f"Processing {len(urls)} unique URL(s)")

    try:
        # Validate environment
        validate_environment()

        # Run scraper
        results = run_contact_scraper(
            urls=urls,
            max_pages=args.max_pages,
            include_social=args.include_social
        )

        if not results["success"]:
            print(f"Scraping failed: {results.get('error')}")
            return 1

        # Process results
        processed_data = process_results(
            results,
            include_social=args.include_social
        )

        # Save results
        save_results(processed_data, args.output)

        print("\nContact enrichment completed successfully!")
        return 0

    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
