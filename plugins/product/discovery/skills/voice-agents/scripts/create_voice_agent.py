#!/usr/bin/env python3
"""
Create ElevenLabs Voice Agent

Creates an ElevenLabs conversational AI agent for client discovery calls.
Fetches context from Google Drive and generates agent configuration using AI.

Directive: directives/create_voice_agent.md

Usage:
    # Create discovery agent
    python execution/create_voice_agent.py "Microsoft" --scope discovery --notes "CRM migration"

    # Create feedback agent
    python execution/create_voice_agent.py "Acme Corp" --scope feedback --notes "Post-project review"

    # Dry run (preview without creating)
    python execution/create_voice_agent.py "Test" --scope discovery --notes "Testing" --dry-run
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import requests

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# Load environment variables
load_dotenv()

# Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SHARED_DRIVE_ID = os.getenv("SHARED_DRIVE_ID", "")

# ElevenLabs webhook ID for post-call processing
POST_CALL_WEBHOOK_ID = os.getenv("ELEVENLABS_WEBHOOK_ID", "")


class VoiceAgentError(Exception):
    """Custom exception for voice agent operations."""
    pass


def authenticate_drive() -> GoogleDrive:
    """Authenticate with Google Drive."""
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("mycreds.txt")

    if gauth.credentials is None:
        print("First time setup - opening browser for authentication...")
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        print("Refreshing credentials...")
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile("mycreds.txt")
    return GoogleDrive(gauth)


def find_client_folder(drive: GoogleDrive, company_name: str) -> Optional[dict]:
    """
    Find client folder in shared drive.

    Args:
        drive: GoogleDrive instance
        company_name: Company name to search for

    Returns:
        Folder info dict or None
    """
    query = (
        f"'{SHARED_DRIVE_ID}' in parents and "
        "mimeType='application/vnd.google-apps.folder' and "
        "trashed=false"
    )

    file_list = drive.ListFile({
        'q': query,
        'supportsAllDrives': True,
        'includeItemsFromAllDrives': True,
        'corpora': 'drive',
        'driveId': SHARED_DRIVE_ID
    }).GetList()

    # Search for matching folder (pattern: [XX] Company Name)
    company_lower = company_name.lower()
    pattern = re.compile(r'^\[(\d+)\]\s*(.+)$')

    for folder in file_list:
        title = folder['title']
        match = pattern.match(title)

        if match:
            folder_name = match.group(2).strip().lower()
            if company_lower in folder_name or folder_name in company_lower:
                return {
                    'id': folder['id'],
                    'title': folder['title']
                }

    return None


def find_subfolder(drive: GoogleDrive, parent_id: str, name: str) -> Optional[dict]:
    """Find a subfolder by name within a parent folder."""
    query = (
        f"'{parent_id}' in parents and "
        "mimeType='application/vnd.google-apps.folder' and "
        f"title contains '{name}' and "
        "trashed=false"
    )

    file_list = drive.ListFile({
        'q': query,
        'supportsAllDrives': True,
        'includeItemsFromAllDrives': True
    }).GetList()

    if file_list:
        return {'id': file_list[0]['id'], 'title': file_list[0]['title']}
    return None


def find_file(drive: GoogleDrive, parent_id: str, name: str) -> Optional[dict]:
    """Find a file by name within a folder."""
    query = (
        f"'{parent_id}' in parents and "
        f"title contains '{name}' and "
        "trashed=false"
    )

    file_list = drive.ListFile({
        'q': query,
        'supportsAllDrives': True,
        'includeItemsFromAllDrives': True
    }).GetList()

    if file_list:
        return {'id': file_list[0]['id'], 'title': file_list[0]['title']}
    return None


def get_doc_content(drive: GoogleDrive, file_id: str) -> str:
    """
    Get content from a Google Doc.

    Args:
        drive: GoogleDrive instance
        file_id: Google Doc ID

    Returns:
        Document content as text
    """
    try:
        file = drive.CreateFile({'id': file_id})
        file.FetchMetadata()

        # Check if it's a Google Doc (needs export) or regular file
        mime_type = file.get('mimeType', '')

        if mime_type == 'application/vnd.google-apps.document':
            # Google Doc - export as plain text
            content = file.GetContentString(mimetype='text/plain')
        else:
            # Regular file - download directly
            content = file.GetContentString()

        return content
    except Exception as e:
        print(f"   Warning: Could not read document: {e}")
        return ""


def fetch_client_context(drive: GoogleDrive, company_name: str) -> dict:
    """
    Fetch all available context for a client from Google Drive.

    Args:
        drive: GoogleDrive instance
        company_name: Company name

    Returns:
        Dict with research_output and intro_transcript
    """
    context = {
        'research_output': '',
        'intro_transcript': ''
    }

    # Find client folder
    client_folder = find_client_folder(drive, company_name)
    if not client_folder:
        print(f"   Client folder not found for '{company_name}'")
        return context

    print(f"   Found client folder: {client_folder['title']}")

    # Find and read Research document
    research_file = find_file(drive, client_folder['id'], 'Research')
    if research_file:
        print(f"   Found research document: {research_file['title']}")
        context['research_output'] = get_doc_content(drive, research_file['id'])

    # Navigate to Discovery -> Meeting Transcripts -> Intro
    discovery_folder = find_subfolder(drive, client_folder['id'], 'Discovery')
    if discovery_folder:
        transcripts_folder = find_subfolder(drive, discovery_folder['id'], 'Meeting Transcripts')
        if transcripts_folder:
            intro_file = find_file(drive, transcripts_folder['id'], 'Intro')
            if intro_file:
                print(f"   Found intro transcript: {intro_file['title']}")
                context['intro_transcript'] = get_doc_content(drive, intro_file['id'])

    return context


def generate_agent_config(
    company_name: str,
    scope: str,
    notes: str,
    research_output: str = "",
    intro_transcript: str = ""
) -> dict:
    """
    Generate agent configuration using OpenRouter AI.

    Args:
        company_name: Client company name
        scope: Agent scope (discovery, feedback, etc.)
        notes: Additional context notes
        research_output: Research document content
        intro_transcript: Intro meeting transcript

    Returns:
        Dict with Agent Name, First Message, and Prompt
    """
    if not OPENROUTER_API_KEY:
        raise VoiceAgentError("OPENROUTER_API_KEY not set")

    prompt = f"""You are an expert Conversation Designer for Voice AI specializing in business consulting and client engagement. Your goal is to generate a configuration for an ElevenLabs ConvAI agent that operates on behalf of Casper Studios, a business automation and AI consulting agency.

