#!/usr/bin/env python3
"""
Flowchart Generator - AI-powered diagram creation from natural language.

Generates professional flowcharts, sequence diagrams, state diagrams, and more
using AI to interpret descriptions and Mermaid syntax for rendering.

Usage:
    # Simple flowchart
    python execution/generate_flowchart.py "user login: enter email, validate, check password, if correct go to dashboard"

    # Sequence diagram
    python execution/generate_flowchart.py "API flow: frontend calls backend, backend calls database, returns data" --type sequence

    # State diagram
    python execution/generate_flowchart.py "order states: pending, confirmed, shipped, delivered, cancelled" --type state

    # Custom styling
    python execution/generate_flowchart.py "approval flow: submit, review, approve or reject" --direction LR --theme dark

    # Multiple output formats
    python execution/generate_flowchart.py "lead flow: capture, qualify, nurture, convert" --output svg png pdf
"""

import os
import sys
import json
import argparse
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OUTPUT_DIR = Path(__file__).parent.parent / ".tmp" / "flowcharts"

# Supported diagram types
DIAGRAM_TYPES = ["flowchart", "sequence", "state", "journey", "gantt", "mindmap", "er"]
DIRECTIONS = ["TB", "BT", "LR", "RL"]
THEMES = ["default", "dark", "forest", "neutral", "base"]
OUTPUT_FORMATS = ["svg", "png", "pdf", "md"]

# AI Prompts for each diagram type
SYSTEM_PROMPTS = {
    "flowchart": """You are an expert at creating Mermaid flowchart diagrams.
Given a natural language description of a process or workflow, generate valid Mermaid flowchart syntax.

Rules:
1. Use clear, concise node labels (max 30 chars)
2. Use appropriate shapes: [] for process, {} for decision, () for rounded, (()) for circle
3. Use meaningful edge labels for conditions
4. Group related nodes logically
5. Return ONLY the Mermaid code, no explanation

Example output:
flowchart TB
    A[Start] --> B{Valid Input?}
    B -->|Yes| C[Process Data]
    B -->|No| D[Show Error]
    C --> E[Save Result]
    D --> A
    E --> F[End]""",

    "sequence": """You are an expert at creating Mermaid sequence diagrams.
Given a description of interactions between systems/actors, generate valid Mermaid sequence diagram syntax.

Rules:
1. Identify all participants clearly
2. Use proper arrow types: ->> for request, -->> for response
3. Use activation boxes for processing time when relevant
4. Add notes for important details
5. Return ONLY the Mermaid code, no explanation

Example output:
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant D as Database

    U->>F: Click login
    F->>B: POST /auth/login
    B->>D: SELECT user
    D-->>B: User data
    B-->>F: JWT token
    F-->>U: Redirect to dashboard""",

    "state": """You are an expert at creating Mermaid state diagrams.
Given a description of states and transitions, generate valid Mermaid state diagram syntax.

Rules:
1. Use clear state names (no spaces, use underscores)
2. Define all transitions with trigger labels
3. Use [*] for start and end states
4. Include composite states if needed
5. Return ONLY the Mermaid code, no explanation

Example output:
stateDiagram-v2
    [*] --> Pending
    Pending --> Confirmed: payment_received
    Pending --> Cancelled: cancel
    Confirmed --> Shipped: ship
    Confirmed --> Cancelled: cancel
    Shipped --> Delivered: deliver
    Delivered --> [*]
    Cancelled --> [*]""",

    "journey": """You are an expert at creating Mermaid user journey diagrams.
Given a description of user experience steps, generate valid Mermaid journey syntax.

Rules:
1. Group steps into logical sections
2. Rate each step 1-5 (1=frustrated, 5=delighted)
3. Identify the actor for each step
4. Keep step descriptions short
5. Return ONLY the Mermaid code, no explanation

Example output:
journey
    title Customer Onboarding Journey
    section Signup
        Visit website: 5: Customer
        Fill registration form: 3: Customer
        Verify email: 4: Customer
    section First Use
        Complete profile: 2: Customer
        Watch tutorial: 4: Customer
        Create first project: 5: Customer""",

    "gantt": """You are an expert at creating Mermaid Gantt charts.
Given a description of tasks and timeline, generate valid Mermaid Gantt syntax.

Rules:
1. Define clear sections
2. Use proper date format or relative durations
3. Show dependencies where relevant
4. Keep task names concise
5. Return ONLY the Mermaid code, no explanation

Example output:
gantt
    title Project Timeline
    dateFormat  YYYY-MM-DD
    section Planning
        Requirements: a1, 2024-01-01, 7d
        Design: a2, after a1, 5d
    section Development
        Backend: b1, after a2, 14d
        Frontend: b2, after a2, 14d
    section Testing
        QA: c1, after b1 b2, 7d""",

    "mindmap": """You are an expert at creating Mermaid mind maps.
Given a description of concepts and relationships, generate valid Mermaid mindmap syntax.

Rules:
1. Start with central concept
2. Use proper indentation for hierarchy
3. Keep node text concise
4. Organize branches logically
5. Return ONLY the Mermaid code, no explanation

Example output:
mindmap
    root((AI Tools))
        Research
            Web Search
            Document Analysis
            Data Extraction
        Generation
            Text
            Images
            Code
        Automation
            Workflows
            Integrations
            Scheduling""",

    "er": """You are an expert at creating Mermaid entity-relationship diagrams.
Given a description of data entities and relationships, generate valid Mermaid ER syntax.

Rules:
1. Define all entities with attributes
2. Use proper relationship notation (||, |{, o{, etc.)
3. Label relationships clearly
4. Include key attributes (PK, FK)
5. Return ONLY the Mermaid code, no explanation

Example output:
erDiagram
    USER ||--o{ ORDER : places
    USER {
        int id PK
        string email
        string name
    }
    ORDER ||--|{ ORDER_ITEM : contains
    ORDER {
        int id PK
        int user_id FK
        date created_at
    }
    ORDER_ITEM }|--|| PRODUCT : references
    ORDER_ITEM {
        int order_id FK
        int product_id FK
        int quantity
    }
    PRODUCT {
        int id PK
        string name
        float price
    }"""
}


