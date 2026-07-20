#!/usr/bin/env python3
"""
ICP Filter for LinkedIn Engagers
Filters scraped engagers against an Ideal Customer Profile and outputs
a Lemlist-ready CSV of matching contacts.

Usage:
    python filter_icp.py <engagers_json> [--icp <icp_json>]

Interactive mode (no --icp flag):
    Prompts you to define your ICP, then filters and outputs matches.

Automated mode (with --icp flag):
    Reads ICP criteria from a JSON file. Useful for rerunning the same
    filter on new scrapes.

Output:
    output/icp_matches_YYYY-MM-DD_HHMMSS.csv  — Lemlist-ready CSV of ICP matches
"""

import csv
import json
import os
import re
import sys
from datetime import datetime

LEMLIST_COLUMNS = [
    "email", "firstName", "lastName", "companyName",
    "linkedinUrl", "jobTitle", "icebreaker", "icpFit",
]

SENIORITY_HIERARCHY = [
    "c_suite", "vp", "director", "manager", "senior_ic", "individual_contributor", "unknown"
]


def load_engagers(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_icp(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def prompt_icp():
    """Interactive ICP definition."""
    print("\n--- Define your Ideal Customer Profile ---\n")

    icp = {"segments": []}
    segment_num = 1

    while True:
        print(f"Segment {segment_num}:")

        industries = input("  Industries (comma-separated, or blank for any): ").strip()
        titles = input("  Target titles/keywords (comma-separated, or blank for any): ").strip()
        min_seniority = input("  Minimum seniority [c_suite / vp / director / manager / senior_ic / any]: ").strip()
        company_keywords = input("  Company name keywords (comma-separated, or blank for any): ").strip()

        segment = {}
        if industries:
            segment["industries"] = [i.strip().lower() for i in industries.split(",")]
        if titles:
            segment["title_keywords"] = [t.strip().lower() for t in titles.split(",")]
        if min_seniority and min_seniority != "any":
            segment["min_seniority"] = min_seniority.strip().lower()
        if company_keywords:
            segment["company_keywords"] = [c.strip().lower() for c in company_keywords.split(",")]

        if segment:
            segment["name"] = f"Segment {segment_num}"
            icp["segments"].append(segment)
            segment_num += 1

        more = input("\n  Add another segment? (y/n): ").strip().lower()
        if more != "y":
            break

    # Save ICP for reuse
    os.makedirs("output", exist_ok=True)
    icp_path = "output/icp_criteria.json"
    with open(icp_path, "w") as f:
        json.dump(icp, f, indent=2)
    print(f"\nICP saved to {icp_path} (reuse with --icp flag)\n")

    return icp


def seniority_meets_minimum(contact_seniority, min_seniority):
    """Check if the contact's seniority meets the minimum threshold."""
    if not min_seniority:
        return True
    try:
        contact_rank = SENIORITY_HIERARCHY.index(contact_seniority)
        min_rank = SENIORITY_HIERARCHY.index(min_seniority)
    except ValueError:
        return True
    return contact_rank <= min_rank


def match_contact(contact, icp):
    """Score a contact against all ICP segments. Returns (fit_level, matched_segment)."""
    title_lower = (contact.get("jobTitle") or "").lower()
    company_lower = (contact.get("companyName") or "").lower()
    occupation_lower = (contact.get("occupationRaw") or "").lower()
    seniority = contact.get("seniority", "unknown")

    best_fit = "no_fit"
    best_segment = None

    for segment in icp.get("segments", []):
        title_match = True
        company_match = True
        seniority_match = True
        industry_match = True

        # Title keywords
        if segment.get("title_keywords"):
            title_match = any(
                kw in title_lower or kw in occupation_lower
                for kw in segment["title_keywords"]
            )

        # Company keywords
        if segment.get("company_keywords"):
            company_match = any(
                kw in company_lower or kw in occupation_lower
                for kw in segment["company_keywords"]
            )

        # Seniority
        if segment.get("min_seniority"):
            seniority_match = seniority_meets_minimum(seniority, segment["min_seniority"])

        # Industry (matched against occupation since we don't have a separate industry field)
        if segment.get("industries"):
            industry_match = any(
                ind in occupation_lower or ind in company_lower
                for ind in segment["industries"]
            )

        # Score
        signals = [title_match, company_match, seniority_match, industry_match]
        active_criteria = sum(1 for s in [
            segment.get("title_keywords"),
            segment.get("company_keywords"),
            segment.get("min_seniority"),
            segment.get("industries"),
        ] if s)

        if active_criteria == 0:
            continue

        passing = sum(signals[:active_criteria]) if active_criteria <= len(signals) else sum(signals)
        # Recalculate: only count criteria that were actually set
        checks = []
        if segment.get("title_keywords"):
            checks.append(title_match)
        if segment.get("company_keywords"):
            checks.append(company_match)
        if segment.get("min_seniority"):
            checks.append(seniority_match)
        if segment.get("industries"):
            checks.append(industry_match)

        passing = sum(checks)
        total = len(checks)

        if total > 0 and passing == total:
            fit = "strong_fit"
        elif total > 0 and passing >= total - 1 and passing > 0:
            fit = "likely_fit"
        elif passing > 0:
            fit = "weak_fit"
        else:
            fit = "no_fit"

        fit_rank = ["strong_fit", "likely_fit", "weak_fit", "no_fit"]
        if fit_rank.index(fit) < fit_rank.index(best_fit):
            best_fit = fit
            best_segment = segment.get("name", "")

    return best_fit, best_segment


def filter_contacts(contacts, icp):
    """Filter and score all contacts against the ICP."""
    results = {"strong_fit": [], "likely_fit": [], "weak_fit": [], "no_fit": []}

    for contact in contacts:
        fit, segment = match_contact(contact, icp)
        contact_copy = dict(contact)
        contact_copy["icpFit"] = fit
        contact_copy["matchedSegment"] = segment or ""
        results[fit].append(contact_copy)

    return results


def write_lemlist_csv(contacts, filename):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LEMLIST_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(contacts)
    print(f"Wrote {len(contacts)} contacts to {filename}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python filter_icp.py <engagers_json> [--icp <icp_json>]")
        sys.exit(1)

    engagers_path = sys.argv[1]
    contacts = load_engagers(engagers_path)
    print(f"Loaded {len(contacts)} contacts from {engagers_path}")

    # Load or prompt for ICP
    icp = None
    if "--icp" in sys.argv:
        icp_idx = sys.argv.index("--icp")
        if icp_idx + 1 < len(sys.argv):
            icp = load_icp(sys.argv[icp_idx + 1])
            print(f"Loaded ICP from {sys.argv[icp_idx + 1]}")

    if not icp:
        icp = prompt_icp()

    # Print ICP summary
    print("ICP Segments:")
    for seg in icp.get("segments", []):
        print(f"  {seg.get('name', 'Unnamed')}:")
        if seg.get("industries"):
            print(f"    Industries: {', '.join(seg['industries'])}")
        if seg.get("title_keywords"):
            print(f"    Title keywords: {', '.join(seg['title_keywords'])}")
        if seg.get("min_seniority"):
            print(f"    Min seniority: {seg['min_seniority']}")
        if seg.get("company_keywords"):
            print(f"    Company keywords: {', '.join(seg['company_keywords'])}")

    # Filter
    results = filter_contacts(contacts, icp)

    strong = results["strong_fit"]
    likely = results["likely_fit"]
    weak = results["weak_fit"]
    no_fit = results["no_fit"]

    print(f"\nResults:")
    print(f"  Strong fit: {len(strong)}")
    print(f"  Likely fit: {len(likely)}")
    print(f"  Weak fit:   {len(weak)}")
    print(f"  No fit:     {len(no_fit)}")

    # Output: ICP matches (strong + likely) as Lemlist CSV
    icp_matches = strong + likely
    os.makedirs("output", exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    if icp_matches:
        write_lemlist_csv(icp_matches, f"output/icp_matches_{ts}.csv")
    else:
        print("\nNo strong or likely matches found. Try broadening your ICP criteria.")
        # Still write weak fits if any
        if weak:
            write_lemlist_csv(weak, f"output/icp_weak_matches_{ts}.csv")
            print(f"Wrote {len(weak)} weak matches as fallback.")

    print("\nDone!")


if __name__ == "__main__":
    main()
