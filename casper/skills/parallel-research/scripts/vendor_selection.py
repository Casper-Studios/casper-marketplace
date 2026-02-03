#!/usr/bin/env python3
"""
Vendor Selection & Comparison
Research, compare, and recommend software vendors using deep research and site scraping.

See directives/vendor_selection.md for full documentation.

Usage:
    python execution/vendor_selection.py --spec requirements.yaml
    python execution/vendor_selection.py --spec requirements.yaml --quick
    python execution/vendor_selection.py --spec requirements.yaml --thorough
"""

import os
import sys
import json
import argparse
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dotenv import load_dotenv

# Add execution directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from parallel_research import chat_with_web, deep_research, validate_api_key
from firecrawl_scrape import scrape_page
from md_to_pdf import convert_md_to_pdf

import yaml

# Load environment
load_dotenv()

# Output directories
OUTPUT_DIR = Path(".tmp/vendor_selection")
REPORTS_DIR = OUTPUT_DIR / "reports"
DATA_DIR = OUTPUT_DIR / "data"

for dir_path in [REPORTS_DIR, DATA_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Fixed scoring weights (from directive)
SCORING_WEIGHTS = {
    "core_features": 0.25,
    "integration_ecosystem": 0.25,
    "pricing_fit": 0.20,
    "reviews": 0.15,
    "compliance": 0.10,
    "support_reliability": 0.05
}


def load_requirements(spec_path: str) -> Dict:
    """Load requirements from YAML spec file."""
    with open(spec_path, 'r') as f:
        spec = yaml.safe_load(f)

    # Validate required fields
    required = ["category", "requirements"]
    for field in required:
        if field not in spec:
            raise ValueError(f"Missing required field: {field}")

    return spec


def discover_vendors(spec: Dict, vendor_limit: int = 10) -> List[Dict]:
    """
    Stage 1: Discover vendors via Chat with Web.

    Returns list of {"name": str, "website": str, "description": str}
    """
    print("\n" + "="*60)
    print("STAGE 1: VENDOR DISCOVERY")
    print("="*60)

    category = spec["category"]
    use_case = spec.get("use_case", "")
    excluded = spec.get("exclude_vendors", [])

    # Build discovery query
    exclude_text = f"\nDo NOT include these vendors: {', '.join(excluded)}" if excluded else ""

    query = f"""List the top {vendor_limit + 3} {category} vendors suitable for this use case: {use_case}

Include:
- Market leaders (top 3-4 well-known solutions)
- Mid-market options (3-4 solid alternatives)
- Emerging/niche players (2-3 newer or specialized options)

For each vendor, provide EXACTLY this format (one per line):
VENDOR: [Name] | WEBSITE: [full URL] | DESCRIPTION: [one sentence]
{exclude_text}

Only include vendors that actually exist and are relevant to {category}."""

    result = chat_with_web(query)
    answer = result["answer"]

    # Parse vendors from response
    vendors = []
    lines = answer.split("\n")

    for line in lines:
        if "VENDOR:" in line and "WEBSITE:" in line:
            try:
                # Parse the structured format
                parts = line.split("|")
                name_part = [p for p in parts if "VENDOR:" in p][0]
                website_part = [p for p in parts if "WEBSITE:" in p][0]
                desc_part = [p for p in parts if "DESCRIPTION:" in p][0] if any("DESCRIPTION:" in p for p in parts) else ""

                name = name_part.split("VENDOR:")[1].strip().strip("*").strip()
                website = website_part.split("WEBSITE:")[1].strip()
                description = desc_part.split("DESCRIPTION:")[1].strip() if desc_part else ""

                # Clean up website URL
                website = website.split()[0]  # Take first word only
                if not website.startswith("http"):
                    website = "https://" + website

                # Skip excluded vendors
                if any(ex.lower() in name.lower() for ex in excluded):
                    continue

                vendors.append({
                    "name": name,
                    "website": website,
                    "description": description
                })
            except (IndexError, ValueError):
                continue

    # Also try to parse simpler formats
    if len(vendors) < 5:
        # Try numbered list format
        pattern = r'\d+\.\s*\*?\*?([^*\n:]+)\*?\*?\s*[-–:]?\s*(https?://[^\s\)]+)?'
        matches = re.findall(pattern, answer)
        for name, url in matches:
            name = name.strip().strip("*").strip()
            if name and len(name) < 50:
                # Skip if already found or excluded
                if any(v["name"].lower() == name.lower() for v in vendors):
                    continue
                if any(ex.lower() in name.lower() for ex in excluded):
                    continue

                vendors.append({
                    "name": name,
                    "website": url.strip() if url else "",
                    "description": ""
                })

    # Limit to requested count
    vendors = vendors[:vendor_limit]

    print(f"\n✅ Discovered {len(vendors)} vendors:")
    for v in vendors:
        print(f"   • {v['name']} - {v['website']}")

    return vendors


def research_vendor(vendor: Dict, spec: Dict) -> Dict:
    """
    Stage 2: Deep research a single vendor using Parallel AI ultra processor.

    Returns comprehensive vendor data.
    """
    name = vendor["name"]
    category = spec["category"]
    requirements = spec.get("requirements", [])
    integrations = spec.get("integrations", {})
    compliance_req = spec.get("compliance", {})
    budget = spec.get("budget", {})

    print(f"\n🔬 Researching: {name}")

    # Build comprehensive research objective
    requirements_text = "\n".join(f"   - {r}" for r in requirements)
    integrations_text = ", ".join(integrations.get("must_integrate_with", []))
    compliance_text = ", ".join(compliance_req.get("required", []))
    budget_text = budget.get("monthly_range", "Not specified")

    objective = f"""Comprehensive analysis of {name} as a {category} solution.

RESEARCH THESE SPECIFIC AREAS:

1. PRICING (Critical):
   - List ALL pricing tiers with exact monthly/annual costs
   - Note what's included in each tier
   - Free tier availability and limits
   - Per-seat vs usage-based pricing model
   - Any volume discounts or annual savings
   - Enterprise/custom pricing details

2. CORE FEATURES:
   - Full feature list organized by tier
   - Evaluate against these specific requirements:
{requirements_text}
   - For each requirement, note if it's ✅ Fully supported, ⚠️ Partially supported, or ❌ Not available

3. INTEGRATIONS:
   - Total number of native integrations
   - Specifically check for: {integrations_text}
   - API capabilities (REST, GraphQL, webhooks)
   - API rate limits and documentation quality
   - Zapier/Make/n8n support (number of triggers/actions)
   - SDKs available (Python, JavaScript, etc.)

4. REVIEWS & REPUTATION:
   - G2 rating and review count
   - Capterra rating and review count
   - TrustRadius score and review count
   - Common praise themes (what users love)
   - Common complaints (what users dislike)

5. COMPLIANCE & SECURITY:
   - Check for: {compliance_text}
   - Also check: SOC 2 Type II, GDPR, HIPAA, ISO 27001
   - Data residency options (US, EU, etc.)
   - Security certifications page URL

6. COMPANY INFO:
   - Founded year
   - Headquarters location
   - Funding/company size
   - Target market (SMB, Mid-market, Enterprise)

Provide specific numbers, prices, and facts. Cite sources for key claims."""

    try:
        result = deep_research(objective, processor="ultra")

        return {
            "name": name,
            "website": vendor.get("website", ""),
            "description": vendor.get("description", ""),
            "research_content": result.get("content", ""),
            "citations": result.get("citations", []),
            "research_status": "completed"
        }
    except Exception as e:
        print(f"   ❌ Research failed: {str(e)}")
        return {
            "name": name,
            "website": vendor.get("website", ""),
            "description": vendor.get("description", ""),
            "research_content": "",
            "citations": [],
            "research_status": "failed",
            "error": str(e)
        }


def scrape_pricing_page(vendor: Dict) -> Dict:
    """
    Stage 3: Scrape vendor pricing page for verification.
    """
    website = vendor.get("website", "")
    if not website:
        return {"pricing_scraped": False, "error": "No website URL"}

    # Try common pricing page URLs
    pricing_urls = [
        f"{website.rstrip('/')}/pricing",
        f"{website.rstrip('/')}/pricing/",
        f"{website.rstrip('/')}/plans",
        f"{website.rstrip('/')}/plans-pricing",
    ]

    print(f"   📄 Scraping pricing page...")

    for url in pricing_urls:
        try:
            result = scrape_page(url, formats=["markdown"], timeout=30000)
            if result.get("success") and result.get("markdown"):
                markdown_content = result["markdown"]
                # Check if it looks like a pricing page
                pricing_indicators = ["$", "€", "£", "month", "year", "tier", "plan", "free", "pro", "enterprise"]
                if any(ind.lower() in markdown_content.lower() for ind in pricing_indicators):
                    print(f"   ✅ Found pricing page: {url}")
                    return {
                        "pricing_scraped": True,
                        "pricing_url": url,
                        "pricing_content": markdown_content[:5000],  # Limit size
                        "scraped_at": datetime.now().isoformat()
                    }
        except Exception as e:
            continue

    print(f"   ⚠️ Could not scrape pricing page")
    return {"pricing_scraped": False, "error": "No pricing page found"}


def parse_vendor_data(vendor: Dict, spec: Dict) -> Dict:
    """
    Parse research content into structured data for scoring.
    """
    content = vendor.get("research_content", "")

    # Initialize scores
    data = {
        "name": vendor["name"],
        "website": vendor.get("website", ""),
        "description": vendor.get("description", ""),

        # Pricing
        "pricing": {
            "has_free_tier": "free" in content.lower() and ("tier" in content.lower() or "plan" in content.lower()),
            "pricing_model": "unknown",
            "tiers": [],
            "verified": vendor.get("pricing_scraped", False)
        },

        # Features
        "features": {
            "requirements_met": [],
            "requirements_partial": [],
            "requirements_missing": []
        },

        # Integrations
        "integrations": {
            "native_count": 0,
            "has_api": False,
            "has_webhooks": False,
            "zapier_support": False,
            "make_support": False,
            "required_integrations": {}
        },

        # Reviews
        "reviews": {
            "g2_score": None,
            "g2_count": None,
            "capterra_score": None,
            "capterra_count": None,
            "trustradius_score": None,
            "trustradius_count": None
        },

        # Compliance
        "compliance": {
            "soc2": False,
            "gdpr": False,
            "hipaa": False,
            "iso27001": False
        },

        # Company
        "company": {
            "founded": None,
            "hq": None
        },

        # Raw
        "research_content": content,
        "citations": vendor.get("citations", [])
    }

    # Parse requirements matching from content
    requirements = spec.get("requirements", [])
    for req in requirements:
        req_lower = req.lower()
        # Check for explicit markers or keyword presence
        if f"✅" in content and req_lower in content.lower():
            data["features"]["requirements_met"].append(req)
        elif f"⚠️" in content and req_lower in content.lower():
            data["features"]["requirements_partial"].append(req)
        elif f"❌" in content and req_lower in content.lower():
            data["features"]["requirements_missing"].append(req)
        elif req_lower in content.lower():
            # Keyword present, assume partial support
            data["features"]["requirements_partial"].append(req)
        else:
            data["features"]["requirements_missing"].append(req)

    # Parse review scores with regex
    g2_match = re.search(r'G2[:\s]+(\d+\.?\d*)/5\s*\(?(\d+[,\d]*)\s*review', content, re.I)
    if g2_match:
        data["reviews"]["g2_score"] = float(g2_match.group(1))
        data["reviews"]["g2_count"] = int(g2_match.group(2).replace(",", ""))

    capterra_match = re.search(r'Capterra[:\s]+(\d+\.?\d*)/5\s*\(?(\d+[,\d]*)\s*review', content, re.I)
    if capterra_match:
        data["reviews"]["capterra_score"] = float(capterra_match.group(1))
        data["reviews"]["capterra_count"] = int(capterra_match.group(2).replace(",", ""))

    trustradius_match = re.search(r'TrustRadius[:\s]+(\d+\.?\d*)/10\s*\(?(\d+[,\d]*)\s*review', content, re.I)
    if trustradius_match:
        data["reviews"]["trustradius_score"] = float(trustradius_match.group(1))
        data["reviews"]["trustradius_count"] = int(trustradius_match.group(2).replace(",", ""))

    # Parse compliance
    if re.search(r'SOC\s*2', content, re.I):
        data["compliance"]["soc2"] = True
    if re.search(r'GDPR', content, re.I):
        data["compliance"]["gdpr"] = True
    if re.search(r'HIPAA', content, re.I):
        data["compliance"]["hipaa"] = True
    if re.search(r'ISO\s*27001', content, re.I):
        data["compliance"]["iso27001"] = True

    # Parse integrations
    if re.search(r'API|REST|GraphQL', content, re.I):
        data["integrations"]["has_api"] = True
    if re.search(r'webhook', content, re.I):
        data["integrations"]["has_webhooks"] = True
    if re.search(r'Zapier', content, re.I):
        data["integrations"]["zapier_support"] = True
    if re.search(r'Make|Integromat', content, re.I):
        data["integrations"]["make_support"] = True

    # Parse native integrations count
    int_match = re.search(r'(\d+)\+?\s*(?:native\s+)?integrations', content, re.I)
    if int_match:
        data["integrations"]["native_count"] = int(int_match.group(1))

    # Check required integrations
    required_integrations = spec.get("integrations", {}).get("must_integrate_with", [])
    for integration in required_integrations:
        data["integrations"]["required_integrations"][integration] = integration.lower() in content.lower()

    return data


def score_vendor(vendor_data: Dict, spec: Dict) -> Dict:
    """
    Stage 4: Score vendor against requirements.

    Returns scores dict with individual and total scores.
    """
    scores = {}

    # 1. Core Features (25%)
    requirements = spec.get("requirements", [])
    nice_to_haves = spec.get("nice_to_haves", [])

    total_reqs = len(requirements)
    met = len(vendor_data["features"]["requirements_met"])
    partial = len(vendor_data["features"]["requirements_partial"])

    if total_reqs > 0:
        # Full points for met, half for partial
        feature_score = ((met * 10) + (partial * 5)) / total_reqs
    else:
        feature_score = 5  # Neutral if no requirements

    scores["core_features"] = min(10, feature_score)

    # 2. Integration Ecosystem (25%)
    integrations = vendor_data["integrations"]
    int_score = 0

    # API capabilities (4 points max)
    if integrations["has_api"]:
        int_score += 2
    if integrations["has_webhooks"]:
        int_score += 2

    # iPaaS support (3 points max)
    if integrations["zapier_support"]:
        int_score += 1.5
    if integrations["make_support"]:
        int_score += 1.5

    # Required integrations (3 points max)
    required_ints = integrations.get("required_integrations", {})
    if required_ints:
        int_pct = sum(1 for v in required_ints.values() if v) / len(required_ints)
        int_score += int_pct * 3

    scores["integration_ecosystem"] = min(10, int_score)

    # 3. Pricing Fit (20%)
    budget = spec.get("budget", {})
    budget_range = budget.get("monthly_range", "")

    # Simple budget scoring - can be improved with actual price parsing
    pricing = vendor_data.get("pricing", {})
    if pricing.get("has_free_tier"):
        scores["pricing_fit"] = 8  # Free tier is good
    elif budget_range and "$" in budget_range:
        scores["pricing_fit"] = 7  # Assume reasonable fit
    else:
        scores["pricing_fit"] = 6  # Neutral

    # 4. Reviews (15%)
    reviews = vendor_data["reviews"]
    review_scores = []

    if reviews["g2_score"]:
        review_scores.append(reviews["g2_score"] * 2)  # Scale 5 to 10
    if reviews["capterra_score"]:
        review_scores.append(reviews["capterra_score"] * 2)
    if reviews["trustradius_score"]:
        review_scores.append(reviews["trustradius_score"])  # Already /10

    if review_scores:
        scores["reviews"] = sum(review_scores) / len(review_scores)
    else:
        scores["reviews"] = 5  # Neutral if no reviews found

    # 5. Compliance (10%)
    compliance_req = spec.get("compliance", {}).get("required", [])
    vendor_compliance = vendor_data["compliance"]

    compliance_map = {
        "SOC 2": "soc2", "SOC2": "soc2",
        "GDPR": "gdpr",
        "HIPAA": "hipaa",
        "ISO 27001": "iso27001", "ISO27001": "iso27001"
    }

    if compliance_req:
        met_count = 0
        for req in compliance_req:
            key = compliance_map.get(req.upper().replace(" ", ""), req.lower())
            if vendor_compliance.get(key, False):
                met_count += 1
        scores["compliance"] = (met_count / len(compliance_req)) * 10
    else:
        # No specific requirements, give points for having any
        has_any = any(vendor_compliance.values())
        scores["compliance"] = 8 if has_any else 5

    # 6. Support & Reliability (5%)
    # Default to neutral - would need more specific data
    scores["support_reliability"] = 6

    # Calculate weighted total
    total = sum(scores[k] * SCORING_WEIGHTS[k] for k in SCORING_WEIGHTS)
    scores["total"] = round(total, 2)

    return scores


def generate_report(vendors_data: List[Dict], spec: Dict) -> str:
    """
    Stage 5: Generate markdown report.
    """
    category = spec["category"]
    use_case = spec.get("use_case", "")
    requirements = spec.get("requirements", [])

    # Sort by total score
    vendors_data.sort(key=lambda x: x.get("scores", {}).get("total", 0), reverse=True)

    # Get top vendors
    top_vendor = vendors_data[0] if vendors_data else None
    runner_up = vendors_data[1] if len(vendors_data) > 1 else None

    # Build report
    report = f"""# Vendor Selection Report: {category}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Use Case:** {use_case}

---

## Executive Summary

"""

    if top_vendor:
        report += f"""Based on comprehensive research and scoring against your requirements, **{top_vendor['name']}** emerges as the top recommendation with a score of **{top_vendor['scores']['total']}/10**."""

        if runner_up:
            report += f""" **{runner_up['name']}** ({runner_up['scores']['total']}/10) is a strong runner-up that may be preferred depending on specific needs."""

    report += """

---

## Requirements Matrix

| Requirement | """ + " | ".join(v["name"][:15] for v in vendors_data[:5]) + " |\n"
    report += "|" + "----|" * (len(vendors_data[:5]) + 1) + "\n"

    for req in requirements:
        row = f"| {req[:40]} |"
        for v in vendors_data[:5]:
            if req in v.get("features", {}).get("requirements_met", []):
                row += " ✅ |"
            elif req in v.get("features", {}).get("requirements_partial", []):
                row += " ⚠️ |"
            else:
                row += " ❌ |"
        report += row + "\n"

    report += """

---

## Detailed Vendor Analysis

"""

    for i, vendor in enumerate(vendors_data, 1):
        scores = vendor.get("scores", {})
        is_recommended = i == 1

        report += f"### {i}. {vendor['name']}"
        if is_recommended:
            report += " ⭐ RECOMMENDED"
        report += "\n\n"

        report += f"**Website:** {vendor.get('website', 'N/A')}\n"
        report += f"**Overall Score:** {scores.get('total', 'N/A')}/10\n\n"

        # Scores breakdown
        report += "**Score Breakdown:**\n"
        report += f"- Core Features: {scores.get('core_features', 'N/A')}/10\n"
        report += f"- Integration Ecosystem: {scores.get('integration_ecosystem', 'N/A')}/10\n"
        report += f"- Pricing Fit: {scores.get('pricing_fit', 'N/A')}/10\n"
        report += f"- Reviews: {scores.get('reviews', 'N/A')}/10\n"
        report += f"- Compliance: {scores.get('compliance', 'N/A')}/10\n"
        report += f"- Support/Reliability: {scores.get('support_reliability', 'N/A')}/10\n\n"

        # Reviews
        reviews = vendor.get("reviews", {})
        if any([reviews.get("g2_score"), reviews.get("capterra_score")]):
            report += "**Reviews:**\n"
            if reviews.get("g2_score"):
                report += f"- G2: {reviews['g2_score']}/5 ({reviews.get('g2_count', 'N/A')} reviews)\n"
            if reviews.get("capterra_score"):
                report += f"- Capterra: {reviews['capterra_score']}/5 ({reviews.get('capterra_count', 'N/A')} reviews)\n"
            if reviews.get("trustradius_score"):
                report += f"- TrustRadius: {reviews['trustradius_score']}/10 ({reviews.get('trustradius_count', 'N/A')} reviews)\n"
            report += "\n"

        # Compliance
        compliance = vendor.get("compliance", {})
        compliance_items = []
        if compliance.get("soc2"):
            compliance_items.append("SOC 2")
        if compliance.get("gdpr"):
            compliance_items.append("GDPR")
        if compliance.get("hipaa"):
            compliance_items.append("HIPAA")
        if compliance.get("iso27001"):
            compliance_items.append("ISO 27001")

        if compliance_items:
            report += f"**Compliance:** {', '.join(compliance_items)}\n\n"

        # Integrations
        integrations = vendor.get("integrations", {})
        report += "**Integrations:**\n"
        if integrations.get("native_count"):
            report += f"- Native integrations: {integrations['native_count']}+\n"
        report += f"- API: {'✅' if integrations.get('has_api') else '❌'}\n"
        report += f"- Webhooks: {'✅' if integrations.get('has_webhooks') else '❌'}\n"
        report += f"- Zapier: {'✅' if integrations.get('zapier_support') else '❌'}\n"
        report += f"- Make: {'✅' if integrations.get('make_support') else '❌'}\n\n"

        # Required integrations check
        req_ints = integrations.get("required_integrations", {})
        if req_ints:
            report += "**Required Integrations Check:**\n"
            for name, supported in req_ints.items():
                report += f"- {name}: {'✅' if supported else '❌'}\n"
            report += "\n"

        report += "---\n\n"

    # Comparison Matrix
    report += """## Comparison Matrix

| Criteria | Weight |"""
    for v in vendors_data[:5]:
        report += f" {v['name'][:12]} |"
    report += "\n|" + "----|" * (len(vendors_data[:5]) + 2) + "\n"

    criteria_names = {
        "core_features": "Core Features",
        "integration_ecosystem": "Integrations",
        "pricing_fit": "Pricing Fit",
        "reviews": "Reviews",
        "compliance": "Compliance",
        "support_reliability": "Support"
    }

    for key, weight in SCORING_WEIGHTS.items():
        row = f"| {criteria_names.get(key, key)} | {int(weight*100)}% |"
        for v in vendors_data[:5]:
            score = v.get("scores", {}).get(key, "N/A")
            if isinstance(score, (int, float)):
                row += f" {score:.1f}/10 |"
            else:
                row += f" {score} |"
        report += row + "\n"

    report += "| **TOTAL** | 100% |"
    for v in vendors_data[:5]:
        total = v.get("scores", {}).get("total", "N/A")
        report += f" **{total}** |"
    report += "\n"

    # Final Recommendation
    report += """

---

## Final Recommendation

"""

    if top_vendor:
        report += f"""**Primary Choice: {top_vendor['name']}**
- Overall score: {top_vendor['scores']['total']}/10
"""
        # Add key strengths
        strengths = []
        if top_vendor['scores'].get('core_features', 0) >= 8:
            strengths.append("Strong feature match")
        if top_vendor['scores'].get('integration_ecosystem', 0) >= 8:
            strengths.append("Excellent integration ecosystem")
        if top_vendor['scores'].get('reviews', 0) >= 8:
            strengths.append("Highly rated by users")
        if strengths:
            report += f"- Key strengths: {', '.join(strengths)}\n"

    if runner_up:
        report += f"""
**Runner-up: {runner_up['name']}**
- Overall score: {runner_up['scores']['total']}/10
- Consider if: specific features or pricing better match your needs
"""

    if len(vendors_data) >= 3:
        budget_alt = min(vendors_data[2:], key=lambda x: x.get("scores", {}).get("pricing_fit", 0), default=None)
        if budget_alt and budget_alt != runner_up:
            report += f"""
**Budget Alternative: {budget_alt['name']}**
- Overall score: {budget_alt['scores']['total']}/10
- Trade-off: May have fewer features but potentially better value
"""

    # Sources
    report += """

---

## Sources

"""

    all_citations = []
    for v in vendors_data:
        for citation in v.get("citations", [])[:3]:  # Top 3 per vendor
            if isinstance(citation, dict):
                url = citation.get("url", citation.get("link", ""))
                title = citation.get("title", url)
            else:
                url = str(citation)
                title = url
            if url and url not in [c[1] for c in all_citations]:
                all_citations.append((title, url))

    for title, url in all_citations[:20]:  # Limit to 20 sources
        report += f"- [{title[:60]}]({url})\n"

    return report


def run_vendor_selection(spec_path: str, mode: str = "default") -> Tuple[str, str, Dict]:
    """
    Main execution function.

    Args:
        spec_path: Path to requirements YAML file
        mode: "quick" (5 vendors), "default" (10), or "thorough" (15)

    Returns:
        Tuple of (report_path, pdf_path, raw_data)
    """
    # Load requirements
    print("📋 Loading requirements...")
    spec = load_requirements(spec_path)

    # Set vendor limit based on mode
    vendor_limits = {"quick": 5, "default": 10, "thorough": 15}
    vendor_limit = vendor_limits.get(mode, 10)

    print(f"   Category: {spec['category']}")
    print(f"   Mode: {mode} ({vendor_limit} vendors)")
    print(f"   Requirements: {len(spec.get('requirements', []))}")

    # Validate API keys
    validate_api_key()

    # Stage 1: Discover vendors
    vendors = discover_vendors(spec, vendor_limit)

    if not vendors:
        raise ValueError("No vendors discovered. Check your category and requirements.")

    # Stage 2: Deep research each vendor
    print("\n" + "="*60)
    print("STAGE 2: DEEP RESEARCH")
    print("="*60)

    vendors_data = []
    for i, vendor in enumerate(vendors, 1):
        print(f"\n[{i}/{len(vendors)}] ", end="")

        # Research vendor
        research_result = research_vendor(vendor, spec)

        # Stage 3: Scrape pricing (optional, may fail)
        pricing_data = scrape_pricing_page(vendor)
        research_result.update(pricing_data)

        # Parse into structured data
        parsed = parse_vendor_data(research_result, spec)

        # Stage 4: Score vendor
        scores = score_vendor(parsed, spec)
        parsed["scores"] = scores

        vendors_data.append(parsed)

        print(f"   Score: {scores['total']}/10")

        # Small delay between vendors
        if i < len(vendors):
            time.sleep(1)

    # Stage 5: Generate report
    print("\n" + "="*60)
    print("STAGE 5: REPORT GENERATION")
    print("="*60)

    report_content = generate_report(vendors_data, spec)

    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    category_slug = re.sub(r'[^a-zA-Z0-9]+', '_', spec['category'])[:40]

    report_filename = f"vendor_comparison_{category_slug}_{timestamp}.md"
    report_path = REPORTS_DIR / report_filename
    report_path.write_text(report_content)
    print(f"\n📄 Report saved: {report_path}")

    # Convert to PDF
    pdf_path = report_path.with_suffix('.pdf')
    try:
        pdf_result = convert_md_to_pdf(
            str(report_path),
            str(pdf_path),
            style="report"
        )
        print(f"📑 PDF saved: {pdf_path}")
    except Exception as e:
        print(f"⚠️ PDF conversion failed: {e}")
        pdf_path = None

    # Save raw data
    data_filename = f"vendor_data_{timestamp}.json"
    data_path = DATA_DIR / data_filename

    raw_data = {
        "metadata": {
            "category": spec["category"],
            "use_case": spec.get("use_case", ""),
            "generated": datetime.now().isoformat(),
            "vendor_count": len(vendors_data),
            "mode": mode
        },
        "requirements": spec,
        "vendors": vendors_data,
        "recommendation": {
            "primary": vendors_data[0]["name"] if vendors_data else None,
            "primary_score": vendors_data[0]["scores"]["total"] if vendors_data else None,
            "runner_up": vendors_data[1]["name"] if len(vendors_data) > 1 else None
        }
    }

    data_path.write_text(json.dumps(raw_data, indent=2, default=str))
    print(f"💾 Data saved: {data_path}")

    # Summary
    print("\n" + "="*60)
    print("COMPLETE")
    print("="*60)

    if vendors_data:
        print(f"\n🏆 Top Recommendation: {vendors_data[0]['name']} ({vendors_data[0]['scores']['total']}/10)")
        if len(vendors_data) > 1:
            print(f"🥈 Runner-up: {vendors_data[1]['name']} ({vendors_data[1]['scores']['total']}/10)")

    return str(report_path), str(pdf_path) if pdf_path else None, raw_data


def main():
    parser = argparse.ArgumentParser(
        description="Vendor Selection & Comparison Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python execution/vendor_selection.py --spec requirements.yaml
    python execution/vendor_selection.py --spec requirements.yaml --quick
    python execution/vendor_selection.py --spec requirements.yaml --thorough
        """
    )

    parser.add_argument(
        "--spec", "-s",
        required=True,
        help="Path to requirements YAML file"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick mode: 5 vendors, faster research"
    )
    parser.add_argument(
        "--thorough",
        action="store_true",
        help="Thorough mode: 15 vendors, comprehensive research"
    )

    args = parser.parse_args()

    # Determine mode
    if args.quick:
        mode = "quick"
    elif args.thorough:
        mode = "thorough"
    else:
        mode = "default"

    try:
        report_path, pdf_path, data = run_vendor_selection(args.spec, mode)
        return 0
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
