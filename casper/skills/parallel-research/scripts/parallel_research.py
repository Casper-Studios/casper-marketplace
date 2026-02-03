#!/usr/bin/env python3
"""
Parallel AI Research & Enrichment
Comprehensive web research, entity discovery, and data enrichment.

Usage:
    # Quick Q&A with web citations
    python execution/parallel_research.py chat "What is the latest funding round for Anthropic?"

    # Deep research report (markdown)
    python execution/parallel_research.py deep-research "Research the competitive landscape of AI code editors" --processor ultra

    # Find entities matching criteria (dataset generation)
    python execution/parallel_research.py findall "FindAll AI startups in SF that raised Series A in 2024" --generator core --match-limit 50

    # Enrich existing data with web research
    python execution/parallel_research.py enrich "Anthropic" --fields "latest_funding_round,total_funding,employee_count"

    # Save outputs
    python execution/parallel_research.py deep-research "Market trends in AI" --processor ultra --save-drive "Research/AI Trends"
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("PARALLEL_API_KEY")
CHAT_API_URL = "https://api.parallel.ai/chat/completions"
TASK_API_URL = "https://api.parallel.ai/v1/tasks/runs"
FINDALL_INGEST_URL = "https://api.parallel.ai/v1beta/findall/ingest"
FINDALL_RUNS_URL = "https://api.parallel.ai/v1beta/findall/runs"

# Output directories
OUTPUT_DIR = Path(".tmp/parallel_research")
REPORTS_DIR = OUTPUT_DIR / "reports"
DATASETS_DIR = OUTPUT_DIR / "datasets"
ENRICHMENTS_DIR = OUTPUT_DIR / "enrichments"

# Create output directories
for dir_path in [REPORTS_DIR, DATASETS_DIR, ENRICHMENTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

def validate_api_key():
    """Validate API key is set."""
    if not API_KEY:
        raise ValueError(
            "PARALLEL_API_KEY not found in environment!\n\n"
            "Setup:\n"
            "1. Get API key from https://platform.parallel.ai/settings/api-keys\n"
            "2. Add to .env: PARALLEL_API_KEY=your_key_here\n"
        )

def chat_with_web(query: str, system_prompt: Optional[str] = None) -> Dict:
    """
    Quick Q&A with web citations.

    Args:
        query: User question
        system_prompt: Optional system message

    Returns:
        Dict with answer and citations
    """
    print(f"💬 Chat with Web")
    print(f"   Query: {query[:80]}...")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": query})

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "speed",
        "messages": messages,
        "stream": False
    }

    response = requests.post(CHAT_API_URL, headers=headers, json=payload, timeout=120)
    response.raise_for_status()

    result = response.json()

    answer = result["choices"][0]["message"]["content"]
    citations = result.get("citations", [])

    print(f"✅ Answer received ({len(answer)} chars)")
    print(f"   Citations: {len(citations)}")

    return {
        "answer": answer,
        "citations": citations,
        "raw_response": result
    }

def deep_research(
    objective: str,
    processor: str = "ultra",
    fast: bool = False
) -> Dict:
    """
    Start comprehensive deep research task.

    Args:
        objective: Research objective
        processor: Processor tier (lite, base, core, pro, ultra, ultra2x, ultra4x, ultra8x)
        fast: Use fast variant (2-5x speed, same cost)

    Returns:
        Dict with markdown report and citations
    """
    processor_name = f"{processor}-fast" if fast else processor

    print(f"🔬 Deep Research")
    print(f"   Objective: {objective[:80]}...")
    print(f"   Processor: {processor_name}")

    # Cost estimates
    cost_per_1k = {
        "lite": 5, "base": 10, "core": 25, "core2x": 50,
        "pro": 100, "ultra": 300, "ultra2x": 600,
        "ultra4x": 1200, "ultra8x": 2400
    }
    estimated_cost = cost_per_1k.get(processor, 0) / 1000
    print(f"   Estimated cost: ${estimated_cost:.3f}")

    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "processor": processor_name,
        "input": objective
    }

    # Submit task
    print(f"🚀 Submitting research task...")
    response = requests.post(TASK_API_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()

    task_data = response.json()
    run_id = task_data["run_id"]

    print(f"   Task ID: {run_id}")
    print(f"⏳ Waiting for completion (this may take 5min-2hr)...")

    # Poll for results (blocking)
    result_url = f"{TASK_API_URL}/{run_id}/result"
    start_time = time.time()

    while True:
        try:
            result_response = requests.get(result_url, headers=headers, timeout=300)
            result_response.raise_for_status()

            result = result_response.json()

            if result.get("status") == "completed":
                elapsed = time.time() - start_time
                print(f"✅ Research completed in {elapsed:.1f}s")

                content = result.get("result", {}).get("content", "")
                basis = result.get("result", {}).get("basis", [])

                print(f"   Report length: {len(content)} chars")
                print(f"   Citations: {len(basis)}")

                return {
                    "run_id": run_id,
                    "content": content,
                    "citations": basis,
                    "raw_response": result
                }

            elif result.get("status") == "failed":
                error = result.get("error", "Unknown error")
                raise Exception(f"Research task failed: {error}")

            # Still processing
            elapsed = time.time() - start_time
            print(f"   Status: {result.get('status', 'processing')} ({elapsed:.0f}s elapsed)")
            time.sleep(10)

        except requests.exceptions.Timeout:
            # Continue polling on timeout
            continue

def findall_entities(
    objective: str,
    generator: str = "core",
    match_limit: int = 100,
    preview: bool = False
) -> Dict:
    """
    Generate dataset of entities matching criteria.

    Args:
        objective: Natural language objective
        generator: Generator tier (base, core, pro)
        match_limit: Max entities to return
        preview: Preview mode (~10 candidates)

    Returns:
        Dict with matched entities and enrichments
    """
    print(f"🔍 FindAll Dataset Generation")
    print(f"   Objective: {objective[:80]}...")
    print(f"   Generator: {generator}")
    print(f"   Match limit: {match_limit}")
    if preview:
        print(f"   Mode: PREVIEW (~10 candidates)")

    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    # Step 1: Ingest objective → schema
    print(f"📋 Ingesting objective...")
    ingest_payload = {"objective": objective}
    ingest_response = requests.post(FINDALL_INGEST_URL, headers=headers, json=ingest_payload, timeout=30)
    ingest_response.raise_for_status()

    schema = ingest_response.json()
    print(f"   Entity type: {schema.get('entity_type', 'N/A')}")
    print(f"   Match conditions: {len(schema.get('match_conditions', []))}")
    print(f"   Enrichments: {len(schema.get('enrichments', []))}")

    # Step 2: Create FindAll run
    print(f"🚀 Starting FindAll run...")
    run_payload = {
        **schema,
        "generator": generator,
        "match_limit": match_limit
    }
    if preview:
        run_payload["preview"] = True

    run_response = requests.post(FINDALL_RUNS_URL, headers=headers, json=run_payload, timeout=30)
    run_response.raise_for_status()

    run_data = run_response.json()
    findall_id = run_data["findall_id"]

    print(f"   FindAll ID: {findall_id}")
    print(f"⏳ Discovering and evaluating candidates...")

    # Step 3: Poll for completion
    result_url = f"{FINDALL_RUNS_URL}/{findall_id}/result"
    start_time = time.time()

    while True:
        try:
            result_response = requests.get(result_url, headers=headers, timeout=60)
            result_response.raise_for_status()

            result = result_response.json()

            if result.get("status") == "completed":
                elapsed = time.time() - start_time
                print(f"✅ FindAll completed in {elapsed:.1f}s")

                matches = result.get("matches", [])
                print(f"   Matched entities: {len(matches)}")

                return {
                    "findall_id": findall_id,
                    "matches": matches,
                    "schema": schema,
                    "raw_response": result
                }

            elif result.get("status") == "failed":
                error = result.get("error", "Unknown error")
                raise Exception(f"FindAll failed: {error}")

            # Still processing
            status = result.get("status", "processing")
            candidates_found = result.get("candidates_found", 0)
            elapsed = time.time() - start_time
            print(f"   Status: {status} | Candidates: {candidates_found} | {elapsed:.0f}s elapsed")
            time.sleep(5)

        except requests.exceptions.Timeout:
            continue

def enrich_entity(
    entity_name: str,
    entity_context: Optional[str] = None,
    fields: List[str] = None,
    processor: str = "core"
) -> Dict:
    """
    Enrich single entity with web data.

    Args:
        entity_name: Entity to enrich (company, person, etc.)
        entity_context: Optional context about entity
        fields: List of fields to enrich (e.g., ["funding_round", "employee_count"])
        processor: Processor tier

    Returns:
        Dict with enriched data
    """
    print(f"💎 Enrich Entity")
    print(f"   Entity: {entity_name}")
    print(f"   Fields: {', '.join(fields) if fields else 'default'}")
    print(f"   Processor: {processor}")

    # Build input
    input_text = f"Entity: {entity_name}"
    if entity_context:
        input_text += f". Context: {entity_context}"

    # Build schema
    properties = {}
    for field in (fields or ["description", "website", "industry"]):
        properties[field] = {"type": "string"}

    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "processor": processor,
        "input": input_text,
        "task_spec": {
            "output_schema": {
                "type": "object",
                "properties": properties
            }
        }
    }

    print(f"🚀 Submitting enrichment task...")
    response = requests.post(TASK_API_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()

    task_data = response.json()
    run_id = task_data["run_id"]

    print(f"   Task ID: {run_id}")
    print(f"⏳ Enriching...")

    # Poll for results
    result_url = f"{TASK_API_URL}/{run_id}/result"

    while True:
        try:
            result_response = requests.get(result_url, headers=headers, timeout=60)
            result_response.raise_for_status()

            result = result_response.json()

            if result.get("status") == "completed":
                print(f"✅ Enrichment completed")

                enriched_data = result.get("result", {})
                basis = enriched_data.get("basis", [])

                print(f"   Fields enriched: {len(properties)}")
                print(f"   Citations: {len(basis)}")

                return {
                    "run_id": run_id,
                    "entity": entity_name,
                    "data": enriched_data,
                    "raw_response": result
                }

            elif result.get("status") == "failed":
                error = result.get("error", "Unknown error")
                raise Exception(f"Enrichment failed: {error}")

            time.sleep(3)

        except requests.exceptions.Timeout:
            continue

def save_report(content: str, filename: str) -> Path:
    """Save markdown report to file."""
    filepath = REPORTS_DIR / filename
    filepath.write_text(content)
    print(f"💾 Report saved: {filepath}")
    return filepath

def save_dataset(matches: List[Dict], filename: str) -> Path:
    """Save dataset to JSON file."""
    filepath = DATASETS_DIR / filename
    filepath.write_text(json.dumps(matches, indent=2))
    print(f"💾 Dataset saved: {filepath}")
    return filepath

def save_enrichment(data: Dict, filename: str) -> Path:
    """Save enrichment result to JSON file."""
    filepath = ENRICHMENTS_DIR / filename
    filepath.write_text(json.dumps(data, indent=2))
    print(f"💾 Enrichment saved: {filepath}")
    return filepath

def upload_to_drive(local_path: Path, drive_folder: str):
    """Upload file to Google Drive."""
    # Import here to avoid dependency if not used
    from pydrive2.auth import GoogleAuth
    from pydrive2.drive import GoogleDrive

    print(f"☁️  Uploading to Google Drive: {drive_folder}")

    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile("mycreds.txt")

    drive = GoogleDrive(gauth)

    # Create folder structure
    parts = drive_folder.split('/')
    current_id = 'root'

    for folder_name in parts:
        query = f"'{current_id}' in parents and title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        file_list = drive.ListFile({'q': query}).GetList()

        if file_list:
            current_id = file_list[0]['id']
        else:
            folder = drive.CreateFile({
                'title': folder_name,
                'parents': [{'id': current_id}],
                'mimeType': 'application/vnd.google-apps.folder'
            })
            folder.Upload()
            current_id = folder['id']

    # Upload file
    file = drive.CreateFile({
        'title': local_path.name,
        'parents': [{'id': current_id}]
    })
    file.SetContentFile(str(local_path))
    file.Upload()

    print(f"   ✅ Uploaded: {file['alternateLink']}")
    return file['alternateLink']

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Parallel AI Research & Enrichment",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Quick Q&A with web citations")
    chat_parser.add_argument("query", help="Question to ask")
    chat_parser.add_argument("--system", help="System prompt")

    # Deep research command
    research_parser = subparsers.add_parser("deep-research", help="Comprehensive research report")
    research_parser.add_argument("objective", help="Research objective")
    research_parser.add_argument("--processor", default="ultra",
                                 choices=["lite", "base", "core", "core2x", "pro", "ultra", "ultra2x", "ultra4x", "ultra8x"],
                                 help="Processor tier")
    research_parser.add_argument("--fast", action="store_true", help="Use fast variant")
    research_parser.add_argument("--save-drive", help="Upload to Google Drive folder")

    # FindAll command
    findall_parser = subparsers.add_parser("findall", help="Generate web dataset")
    findall_parser.add_argument("objective", help="FindAll objective")
    findall_parser.add_argument("--generator", default="core", choices=["base", "core", "pro"],
                                help="Generator tier")
    findall_parser.add_argument("--match-limit", type=int, default=100, help="Max entities")
    findall_parser.add_argument("--preview", action="store_true", help="Preview mode")
    findall_parser.add_argument("--save-drive", help="Upload to Google Drive folder")

    # Enrich command
    enrich_parser = subparsers.add_parser("enrich", help="Enrich entity with web data")
    enrich_parser.add_argument("entity", help="Entity name")
    enrich_parser.add_argument("--context", help="Additional context")
    enrich_parser.add_argument("--fields", help="Comma-separated fields to enrich")
    enrich_parser.add_argument("--processor", default="core",
                               choices=["lite", "base", "core", "pro"],
                               help="Processor tier")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        validate_api_key()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if args.command == "chat":
            result = chat_with_web(args.query, args.system)

            print(f"\n{'='*80}")
            print(f"ANSWER:")
            print(f"{'='*80}")
            print(result["answer"])

            if result["citations"]:
                print(f"\n{'='*80}")
                print(f"CITATIONS:")
                print(f"{'='*80}")
                for i, citation in enumerate(result["citations"], 1):
                    print(f"{i}. {citation.get('title', 'N/A')}")
                    print(f"   {citation.get('url', 'N/A')}")

        elif args.command == "deep-research":
            result = deep_research(args.objective, args.processor, args.fast)

            # Save report
            filename = f"{timestamp}_research_report.md"
            filepath = save_report(result["content"], filename)

            print(f"\n{'='*80}")
            print(f"RESEARCH REPORT:")
            print(f"{'='*80}")
            print(result["content"][:500] + "..." if len(result["content"]) > 500 else result["content"])

            # Upload to Drive if requested
            if args.save_drive:
                upload_to_drive(filepath, args.save_drive)

        elif args.command == "findall":
            result = findall_entities(args.objective, args.generator, args.match_limit, args.preview)

            # Save dataset
            filename = f"{timestamp}_dataset.json"
            filepath = save_dataset(result["matches"], filename)

            print(f"\n{'='*80}")
            print(f"MATCHED ENTITIES:")
            print(f"{'='*80}")
            for i, match in enumerate(result["matches"][:10], 1):
                print(f"{i}. {match.get('name', 'N/A')}")
                print(f"   URL: {match.get('url', 'N/A')}")
                print(f"   Status: {match.get('match_status', 'N/A')}")

            if len(result["matches"]) > 10:
                print(f"... and {len(result['matches']) - 10} more")

            # Upload to Drive if requested
            if args.save_drive:
                upload_to_drive(filepath, args.save_drive)

        elif args.command == "enrich":
            fields = args.fields.split(",") if args.fields else None
            result = enrich_entity(args.entity, args.context, fields, args.processor)

            # Save enrichment
            filename = f"{timestamp}_{args.entity.replace(' ', '_')}_enrichment.json"
            filepath = save_enrichment(result, filename)

            print(f"\n{'='*80}")
            print(f"ENRICHED DATA:")
            print(f"{'='*80}")
            print(json.dumps(result["data"], indent=2))

        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