## Understanding the Agent's Purpose

This agent represents Casper Studios and will be sent to the client's team to conduct conversations. The scope variable determines what type of conversation this agent should have:

- **discovery** (default if scope is empty or unclear): Interview client team members to understand their current operations, pain points, tech stack, workflows, and automation opportunities. Casper Studios will analyze the recordings to inform proposals and project scoping.
- **feedback**: Gather feedback on a completed project or ongoing engagement
- **check-in**: Conduct periodic relationship check-ins with existing clients
- **qualification**: Qualify inbound leads before scheduling sales calls
- **onboarding**: Guide new client contacts through initial information gathering

<input_data>
Client Company: {company_name}
Scope: {scope}
Additional Context from Casper Team: {notes}

---
Transcript from Casper Studios conversation with client (if available):
{intro_transcript if intro_transcript else "(Not available)"}

---
Research on the client company (if available):
{research_output if research_output else "(Not available)"}
</input_data>

## Your Task

Analyze all provided context deeply, then generate an agent configuration precisely tailored to this client and scope.

### Output Specification

Return a single valid JSON object with exactly three fields: "Agent Name", "First Message", and "Prompt"

---

#### Field 1: Agent Name

Format: `[Client Name] {{Scope}} Agent v1`
- Client name always in square brackets
- Scope capitalized appropriately
- Examples: "[Acme Corp] Discovery Agent v1", "[TechFlow] Feedback Agent v1"

