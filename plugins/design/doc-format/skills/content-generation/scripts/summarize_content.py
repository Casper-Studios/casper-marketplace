#!/usr/bin/env python3
"""
Content Summarizer
Summarizes scraped content using Claude Haiku 4.5 via OpenRouter.

Usage:
    python execution/summarize_content.py "Content to summarize" --type twitter
    python execution/summarize_content.py --file .tmp/scraped_twitter_123.json
    echo "Content" | python execution/summarize_content.py --stdin --type youtube
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
MODEL = "anthropic/claude-haiku-4.5"
OUTPUT_DIR = Path(__file__).parent.parent / ".tmp"


def validate_environment():
    """Validate required environment variables."""
    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY not found in environment. "
            "Please add it to your .env file.\n"
            "Get your key from: https://openrouter.ai/keys"
        )


def get_system_prompt(content_type):
    """
    Get content-type specific system prompt.

    Args:
        content_type: One of 'twitter', 'youtube', 'reddit', 'website'

    Returns:
        str: System prompt
    """
    prompts = {
        "twitter": """You are a content analyst specializing in social media. Summarize this tweet concisely.
Focus on: the main point or claim, why it might be notable or newsworthy, and any key information shared.
Keep the summary brief but informative (2-3 sentences max).

Return ONLY valid JSON in this exact format:
{"summary": "...", "key_points": ["point1", "point2"], "topics": ["topic1", "topic2"], "sentiment": "positive|neutral|negative"}""",

        "youtube": """You are a video content analyst. Summarize this video transcript or description.
Focus on: main topics covered, key takeaways and insights, and any actionable conclusions.
Keep the summary comprehensive but concise (3-5 sentences).

Return ONLY valid JSON in this exact format:
{"summary": "...", "key_points": ["point1", "point2", "point3"], "topics": ["topic1", "topic2"], "sentiment": "positive|neutral|negative"}""",

        "reddit": """You are a discussion analyst. Summarize this Reddit post or discussion.
Focus on: the main argument or question, key points from the discussion, and community sentiment.
Keep the summary balanced and informative (2-4 sentences).

Return ONLY valid JSON in this exact format:
{"summary": "...", "key_points": ["point1", "point2"], "topics": ["topic1", "topic2"], "sentiment": "positive|neutral|negative"}""",

        "website": """You are an article analyst. Summarize this web content or article.
Focus on: the main thesis or purpose, key facts and information, and conclusions or takeaways.
Keep the summary clear and comprehensive (3-5 sentences).

Return ONLY valid JSON in this exact format:
{"summary": "...", "key_points": ["point1", "point2", "point3"], "topics": ["topic1", "topic2"], "sentiment": "positive|neutral|negative"}"""
    }

    return prompts.get(content_type, prompts["website"])


def summarize_content(content, content_type="website", max_content_length=10000):
    """
    Summarize content using Claude Haiku 4.5.

    Args:
        content: Text content to summarize
        content_type: Type of content for context
        max_content_length: Max chars to process

    Returns:
        dict: Summary result with metadata
    """
    if not content or not content.strip():
        return {
            "error": "Empty content provided",
            "summary": "",
            "key_points": [],
            "topics": [],
            "sentiment": "neutral"
        }

    # Truncate if too long
    original_length = len(content)
    if len(content) > max_content_length:
        content = content[:max_content_length] + "... [truncated]"

    # Initialize OpenRouter client
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    system_prompt = get_system_prompt(content_type)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            temperature=0.3,
            max_tokens=500
        )

        ai_response = response.choices[0].message.content.strip()

        # Try to parse JSON response
        try:
            # Handle markdown code blocks
            if "```json" in ai_response:
                ai_response = ai_response.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_response:
                ai_response = ai_response.split("```")[1].split("```")[0].strip()

            result = json.loads(ai_response)

            return {
                "original_length": original_length,
                "summary": result.get("summary", ""),
                "key_points": result.get("key_points", []),
                "topics": result.get("topics", []),
                "sentiment": result.get("sentiment", "neutral"),
                "model_used": MODEL,
                "truncated": original_length > max_content_length
            }

        except json.JSONDecodeError:
            # If JSON parsing fails, use raw response as summary
            return {
                "original_length": original_length,
                "summary": ai_response,
                "key_points": [],
                "topics": [],
                "sentiment": "neutral",
                "model_used": MODEL,
                "truncated": original_length > max_content_length,
                "parse_warning": "Could not parse structured response"
            }

    except Exception as e:
        return {
            "error": str(e),
            "original_length": original_length,
            "summary": "",
            "key_points": [],
            "topics": [],
            "sentiment": "neutral"
        }


def summarize_scraped_file(file_path):
    """
    Summarize content from a scraped JSON file.

    Args:
        file_path: Path to scraped JSON file

    Returns:
        dict: Summary result
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    content_type = data.get("type", "website")
    content_data = data.get("content", {})

    # Extract text based on content type
    if content_type == "twitter":
        text = content_data.get("text", "")
    elif content_type == "youtube":
        # Prefer subtitles/transcript, fall back to description
        text = content_data.get("subtitles", "") or content_data.get("description", "")
        if content_data.get("title"):
            text = f"Title: {content_data['title']}\n\n{text}"
    elif content_type == "reddit":
        text = content_data.get("body", "") or content_data.get("title", "")
        if content_data.get("title") and content_data.get("body"):
            text = f"Title: {content_data['title']}\n\n{content_data['body']}"
    else:
        text = content_data.get("text", "")
        if content_data.get("title"):
            text = f"Title: {content_data['title']}\n\n{text}"

    return summarize_content(text, content_type)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Summarize content using Claude Haiku 4.5"
    )
    parser.add_argument(
        "content",
        nargs="?",
        help="Content to summarize (or use --file/--stdin)"
    )
    parser.add_argument(
        "--file",
        help="Path to scraped JSON file to summarize"
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read content from stdin"
    )
    parser.add_argument(
        "--type",
        choices=["twitter", "youtube", "reddit", "website"],
        default="website",
        help="Content type for context-aware summarization"
    )
    parser.add_argument(
        "--output",
        help="Custom output filename"
    )

    args = parser.parse_args()

    try:
        # Validate environment
        validate_environment()

        # Get content
        if args.file:
            print(f"📄 Reading from file: {args.file}")
            result = summarize_scraped_file(args.file)
        elif args.stdin:
            print("📥 Reading from stdin...")
            content = sys.stdin.read()
            result = summarize_content(content, args.type)
        elif args.content:
            result = summarize_content(args.content, args.type)
        else:
            print("❌ No content provided. Use positional arg, --file, or --stdin")
            return 1

        if "error" in result and result["error"]:
            print(f"❌ Error: {result['error']}")
            return 1

        # Save results
        OUTPUT_DIR.mkdir(exist_ok=True)

        if args.output:
            filename = args.output
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"summary_{timestamp}.json"

        output_path = OUTPUT_DIR / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Saved to: {output_path}")
        print(f"\n📝 Summary ({result.get('original_length', 0)} chars -> {len(result.get('summary', ''))} chars):")
        print(f"   {result.get('summary', 'No summary generated')}")

        if result.get("key_points"):
            print(f"\n🔑 Key Points:")
            for point in result["key_points"]:
                print(f"   • {point}")

        if result.get("topics"):
            print(f"\n🏷️  Topics: {', '.join(result['topics'])}")

        print(f"📊 Sentiment: {result.get('sentiment', 'unknown')}")

        print("\n✅ Summarization completed!")
        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
