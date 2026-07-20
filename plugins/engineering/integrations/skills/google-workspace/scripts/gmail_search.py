#!/usr/bin/env python3
"""
Gmail Search and Read

Search Gmail for emails and read threads.
Used for client overview and communication history.

Directive: directives/gmail_search.md

Usage:
    # Search emails from/to a domain
    python execution/gmail_search.py --domain "microsoft.com" --days 14

    # Search by subject or content
    python execution/gmail_search.py --query "proposal" --days 30

    # Search internal emails mentioning a client
    python execution/gmail_search.py --query "Microsoft" --internal-only --days 14
"""

import os
import sys
import json
import argparse
import pickle
import base64
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv
from email.utils import parsedate_to_datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables
load_dotenv()

# OAuth scopes for Gmail (readonly)
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Credentials files
CLIENT_SECRETS_FILE = "client_secrets.json"
GMAIL_TOKEN_FILE = "gmail_token.pickle"


class GmailSearchError(Exception):
    """Custom exception for Gmail search operations."""
    pass


def get_gmail_service():
    """
    Authenticate and get Gmail service.

    Returns:
        Gmail API service
    """
    creds = None

    # Load saved credentials
    if Path(GMAIL_TOKEN_FILE).exists():
        with open(GMAIL_TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing Gmail credentials...")
            creds.refresh(Request())
        else:
            if not Path(CLIENT_SECRETS_FILE).exists():
                raise GmailSearchError(
                    f"{CLIENT_SECRETS_FILE} not found. "
                    "Download OAuth credentials from Google Cloud Console."
                )
            print("First time Gmail auth - opening browser...")
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save credentials
        with open(GMAIL_TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        print("Gmail credentials saved.")

    return build('gmail', 'v1', credentials=creds)


def build_search_query(
    query: str = None,
    domain: str = None,
    days: int = 14,
    internal_only: bool = False,
    exclude_domain: str = None
) -> str:
    """
    Build Gmail search query string.

    Args:
        query: Free text search
        domain: Email domain to filter (from/to)
        days: Limit to last N days
        internal_only: Only internal emails (exclude external domain)
        exclude_domain: Domain to exclude from results

    Returns:
        Gmail query string
    """
    parts = []

    # Date filter
    if days > 0:
        parts.append(f"newer_than:{days}d")

    # Domain filter
    if domain:
        if internal_only:
            # Internal emails that mention the domain/query
            parts.append(f"-from:@{domain}")
            parts.append(f"-to:@{domain}")
        else:
            # Emails from or to the domain
            parts.append(f"(from:@{domain} OR to:@{domain})")

    # Exclude domain
    if exclude_domain:
        parts.append(f"-from:@{exclude_domain}")
        parts.append(f"-to:@{exclude_domain}")

    # Free text query
    if query:
        parts.append(query)

    return " ".join(parts)


def search_messages(
    query: str = None,
    domain: str = None,
    days: int = 14,
    internal_only: bool = False,
    max_results: int = 50
) -> List[dict]:
    """
    Search Gmail messages.

    Args:
        query: Search query
        domain: Filter by domain
        days: Days back to search
        internal_only: Only internal emails
        max_results: Maximum results

    Returns:
        List of message summaries
    """
    service = get_gmail_service()

    # Build query
    q = build_search_query(
        query=query,
        domain=domain,
        days=days,
        internal_only=internal_only
    )

    print(f"Gmail query: {q}")

    try:
        # Search messages
        result = service.users().messages().list(
            userId='me',
            q=q,
            maxResults=max_results
        ).execute()

        messages = result.get('messages', [])

        if not messages:
            return []

        # Get message details
        processed = []
        for msg in messages:
            try:
                detail = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'To', 'Subject', 'Date']
                ).execute()

                # Extract headers
                headers = {h['name']: h['value'] for h in detail.get('payload', {}).get('headers', [])}

                # Parse date
                date_str = headers.get('Date', '')
                try:
                    date_dt = parsedate_to_datetime(date_str)
                    date_iso = date_dt.isoformat()
                    date_display = date_dt.strftime('%Y-%m-%d %H:%M')
                except Exception:
                    date_iso = date_str
                    date_display = date_str

                processed.append({
                    'id': msg['id'],
                    'thread_id': msg.get('threadId'),
                    'subject': headers.get('Subject', 'No subject'),
                    'from': headers.get('From', ''),
                    'to': headers.get('To', ''),
                    'date': date_iso,
                    'date_display': date_display,
                    'snippet': detail.get('snippet', ''),
                    'labels': detail.get('labelIds', [])
                })
            except HttpError:
                continue

        return processed

    except HttpError as e:
        raise GmailSearchError(f"Gmail API error: {e}")


