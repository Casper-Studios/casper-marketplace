#!/usr/bin/env python3
"""
Slack Message Categorization
Uses OpenRouter (Grok) to filter useful messages and classify link types.

Usage:
    python execution/categorize_slack_messages.py <slack_json_file>
    python execution/categorize_slack_messages.py .tmp/slack_news_20251209_003501.json
    python execution/categorize_slack_messages.py .tmp/slack_news_20251209_003501.json --model x-ai/grok-4.1-fast
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import argparse
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OUTPUT_DIR = Path(__file__).parent.parent / ".tmp"

def validate_environment():
    """Validate required environment variables."""
    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY not found in environment. "
            "Please add it to your .env file.\n"
            "Get your key from: https://openrouter.ai/keys"
        )

def classify_link_type(url):
    """
    Classify link type based on domain.

    Args:
        url: URL string

    Returns:
        str: Link type (twitter, youtube, reddit, website)
    """
    url_lower = url.lower()

    if "twitter.com" in url_lower or "x.com" in url_lower:
        return "twitter"
    elif "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "youtube"
    elif "reddit.com" in url_lower:
        return "reddit"
    else:
        return "website"

def categorize_message(client, message, model="x-ai/grok-4.1-fast"):
    """
    Use AI to categorize a single message.

    Args:
        client: OpenAI client configured for OpenRouter
        message: Message dict with text and links
        model: Model ID to use

    Returns:
        dict: Categorization result
    """
    text = message.get("text", "")
    links = message.get("links", [])

    # Build prompt
    prompt = f"""Analyze this Slack message from a news channel.

Message: "{text}"
Links: {links if links else "none"}

Determine:
1. Is this useful content (news, articles, insights) or just casual chat?
2. Brief reasoning

Respond in JSON format ONLY:
{{
  "is_useful": true/false,
  "reasoning": "brief explanation"
}}"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a content categorization assistant. Respond only with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=150
        )

        # Parse AI response
        ai_response = response.choices[0].message.content.strip()

        # Try to extract JSON if wrapped in markdown code blocks
        if "```json" in ai_response:
            ai_response = ai_response.split("```json")[1].split("```")[0].strip()
        elif "```" in ai_response:
            ai_response = ai_response.split("```")[1].split("```")[0].strip()

        result = json.loads(ai_response)

        # Classify links if useful
        categorized_links = []
        if result.get("is_useful") and links:
            for link in links:
                link_type = classify_link_type(link)
                categorized_links.append({
                    "url": link,
                    "type": link_type
                })

        return {
            "is_useful": result.get("is_useful", False),
            "reasoning": result.get("reasoning", ""),
            "links": categorized_links
        }

    except json.JSONDecodeError as e:
        print(f"⚠️  JSON parse error for message: {text[:50]}...")
        print(f"   AI response: {ai_response[:100]}")
        return {
            "is_useful": False,
            "reasoning": "AI response parsing failed",
            "links": []
        }
    except Exception as e:
        print(f"⚠️  Error categorizing message: {str(e)}")
        return {
            "is_useful": False,
            "reasoning": f"Error: {str(e)}",
            "links": []
        }

def process_messages(messages, model="x-ai/grok-4.1-fast"):
    """
    Process all messages with AI categorization.

    Args:
        messages: List of message dicts
        model: OpenRouter model ID

    Returns:
        tuple: (categorized_messages, stats)
    """
    # Initialize OpenRouter client (using OpenAI SDK)
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    categorized = []
    stats = {
        "total_messages": len(messages),
        "useful_messages": 0,
        "not_useful_messages": 0,
        "by_type": {
            "twitter": 0,
            "youtube": 0,
            "reddit": 0,
            "website": 0
        }
    }

    print(f"🤖 Categorizing {len(messages)} messages with {model}...")

    for i, msg in enumerate(messages, 1):
        print(f"   Processing {i}/{len(messages)}...", end="\r")

        # Categorize with AI
        result = categorize_message(client, msg, model)

        # Merge with original message
        categorized_msg = {
            **msg,  # Keep original fields
            "is_useful": result["is_useful"],
            "ai_reasoning": result["reasoning"],
            "categorized_links": result["links"]
        }

        categorized.append(categorized_msg)

        # Update stats
        if result["is_useful"]:
            stats["useful_messages"] += 1

            # Count by link type
            for link in result["links"]:
                link_type = link["type"]
                stats["by_type"][link_type] = stats["by_type"].get(link_type, 0) + 1
        else:
            stats["not_useful_messages"] += 1

    print(f"\n✅ Categorization complete!")

    return categorized, stats

def save_results(data, input_filename):
    """
    Save categorized results to .tmp directory.

    Args:
        data: Complete result dict
        input_filename: Original input filename
    """
    OUTPUT_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"slack_news_categorized_{timestamp}.json"
    output_path = OUTPUT_DIR / filename

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Results saved to: {output_path}")
    print(f"\n📊 Statistics:")
    print(f"   Total messages: {data['stats']['total_messages']}")
    print(f"   Useful: {data['stats']['useful_messages']}")
    print(f"   Not useful: {data['stats']['not_useful_messages']}")

    if data['stats']['useful_messages'] > 0:
        print(f"\n🔗 Link types found:")
        for link_type, count in data['stats']['by_type'].items():
            if count > 0:
                print(f"   {link_type}: {count}")

    # Show sample useful messages
    useful_msgs = [m for m in data['messages'] if m['is_useful']]
    if useful_msgs:
        print(f"\n📬 Sample useful messages:")
        for i, msg in enumerate(useful_msgs[:3], 1):
            print(f"\n{i}. [{msg['datetime']}] {msg['user']}")
            print(f"   {msg['text'][:100]}{'...' if len(msg['text']) > 100 else ''}")
            if msg.get('categorized_links'):
                for link in msg['categorized_links']:
                    print(f"   🔗 {link['type']}: {link['url']}")

    return output_path

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Categorize Slack messages using AI"
    )
    parser.add_argument(
        "input_file",
        help="Path to Slack JSON file (from fetch_slack_news.py)"
    )
    parser.add_argument(
        "--model",
        default="x-ai/grok-4.1-fast",
        help="OpenRouter model ID (default: x-ai/grok-4.1-fast)"
    )
    parser.add_argument(
        "--filter-useful-only",
        action="store_true",
        help="Only save useful messages in output"
    )

    args = parser.parse_args()

    try:
        # Validate environment
        validate_environment()

        print(f"🚀 Starting Slack Message Categorization")

        # Load input file
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"❌ File not found: {input_path}")
            return 1

        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        messages = data.get("messages", [])
        if not messages:
            print("⚠️  No messages found in input file")
            return 0

        # Process messages
        categorized_messages, stats = process_messages(messages, args.model)

        # Filter if requested
        if args.filter_useful_only:
            categorized_messages = [m for m in categorized_messages if m["is_useful"]]
            print(f"\n🔍 Filtered to {len(categorized_messages)} useful messages")

        # Build output
        result = {
            "messages": categorized_messages,
            "stats": stats,
            "metadata": {
                "source_file": str(input_path),
                "model_used": args.model,
                "categorized_at": datetime.now().isoformat(),
                "filter_useful_only": args.filter_useful_only
            }
        }

        # Save results
        save_results(result, input_path.name)

        print("\n✅ Categorization completed successfully!")
        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
