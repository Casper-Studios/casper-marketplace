#!/usr/bin/env python3
"""
Slack Search and Channel Reader

Search for channels and read recent messages from Slack.
Used for client overview and other intelligence gathering.

Directive: directives/slack_search.md

Usage:
    # Search for a channel
    python execution/slack_search.py search "internal-microsoft"

    # Read messages from a channel
    python execution/slack_search.py read "internal-microsoft" --days 7

    # Get channel by ID
    python execution/slack_search.py read-id "C1234567890" --days 14
"""

import os
import re
import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import Optional, List
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load environment variables (override=True to get fresh values)
load_dotenv(override=True)

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")


class SlackSearchError(Exception):
    """Custom exception for Slack search operations."""
    pass


def get_client() -> WebClient:
    """Get authenticated Slack client."""
    if not SLACK_BOT_TOKEN:
        raise SlackSearchError(
            "SLACK_BOT_TOKEN not set. Add it to your .env file."
        )
    return WebClient(token=SLACK_BOT_TOKEN)


def search_channels(query: str, limit: int = 20, include_private: bool = True) -> List[dict]:
    """
    Search for channels matching a query.

    Args:
        query: Search query (partial channel name)
        limit: Maximum results to return
        include_private: Whether to include private channels (requires groups:read)

    Returns:
        List of matching channels with id, name, is_private
    """
    client = get_client()

    try:
        # List all channels with pagination
        channels = []
        cursor = None

        # Determine channel types to query
        channel_types = ["public_channel"]
        if include_private:
            channel_types.append("private_channel")

        while len(channels) < limit:
            params = {
                "types": ",".join(channel_types),
                "limit": 200
            }
            if cursor:
                params["cursor"] = cursor

            try:
                result = client.conversations_list(**params)
                channels.extend(result["channels"])
            except SlackApiError as e:
                # If missing scope for private channels, retry with public only
                if "missing_scope" in str(e) and include_private:
                    channel_types = ["public_channel"]
                    params["types"] = "public_channel"
                    result = client.conversations_list(**params)
                    channels.extend(result["channels"])
                else:
                    raise

            if not result.get("response_metadata", {}).get("next_cursor"):
                break
            cursor = result["response_metadata"]["next_cursor"]

        # Filter by query
        query_lower = query.lower()
        matches = []

        for channel in channels:
            name = channel["name"].lower()
            if query_lower in name:
                matches.append({
                    "id": channel["id"],
                    "name": channel["name"],
                    "is_private": channel.get("is_private", False),
                    "num_members": channel.get("num_members", 0),
                    "purpose": channel.get("purpose", {}).get("value", "")
                })

                if len(matches) >= limit:
                    break

        return matches

    except SlackApiError as e:
        raise SlackSearchError(f"Failed to search channels: {e.response['error']}")


def find_channel(name: str) -> Optional[dict]:
    """
    Find a specific channel by name.

    Args:
        name: Exact channel name (without #)

    Returns:
        Channel info or None if not found
    """
    name = name.lstrip("#")
    results = search_channels(name, limit=100)

    for channel in results:
        if channel["name"] == name:
            return channel

    return None


def get_user_name(client: WebClient, user_id: str, cache: dict) -> str:
    """Get user's display name with caching."""
    if user_id in cache:
        return cache[user_id]

    try:
        result = client.users_info(user=user_id)
        user = result["user"]
        name = user.get("real_name") or user.get("name", user_id)
        cache[user_id] = name
        return name
    except SlackApiError:
        return user_id


