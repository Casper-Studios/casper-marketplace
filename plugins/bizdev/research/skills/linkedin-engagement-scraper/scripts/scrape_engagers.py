#!/usr/bin/env python3
"""
LinkedIn Engagement Scraper
Scrapes commenters from a LinkedIn post via PhantomBuster,
parses their profiles, and outputs a Lemlist-ready CSV.

Usage:
    python scrape_engagers.py <linkedin_post_url>

Output:
    output/all_engagers_YYYY-MM-DD_HHMMSS.csv   — All scraped contacts
    output/engagers.json                         — Raw JSON for ICP filtering
"""

import csv
import json
import os
import re
import sys
import time
from datetime import datetime
from functools import partial

import requests
from dotenv import load_dotenv

load_dotenv()

print = partial(print, flush=True)

# --- Config ---
PB_API_KEY = os.getenv("PHANTOMBUSTER_API_KEY")
PB_AGENT_ID = os.getenv("PHANTOMBUSTER_AGENT_ID")
PB_BASE = "https://api.phantombuster.com/api/v2"

LEMLIST_COLUMNS = ["email", "firstName", "lastName", "companyName", "linkedinUrl", "jobTitle", "icebreaker"]

COMPANY_SUFFIXES = re.compile(
    r",?\s*\b(Inc\.?|LLC\.?|Ltd\.?|Corp\.?|Corporation|Incorporated|Limited|"
    r"PLC|plc|Co\.?|Company|Group|Holdings?|GmbH|AG|LLP|LP)\s*$",
    re.IGNORECASE,
)

SENIORITY_PATTERNS = {
    "c_suite": re.compile(
        r"\b(CEO|CTO|CIO|CDO|CAIO|CFO|COO|CMO|CPO|CRO|CISO|"
        r"Chief\s+\w+\s+Officer|Co-?Founder|Founder|President)\b",
        re.IGNORECASE,
    ),
    "vp": re.compile(
        r"\b(VP|Vice\s+President|SVP|Senior\s+Vice\s+President|"
        r"EVP|Executive\s+Vice\s+President|Head\s+of|Global\s+Head|Partner)\b",
        re.IGNORECASE,
    ),
    "director": re.compile(
        r"\b(Director|Senior\s+Director|Managing\s+Director|"
        r"Group\s+Director|Associate\s+Director)\b",
        re.IGNORECASE,
    ),
    "manager": re.compile(
        r"\b(Manager|Senior\s+Manager|Program\s+Manager|"
        r"Product\s+Manager|Engineering\s+Manager)\b",
        re.IGNORECASE,
    ),
    "senior_ic": re.compile(
        r"\b(Principal|Staff|Senior\s+\w+|Lead\s+\w+|Architect)\b",
        re.IGNORECASE,
    ),
}


# --- PhantomBuster ---

def launch_phantom(post_url):
    print(f"Launching PhantomBuster for: {post_url}")
    resp = requests.post(
        f"{PB_BASE}/agents/launch",
        headers={"X-Phantombuster-Key": PB_API_KEY},
        json={"id": PB_AGENT_ID, "bonusArgument": {"postUrl": post_url}},
    )
    if not resp.ok:
        print(f"PhantomBuster launch error ({resp.status_code}): {resp.text}")
        sys.exit(1)
    print(f"Phantom launched (container {resp.json().get('containerId')})")


def wait_for_phantom():
    print("Waiting for PhantomBuster to finish...")
    while True:
        resp = requests.get(
            f"{PB_BASE}/agents/fetch-output",
            headers={"X-Phantombuster-Key": PB_API_KEY},
            params={"id": PB_AGENT_ID},
        )
        resp.raise_for_status()
        status = resp.json().get("status")

        if status == "finished":
            print("  Done!")
            break
        if status == "error":
            print(f"PhantomBuster error: {resp.json().get('output', 'unknown')}")
            sys.exit(1)

        print(f"  Still running... ({status})")
        time.sleep(15)