def get_thread(thread_id: str, include_body: bool = False) -> dict:
    """
    Get full email thread.

    Args:
        thread_id: Thread ID
        include_body: Whether to include message bodies

    Returns:
        Thread data with all messages
    """
    service = get_gmail_service()

    try:
        thread = service.users().threads().get(
            userId='me',
            id=thread_id,
            format='full' if include_body else 'metadata'
        ).execute()

        messages = []
        for msg in thread.get('messages', []):
            headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}

            message_data = {
                'id': msg['id'],
                'from': headers.get('From', ''),
                'to': headers.get('To', ''),
                'subject': headers.get('Subject', ''),
                'date': headers.get('Date', ''),
                'snippet': msg.get('snippet', '')
            }

            # Extract body if requested
            if include_body:
                body = extract_body(msg.get('payload', {}))
                message_data['body'] = body[:2000] if body else ''

            messages.append(message_data)

        return {
            'thread_id': thread_id,
            'message_count': len(messages),
            'messages': messages
        }

    except HttpError as e:
        raise GmailSearchError(f"Failed to get thread: {e}")


def extract_body(payload: dict) -> str:
    """Extract plain text body from email payload."""
    if 'body' in payload and payload['body'].get('data'):
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')

    if 'parts' in payload:
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain':
                if 'body' in part and part['body'].get('data'):
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
            elif 'parts' in part:
                # Nested multipart
                body = extract_body(part)
                if body:
                    return body

    return ''


def summarize_emails(messages: List[dict], client_domain: str = None) -> dict:
    """
    Summarize emails for client overview.

    Args:
        messages: List of processed messages
        client_domain: Client's email domain for categorization

    Returns:
        Summary dict
    """
    external = []  # With client
    internal = []  # About client (internal)

    for msg in messages:
        from_addr = msg.get('from', '').lower()
        to_addr = msg.get('to', '').lower()

        if client_domain:
            if client_domain.lower() in from_addr or client_domain.lower() in to_addr:
                external.append(msg)
            else:
                internal.append(msg)
        else:
            external.append(msg)

    return {
        'total': len(messages),
        'external_threads': external[:10],
        'internal_mentions': internal[:10],
        'external_count': len(external),
        'internal_count': len(internal)
    }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Search Gmail for emails"
    )

    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--domain", "-d", help="Filter by email domain")
    parser.add_argument("--days", type=int, default=14, help="Days back to search")
    parser.add_argument("--internal-only", action="store_true",
                        help="Only internal emails (exclude external domain)")
    parser.add_argument("--limit", type=int, default=50, help="Max results")
    parser.add_argument("--thread", help="Get specific thread by ID")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.query and not args.domain and not args.thread:
        parser.print_help()
        print("\nError: Specify --query, --domain, or --thread")
        return 1

    try:
        if args.thread:
            print(f"Getting thread: {args.thread}")
            thread = get_thread(args.thread, include_body=True)

            if args.json:
                print(json.dumps(thread, indent=2))
            else:
                print(f"\nThread: {thread['message_count']} messages")
                for msg in thread['messages']:
                    print(f"\n[{msg['date']}] {msg['from']}")
                    print(f"Subject: {msg['subject']}")
                    print(f"Snippet: {msg['snippet'][:100]}...")

            return 0

        print(f"Searching Gmail (last {args.days} days)...")

        messages = search_messages(
            query=args.query,
            domain=args.domain,
            days=args.days,
            internal_only=args.internal_only,
            max_results=args.limit
        )

        if args.json:
            summary = summarize_emails(messages, args.domain)
            print(json.dumps(summary, indent=2))
            return 0

        if not messages:
            print("No emails found")
            return 0

        print(f"\n=== Gmail Search Results ===")
        print(f"Found: {len(messages)} emails")
        print()

        for msg in messages[:20]:
            print(f"[{msg['date_display']}] {msg['subject'][:50]}")
            print(f"  From: {msg['from'][:40]}")
            print(f"  Snippet: {msg['snippet'][:60]}...")
            print()

        return 0

    except GmailSearchError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