def validate_environment():
    """Validate required environment variables."""
    if not OPENROUTER_API_KEY and not ANTHROPIC_API_KEY:
        raise ValueError(
            "No AI API key found. Please add one of the following to your .env file:\n"
            "  OPENROUTER_API_KEY=sk-or-v1-...\n"
            "  ANTHROPIC_API_KEY=sk-ant-...\n\n"
            "Get keys from:\n"
            "  OpenRouter: https://openrouter.ai/keys\n"
            "  Anthropic: https://console.anthropic.com/settings/keys"
        )


def get_mmdc_path() -> Optional[str]:
    """Get path to Mermaid CLI (mmdc), checking local node_modules first."""
    # Check local node_modules first
    local_mmdc = Path(__file__).parent.parent / "node_modules" / ".bin" / "mmdc"
    if local_mmdc.exists():
        return str(local_mmdc)

    # Fall back to global install
    global_mmdc = shutil.which("mmdc")
    if global_mmdc:
        return global_mmdc

    return None


def check_mermaid_cli() -> bool:
    """Check if Mermaid CLI (mmdc) is installed."""
    return get_mmdc_path() is not None


def generate_mermaid_with_ai(
    description: str,
    diagram_type: str = "flowchart",
    direction: str = "TB",
    title: Optional[str] = None
) -> str:
    """
    Use AI to generate Mermaid syntax from natural language.

    Args:
        description: Natural language description of the diagram
        diagram_type: Type of diagram to generate
        direction: Flow direction (for flowcharts)
        title: Optional diagram title

    Returns:
        Mermaid syntax string
    """
    system_prompt = SYSTEM_PROMPTS.get(diagram_type, SYSTEM_PROMPTS["flowchart"])

    user_prompt = f"Create a {diagram_type} diagram for the following:\n\n{description}"

    if diagram_type == "flowchart" and direction != "TB":
        user_prompt += f"\n\nUse direction: {direction}"

    if title:
        user_prompt += f"\n\nTitle: {title}"

    # Use OpenRouter if available, otherwise Anthropic
    if OPENROUTER_API_KEY:
        return _call_openrouter(system_prompt, user_prompt)
    else:
        return _call_anthropic(system_prompt, user_prompt)


