#!/usr/bin/env python3
"""
Create Slack Channel

Creates a public or private Slack channel with standardized naming.

Directive: directives/create_slack_channel.md

Usage:
    # Create prospect channel
    python execution/create_slack_channel.py "Microsoft" --prefix prospect

    # Create client channel
    python execution/create_slack_channel.py "Acme Corp" --prefix client

    # Create private channel
    python execution/create_slack_channel.py "Secret Project" --private
"""

import os
import re
import sys
import argparse
import json
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load environment variables
load_dotenv()

# Configuration
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")


class SlackChannelError(Exception):
    """Custom exception for Slack channel operations."""
    pass


def sanitize_channel_name(name: str, prefix: str = None) -> str:
    """
    Convert a name to a valid Slack channel name.

    Slack channel names must:
    - Be lowercase
    - Contain only letters, numbers, hyphens, underscores
    - Be 80 characters or less

    Args:
        name: The name to convert (e.g., "Acme Corp")
        prefix: Optional prefix (e.g., "prospect", "client")

    Returns:
        Valid Slack channel name (e.g., "prospect-acme-corp")
    """
    # Convert to lowercase
    channel_name = name.lower()

    # Replace spaces and special chars with hyphens
    channel_name = re.sub(r'[^a-z0-9]+', '-', channel_name)

    # Remove leading/trailing hyphens
    channel_name = channel_name.strip('-')

    # Add prefix if provided
    if prefix:
        prefix = prefix.lower().strip('-')
        channel_name = f"{prefix}-{channel_name}"

    # Truncate to 80 chars
    if len(channel_name) > 80:
        channel_name = channel_name[:80].rstrip('-')

    return channel_name


def create_channel(
    name: str,
    prefix: str = None,
    is_private: bool = False,
    description: str = None
) -> dict:
    """
    Create a Slack channel.

    Args:
        name: Base name for the channel (e.g., "Microsoft")
        prefix: Optional prefix (e.g., "prospect", "client")
        is_private: Whether to create a private channel
        description: Optional channel topic/description

    Returns:
        Dict with channel_id, channel_name, channel_url

    Raises:
        SlackChannelError: If channel creation fails
    """
    if not SLACK_BOT_TOKEN:
        raise SlackChannelError(
            "SLACK_BOT_TOKEN not set. Add it to your .env file."
        )

    client = WebClient(token=SLACK_BOT_TOKEN)

    # Generate valid channel name
    channel_name = sanitize_channel_name(name, prefix)

    try:
        # Create the channel
        response = client.conversations_create(
            name=channel_name,
            is_private=is_private
        )

        channel_id = response["channel"]["id"]
        created_name = response["channel"]["name"]

        # Set channel topic/description if provided
        if description:
            try:
                client.conversations_setTopic(
                    channel=channel_id,
                    topic=description
                )
            except SlackApiError as e:
                # Non-fatal, just log it
                print(f"   Warning: Could not set topic: {e.response['error']}")

        # Get workspace domain for URL
        # Channel URLs follow pattern: https://{workspace}.slack.com/archives/{channel_id}
        try:
            team_info = client.team_info()
            workspace_domain = team_info["team"]["domain"]
            channel_url = f"https://{workspace_domain}.slack.com/archives/{channel_id}"
        except SlackApiError:
            # Fallback URL format
            channel_url = f"https://slack.com/app_redirect?channel={channel_id}"

        return {
            "channel_id": channel_id,
            "channel_name": created_name,
            "channel_url": channel_url,
            "is_private": is_private
        }

    except SlackApiError as e:
        error = e.response.get("error", "unknown_error")

        # Handle common errors
        if error == "name_taken":
            # Channel exists, try to find it
            print(f"   Channel '{channel_name}' already exists, looking it up...")
            return find_channel(channel_name)
        elif error == "invalid_name_specials":
            raise SlackChannelError(
                f"Invalid channel name '{channel_name}'. "
                "Names can only contain lowercase letters, numbers, hyphens, underscores."
            )
        elif error == "missing_scope":
            raise SlackChannelError(
                f"Missing Slack permission. Ensure bot has 'channels:manage' scope. "
                f"Error: {error}"
            )
        else:
            raise SlackChannelError(f"Failed to create channel: {error}")


def find_channel(name: str) -> dict:
    """
    Find an existing channel by name.

    Args:
        name: Channel name to find

    Returns:
        Dict with channel_id, channel_name, channel_url
    """
    client = WebClient(token=SLACK_BOT_TOKEN)

    try:
        # List public channels
        response = client.conversations_list(
            types="public_channel,private_channel",
            limit=1000
        )

        for channel in response["channels"]:
            if channel["name"] == name:
                channel_id = channel["id"]

                # Get workspace domain for URL
                try:
                    team_info = client.team_info()
                    workspace_domain = team_info["team"]["domain"]
                    channel_url = f"https://{workspace_domain}.slack.com/archives/{channel_id}"
                except SlackApiError:
                    channel_url = f"https://slack.com/app_redirect?channel={channel_id}"

                return {
                    "channel_id": channel_id,
                    "channel_name": name,
                    "channel_url": channel_url,
                    "is_private": channel.get("is_private", False),
                    "existed": True
                }

        raise SlackChannelError(f"Channel '{name}' not found")

    except SlackApiError as e:
        raise SlackChannelError(f"Failed to list channels: {e.response['error']}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Create a Slack channel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create prospect channel
  %(prog)s "Microsoft" --prefix prospect

  # Create client channel
  %(prog)s "Acme Corp" --prefix client

  # Create private channel with description
  %(prog)s "Project X" --private --description "Internal project discussion"
        """
    )

    parser.add_argument("name", help="Base name for the channel")
    parser.add_argument("--prefix", help="Channel prefix (e.g., prospect, client)")
    parser.add_argument("--private", action="store_true", help="Create private channel")
    parser.add_argument("--description", help="Channel topic/description")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    try:
        print(f"Creating Slack channel for: {args.name}")

        result = create_channel(
            name=args.name,
            prefix=args.prefix,
            is_private=args.private,
            description=args.description
        )

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            existed = result.get("existed", False)
            status = "Found existing" if existed else "Created"
            print(f"\n{status} channel:")
            print(f"  Name: #{result['channel_name']}")
            print(f"  ID: {result['channel_id']}")
            print(f"  URL: {result['channel_url']}")
            print(f"  Private: {result['is_private']}")

        return 0

    except SlackChannelError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
