#!/usr/bin/env python3
"""
Fireflies Transcript Search

Search and retrieve meeting transcripts from Fireflies.ai by company name,
keyword, or other filters.

Directive: directives/fireflies_transcript_search.md

Usage:
    # Search transcripts by company/keyword
    python execution/fireflies_transcript_search.py "Microsoft"

    # Search with date range
    python execution/fireflies_transcript_search.py "Acme" --from-date 2025-01-01

    # Get specific transcript by ID
    python execution/fireflies_transcript_search.py --id abc123

    # Search in transcript content (not just title)
    python execution/fireflies_transcript_search.py "pricing" --scope all

    # Limit results
    python execution/fireflies_transcript_search.py "Client" --limit 5

    # Output as JSON
    python execution/fireflies_transcript_search.py "Company" --json
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Configuration
FIREFLIES_API_KEY = os.getenv("FIREFLIES_API_KEY")
GRAPHQL_ENDPOINT = "https://api.fireflies.ai/graphql"

# Output directory
OUTPUT_DIR = Path(".tmp/fireflies_transcripts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class FirefliesError(Exception):
    """Custom exception for Fireflies API operations."""
    pass


def _make_graphql_request(query: str, variables: dict = None) -> dict:
    """
    Make a GraphQL request to Fireflies API.

    Args:
        query: GraphQL query string
        variables: Query variables

    Returns:
        Response data dict

    Raises:
        FirefliesError: If API request fails
    """
    if not FIREFLIES_API_KEY:
        raise FirefliesError(
            "FIREFLIES_API_KEY not found. Add it to your .env file.\n"
            "Get your API key from: https://app.fireflies.ai/integrations/custom/fireflies"
        )

    headers = {
        "Authorization": f"Bearer {FIREFLIES_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    response = requests.post(
        GRAPHQL_ENDPOINT,
        headers=headers,
        json=payload,
        timeout=30
    )

    if response.status_code != 200:
        raise FirefliesError(
            f"Fireflies API error: {response.status_code} - {response.text}"
        )

    result = response.json()

    if "errors" in result:
        error_msg = result["errors"][0].get("message", "Unknown GraphQL error")
        raise FirefliesError(f"GraphQL error: {error_msg}")

    return result.get("data", {})


def search_transcripts(
    keyword: str = None,
    from_date: str = None,
    to_date: str = None,
    host_email: str = None,
    limit: int = 10,
    skip: int = 0
) -> List[dict]:
    """
    Search for transcripts matching filters.

    Args:
        keyword: Search term (company name, topic, etc.) - searches title
        from_date: ISO date string (e.g., "2025-01-01")
        to_date: ISO date string
        host_email: Filter by meeting host
        limit: Max results (max 50)
        skip: Pagination offset

    Returns:
        List of transcript summaries
    """
    # Build query - use title filter which is simpler and well-supported
    query = """
    query SearchTranscripts(
        $title: String,
        $fromDate: DateTime,
        $toDate: DateTime,
        $host_email: String,
        $limit: Int,
        $skip: Int
    ) {
        transcripts(
            title: $title,
            fromDate: $fromDate,
            toDate: $toDate,
            host_email: $host_email,
            limit: $limit,
            skip: $skip
        ) {
            id
            title
            date
            duration
            host_email
            organizer_email
            transcript_url
            audio_url
            participants
            meeting_attendees {
                displayName
                email
            }
            speakers {
                id
                name
            }
            summary {
                overview
                keywords
                action_items
            }
        }
    }
    """

    variables = {
        "limit": min(limit, 50),
        "skip": skip
    }

    if keyword:
        variables["title"] = keyword

    if from_date:
        variables["fromDate"] = from_date

    if to_date:
        variables["toDate"] = to_date

    if host_email:
        variables["host_email"] = host_email

    data = _make_graphql_request(query, variables)
    return data.get("transcripts", [])


def get_transcript(transcript_id: str, include_sentences: bool = True) -> dict:
    """
    Get a specific transcript by ID with full content.

    Args:
        transcript_id: Fireflies transcript ID
        include_sentences: Include full transcript sentences

    Returns:
        Complete transcript data
    """
    # Build sentences fragment conditionally
    sentences_fragment = """
        sentences {
            index
            speaker_name
            speaker_id
            text
            raw_text
            start_time
            end_time
        }
    """ if include_sentences else ""

    query = f"""
    query GetTranscript($id: String!) {{
        transcript(id: $id) {{
            id
            title
            date
            dateString
            duration
            privacy
            host_email
            organizer_email
            transcript_url
            audio_url
            video_url
            meeting_link
            participants
            meeting_attendees {{
                displayName
                email
                phoneNumber
            }}
            speakers {{
                id
                name
            }}
            {sentences_fragment}
            summary {{
                overview
                keywords
                action_items
                outline
                shorthand_bullet
            }}
        }}
    }}
    """

    data = _make_graphql_request(query, {"id": transcript_id})
    return data.get("transcript")


def get_transcript_text(transcript_id: str) -> str:
    """
    Get the full transcript text as a formatted string.

    Args:
        transcript_id: Fireflies transcript ID

    Returns:
        Formatted transcript text with speaker labels
    """
    transcript = get_transcript(transcript_id, include_sentences=True)

    if not transcript:
        return None

    sentences = transcript.get("sentences", [])
    if not sentences:
        return None

    # Format as readable text
    lines = []
    current_speaker = None

    for sentence in sentences:
        speaker = sentence.get("speaker_name", "Unknown")
        text = sentence.get("text", "")

        if speaker != current_speaker:
            if lines:
                lines.append("")  # Blank line between speakers
            lines.append(f"**{speaker}:**")
            current_speaker = speaker

        lines.append(text)

    return "\n".join(lines)


def search_by_company(
    company_name: str,
    days_back: int = 90,
    limit: int = 10
) -> List[dict]:
    """
    Search for transcripts related to a company.

    Searches transcript titles for company name.

    Args:
        company_name: Company name to search
        days_back: How far back to search (default 90 days)
        limit: Max results

    Returns:
        List of matching transcripts
    """
    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    return search_transcripts(
        keyword=company_name,
        from_date=from_date,
        limit=limit
    )


def fireflies_transcript_search(
    keyword: str = None,
    transcript_id: str = None,
    from_date: str = None,
    to_date: str = None,
    days_back: int = None,
    limit: int = 10,
    include_content: bool = False
) -> dict:
    """
    Main search function with flexible options.

    Args:
        keyword: Search term (company name, topic) - searches title
        transcript_id: Specific transcript ID to retrieve
        from_date: Start date (ISO format)
        to_date: End date (ISO format)
        days_back: Alternative to from_date - search last N days
        limit: Max results
        include_content: Include full transcript content for each result

    Returns:
        Dict with transcripts and metadata
    """
    result = {
        "success": False,
        "query": {
            "keyword": keyword,
            "transcript_id": transcript_id,
            "from_date": from_date,
            "to_date": to_date,
            "limit": limit
        },
        "transcripts": [],
        "count": 0,
        "error": None
    }

    try:
        # If specific ID requested, get that transcript
        if transcript_id:
            transcript = get_transcript(transcript_id, include_sentences=include_content)
            if transcript:
                result["transcripts"] = [transcript]
                result["count"] = 1
            else:
                result["error"] = f"Transcript {transcript_id} not found"

        # Otherwise, search
        else:
            # Calculate from_date from days_back if provided
            if days_back and not from_date:
                from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
                result["query"]["from_date"] = from_date

            transcripts = search_transcripts(
                keyword=keyword,
                from_date=from_date,
                to_date=to_date,
                limit=limit
            )

            # Optionally fetch full content for each
            if include_content and transcripts:
                full_transcripts = []
                for t in transcripts:
                    full = get_transcript(t["id"], include_sentences=True)
                    if full:
                        full_transcripts.append(full)
                    else:
                        full_transcripts.append(t)
                transcripts = full_transcripts

            result["transcripts"] = transcripts
            result["count"] = len(transcripts)

        result["success"] = True

    except FirefliesError as e:
        result["error"] = str(e)
    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"

    return result


def print_transcript_list(transcripts: List[dict], verbose: bool = False):
    """Print formatted list of transcripts."""
    if not transcripts:
        print("No transcripts found.")
        return

    print(f"\nFound {len(transcripts)} transcript(s):\n")
    print("-" * 70)

    for t in transcripts:
        print(f"\n**{t.get('title', 'Untitled')}**")
        print(f"  ID: {t.get('id')}")

        # Handle date - could be timestamp in ms or ISO string
        date_val = t.get('date', t.get('dateString', 'Unknown'))
        if isinstance(date_val, (int, float)) and date_val > 1000000000000:
            # Milliseconds timestamp
            date_str = datetime.fromtimestamp(date_val / 1000).strftime("%Y-%m-%d %H:%M")
        elif isinstance(date_val, (int, float)):
            # Seconds timestamp
            date_str = datetime.fromtimestamp(date_val).strftime("%Y-%m-%d %H:%M")
        else:
            date_str = str(date_val)
        print(f"  Date: {date_str}")

        duration = t.get('duration')
        if duration and duration > 0:
            minutes = int(duration // 60)
            print(f"  Duration: {minutes} minutes")

        host = t.get('host_email') or t.get('organizer_email')
        if host:
            print(f"  Host: {host}")

        speakers = t.get('speakers', [])
        if speakers:
            names = [s.get('name', 'Unknown') for s in speakers]
            print(f"  Speakers: {', '.join(names)}")

        if verbose:
            summary = t.get('summary', {})
            if summary:
                overview = summary.get('overview')
                if overview:
                    print(f"  Summary: {overview[:200]}...")

                keywords = summary.get('keywords', [])
                if keywords:
                    print(f"  Keywords: {', '.join(keywords[:5])}")

        print(f"  URL: {t.get('transcript_url', 'N/A')}")

    print("\n" + "-" * 70)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Search Fireflies.ai transcripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Microsoft"                    # Search by company name
  %(prog)s "pricing" --scope all          # Search in content too
  %(prog)s --id abc123                    # Get specific transcript
  %(prog)s "Client" --days-back 30        # Last 30 days
  %(prog)s "Acme" --from-date 2025-01-01  # Since date
  %(prog)s "Company" --content            # Include full text
        """
    )

    parser.add_argument("keyword", nargs="?", help="Search term (company name, topic) - searches title")
    parser.add_argument("--id", dest="transcript_id", help="Specific transcript ID")
    parser.add_argument("--from-date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to-date", help="End date (YYYY-MM-DD)")
    parser.add_argument("--days-back", type=int, help="Search last N days")
    parser.add_argument("--limit", type=int, default=10, help="Max results (default: 10)")
    parser.add_argument("--content", action="store_true",
                        help="Include full transcript content")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--save", help="Save transcript text to file")

    args = parser.parse_args()

    # Validate arguments
    if not args.keyword and not args.transcript_id:
        parser.error("Either keyword or --id is required")

    print(f"\n{'='*60}")
    print("  Fireflies Transcript Search")
    print(f"{'='*60}")

    if args.keyword:
        print(f"  Keyword: {args.keyword}")
    if args.transcript_id:
        print(f"  Transcript ID: {args.transcript_id}")
    if args.days_back:
        print(f"  Days back: {args.days_back}")
    if args.from_date:
        print(f"  From: {args.from_date}")

    print(f"{'='*60}\n")

    try:
        result = fireflies_transcript_search(
            keyword=args.keyword,
            transcript_id=args.transcript_id,
            from_date=args.from_date,
            to_date=args.to_date,
            days_back=args.days_back,
            limit=args.limit,
            include_content=args.content
        )

        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            if result["success"]:
                print_transcript_list(result["transcripts"], verbose=args.verbose)

                # Save transcript text if requested
                if args.save and result["transcripts"]:
                    transcript = result["transcripts"][0]
                    if "sentences" in transcript:
                        text = get_transcript_text(transcript["id"])
                        if text:
                            Path(args.save).write_text(text)
                            print(f"\nTranscript saved to: {args.save}")
            else:
                print(f"Error: {result['error']}")

        # Save result to .tmp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        search_term = args.keyword or args.transcript_id or "search"
        safe_name = search_term.lower().replace(" ", "_")[:30]
        output_file = OUTPUT_DIR / f"{safe_name}_{timestamp}.json"
        output_file.write_text(json.dumps(result, indent=2, default=str))
        print(f"\nResults saved to: {output_file}")

        return 0 if result["success"] else 1

    except FirefliesError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