---

#### Field 2: First Message

Write the exact opening the AI will speak when the call connects. Requirements:

**Content Structure:**
- Warm, professional greeting
- Introduce as calling on behalf of Casper Studios (not AS Casper Studios - the AI is a tool representing the agency)
- Reference the client company by name to confirm correct person
- Briefly state the purpose aligned with scope
- Set time expectations (typically 10-15 minutes)
- Ask for verbal confirmation before proceeding

**Voice Optimization:**
- Write for spoken delivery, not reading
- Use natural contractions (I'm, we're, you've)
- Short sentences. Conversational rhythm.
- No special characters, emojis, hashtags, or bullet points
- Punctuation guides pacing: periods for pauses, commas for flow

---

#### Field 3: Prompt

Write a comprehensive system prompt that governs the AI's entire behavior during the conversation. Include:

1. **Identity**: Who the AI is and what it represents
2. **Context**: Specific information about this client
3. **Tone and Communication Style**: How to conduct the conversation
4. **Conversation Flow**: 5-7 stages with specific questions for this client
5. **Interviewing Techniques**: How to dig deeper and follow up
6. **Guardrails**: What not to do (no pricing promises, no consulting advice)
7. **Response Behavior**: Keep responses concise, one question at a time

---

## STRICT OUTPUT RULES

1. **Raw JSON Only**: Return ONLY the JSON object. No markdown code fences. No text before or after.

2. **Newline Handling**: The Prompt field must be a single line in valid JSON. Replace all line breaks with the literal two-character sequence \\n

3. **Quote Handling**: Use single quotes (') inside all text values. Never use double quotes (") inside string content.

4. **Valid JSON**: The output must parse without errors.

## Output Format

{{
 "Agent Name": "[ClientName] Scope Agent v1",
 "First Message": "Hi there! This is an AI assistant calling on behalf of Casper Studios...",
 "Prompt": "# Identity\\nYou are a voice AI assistant...\\n\\n# Context\\n..."
}}"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "anthropic/claude-sonnet-4",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
    )

    if not response.ok:
        raise VoiceAgentError(f"OpenRouter API error: {response.status_code} {response.text}")

    result = response.json()
    content = result['choices'][0]['message']['content']

    # Parse JSON from response
    try:
        # Try to extract JSON if wrapped in code fences
        if '```' in content:
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
            if json_match:
                content = json_match.group(1)

        config = json.loads(content)
        return config
    except json.JSONDecodeError as e:
        raise VoiceAgentError(f"Failed to parse AI response as JSON: {e}\nResponse: {content[:500]}")


def create_elevenlabs_agent(config: dict) -> dict:
    """
    Create an ElevenLabs conversational AI agent.

    Args:
        config: Dict with Agent Name, First Message, and Prompt

    Returns:
        Dict with agent_id and other details
    """
    if not ELEVENLABS_API_KEY:
        raise VoiceAgentError("ELEVENLABS_API_KEY not set")

    payload = {
        "name": config["Agent Name"],
        "conversation_config": {
            "agent": {
                "prompt": {
                    "prompt": config["Prompt"]
                },
                "first_message": config["First Message"]
            }
        },
        "platform_settings": {
            "workspace_overrides": {
                "webhooks": {
                    "post_call_webhook_id": POST_CALL_WEBHOOK_ID
                }
            }
        }
    }

    response = requests.post(
        "https://api.elevenlabs.io/v1/convai/agents/create",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        },
        json=payload
    )

    if not response.ok:
        raise VoiceAgentError(f"ElevenLabs API error: {response.status_code} {response.text}")

    result = response.json()
    return result


