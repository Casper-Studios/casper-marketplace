#!/usr/bin/env python3
"""
Firecrawl Page Scraper
Scrape individual web pages using Firecrawl API.

See directives/firecrawl_scrape.md for full documentation.

Usage:
    # Simple scrape
    python execution/firecrawl_scrape.py https://example.com/article

    # With options
    python execution/firecrawl_scrape.py https://wsj.com/article --proxy stealth --timeout 60000

    # Get summary too
    python execution/firecrawl_scrape.py https://example.com --formats markdown,summary

    # Output to file
    python execution/firecrawl_scrape.py https://example.com --output .tmp/scraped.json
"""

import os
import sys
import json
import argparse
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment
load_dotenv()


def scrape_page(
    url: str,
    formats: List[str] = None,
    only_main_content: bool = True,
    timeout: int = 30000,
    wait_for: int = 0,
    mobile: bool = False,
    proxy: str = "auto",
    headers: Dict[str, str] = None,
    actions: List[Dict] = None,
    max_retries: int = 2
) -> Dict[str, Any]:
    """
    Scrape a single page using Firecrawl.

    Args:
        url: URL to scrape
        formats: Output formats (markdown, html, rawHtml, summary, screenshot, links, json)
        only_main_content: Extract only main content
        timeout: Timeout in milliseconds
        wait_for: Wait before scraping (ms)
        mobile: Emulate mobile device
        proxy: Proxy mode (basic, stealth, auto)
        headers: Custom HTTP headers
        actions: Browser actions (click, wait, etc.)
        max_retries: Number of retry attempts

    Returns:
        Dict with scraped content and metadata
    """
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY environment variable not set")

    # Default formats
    if formats is None:
        formats = ["markdown"]

    # Try to use the SDK first, fall back to requests
    try:
        from firecrawl import Firecrawl
        use_sdk = True
    except ImportError:
        use_sdk = False

    for attempt in range(max_retries + 1):
        try:
            if use_sdk:
                result = _scrape_with_sdk(
                    api_key, url, formats, only_main_content, timeout,
                    wait_for, mobile, proxy, headers, actions
                )
            else:
                result = _scrape_with_requests(
                    api_key, url, formats, only_main_content, timeout,
                    wait_for, mobile, proxy, headers, actions
                )

            return result

        except Exception as e:
            error_msg = str(e)

            # Check for rate limiting
            if "429" in error_msg or "rate" in error_msg.lower():
                wait_time = (attempt + 1) * 5
                print(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue

            # Check for server errors
            if "500" in error_msg or "502" in error_msg or "503" in error_msg:
                wait_time = (attempt + 1) * 2
                print(f"Server error, retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue

            # For other errors on last attempt, raise
            if attempt == max_retries:
                raise

            time.sleep(1)

    raise Exception(f"Failed to scrape {url} after {max_retries + 1} attempts")


def _scrape_with_sdk(
    api_key: str,
    url: str,
    formats: List[str],
    only_main_content: bool,
    timeout: int,
    wait_for: int,
    mobile: bool,
    proxy: str,
    headers: Dict[str, str],
    actions: List[Dict]
) -> Dict[str, Any]:
    """Scrape using the Firecrawl Python SDK."""
    from firecrawl import Firecrawl

    client = Firecrawl(api_key=api_key)

    # Build kwargs
    kwargs = {
        "formats": formats,
        "only_main_content": only_main_content,
        "timeout": timeout,
        "mobile": mobile,
        "proxy": proxy
    }

    if wait_for > 0:
        kwargs["wait_for"] = wait_for

    if headers:
        kwargs["headers"] = headers

    if actions:
        kwargs["actions"] = actions

    # Make request
    response = client.scrape(url, **kwargs)

    # SDK returns a Document object, convert to dict
    if hasattr(response, 'markdown'):
        # It's a Document object
        data = {
            "markdown": response.markdown or "",
            "html": getattr(response, 'html', None),
            "rawHtml": getattr(response, 'rawHtml', None),
            "summary": getattr(response, 'summary', None),
            "screenshot": getattr(response, 'screenshot', None),
            "links": getattr(response, 'links', []),
            "metadata": {}
        }
        # Extract metadata if available
        if hasattr(response, 'metadata') and response.metadata:
            meta = response.metadata
            data["metadata"] = {
                "title": getattr(meta, 'title', None),
                "description": getattr(meta, 'description', None),
                "language": getattr(meta, 'language', None),
                "sourceURL": getattr(meta, 'sourceURL', url),
                "statusCode": getattr(meta, 'statusCode', 200),
                "ogImage": getattr(meta, 'ogImage', None),
                "ogTitle": getattr(meta, 'ogTitle', None),
            }
    elif isinstance(response, dict):
        data = response
    else:
        data = {}

    # Normalize response
    return _normalize_response(url, data)


def _scrape_with_requests(
    api_key: str,
    url: str,
    formats: List[str],
    only_main_content: bool,
    timeout: int,
    wait_for: int,
    mobile: bool,
    proxy: str,
    headers: Dict[str, str],
    actions: List[Dict]
) -> Dict[str, Any]:
    """Scrape using direct API requests (fallback)."""
    import requests

    api_url = "https://api.firecrawl.dev/v2/scrape"

    # Build request body
    body = {
        "url": url,
        "formats": formats,
        "onlyMainContent": only_main_content,
        "timeout": timeout,
        "mobile": mobile,
        "proxy": proxy
    }

    if wait_for > 0:
        body["waitFor"] = wait_for

    if headers:
        body["headers"] = headers

    if actions:
        body["actions"] = actions

    # Make request
    response = requests.post(
        api_url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json=body,
        timeout=timeout / 1000 + 30  # Convert to seconds + buffer
    )

    # Handle errors
    if response.status_code != 200:
        error_detail = response.text
        try:
            error_json = response.json()
            error_detail = error_json.get("error", error_json.get("message", error_detail))
        except:
            pass
        raise Exception(f"Firecrawl API error ({response.status_code}): {error_detail}")

    data = response.json()

    if not data.get("success"):
        raise Exception(f"Firecrawl scrape failed: {data.get('error', 'Unknown error')}")

    return _normalize_response(url, data.get("data", {}))


def _normalize_response(url: str, data: Dict) -> Dict[str, Any]:
    """Normalize response to consistent format."""
    metadata = data.get("metadata", {})

    return {
        "success": True,
        "url": url,
        "title": metadata.get("title", ""),
        "description": metadata.get("description", ""),
        "markdown": data.get("markdown", ""),
        "html": data.get("html"),
        "raw_html": data.get("rawHtml"),
        "summary": data.get("summary"),
        "screenshot": data.get("screenshot"),
        "links": data.get("links", []),
        "metadata": {
            "title": metadata.get("title"),
            "description": metadata.get("description"),
            "language": metadata.get("language"),
            "source_url": metadata.get("sourceURL", url),
            "status_code": metadata.get("statusCode", 200),
            "og_image": metadata.get("ogImage"),
            "og_title": metadata.get("ogTitle")
        },
        "scraped_at": datetime.now().isoformat(),
        "source": "firecrawl"
    }


def scrape_batch(
    urls: List[str],
    formats: List[str] = None,
    only_main_content: bool = True,
    timeout: int = 30000,
    proxy: str = "auto",
    delay_between: float = 0.5
) -> List[Dict[str, Any]]:
    """
    Scrape multiple URLs sequentially.

    For large batches, consider using Firecrawl's native batch API.

    Args:
        urls: List of URLs to scrape
        formats: Output formats
        only_main_content: Extract main content only
        timeout: Timeout per page (ms)
        proxy: Proxy mode
        delay_between: Delay between requests (seconds)

    Returns:
        List of scrape results
    """
    results = []

    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Scraping: {url[:60]}...")

        try:
            result = scrape_page(
                url=url,
                formats=formats,
                only_main_content=only_main_content,
                timeout=timeout,
                proxy=proxy
            )
            results.append(result)
            print(f"   ✅ Success: {len(result.get('markdown', ''))} chars")

        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")
            results.append({
                "success": False,
                "url": url,
                "error": str(e),
                "scraped_at": datetime.now().isoformat(),
                "source": "firecrawl"
            })

        # Delay between requests
        if i < len(urls) and delay_between > 0:
            time.sleep(delay_between)

    return results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Scrape web pages using Firecrawl"
    )

    parser.add_argument(
        "url",
        help="URL to scrape"
    )
    parser.add_argument(
        "--formats",
        default="markdown",
        help="Comma-separated output formats (markdown,html,summary,links,screenshot)"
    )
    parser.add_argument(
        "--full-page",
        action="store_true",
        help="Include headers, nav, footer (disable only_main_content)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30000,
        help="Timeout in milliseconds (default: 30000)"
    )
    parser.add_argument(
        "--wait-for",
        type=int,
        default=0,
        help="Wait time before scraping (ms) for JS to load"
    )
    parser.add_argument(
        "--mobile",
        action="store_true",
        help="Emulate mobile device"
    )
    parser.add_argument(
        "--proxy",
        choices=["basic", "stealth", "auto"],
        default="auto",
        help="Proxy mode (default: auto)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout as JSON)"
    )
    parser.add_argument(
        "--markdown-only",
        action="store_true",
        help="Output only markdown content (no JSON wrapper)"
    )

    args = parser.parse_args()

    # Parse formats
    formats = [f.strip() for f in args.formats.split(",")]

    try:
        # Scrape
        result = scrape_page(
            url=args.url,
            formats=formats,
            only_main_content=not args.full_page,
            timeout=args.timeout,
            wait_for=args.wait_for,
            mobile=args.mobile,
            proxy=args.proxy
        )

        # Output
        if args.markdown_only:
            output = result.get("markdown", "")
        else:
            output = json.dumps(result, indent=2, ensure_ascii=False)

        if args.output:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"✅ Saved to {args.output}")
        else:
            print(output)

        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    exit(main())
