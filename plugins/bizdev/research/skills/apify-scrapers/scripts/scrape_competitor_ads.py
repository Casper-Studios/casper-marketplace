#!/usr/bin/env python3
"""
Competitor Ads Intelligence Scraper
Comprehensive competitor advertising analysis across Meta Ads Library and Google Ads Transparency.

Features:
- Multi-competitor analysis across Facebook/Meta and Google platforms
- Spend estimation and ranking
- Creative strategy analysis (format distribution)
- Messaging theme extraction
- Platform focus comparison
- Competitive benchmarking

Usage:
    # Single competitor
    python scrape_competitor_ads.py "Nike" --platforms facebook google --country US --days 30

    # Multiple competitors comparison
    python scrape_competitor_ads.py "Nike" "Adidas" "Puma" --compare --output comparison.json

    # Keyword-based discovery
    python scrape_competitor_ads.py --search "running shoes" --country US --max-ads 200
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict
from typing import Optional, List, Dict, Any
from apify_client import ApifyClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
OUTPUT_DIR = Path(__file__).parent.parent / ".tmp"

# Apify Actor IDs
ACTORS = {
    "facebook_ads": "apify/facebook-ads-scraper",
    "facebook_ads_alt": "curious_coder/facebook-ads-library-scraper",
    "google_ads": "lexis-solutions/google-ads-scraper",
    "google_ads_alt": "xtech/google-ad-transparency-scraper",
}

# Messaging themes for analysis
THEME_KEYWORDS = {
    "Performance/Speed": ["fast", "performance", "speed", "power", "quick", "efficient", "boost"],
    "Innovation/Technology": ["new", "technology", "innovation", "advanced", "cutting-edge", "smart", "ai"],
    "Lifestyle/Culture": ["style", "culture", "life", "everyday", "urban", "street", "lifestyle"],
    "Value/Savings": ["save", "discount", "deal", "offer", "affordable", "value", "cheap", "free"],
    "Quality/Premium": ["premium", "quality", "luxury", "exclusive", "best", "top", "elite"],
    "Sustainability": ["sustainable", "eco", "green", "environment", "recycle", "organic", "earth"],
    "Health/Wellness": ["health", "wellness", "fitness", "workout", "energy", "active", "strong"],
    "Community/Social": ["together", "community", "join", "share", "connect", "team", "family"],
    "Limited/Urgency": ["limited", "hurry", "now", "today", "exclusive", "last chance", "ending"],
    "Trust/Security": ["trust", "secure", "safe", "reliable", "proven", "certified", "guaranteed"],
}


def validate_environment():
    """Validate required environment variables."""
    if not APIFY_TOKEN:
        raise ValueError(
            "APIFY_TOKEN not found in environment. "
            "Please add it to your .env file."
        )


def scrape_facebook_ads(
    competitor: str,
    country: str = "US",
    days: int = 30,
    max_ads: int = 100,
    status: str = "active",
    media_types: Optional[List[str]] = None,
    is_search_mode: bool = False,
) -> Dict[str, Any]:
    """
    Scrape Facebook/Meta Ads Library for competitor ads.

    Args:
        competitor: Competitor name, page URL, or search keyword
        country: Target country ISO code
        days: Lookback period
        max_ads: Maximum ads to retrieve
        status: Ad status filter (active, inactive, all)
        media_types: Filter by media types
        is_search_mode: Whether this is keyword-based discovery

    Returns:
        dict: Scraped ads data with metadata
    """
    client = ApifyClient(APIFY_TOKEN)

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Build actor input
    run_input = {
        "country": country,
        "maxAds": max_ads,
        "proxyConfiguration": {"useApifyProxy": True},
    }

    # Set search type based on input
    if is_search_mode:
        run_input["searchQuery"] = competitor
        run_input["searchType"] = "keyword"
    elif competitor.startswith("http"):
        run_input["startUrls"] = [{"url": competitor}]
    else:
        # Assume it's a page name or advertiser name
        run_input["searchQuery"] = competitor
        run_input["searchType"] = "advertiser"

    # Add status filter
    if status != "all":
        run_input["adActiveStatus"] = status.upper()

    # Add media type filter if specified
    if media_types:
        run_input["mediaTypes"] = media_types

    print(f"Scraping Facebook ads for: {competitor}")
    print(f"  Country: {country}, Days: {days}, Max ads: {max_ads}")

    try:
        run = client.actor(ACTORS["facebook_ads"]).call(run_input=run_input)
        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        return {
            "success": True,
            "platform": "facebook",
            "competitor": competitor,
            "ads": dataset_items,
            "count": len(dataset_items),
            "scraped_at": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"  Warning: Facebook scraper failed, trying alternate actor...")

        # Try alternate actor
        try:
            run = client.actor(ACTORS["facebook_ads_alt"]).call(run_input=run_input)
            dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

            return {
                "success": True,
                "platform": "facebook",
                "competitor": competitor,
                "ads": dataset_items,
                "count": len(dataset_items),
                "scraped_at": datetime.now().isoformat(),
            }
        except Exception as e2:
            print(f"  Error: Both Facebook actors failed - {str(e2)}")
            return {
                "success": False,
                "platform": "facebook",
                "competitor": competitor,
                "ads": [],
                "count": 0,
                "error": str(e2),
            }


def scrape_google_ads(
    competitor: str,
    country: str = "US",
    max_ads: int = 100,
    is_search_mode: bool = False,
) -> Dict[str, Any]:
    """
    Scrape Google Ads Transparency Center for competitor ads.

    Args:
        competitor: Competitor domain or search keyword
        country: Target country ISO code
        max_ads: Maximum ads to retrieve
        is_search_mode: Whether this is keyword-based discovery

    Returns:
        dict: Scraped ads data with metadata
    """
    client = ApifyClient(APIFY_TOKEN)

    # Build actor input
    run_input = {
        "country": country,
        "maxResults": max_ads,
        "proxyConfiguration": {"useApifyProxy": True},
    }

    # Set search mode
    if is_search_mode:
        run_input["searchQuery"] = competitor
    else:
        # Extract domain if URL provided
        if competitor.startswith("http"):
            from urllib.parse import urlparse
            domain = urlparse(competitor).netloc
            run_input["advertiserDomain"] = domain
        elif "." in competitor:
            run_input["advertiserDomain"] = competitor
        else:
            run_input["searchQuery"] = competitor

    print(f"Scraping Google ads for: {competitor}")
    print(f"  Country: {country}, Max ads: {max_ads}")

    try:
        run = client.actor(ACTORS["google_ads"]).call(run_input=run_input)
        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        return {
            "success": True,
            "platform": "google",
            "competitor": competitor,
            "ads": dataset_items,
            "count": len(dataset_items),
            "scraped_at": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"  Warning: Google scraper failed, trying alternate actor...")

        # Try alternate actor
        try:
            run = client.actor(ACTORS["google_ads_alt"]).call(run_input=run_input)
            dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

            return {
                "success": True,
                "platform": "google",
                "competitor": competitor,
                "ads": dataset_items,
                "count": len(dataset_items),
                "scraped_at": datetime.now().isoformat(),
            }
        except Exception as e2:
            print(f"  Error: Both Google actors failed - {str(e2)}")
            return {
                "success": False,
                "platform": "google",
                "competitor": competitor,
                "ads": [],
                "count": 0,
                "error": str(e2),
            }


def process_facebook_ads(raw_ads: List[Dict]) -> Dict[str, Any]:
    """
    Process and enrich raw Facebook ads data.

    Args:
        raw_ads: Raw ads data from Apify

    Returns:
        dict: Processed ads with analytics
    """
    processed_ads = []
    spend_lower = 0
    spend_upper = 0
    reach_lower = 0
    reach_upper = 0

    platform_distribution = Counter()
    media_breakdown = Counter()
    status_count = Counter()

    for ad in raw_ads:
        # Extract spend estimates
        spend = ad.get("spend", {}) or ad.get("spendEstimate", {}) or {}
        ad_spend_lower = spend.get("lowerBound", 0) or spend.get("lower", 0) or 0
        ad_spend_upper = spend.get("upperBound", 0) or spend.get("upper", 0) or 0
        spend_lower += ad_spend_lower
        spend_upper += ad_spend_upper

        # Extract reach estimates
        reach = ad.get("reach", {}) or ad.get("impressions", {}) or {}
        ad_reach_lower = reach.get("lowerBound", 0) or reach.get("lower", 0) or 0
        ad_reach_upper = reach.get("upperBound", 0) or reach.get("upper", 0) or 0
        reach_lower += ad_reach_lower
        reach_upper += ad_reach_upper

        # Count platforms
        platforms = ad.get("platforms", []) or ad.get("publisherPlatforms", []) or []
        if isinstance(platforms, str):
            platforms = [platforms]
        for platform in platforms:
            platform_distribution[platform.lower()] += 1

        # Count media types
        media_type = (
            ad.get("mediaType", "") or
            ad.get("adFormat", "") or
            ad.get("creativeType", "") or
            "unknown"
        ).lower()
        if "video" in media_type:
            media_breakdown["video"] += 1
        elif "carousel" in media_type or "collection" in media_type:
            media_breakdown["carousel"] += 1
        elif "image" in media_type or "photo" in media_type:
            media_breakdown["image"] += 1
        else:
            media_breakdown["other"] += 1

        # Count status
        status = (ad.get("status", "") or ad.get("adActiveStatus", "") or "unknown").lower()
        status_count[status] += 1

        # Build processed ad
        processed_ad = {
            "id": ad.get("id", "") or ad.get("adId", ""),
            "status": status,
            "start_date": ad.get("startDate", "") or ad.get("adCreationTime", ""),
            "end_date": ad.get("endDate"),
            "creative": {
                "type": media_type,
                "headline": ad.get("adTitle", "") or ad.get("headline", ""),
                "body_text": ad.get("adBody", "") or ad.get("bodyText", "") or ad.get("text", ""),
                "call_to_action": ad.get("callToAction", "") or ad.get("cta", ""),
                "landing_url": ad.get("landingPageUrl", "") or ad.get("linkUrl", ""),
                "media_urls": ad.get("mediaUrls", []) or ad.get("images", []) or [],
            },
            "targeting": {
                "age_range": ad.get("ageRange", ""),
                "gender": ad.get("gender", "all"),
                "locations": ad.get("locations", []) or ad.get("regions", []),
            },
            "spend_estimate": {
                "lower_bound_usd": ad_spend_lower,
                "upper_bound_usd": ad_spend_upper,
            },
            "impressions_estimate": {
                "lower_bound": ad_reach_lower,
                "upper_bound": ad_reach_upper,
            },
        }
        processed_ads.append(processed_ad)

    return {
        "total_ads": len(processed_ads),
        "active_ads": status_count.get("active", 0),
        "inactive_ads": status_count.get("inactive", 0),
        "spend_estimate": {
            "lower_bound_usd": spend_lower,
            "upper_bound_usd": spend_upper,
            "midpoint_usd": (spend_lower + spend_upper) / 2,
            "currency": "USD",
        },
        "reach_estimate": {
            "lower_bound": reach_lower,
            "upper_bound": reach_upper,
        },
        "platform_distribution": dict(platform_distribution),
        "media_breakdown": dict(media_breakdown),
        "ads": processed_ads,
    }


def process_google_ads(raw_ads: List[Dict]) -> Dict[str, Any]:
    """
    Process and enrich raw Google ads data.

    Args:
        raw_ads: Raw ads data from Apify

    Returns:
        dict: Processed ads with analytics
    """
    processed_ads = []
    format_breakdown = Counter()
    regions_targeted = set()

    for ad in raw_ads:
        # Determine ad format
        ad_format = (
            ad.get("format", "") or
            ad.get("adFormat", "") or
            ad.get("type", "") or
            "unknown"
        ).lower()

        if "video" in ad_format or "youtube" in str(ad.get("placement", "")).lower():
            format_breakdown["video"] += 1
        elif "image" in ad_format or "display" in ad_format:
            format_breakdown["image"] += 1
        elif "text" in ad_format or "search" in ad_format:
            format_breakdown["text"] += 1
        else:
            format_breakdown["other"] += 1

        # Collect regions
        regions = ad.get("regions", []) or ad.get("targetedRegions", []) or []
        if isinstance(regions, str):
            regions = [regions]
        regions_targeted.update(regions)

        # Build processed ad
        processed_ad = {
            "id": ad.get("id", "") or ad.get("adId", ""),
            "format": ad_format,
            "advertiser": ad.get("advertiserName", "") or ad.get("advertiser", ""),
            "advertiser_id": ad.get("advertiserId", ""),
            "creative": {
                "headline": ad.get("headline", "") or ad.get("title", ""),
                "description": ad.get("description", "") or ad.get("bodyText", ""),
                "landing_url": ad.get("landingPage", "") or ad.get("finalUrl", ""),
                "media_url": ad.get("imageUrl", "") or ad.get("mediaUrl", ""),
            },
            "targeting": {
                "regions": regions,
            },
            "first_shown": ad.get("firstShown", "") or ad.get("startDate", ""),
            "last_shown": ad.get("lastShown", "") or ad.get("endDate", ""),
        }
        processed_ads.append(processed_ad)

    return {
        "total_ads": len(processed_ads),
        "formats": dict(format_breakdown),
        "regions_targeted": list(regions_targeted),
        "ads": processed_ads,
    }


def extract_messaging_themes(ads_data: List[Dict]) -> List[Dict[str, Any]]:
    """
    Extract messaging themes from ad copy using keyword analysis.

    Args:
        ads_data: List of processed ads

    Returns:
        list: Top messaging themes with frequency and keywords
    """
    theme_counts = Counter()
    theme_keywords_found = defaultdict(set)

    for ad in ads_data:
        # Combine all text fields
        text_fields = [
            ad.get("creative", {}).get("headline", ""),
            ad.get("creative", {}).get("body_text", ""),
            ad.get("creative", {}).get("description", ""),
            ad.get("creative", {}).get("call_to_action", ""),
        ]
        combined_text = " ".join(str(f) for f in text_fields if f).lower()

        # Check each theme
        for theme, keywords in THEME_KEYWORDS.items():
            for keyword in keywords:
                if keyword in combined_text:
                    theme_counts[theme] += 1
                    theme_keywords_found[theme].add(keyword)

    # Build result sorted by frequency
    themes = []
    for theme, count in theme_counts.most_common(10):
        themes.append({
            "theme": theme,
            "frequency": count,
            "keywords": list(theme_keywords_found[theme])[:5],
        })

    return themes


def extract_call_to_actions(ads_data: List[Dict]) -> List[Dict[str, Any]]:
    """
    Extract and count call-to-action buttons from ads.

    Args:
        ads_data: List of processed ads

    Returns:
        list: Top CTAs with counts
    """
    cta_counts = Counter()

    for ad in ads_data:
        cta = ad.get("creative", {}).get("call_to_action", "")
        if cta:
            # Normalize CTA text
            cta_normalized = cta.strip().title()
            cta_counts[cta_normalized] += 1

    return [
        {"cta": cta, "count": count}
        for cta, count in cta_counts.most_common(10)
    ]


def generate_summary(competitors_data: List[Dict]) -> Dict[str, Any]:
    """
    Generate aggregate summary statistics across all competitors.

    Args:
        competitors_data: List of competitor analysis results

    Returns:
        dict: Summary statistics
    """
    total_ads = 0
    total_spend_lower = 0
    total_spend_upper = 0

    all_ads = []
    platform_totals = Counter()
    creative_totals = Counter()
    status_totals = Counter()

    for comp in competitors_data:
        for platform, platform_data in comp.get("platforms", {}).items():
            ads = platform_data.get("ads", [])
            all_ads.extend(ads)
            total_ads += platform_data.get("total_ads", 0)

            if platform == "facebook":
                spend = platform_data.get("spend_estimate", {})
                total_spend_lower += spend.get("lower_bound_usd", 0)
                total_spend_upper += spend.get("upper_bound_usd", 0)

                # Aggregate platform distribution
                for plat, count in platform_data.get("platform_distribution", {}).items():
                    platform_totals[plat] += count

                # Aggregate media breakdown
                for media, count in platform_data.get("media_breakdown", {}).items():
                    creative_totals[media] += count

                status_totals["active"] += platform_data.get("active_ads", 0)
                status_totals["inactive"] += platform_data.get("inactive_ads", 0)

            elif platform == "google":
                for fmt, count in platform_data.get("formats", {}).items():
                    creative_totals[fmt] += count
                    platform_totals[f"google_{fmt}"] += count

    # Extract themes and CTAs from all ads
    top_themes = extract_messaging_themes(all_ads)
    top_ctas = extract_call_to_actions(all_ads)

    # Calculate average ad duration (if dates available)
    total_duration_days = 0
    ads_with_duration = 0
    for ad in all_ads:
        start = ad.get("start_date") or ad.get("first_shown")
        end = ad.get("end_date") or ad.get("last_shown")
        if start and end:
            try:
                start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
                duration = (end_dt - start_dt).days
                if duration > 0:
                    total_duration_days += duration
                    ads_with_duration += 1
            except (ValueError, TypeError):
                pass

    avg_duration = total_duration_days / ads_with_duration if ads_with_duration > 0 else None

    return {
        "total_ads_analyzed": total_ads,
        "total_competitors": len(competitors_data),
        "total_spend_estimate": {
            "lower_bound_usd": total_spend_lower,
            "upper_bound_usd": total_spend_upper,
            "midpoint_usd": (total_spend_lower + total_spend_upper) / 2,
        },
        "platform_distribution": dict(platform_totals),
        "creative_breakdown": dict(creative_totals),
        "status_breakdown": dict(status_totals),
        "top_messaging_themes": top_themes,
        "top_call_to_actions": top_ctas,
        "avg_ad_duration_days": avg_duration,
        "ads_per_competitor_avg": total_ads / len(competitors_data) if competitors_data else 0,
    }


def generate_comparison(competitors_data: List[Dict]) -> Dict[str, Any]:
    """
    Generate competitive comparison metrics.

    Args:
        competitors_data: List of competitor analysis results

    Returns:
        dict: Comparison metrics and rankings
    """
    if len(competitors_data) < 2:
        return {}

    # Spend ranking
    spend_data = []
    for comp in competitors_data:
        fb_data = comp.get("platforms", {}).get("facebook", {})
        spend = fb_data.get("spend_estimate", {})
        midpoint = spend.get("midpoint_usd", 0)
        spend_data.append({
            "competitor": comp["name"],
            "spend_estimate_mid": midpoint,
        })

    spend_data.sort(key=lambda x: x["spend_estimate_mid"], reverse=True)
    for i, item in enumerate(spend_data, 1):
        item["rank"] = i

    # Activity ranking
    activity_data = []
    for comp in competitors_data:
        total_ads = 0
        active_ads = 0
        for platform_data in comp.get("platforms", {}).values():
            total_ads += platform_data.get("total_ads", 0)
            active_ads += platform_data.get("active_ads", 0)

        active_rate = active_ads / total_ads if total_ads > 0 else 0
        activity_data.append({
            "competitor": comp["name"],
            "total_ads": total_ads,
            "active_rate": round(active_rate, 2),
        })

    activity_data.sort(key=lambda x: x["total_ads"], reverse=True)
    for i, item in enumerate(activity_data, 1):
        item["rank"] = i

    # Platform focus analysis
    platform_focus = {}
    for comp in competitors_data:
        fb_data = comp.get("platforms", {}).get("facebook", {})
        platform_dist = fb_data.get("platform_distribution", {})
        total = sum(platform_dist.values()) or 1

        # Find primary and secondary platforms
        sorted_platforms = sorted(platform_dist.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_platforms[0][0] if sorted_platforms else "unknown"
        secondary = sorted_platforms[1][0] if len(sorted_platforms) > 1 else "none"
        primary_pct = sorted_platforms[0][1] / total if sorted_platforms else 0

        platform_focus[comp["name"]] = {
            "primary": primary,
            "secondary": secondary,
            f"{primary}_pct": round(primary_pct, 2),
        }

    # Creative strategy analysis
    creative_strategy = {}
    for comp in competitors_data:
        fb_data = comp.get("platforms", {}).get("facebook", {})
        media_breakdown = fb_data.get("media_breakdown", {})
        total = sum(media_breakdown.values()) or 1

        # Find primary format
        sorted_formats = sorted(media_breakdown.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_formats[0][0] if sorted_formats else "unknown"
        primary_pct = sorted_formats[0][1] / total if sorted_formats else 0

        creative_strategy[comp["name"]] = {
            "primary_format": primary,
            f"{primary}_pct": round(primary_pct, 2),
        }

    # Messaging overlap analysis
    competitor_themes = {}
    for comp in competitors_data:
        all_ads = []
        for platform_data in comp.get("platforms", {}).values():
            all_ads.extend(platform_data.get("ads", []))
        themes = extract_messaging_themes(all_ads)
        competitor_themes[comp["name"]] = set(t["theme"] for t in themes[:5])

    # Find shared and unique themes
    all_themes = set()
    for themes in competitor_themes.values():
        all_themes.update(themes)

    shared_themes = set(all_themes)
    for themes in competitor_themes.values():
        shared_themes &= themes

    messaging_overlap = {
        "shared_themes": list(shared_themes),
    }
    for name, themes in competitor_themes.items():
        unique = themes - shared_themes
        messaging_overlap[f"unique_to_{name.lower().replace(' ', '_')}"] = list(unique)

    return {
        "spend_ranking": spend_data,
        "activity_ranking": activity_data,
        "platform_focus": platform_focus,
        "creative_strategy": creative_strategy,
        "messaging_overlap": messaging_overlap,
    }


def save_results(data: Dict, filename: Optional[str] = None) -> Path:
    """
    Save results to .tmp directory.

    Args:
        data: Data to save
        filename: Optional custom filename

    Returns:
        Path: Path to saved file
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"competitor_ads_{timestamp}.json"

    if not filename.endswith(".json"):
        filename += ".json"

    output_path = OUTPUT_DIR / filename

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nResults saved to: {output_path}")
    return output_path