def read_channel_messages(
    channel_id: str,
    days_back: int = 7,
    limit: int = 50,
    include_threads: bool = True
) -> dict:
    """
    Read recent messages from a channel.

    Args:
        channel_id: Channel ID
        days_back: Number of days to look back
        limit: Maximum messages to fetch
        include_threads: Whether to include thread replies

    Returns:
        Dict with channel info and messages
    """
    client = get_client()
    user_cache = {}

    # Calculate timestamp for oldest message
    oldest_dt = datetime.now() - timedelta(days=days_back)
    oldest_ts = oldest_dt.timestamp()

    try:
        # Get channel info
        try:
            info = client.conversations_info(channel=channel_id)
            channel_name = info["channel"]["name"]
        except SlackApiError:
            channel_name = channel_id

        # Fetch messages
        messages = []
        cursor = None

        while len(messages) < limit:
            params = {
                "channel": channel_id,
                "limit": min(100, limit - len(messages)),
                "oldest": str(oldest_ts)
            }
            if cursor:
                params["cursor"] = cursor

            result = client.conversations_history(**params)
            messages.extend(result["messages"])

            if not result.get("has_more"):
                break
            cursor = result.get("response_metadata", {}).get("next_cursor")

        # Process messages
        processed = []
        for msg in messages:
            # Skip system messages
            if msg.get("subtype") in ["channel_join", "channel_leave", "bot_message"]:
                continue

            user_id = msg.get("user", "")
            user_name = get_user_name(client, user_id, user_cache) if user_id else "Unknown"
            ts = float(msg.get("ts", 0))
            dt = datetime.fromtimestamp(ts)

            message_data = {
                "timestamp": msg.get("ts"),
                "datetime": dt.isoformat(),
                "date": dt.strftime("%Y-%m-%d"),
                "user": user_name,
                "text": msg.get("text", ""),
                "reactions": [
                    {"name": r["name"], "count": r["count"]}
                    for r in msg.get("reactions", [])
                ],
                "thread_replies": []
            }

            # Get thread replies if any
            if include_threads and msg.get("reply_count", 0) > 0:
                try:
                    thread_result = client.conversations_replies(
                        channel=channel_id,
                        ts=msg.get("ts")
                    )
                    # Skip first message (it's the parent)
                    for reply in thread_result["messages"][1:]:
                        reply_user_id = reply.get("user", "")
                        reply_user_name = get_user_name(client, reply_user_id, user_cache)
                        reply_ts = float(reply.get("ts", 0))
                        reply_dt = datetime.fromtimestamp(reply_ts)

                        message_data["thread_replies"].append({
                            "datetime": reply_dt.isoformat(),
                            "user": reply_user_name,
                            "text": reply.get("text", "")
                        })
                except SlackApiError:
                    pass

            processed.append(message_data)

        return {
            "channel_id": channel_id,
            "channel_name": channel_name,
            "days_back": days_back,
            "message_count": len(processed),
            "messages": processed
        }

    except SlackApiError as e:
        error = e.response.get("error", "unknown")
        if error == "not_in_channel":
            raise SlackSearchError(
                f"Bot is not in channel {channel_id}. "
                "Invite the bot to the channel first."
            )
        raise SlackSearchError(f"Failed to read channel: {error}")


