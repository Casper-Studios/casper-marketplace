#!/usr/bin/env python3
"""
Google Calendar Event Search

Search for calendar events by query, date range, and attendees.
Used for client overview and meeting history.

Directive: directives/google_calendar_search.md

Usage:
    # Search for events mentioning a client
    python execution/google_calendar_search.py "Microsoft" --days-back 14 --days-forward 14

    # Search by attendee domain
    python execution/google_calendar_search.py --domain "microsoft.com" --days-back 30

    # List upcoming events
    python execution/google_calendar_search.py --upcoming --days-forward 7
"""

import os
import sys
import json
import argparse
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables
load_dotenv()

# OAuth scopes for Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Credentials files
CLIENT_SECRETS_FILE = "client_secrets.json"
CALENDAR_TOKEN_FILE = "calendar_token.pickle"


class CalendarSearchError(Exception):
    """Custom exception for calendar search operations."""
    pass


def get_calendar_service():
    """
    Authenticate and get Google Calendar service.

    Returns:
        Google Calendar API service
    """
    creds = None

    # Load saved credentials
    if Path(CALENDAR_TOKEN_FILE).exists():
        with open(CALENDAR_TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing Calendar credentials...")
            creds.refresh(Request())
        else:
            if not Path(CLIENT_SECRETS_FILE).exists():
                raise CalendarSearchError(
                    f"{CLIENT_SECRETS_FILE} not found. "
                    "Download OAuth credentials from Google Cloud Console."
                )
            print("First time Calendar auth - opening browser...")
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save credentials
        with open(CALENDAR_TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        print("Calendar credentials saved.")

    return build('calendar', 'v3', credentials=creds)


def search_events(
    query: str = None,
    attendee_domain: str = None,
    days_back: int = 14,
    days_forward: int = 14,
    calendar_id: str = 'primary',
    max_results: int = 50
) -> List[dict]:
    """
    Search for calendar events.

    Args:
        query: Text to search for in event title/description
        attendee_domain: Filter by attendee email domain
        days_back: Days in the past to search
        days_forward: Days in the future to search
        calendar_id: Calendar ID (default: primary)
        max_results: Maximum events to return

    Returns:
        List of event dictionaries
    """
    service = get_calendar_service()

    # Calculate time range
    now = datetime.utcnow()
    time_min = (now - timedelta(days=days_back)).isoformat() + 'Z'
    time_max = (now + timedelta(days=days_forward)).isoformat() + 'Z'

    try:
        # Build query parameters
        params = {
            'calendarId': calendar_id,
            'timeMin': time_min,
            'timeMax': time_max,
            'maxResults': max_results,
            'singleEvents': True,
            'orderBy': 'startTime'
        }

        if query:
            params['q'] = query

        # Execute search
        result = service.events().list(**params).execute()
        events = result.get('items', [])

        # Process events
        processed = []
        for event in events:
            # Get start/end times
            start = event.get('start', {})
            end = event.get('end', {})
            start_dt = start.get('dateTime', start.get('date', ''))
            end_dt = end.get('dateTime', end.get('date', ''))

            # Parse datetime for comparison
            if 'T' in start_dt:
                event_start = datetime.fromisoformat(start_dt.replace('Z', '+00:00'))
            else:
                event_start = datetime.strptime(start_dt, '%Y-%m-%d')

            # Get attendees
            attendees = []
            for att in event.get('attendees', []):
                attendees.append({
                    'email': att.get('email', ''),
                    'name': att.get('displayName', ''),
                    'response': att.get('responseStatus', 'unknown'),
                    'organizer': att.get('organizer', False)
                })

            # Filter by attendee domain if specified
            if attendee_domain:
                domain_match = any(
                    attendee_domain.lower() in att['email'].lower()
                    for att in attendees
                )
                if not domain_match:
                    continue

            # Determine if past or upcoming
            is_past = event_start.replace(tzinfo=None) < now

            processed.append({
                'id': event.get('id'),
                'summary': event.get('summary', 'No title'),
                'description': event.get('description', '')[:500] if event.get('description') else '',
                'start': start_dt,
                'end': end_dt,
                'is_past': is_past,
                'location': event.get('location', ''),
                'attendees': attendees,
                'attendee_count': len(attendees),
                'html_link': event.get('htmlLink', ''),
                'organizer': event.get('organizer', {}).get('email', ''),
                'status': event.get('status', 'confirmed')
            })

        return processed

    except HttpError as e:
        raise CalendarSearchError(f"Calendar API error: {e}")


def get_events_summary(events: List[dict]) -> dict:
    """
    Summarize events into past and upcoming.

    Args:
        events: List of processed events

    Returns:
        Dict with past_meetings and upcoming_meetings
    """
    past = [e for e in events if e['is_past']]
    upcoming = [e for e in events if not e['is_past']]

    return {
        'past_meetings': sorted(past, key=lambda x: x['start'], reverse=True),
        'upcoming_meetings': sorted(upcoming, key=lambda x: x['start']),
        'total_past': len(past),
        'total_upcoming': len(upcoming)
    }


def format_event_for_display(event: dict) -> str:
    """Format a single event for display."""
    # Parse date
    start = event['start']
    if 'T' in start:
        dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
        date_str = dt.strftime('%Y-%m-%d %H:%M')
    else:
        date_str = start

    status = "PAST" if event['is_past'] else "UPCOMING"
    attendee_str = f"{event['attendee_count']} attendees" if event['attendee_count'] else "no attendees"

    return f"[{status}] {date_str} - {event['summary']} ({attendee_str})"


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Search Google Calendar events"
    )

    parser.add_argument("query", nargs="?", help="Search query (event title/description)")
    parser.add_argument("--domain", help="Filter by attendee email domain")
    parser.add_argument("--days-back", type=int, default=14, help="Days in past to search")
    parser.add_argument("--days-forward", type=int, default=14, help="Days in future to search")
    parser.add_argument("--calendar", default="primary", help="Calendar ID")
    parser.add_argument("--limit", type=int, default=50, help="Max results")
    parser.add_argument("--upcoming", action="store_true", help="Only show upcoming events")
    parser.add_argument("--past", action="store_true", help="Only show past events")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    try:
        print("Searching calendar...")

        # Adjust time range based on flags
        days_back = 0 if args.upcoming else args.days_back
        days_forward = 0 if args.past else args.days_forward

        events = search_events(
            query=args.query,
            attendee_domain=args.domain,
            days_back=days_back,
            days_forward=days_forward,
            calendar_id=args.calendar,
            max_results=args.limit
        )

        if args.json:
            summary = get_events_summary(events)
            print(json.dumps(summary, indent=2))
            return 0

        if not events:
            print("No events found")
            return 0

        summary = get_events_summary(events)

        print(f"\n=== Calendar Events ===")
        if args.query:
            print(f"Query: {args.query}")
        if args.domain:
            print(f"Domain filter: @{args.domain}")
        print()

        if summary['past_meetings'] and not args.upcoming:
            print(f"PAST MEETINGS ({summary['total_past']}):")
            for event in summary['past_meetings'][:10]:
                print(f"  {format_event_for_display(event)}")
            print()

        if summary['upcoming_meetings'] and not args.past:
            print(f"UPCOMING MEETINGS ({summary['total_upcoming']}):")
            for event in summary['upcoming_meetings'][:10]:
                print(f"  {format_event_for_display(event)}")

        return 0

    except CalendarSearchError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