def print_summary(data: Dict):
    """Print a formatted summary to console."""
    summary = data.get("summary", {})
    comparison = data.get("comparison", {})

    print("\n" + "=" * 60)
    print("COMPETITOR ADS ANALYSIS COMPLETE")
    print("=" * 60)

    print(f"\nTotal Ads Analyzed: {summary.get('total_ads_analyzed', 0)}")
    print(f"Competitors: {summary.get('total_competitors', 0)}")

    # Spend estimate
    spend = summary.get("total_spend_estimate", {})
    if spend.get("midpoint_usd", 0) > 0:
        lower = spend.get("lower_bound_usd", 0)
        upper = spend.get("upper_bound_usd", 0)
        print(f"\nTotal Estimated Spend: ${lower:,.0f} - ${upper:,.0f}")

    # Spend ranking
    if comparison.get("spend_ranking"):
        print("\nSpend Ranking:")
        for item in comparison["spend_ranking"][:5]:
            mid = item.get("spend_estimate_mid", 0)
            print(f"  {item['rank']}. {item['competitor']} - ${mid:,.0f} (est. midpoint)")

    # Creative breakdown
    creative = summary.get("creative_breakdown", {})
    if creative:
        total = sum(creative.values())
        print("\nTop Creative Formats:")
        sorted_creative = sorted(creative.items(), key=lambda x: x[1], reverse=True)
        for fmt, count in sorted_creative[:5]:
            pct = (count / total * 100) if total > 0 else 0
            print(f"  - {fmt.title()}: {pct:.1f}%")

    # Top themes
    themes = summary.get("top_messaging_themes", [])
    if themes:
        print("\nTop Messaging Themes:")
        for theme in themes[:5]:
            print(f"  - {theme['theme']}: {theme['frequency']} mentions")

    print("\n" + "=" * 60)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Competitor Ads Intelligence Scraper - Analyze competitor advertising across platforms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Single competitor analysis
    python scrape_competitor_ads.py "Nike" --platforms facebook google --country US --days 30

    # Multiple competitors with comparison
    python scrape_competitor_ads.py "Nike" "Adidas" "Puma" --compare --output comparison.json

    # Keyword-based discovery
    python scrape_competitor_ads.py --search "running shoes" --country US --max-ads 200

    # Filter by media type
    python scrape_competitor_ads.py "Netflix" --platforms facebook --media-types video --days 7
        """
    )

    # Positional arguments (competitors)
    parser.add_argument(
        "competitors",
        nargs="*",
        help="Competitor names, domains, or page URLs to analyze"
    )

    # Search mode
    parser.add_argument(
        "--search",
        type=str,
        help="Keyword-based discovery mode (instead of specific competitors)"
    )

    # Platform options
    parser.add_argument(
        "--platforms",
        nargs="+",
        default=["facebook"],
        choices=["facebook", "google"],
        help="Platforms to scrape (default: facebook)"
    )

    # Filtering options
    parser.add_argument(
        "--country",
        type=str,
        default="US",
        help="Target country ISO code (default: US)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Lookback period in days (default: 30)"
    )
    parser.add_argument(
        "--max-ads",
        type=int,
        default=100,
        help="Maximum ads per competitor (default: 100)"
    )
    parser.add_argument(
        "--status",
        type=str,
        default="active",
        choices=["active", "inactive", "all"],
        help="Ad status filter (default: active)"
    )
    parser.add_argument(
        "--media-types",
        nargs="+",
        choices=["image", "video", "carousel", "text"],
        help="Filter by media types"
    )

    # Output options
    parser.add_argument(
        "--output",
        type=str,
        help="Output filename (default: auto-generated)"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Enable comparison mode for multiple competitors"
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.competitors and not args.search:
        parser.print_help()
        print("\nError: Provide competitor names or use --search for keyword discovery")
        return 1

    try:
        validate_environment()

        # Build competitor list
        if args.search:
            competitors = [args.search]
            is_search_mode = True
        else:
            competitors = args.competitors
            is_search_mode = False

        # Scrape data for each competitor
        competitors_data = []

        for competitor in competitors:
            print(f"\n{'='*50}")
            print(f"Analyzing: {competitor}")
            print(f"{'='*50}")

            competitor_result = {
                "name": competitor,
                "identifier": competitor.lower().replace(" ", "_"),
                "platforms": {},
            }

            # Scrape Facebook if requested
            if "facebook" in args.platforms:
                fb_result = scrape_facebook_ads(
                    competitor=competitor,
                    country=args.country,
                    days=args.days,
                    max_ads=args.max_ads,
                    status=args.status,
                    media_types=args.media_types,
                    is_search_mode=is_search_mode,
                )

                if fb_result["success"] and fb_result["ads"]:
                    processed = process_facebook_ads(fb_result["ads"])
                    competitor_result["platforms"]["facebook"] = processed
                    print(f"  Facebook: {processed['total_ads']} ads found")
                else:
                    print(f"  Facebook: No ads found or scraper failed")

            # Scrape Google if requested
            if "google" in args.platforms:
                google_result = scrape_google_ads(
                    competitor=competitor,
                    country=args.country,
                    max_ads=args.max_ads,
                    is_search_mode=is_search_mode,
                )

                if google_result["success"] and google_result["ads"]:
                    processed = process_google_ads(google_result["ads"])
                    competitor_result["platforms"]["google"] = processed
                    print(f"  Google: {processed['total_ads']} ads found")
                else:
                    print(f"  Google: No ads found or scraper failed")

            competitors_data.append(competitor_result)

        # Build final output
        output = {
            "metadata": {
                "scraped_at": datetime.now().isoformat(),
                "competitors_analyzed": competitors,
                "platforms": args.platforms,
                "country": args.country,
                "date_range": {
                    "start": (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d"),
                    "end": datetime.now().strftime("%Y-%m-%d"),
                },
                "filters_applied": {
                    "status": args.status,
                    "media_types": args.media_types or "all",
                    "max_ads_per_competitor": args.max_ads,
                },
            },
            "competitors": competitors_data,
            "summary": generate_summary(competitors_data),
        }

        # Add comparison if requested and multiple competitors
        if args.compare and len(competitors_data) >= 2:
            output["comparison"] = generate_comparison(competitors_data)

        # Save results
        save_results(output, args.output)

        # Print summary
        print_summary(output)

        return 0

    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