def download_results():
    agent = requests.get(
        f"{PB_BASE}/agents/fetch",
        headers={"X-Phantombuster-Key": PB_API_KEY},
        params={"id": PB_AGENT_ID},
    ).json()

    url = f"https://phantombuster.s3.amazonaws.com/{agent['orgS3Folder']}/{agent['s3Folder']}/result.json"
    print("Downloading results...")
    resp = requests.get(url)
    resp.raise_for_status()

    try:
        return resp.json()
    except json.JSONDecodeError:
        return [json.loads(line) for line in resp.text.strip().split("\n") if line.strip()]


# --- Data parsing ---

def parse_occupation(occupation):
    """Extract (job_title, company) from a LinkedIn occupation string."""
    if not occupation:
        return "", ""

    for sep in (" at ", " @ "):
        if sep in occupation:
            title, rest = occupation.split(sep, 1)
            company = COMPANY_SUFFIXES.sub("", rest.split("|")[0].strip()).strip()
            return title.strip(), company

    if ", " in occupation:
        first, rest = occupation.split(", ", 1)
        if len(first.split()) <= 5:
            company = COMPANY_SUFFIXES.sub("", rest.split("|")[0].strip()).strip()
            return first.strip(), company

    return occupation, ""


def extract_seniority(title):
    """Return the highest seniority level found in the title."""
    if not title:
        return "unknown"
    for level, pattern in SENIORITY_PATTERNS.items():
        if pattern.search(title):
            return level
    return "individual_contributor"


def build_contacts(raw):
    """Convert PhantomBuster results into structured contact dicts."""
    contacts = []
    seen = set()

    for person in raw:
        url = person.get("profileUrl") or person.get("profileLink") or ""
        if url in seen:
            continue
        if url:
            seen.add(url)

        first = person.get("firstName") or ""
        last = person.get("lastName") or ""
        if not first and person.get("fullName"):
            parts = person["fullName"].split(" ", 1)
            first = parts[0]
            last = parts[1] if len(parts) > 1 else ""

        occupation = person.get("occupation") or ""
        title, company = parse_occupation(occupation)
        comment = person.get("comments") or person.get("comment") or ""

        contacts.append({
            "email": "",
            "firstName": first,
            "lastName": last,
            "companyName": company,
            "linkedinUrl": url,
            "jobTitle": title,
            "icebreaker": comment,
            # Extra fields for ICP filtering (not in Lemlist CSV)
            "seniority": extract_seniority(title),
            "occupationRaw": occupation,
        })

    return contacts


# --- Output ---

def write_lemlist_csv(contacts, filename):
    """Write contacts to a Lemlist-formatted CSV (only Lemlist columns)."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LEMLIST_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(contacts)
    print(f"Wrote {len(contacts)} contacts to {filename}")
    return filename


def write_json(contacts, filename):
    """Write full contact data as JSON for ICP filtering."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(contacts)} contacts to {filename}")


# --- Main ---

def main():
    if len(sys.argv) < 2:
        print("Usage: python scrape_engagers.py <linkedin_post_url>")
        sys.exit(1)

    for var in ("PHANTOMBUSTER_API_KEY", "PHANTOMBUSTER_AGENT_ID"):
        if not os.getenv(var):
            print(f"Missing env var: {var}")
            sys.exit(1)

    post_url = sys.argv[1]
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    os.makedirs("output", exist_ok=True)

    # Stage 1: Scrape
    launch_phantom(post_url)
    wait_for_phantom()
    raw = download_results()
    print(f"Scraped {len(raw)} engagers.")

    # Stage 2: Parse
    contacts = build_contacts(raw)
    print(f"{len(contacts)} unique contacts.")

    # Stage 3: Output
    # CSV with all engagers (Lemlist-ready)
    write_lemlist_csv(contacts, f"output/all_engagers_{ts}.csv")
    # JSON with full data (for ICP filtering)
    write_json(contacts, "output/engagers.json")

    print("\nDone! Two files ready:")
    print(f"  1. output/all_engagers_{ts}.csv  — Import directly into Lemlist")
    print(f"  2. output/engagers.json          — Feed to filter_icp.py for ICP matching")


if __name__ == "__main__":
    main()