def create_voice_agent(
    company_name: str,
    scope: str,
    notes: str,
    dry_run: bool = False
) -> dict:
    """
    Create a complete voice agent for a client.

    Args:
        company_name: Client company name
        scope: Agent scope (discovery, feedback, etc.)
        notes: Additional context
        dry_run: If True, generate config but don't create agent

    Returns:
        Dict with agent details
    """
    result = {
        'company_name': company_name,
        'scope': scope,
        'notes': notes
    }

    # Step 1: Fetch client context from Drive
    print("\n[Step 1/3] Fetching client context from Google Drive...")
    try:
        drive = authenticate_drive()
        context = fetch_client_context(drive, company_name)
        result['has_research'] = bool(context['research_output'])
        result['has_transcript'] = bool(context['intro_transcript'])
    except Exception as e:
        print(f"   Warning: Could not fetch Drive context: {e}")
        context = {'research_output': '', 'intro_transcript': ''}
        result['has_research'] = False
        result['has_transcript'] = False

    # Step 2: Generate agent configuration
    print("\n[Step 2/3] Generating agent configuration...")
    config = generate_agent_config(
        company_name=company_name,
        scope=scope,
        notes=notes,
        research_output=context['research_output'],
        intro_transcript=context['intro_transcript']
    )

    result['agent_name'] = config['Agent Name']
    result['first_message'] = config['First Message']
    result['prompt_preview'] = config['Prompt'][:500] + "..." if len(config['Prompt']) > 500 else config['Prompt']

    if dry_run:
        print("\n[Step 3/3] Dry run - skipping agent creation")
        result['dry_run'] = True
        result['config'] = config
        return result

    # Step 3: Create ElevenLabs agent
    print("\n[Step 3/3] Creating ElevenLabs agent...")
    agent = create_elevenlabs_agent(config)

    result['agent_id'] = agent.get('agent_id')
    result['agent_url'] = f"https://elevenlabs.io/app/conversational-ai/agents/{agent.get('agent_id')}"

    return result


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Create an ElevenLabs voice agent for client calls",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create discovery agent
  %(prog)s "Microsoft" --scope discovery --notes "CRM migration project"

  # Create feedback agent
  %(prog)s "Acme Corp" --scope feedback --notes "Post-project review"

  # Dry run (preview without creating)
  %(prog)s "Test" --scope discovery --notes "Testing" --dry-run

Scopes:
  discovery     - Interview team about operations and pain points (default)
  feedback      - Gather feedback on completed projects
  check-in      - Periodic relationship check-ins
  qualification - Qualify inbound leads
  onboarding    - Guide new contacts through info gathering
        """
    )

    parser.add_argument("company_name", help="Client company name")
    parser.add_argument("--scope", required=True,
                        choices=['discovery', 'feedback', 'check-in', 'qualification', 'onboarding'],
                        help="Agent scope/purpose")
    parser.add_argument("--notes", required=True, help="Additional context about the client/project")
    parser.add_argument("--dry-run", action="store_true", help="Generate config without creating agent")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    try:
        print(f"\n{'=' * 60}")
        print(f"  CREATE VOICE AGENT: {args.company_name}")
        print(f"{'=' * 60}")
        print(f"\n  Scope: {args.scope}")
        print(f"  Notes: {args.notes[:50]}{'...' if len(args.notes) > 50 else ''}")

        result = create_voice_agent(
            company_name=args.company_name,
            scope=args.scope,
            notes=args.notes,
            dry_run=args.dry_run
        )

        if args.json:
            print("\n" + json.dumps(result, indent=2))
        else:
            print(f"\n{'=' * 60}")
            if result.get('dry_run'):
                print("  DRY RUN COMPLETE")
            else:
                print("  VOICE AGENT CREATED")
            print(f"{'=' * 60}")
            print(f"\n  Agent Name: {result['agent_name']}")
            if result.get('agent_id'):
                print(f"  Agent ID: {result['agent_id']}")
                print(f"  Agent URL: {result['agent_url']}")
            print(f"\n  Context Used:")
            print(f"    Research: {'Yes' if result.get('has_research') else 'No'}")
            print(f"    Transcript: {'Yes' if result.get('has_transcript') else 'No'}")
            print(f"\n  First Message Preview:")
            print(f"    {result['first_message'][:150]}...")

        return 0

    except VoiceAgentError as e:
        print(f"\nError: {e}")
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