def _call_openrouter(system_prompt: str, user_prompt: str) -> str:
    """Call OpenRouter API for Mermaid generation."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/casper-ai",
        "X-Title": "Casper AI Flowchart Generator"
    }

    payload = {
        "model": "anthropic/claude-sonnet-4",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 4096,
        "temperature": 0.3  # Lower temperature for more consistent output
    }

    print("   Calling AI to generate diagram...")

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60
    )
    response.raise_for_status()

    result = response.json()
    content = result["choices"][0]["message"]["content"]

    # Extract Mermaid code from response (in case AI added explanation)
    return _extract_mermaid_code(content)


def _call_anthropic(system_prompt: str, user_prompt: str) -> str:
    """Call Anthropic API directly for Mermaid generation."""
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }

    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4096,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_prompt}
        ]
    }

    print("   Calling Anthropic API to generate diagram...")

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=payload,
        timeout=60
    )
    response.raise_for_status()

    result = response.json()
    content = result["content"][0]["text"]

    return _extract_mermaid_code(content)


def _extract_mermaid_code(content: str) -> str:
    """Extract Mermaid code from AI response (handles markdown code blocks)."""
    # Check for code blocks
    if "```mermaid" in content:
        start = content.find("```mermaid") + len("```mermaid")
        end = content.find("```", start)
        return content[start:end].strip()
    elif "```" in content:
        start = content.find("```") + 3
        end = content.find("```", start)
        code = content[start:end].strip()
        # Remove language identifier if present
        if code.startswith("mermaid"):
            code = code[7:].strip()
        return code
    else:
        # Assume entire response is Mermaid code
        return content.strip()


def render_mermaid(
    mermaid_code: str,
    output_path: Path,
    output_format: str = "svg",
    theme: str = "default",
    background_color: str = "transparent"
) -> bool:
    """
    Render Mermaid code to image using mmdc CLI.

    Args:
        mermaid_code: Valid Mermaid syntax
        output_path: Path to save output file
        output_format: svg, png, or pdf
        theme: Visual theme
        background_color: Background color (transparent, white, etc.)

    Returns:
        True if rendering succeeded
    """
    mmdc_path = get_mmdc_path()
    if not mmdc_path:
        print("   Mermaid CLI (mmdc) not found. Install with: npm install @mermaid-js/mermaid-cli")
        return False

    # Write Mermaid code to temp file
    temp_input = output_path.parent / "temp_input.mmd"
    temp_input.write_text(mermaid_code)

    # Build mmdc command
    cmd = [
        mmdc_path,
        "-i", str(temp_input),
        "-o", str(output_path),
        "-t", theme,
        "-b", background_color
    ]

    # Add format-specific options
    if output_format == "png":
        cmd.extend(["-s", "2"])  # 2x scale for better quality

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        # Clean up temp file
        temp_input.unlink(missing_ok=True)

        if result.returncode != 0:
            print(f"   Render error: {result.stderr}")
            return False

        return True

    except subprocess.TimeoutExpired:
        print("   Render timeout (60s exceeded)")
        temp_input.unlink(missing_ok=True)
        return False
    except Exception as e:
        print(f"   Render exception: {str(e)}")
        temp_input.unlink(missing_ok=True)
        return False


def generate_flowchart(
    description: str,
    diagram_type: str = "flowchart",
    direction: str = "TB",
    theme: str = "default",
    output_formats: List[str] = None,
    title: Optional[str] = None,
    output_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Generate a flowchart from natural language description.

    Args:
        description: Natural language description of the flow
        diagram_type: Type of diagram (flowchart, sequence, state, etc.)
        direction: Flow direction (TB, BT, LR, RL)
        theme: Visual theme
        output_formats: List of output formats (svg, png, pdf, md)
        title: Optional diagram title
        output_dir: Custom output directory

    Returns:
        Dict with mermaid_code, file paths, and metadata
    """
    if output_formats is None:
        output_formats = ["svg"]

    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if output_dir is None:
        output_dir = OUTPUT_DIR / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  FLOWCHART GENERATOR")
    print(f"{'='*60}")
    print(f"   Type: {diagram_type}")
    print(f"   Description: {description[:80]}{'...' if len(description) > 80 else ''}")
    print(f"   Direction: {direction}")
    print(f"   Theme: {theme}")
    print(f"   Outputs: {', '.join(output_formats)}")
    print(f"{'='*60}\n")

    # Generate Mermaid code using AI
    print("1. Generating Mermaid code...")
    mermaid_code = generate_mermaid_with_ai(
        description=description,
        diagram_type=diagram_type,
        direction=direction,
        title=title
    )

    print(f"   Generated {len(mermaid_code)} characters of Mermaid code")

    # Save Mermaid source
    mermaid_path = output_dir / "diagram.mmd"
    mermaid_path.write_text(mermaid_code)
    print(f"   Saved: {mermaid_path}")

    # Track output files
    output_files = {"mermaid": str(mermaid_path)}

    # Render to requested formats
    has_mmdc = check_mermaid_cli()

    if not has_mmdc and any(fmt in output_formats for fmt in ["svg", "png", "pdf"]):
        print("\n2. Rendering skipped (mmdc not installed)")
        print("   To enable rendering, install Mermaid CLI:")
        print("   npm install -g @mermaid-js/mermaid-cli")
    else:
        print("\n2. Rendering outputs...")

        for fmt in output_formats:
            if fmt == "md":
                # Just wrap in markdown code block
                md_content = f"```mermaid\n{mermaid_code}\n```"
                md_path = output_dir / "diagram.md"
                md_path.write_text(md_content)
                output_files["md"] = str(md_path)
                print(f"   Created: {md_path}")
            elif fmt in ["svg", "png", "pdf"]:
                output_path = output_dir / f"diagram.{fmt}"
                print(f"   Rendering {fmt.upper()}...")

                if render_mermaid(mermaid_code, output_path, fmt, theme):
                    output_files[fmt] = str(output_path)
                    print(f"   Created: {output_path}")
                else:
                    print(f"   Failed to render {fmt}")

    # Count nodes and edges (rough estimate)
    node_count = len([line for line in mermaid_code.split('\n') if '[' in line or '(' in line])
    edge_count = len([line for line in mermaid_code.split('\n') if '-->' in line or '->>' in line or '-->' in line])

    # Save metadata
    metadata = {
        "description": description,
        "diagram_type": diagram_type,
        "direction": direction,
        "theme": theme,
        "title": title,
        "mermaid_code": mermaid_code,
        "files": output_files,
        "node_count": node_count,
        "edge_count": edge_count,
        "generated_at": datetime.now().isoformat(),
        "mmdc_available": has_mmdc
    }

    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n{'='*60}")
    print(f"  COMPLETE")
    print(f"{'='*60}")
    print(f"   Nodes: ~{node_count}")
    print(f"   Edges: ~{edge_count}")
    print(f"   Files: {output_dir}")
    print(f"{'='*60}\n")

    # Print Mermaid code for easy copying
    print("Mermaid Code:")
    print("-" * 40)
    print(mermaid_code)
    print("-" * 40)

    return metadata


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate flowcharts and diagrams from natural language descriptions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple flowchart
  python generate_flowchart.py "user login: enter credentials, validate, if valid show dashboard, else show error"

  # Sequence diagram
  python generate_flowchart.py "API call: client sends request to server, server queries database, returns response" --type sequence

  # State diagram
  python generate_flowchart.py "order lifecycle: pending, paid, shipped, delivered, can be cancelled from pending or paid" --type state

  # Custom styling
  python generate_flowchart.py "approval process" --direction LR --theme dark --output svg png
        """
    )

    parser.add_argument(
        "description",
        help="Natural language description of the diagram"
    )

    parser.add_argument(
        "--type", "-t",
        choices=DIAGRAM_TYPES,
        default="flowchart",
        help="Type of diagram to generate (default: flowchart)"
    )

    parser.add_argument(
        "--direction", "-d",
        choices=DIRECTIONS,
        default="TB",
        help="Flow direction for flowcharts (default: TB = top to bottom)"
    )

    parser.add_argument(
        "--theme",
        choices=THEMES,
        default="default",
        help="Visual theme (default: default)"
    )

    parser.add_argument(
        "--output", "-o",
        nargs="+",
        choices=OUTPUT_FORMATS,
        default=["svg"],
        help="Output formats (default: svg)"
    )

    parser.add_argument(
        "--title",
        help="Diagram title"
    )

    parser.add_argument(
        "--output-dir",
        help="Custom output directory"
    )

    args = parser.parse_args()

    try:
        # Validate environment
        validate_environment()

        # Generate flowchart
        result = generate_flowchart(
            description=args.description,
            diagram_type=args.type,
            direction=args.direction,
            theme=args.theme,
            output_formats=args.output,
            title=args.title,
            output_dir=Path(args.output_dir) if args.output_dir else None
        )

        return 0

    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