def extract_key_info(messages: List[dict], user_name: str = None) -> dict:
    """
    Extract key information from messages for summary.

    Args:
        messages: List of processed messages
        user_name: User's name to highlight mentions

    Returns:
        Dict with discussions, decisions, action_items, mentions
    """
    discussions = []
    decisions = []
    action_items = []
    user_mentions = []

    decision_keywords = ["decided", "agreed", "finalized", "confirmed", "approved", "signed off"]
    action_keywords = ["todo", "to do", "action item", "need to", "will do", "follow up", "next step"]

    for msg in messages:
        text_lower = msg["text"].lower()

        # Check for decisions
        if any(kw in text_lower for kw in decision_keywords):
            decisions.append({
                "date": msg["date"],
                "user": msg["user"],
                "text": msg["text"][:200]
            })

        # Check for action items
        if any(kw in text_lower for kw in action_keywords):
            action_items.append({
                "date": msg["date"],
                "user": msg["user"],
                "text": msg["text"][:200]
            })

        # Check for user mentions
        if user_name and user_name.lower() in text_lower:
            user_mentions.append({
                "date": msg["date"],
                "user": msg["user"],
                "text": msg["text"][:200]
            })

        # Add to general discussions (top messages by reactions)
        reaction_count = sum(r["count"] for r in msg.get("reactions", []))
        if reaction_count > 0 or msg.get("thread_replies"):
            discussions.append({
                "date": msg["date"],
                "user": msg["user"],
                "text": msg["text"][:200],
                "reactions": reaction_count,
                "replies": len(msg.get("thread_replies", []))
            })

    # Sort discussions by engagement
    discussions.sort(key=lambda x: x["reactions"] + x["replies"], reverse=True)

    return {
        "top_discussions": discussions[:5],
        "decisions": decisions[:5],
        "action_items": action_items[:10],
        "user_mentions": user_mentions[:10]
    }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Search and read Slack channels"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for channels")
    search_parser.add_argument("query", help="Channel name to search for")
    search_parser.add_argument("--limit", type=int, default=10, help="Max results")

    # Read command (by name)
    read_parser = subparsers.add_parser("read", help="Read channel messages")
    read_parser.add_argument("channel", help="Channel name")
    read_parser.add_argument("--days", type=int, default=7, help="Days to look back")
    read_parser.add_argument("--limit", type=int, default=50, help="Max messages")
    read_parser.add_argument("--no-threads", action="store_true", help="Skip thread replies")

    # Read by ID command
    read_id_parser = subparsers.add_parser("read-id", help="Read channel by ID")
    read_id_parser.add_argument("channel_id", help="Channel ID")
    read_id_parser.add_argument("--days", type=int, default=7, help="Days to look back")
    read_id_parser.add_argument("--limit", type=int, default=50, help="Max messages")

    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Get channel summary")
    summary_parser.add_argument("channel", help="Channel name")
    summary_parser.add_argument("--days", type=int, default=7, help="Days to look back")
    summary_parser.add_argument("--user", help="Your name to highlight mentions")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "search":
            print(f"Searching for channels matching: {args.query}")
            results = search_channels(args.query, args.limit)

            if not results:
                print("No channels found")
                return 0

            print(f"\nFound {len(results)} channels:")
            for ch in results:
                private = " (private)" if ch["is_private"] else ""
                print(f"  #{ch['name']}{private} - {ch['num_members']} members")
                if ch["purpose"]:
                    print(f"    {ch['purpose'][:60]}...")

        elif args.command == "read":
            channel = find_channel(args.channel)
            if not channel:
                print(f"Channel #{args.channel} not found")
                return 1

            print(f"Reading #{channel['name']} (last {args.days} days)...")
            result = read_channel_messages(
                channel["id"],
                days_back=args.days,
                limit=args.limit,
                include_threads=not args.no_threads
            )

            print(f"\nFound {result['message_count']} messages")
            print(json.dumps(result, indent=2))

        elif args.command == "read-id":
            print(f"Reading channel {args.channel_id} (last {args.days} days)...")
            result = read_channel_messages(
                args.channel_id,
                days_back=args.days,
                limit=args.limit
            )

            print(f"\nFound {result['message_count']} messages")
            print(json.dumps(result, indent=2))

        elif args.command == "summary":
            channel = find_channel(args.channel)
            if not channel:
                print(f"Channel #{args.channel} not found")
                return 1

            print(f"Getting summary for #{channel['name']}...")
            result = read_channel_messages(
                channel["id"],
                days_back=args.days,
                limit=100
            )

            summary = extract_key_info(result["messages"], args.user)

            print(f"\n=== Channel Summary: #{channel['name']} ===")
            print(f"Period: Last {args.days} days")
            print(f"Total messages: {result['message_count']}")

            if summary["top_discussions"]:
                print(f"\nTop Discussions:")
                for d in summary["top_discussions"][:3]:
                    print(f"  [{d['date']}] {d['user']}: {d['text'][:80]}...")

            if summary["decisions"]:
                print(f"\nDecisions/Agreements:")
                for d in summary["decisions"]:
                    print(f"  [{d['date']}] {d['user']}: {d['text'][:80]}...")

            if summary["action_items"]:
                print(f"\nAction Items:")
                for a in summary["action_items"]:
                    print(f"  [{a['date']}] {a['user']}: {a['text'][:80]}...")

            if args.user and summary["user_mentions"]:
                print(f"\nMentions of {args.user}:")
                for m in summary["user_mentions"]:
                    print(f"  [{m['date']}] {m['user']}: {m['text'][:80]}...")

        return 0

    except SlackSearchError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
