#!/usr/bin/env python3
"""
Slack News Channel Fetcher
Fetches messages from the #news Slack channel with optional date range filtering.

Usage:
    python execution/fetch_slack_news.py
    python execution/fetch_slack_news.py --days-back 7
    python execution/fetch_slack_news.py --start-date 2025-12-01 --end-date 2025-12-08
    python execution/fetch_slack_news.py --channel news --max-messages 100 --include-threads
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import argparse
import time

# Load environment variables
load_dotenv()

# Configuration
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
OUTPUT_DIR = Path(__file__).parent.parent / ".tmp"

def validate_environment():
    """Validate required environment variables."""
    if not SLACK_BOT_TOKEN:
        raise ValueError(
            "SLACK_BOT_TOKEN not found in environment. "
            "Please add it to your .env file.\n"
            "Get your token from: https://api.slack.com/apps > Your App > OAuth & Permissions"
        )

def find_channel_id(client, channel_name):
    """
    Find channel ID by name.

    Args:
        client: Slack WebClient
        channel_name: Channel name without # (e.g., "news")

    Returns:
        str: Channel ID or None if not found
    """
    try:
        # Remove # if present
        channel_name = channel_name.lstrip("#")

        print(f"🔍 Looking for channel: #{channel_name}")

        # List all channels (public and private) with pagination
        channels = []
        cursor = None
        while True:
            params = {"types": "public_channel,private_channel", "limit": 200}
            if cursor:
                params["cursor"] = cursor

            result = client.conversations_list(**params)
            channels.extend(result["channels"])

            # Check for more pages
            if not result.get("response_metadata", {}).get("next_cursor"):
                break
            cursor = result["response_metadata"]["next_cursor"]

        # Find matching channel
        for channel in channels:
            if channel["name"] == channel_name:
                print(f"✅ Found channel: #{channel['name']} (ID: {channel['id']})")
                return channel["id"]

        # Channel not found
        print(f"❌ Channel #{channel_name} not found.")
        print(f"\nAvailable channels:")
        for ch in channels[:10]:  # Show first 10
            print(f"  - #{ch['name']}")

        return None

    except SlackApiError as e:
        print(f"❌ Error finding channel: {e.response['error']}")
        return None

def fetch_messages(
    client,
    channel_id,
    oldest=None,
    latest=None,
    max_messages=100
):
    """
    Fetch messages from a Slack channel.

    Args:
        client: Slack WebClient
        channel_id: Channel ID
        oldest: Unix timestamp for oldest message (optional)
        latest: Unix timestamp for latest message (optional)
        max_messages: Maximum number of messages to fetch

    Returns:
        list: List of message objects
    """
    messages = []
    cursor = None

    print(f"📥 Fetching messages from channel...")

    try:
        while len(messages) < max_messages:
            # Fetch messages with pagination
            params = {
                "channel": channel_id,
                "limit": min(100, max_messages - len(messages))  # Slack max per request: 100
            }

            if oldest:
                params["oldest"] = oldest
            if latest:
                params["latest"] = latest
            if cursor:
                params["cursor"] = cursor

            result = client.conversations_history(**params)

            batch_messages = result["messages"]
            messages.extend(batch_messages)

            print(f"  Fetched {len(batch_messages)} messages (total: {len(messages)})")

            # Check if there are more messages
            if not result.get("has_more") or not result.get("response_metadata", {}).get("next_cursor"):
                break

            cursor = result["response_metadata"]["next_cursor"]
            time.sleep(0.5)  # Rate limit protection

        print(f"✅ Fetched {len(messages)} messages total")
        return messages

    except SlackApiError as e:
        error = e.response['error']

        if error == "not_in_channel":
            print(f"❌ Bot is not in the channel!")
            print(f"To fix: Go to Slack and type: /invite @YourBotName in the channel")
        else:
            print(f"❌ Error fetching messages: {error}")

        return []

def fetch_thread_replies(client, channel_id, thread_ts):
    """
    Fetch replies from a message thread.

    Args:
        client: Slack WebClient
        channel_id: Channel ID
        thread_ts: Thread timestamp

    Returns:
        list: List of reply messages
    """
    try:
        result = client.conversations_replies(
            channel=channel_id,
            ts=thread_ts
        )
        # Skip first message (it's the parent)
        return result["messages"][1:] if len(result["messages"]) > 1 else []
    except SlackApiError:
        return []

def get_user_name(client, user_id, user_cache):
    """
    Get user's real name from ID with caching.

    Args:
        client: Slack WebClient
        user_id: User ID
        user_cache: Dict to cache user lookups

    Returns:
        str: User's real name or username
    """
    if user_id in user_cache:
        return user_cache[user_id]

    try:
        result = client.users_info(user=user_id)
        user = result["user"]
        name = user.get("real_name") or user.get("name", user_id)
        user_cache[user_id] = name
        return name
    except SlackApiError:
        return user_id

def process_messages(
    client,
    messages,
    channel_id,
    include_threads=True,
    search_keywords=None
):
    """
    Process and enrich message data.

    Args:
        client: Slack WebClient
        messages: Raw message list
        channel_id: Channel ID
        include_threads: Whether to fetch thread replies
        search_keywords: Optional keyword filter

    Returns:
        list: Processed message objects
    """
    processed = []
    user_cache = {}

    print(f"🔧 Processing {len(messages)} messages...")

    for msg in messages:
        # Skip bot messages or system messages if desired
        if msg.get("subtype") in ["channel_join", "channel_leave"]:
            continue

        # Extract user info
        user_id = msg.get("user", "")
        user_name = get_user_name(client, user_id, user_cache) if user_id else "Unknown"

        # Convert timestamp to readable datetime
        ts = float(msg.get("ts", 0))
        dt = datetime.fromtimestamp(ts)

        # Extract text
        text = msg.get("text", "")

        # Keyword filtering
        if search_keywords:
            if not any(kw.lower() in text.lower() for kw in search_keywords):
                continue

        # Extract reactions
        reactions = []
        for reaction in msg.get("reactions", []):
            reactions.append({
                "name": reaction["name"],
                "count": reaction["count"]
            })

        # Extract links from text
        links = []
        import re
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        links = re.findall(url_pattern, text)

        # Build message object
        processed_msg = {
            "timestamp": msg.get("ts"),
            "datetime": dt.isoformat(),
            "user": user_name,
            "user_id": user_id,
            "text": text,
            "reactions": reactions,
            "thread_replies": [],
            "attachments": msg.get("attachments", []),
            "files": msg.get("files", []),
            "links": links
        }

        # Fetch thread replies if present
        if include_threads and msg.get("reply_count", 0) > 0:
            thread_ts = msg.get("ts")
            replies = fetch_thread_replies(client, channel_id, thread_ts)

            for reply in replies:
                reply_user_id = reply.get("user", "")
                reply_user_name = get_user_name(client, reply_user_id, user_cache) if reply_user_id else "Unknown"
                reply_ts = float(reply.get("ts", 0))
                reply_dt = datetime.fromtimestamp(reply_ts)

                processed_msg["thread_replies"].append({
                    "timestamp": reply.get("ts"),
                    "datetime": reply_dt.isoformat(),
                    "user": reply_user_name,
                    "user_id": reply_user_id,
                    "text": reply.get("text", "")
                })

            time.sleep(0.3)  # Rate limit protection

        processed.append(processed_msg)

    print(f"✅ Processed {len(processed)} messages")
    return processed

def save_results(data, channel_name, filename=None):
    """
    Save results to .tmp directory.

    Args:
        data: Processed message data
        channel_name: Name of the channel
        filename: Optional custom filename
    """
    OUTPUT_DIR.mkdir(exist_ok=True)

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"slack_{channel_name}_{timestamp}.json"

    output_path = OUTPUT_DIR / filename

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Results saved to: {output_path}")
    print(f"📊 Total messages: {data['total_count']}")

    # Print sample messages
    if data['messages']:
        print(f"\n📬 Sample messages:")
        for i, msg in enumerate(data['messages'][:3], 1):
            print(f"\n{i}. [{msg['datetime']}] {msg['user']}")
            print(f"   {msg['text'][:100]}{'...' if len(msg['text']) > 100 else ''}")
            if msg['reactions']:
                reactions_str = ", ".join([f":{r['name']}: {r['count']}" for r in msg['reactions']])
                print(f"   Reactions: {reactions_str}")
            if msg['thread_replies']:
                print(f"   💬 {len(msg['thread_replies'])} replies")

    return output_path

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Fetch messages from Slack #news channel"
    )
    parser.add_argument(
        "--channel",
        default="news",
        help="Channel name (default: news)"
    )
    parser.add_argument(
        "--channel-id",
        help="Channel ID (if known, skips lookup)"
    )
    parser.add_argument(
        "--days-back",
        type=int,
        help="Number of days to look back (e.g., 7 for last week)"
    )
    parser.add_argument(
        "--start-date",
        help="Start date (YYYY-MM-DD format)"
    )
    parser.add_argument(
        "--end-date",
        help="End date (YYYY-MM-DD format)"
    )
    parser.add_argument(
        "--max-messages",
        type=int,
        default=100,
        help="Maximum messages to fetch (default: 100)"
    )
    parser.add_argument(
        "--include-threads",
        action="store_true",
        default=True,
        help="Include thread replies (default: true)"
    )
    parser.add_argument(
        "--no-threads",
        action="store_true",
        help="Exclude thread replies"
    )
    parser.add_argument(
        "--search",
        nargs="+",
        help="Filter messages by keywords"
    )
    parser.add_argument(
        "--output",
        help="Custom output filename"
    )

    args = parser.parse_args()

    try:
        # Validate environment
        validate_environment()

        # Initialize Slack client
        client = WebClient(token=SLACK_BOT_TOKEN)

        print(f"🚀 Starting Slack News Fetcher")

        # Get channel ID
        if args.channel_id:
            channel_id = args.channel_id
        else:
            channel_id = find_channel_id(client, args.channel)
            if not channel_id:
                return 1

        # Calculate date range
        oldest = None
        latest = None

        if args.days_back:
            oldest_dt = datetime.now() - timedelta(days=args.days_back)
            oldest = oldest_dt.timestamp()
            print(f"📅 Fetching messages from last {args.days_back} days")
        elif args.start_date or args.end_date:
            if args.start_date:
                oldest_dt = datetime.strptime(args.start_date, "%Y-%m-%d")
                oldest = oldest_dt.timestamp()
            if args.end_date:
                latest_dt = datetime.strptime(args.end_date, "%Y-%m-%d")
                latest = (latest_dt + timedelta(days=1)).timestamp()  # End of day
            print(f"📅 Date range: {args.start_date or 'beginning'} to {args.end_date or 'now'}")
        else:
            # Default: last 24 hours
            oldest_dt = datetime.now() - timedelta(days=1)
            oldest = oldest_dt.timestamp()
            print(f"📅 Fetching messages from last 24 hours (default)")

        # Fetch messages
        messages = fetch_messages(
            client,
            channel_id,
            oldest=oldest,
            latest=latest,
            max_messages=args.max_messages
        )

        if not messages:
            print("⚠️  No messages found")
            return 0

        # Process messages
        include_threads = args.include_threads and not args.no_threads
        processed_messages = process_messages(
            client,
            messages,
            channel_id,
            include_threads=include_threads,
            search_keywords=args.search
        )

        # Build result object
        result = {
            "messages": processed_messages,
            "channel": args.channel,
            "channel_id": channel_id,
            "fetched_at": datetime.now().isoformat(),
            "total_count": len(processed_messages),
            "date_range": {
                "start": datetime.fromtimestamp(oldest).isoformat() if oldest else None,
                "end": datetime.fromtimestamp(latest).isoformat() if latest else None
            },
            "filters": {
                "keywords": args.search if args.search else None,
                "include_threads": include_threads
            }
        }

        # Save results
        save_results(result, args.channel, args.output)

        print("\n✅ Fetch completed successfully!")
        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
