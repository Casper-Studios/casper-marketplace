#!/usr/bin/env python3
"""
Proposal Generator - AI Agent-based proposal generation with template-perfect output.

Uses Pydantic AI to create an autonomous agent that:
1. Decides when to research the client company
2. Decides when to look up software tool URLs
3. Decides when to research industry trends
4. Generates a complete, structured proposal matching the exact Casper Studios template

Template Reference: knowledge/templates/TemplateProposal.html
Directive: directives/generate_proposal.md

Usage:
    python execution/generate_proposal.py \
        --transcript-file meeting_notes.txt \
        --client "Acme Corp"

    python execution/generate_proposal.py \
        --transcript "Meeting notes here..." \
        --client "Acme Corp" \
        --project "Custom Project Name"
"""

import os
import sys
import asyncio
import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# Pydantic AI imports
from pydantic import BaseModel, Field, ConfigDict
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel

# Google API imports
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

# Import parallel research for web-enabled tools
# Add scripts directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from parallel_research import chat_with_web
    PARALLEL_RESEARCH_AVAILABLE = True
except ImportError:
    PARALLEL_RESEARCH_AVAILABLE = False
    print("⚠️  parallel_research not available - tools will be limited")

# Configuration
SETTINGS_FILE = "settings.yaml"
CREDENTIALS_FILE = "mycreds.txt"
DEFAULT_TEMPLATE_ID = "1LakD2oCGrTQSeoTDZJhEBD3c2gE_gwNKoG2bAlK8DNs"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# =============================================================================
# BRAND STYLING (from TemplateProposal.html CSS analysis)
# =============================================================================

# Colors extracted from template CSS
BRAND_COLORS = {
    # Section headers - #548ce9 (blue)
    "blue_header": {"red": 0.33, "green": 0.55, "blue": 0.91},
    # Links and table headers - #4a86e8
    "blue_link": {"red": 0.29, "green": 0.53, "blue": 0.91},
    # Body text - black
    "black": {"red": 0.0, "green": 0.0, "blue": 0.0},
    # Table header text
    "white": {"red": 1.0, "green": 1.0, "blue": 1.0},
}

# Typography styles matching template exactly
BRAND_PROFILE = {
    # Centered title: "Proposal for [Company]: [Project]"
    "title_style": {
        "bold": True,
        "fontSize": {"magnitude": 11, "unit": "PT"},
        "weightedFontFamily": {"fontFamily": "Source Sans Pro", "weight": 700},
        "foregroundColor": {"color": {"rgbColor": BRAND_COLORS["black"]}}
    },
    # Blue section headers: "Context", "Proposed Approach", etc.
    "section_header_style": {
        "bold": True,
        "fontSize": {"magnitude": 11, "unit": "PT"},
        "weightedFontFamily": {"fontFamily": "Source Sans Pro", "weight": 700},
        "foregroundColor": {"color": {"rgbColor": BRAND_COLORS["blue_header"]}}
    },
    # Black subsection headers: "Current challenges", "Goals", etc.
    "subsection_header_style": {
        "bold": True,
        "fontSize": {"magnitude": 11, "unit": "PT"},
        "weightedFontFamily": {"fontFamily": "Source Sans Pro", "weight": 700},
        "foregroundColor": {"color": {"rgbColor": BRAND_COLORS["black"]}}
    },
    # Normal body text
    "body_style": {
        "fontSize": {"magnitude": 11, "unit": "PT"},
        "weightedFontFamily": {"fontFamily": "Source Sans Pro", "weight": 400},
        "foregroundColor": {"color": {"rgbColor": BRAND_COLORS["black"]}}
    },
    # Bold text within body (for list item titles)
    "bold_body_style": {
        "bold": True,
        "fontSize": {"magnitude": 11, "unit": "PT"},
        "weightedFontFamily": {"fontFamily": "Source Sans Pro", "weight": 700},
        "foregroundColor": {"color": {"rgbColor": BRAND_COLORS["black"]}}
    },
    # Italic placeholder text (for template instructions)
    "italic_style": {
        "italic": True,
        "fontSize": {"magnitude": 11, "unit": "PT"},
        "weightedFontFamily": {"fontFamily": "Source Sans Pro", "weight": 400},
        "foregroundColor": {"color": {"rgbColor": BRAND_COLORS["black"]}}
    },
}


# =============================================================================
# PYDANTIC MODELS FOR STRUCTURED OUTPUT
# =============================================================================

class BulletItem(BaseModel):
    """A bullet list item with optional bold title and description."""
    title: Optional[str] = Field(None, description="Bold title for the item (optional). Example: 'Manual lead qualification'")
    description: str = Field(..., description="The item description/content that follows the title")


class NumberedItem(BaseModel):
    """A numbered list item with optional bold title and description."""
    title: Optional[str] = Field(None, description="Bold title for the item (optional). Example: 'Discovery and data audit'")
    description: str = Field(..., description="The item description/content")


class ProposalSection(BaseModel):
    """A single section in the proposal."""
    type: str = Field(
        ...,
        description="""Section type. Must be one of:
        - section_header: Blue header (Context, Proposed Approach, Expected Outcomes, etc.)
        - subsection_header: Black bold header (Current challenges, Goals, Workflow mapping, etc.)
        - paragraph: Normal body paragraph
        - bullet_list: Unordered list with items
        - numbered_list: Ordered list with items
        - closing_paragraph: Paragraph with 12pt spacing (timeline summaries)
        - cost: Estimated cost line with bold prefix"""
    )
    content: Optional[str] = Field(None, description="Text content for headers/paragraphs/cost")
    items: Optional[list[BulletItem | NumberedItem]] = Field(None, description="Items for bullet_list or numbered_list types")


class ProposalOutput(BaseModel):
    """Complete structured proposal output matching Casper Studios template."""
    title: str = Field(
        ...,
        description="Proposal title. Format: 'Proposal for [Company]: [Brief Project Description]'. Example: 'Proposal for Acme Corp: Intelligent Lead Routing System'"
    )
    context: str = Field(
        ...,
        description="Opening paragraph for the Context section. Explains the partnership opportunity, client situation, strategic goals, and why this engagement matters. 2-4 sentences."
    )
    sections: list[ProposalSection] = Field(
        ...,
        description="All proposal sections in order. Must include: Problem statement & objectives, Proposed Approach (with work streams), Expected Outcomes, Next Steps"
    )
    tool_links: dict[str, str] = Field(
        default_factory=dict,
        description="Map of tool/product names to their official URLs for hyperlinking. Example: {'n8n': 'https://n8n.io', 'Brevo': 'https://brevo.com'}"
    )


# =============================================================================
# AGENT DEPENDENCIES (context passed to tools)
# =============================================================================

class ProposalDeps(BaseModel):
    """Dependencies available to the agent during execution."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    client_name: str
    project_name: str
    transcript: str
    current_date: str = Field(default_factory=lambda: datetime.now().strftime("%B %Y"))
    current_year: int = Field(default_factory=lambda: datetime.now().year)


# =============================================================================
# SYSTEM PROMPT - Comprehensive template-matching instructions
# =============================================================================

AGENT_SYSTEM_PROMPT = """You are the Proposal Generation Agent for Casper Studios, an elite AI automation consultancy.

## YOUR ROLE

Create COMPELLING, PROFESSIONAL proposals that exactly match the Casper Studios template structure. You have web research tools available - use them when they would improve the proposal.

## TEMPLATE STRUCTURE (MANDATORY)

Your output MUST follow this exact structure. The template is documented in knowledge/templates/TemplateProposal.html.

### Required Sections (in order):

1. **Title**: "Proposal for [Company]: [Brief Project Description]"

2. **Context** (section_header)
   - 2-4 sentence opening paragraph
   - Explains partnership opportunity, client situation, strategic goals
   - Sets the stage for why this engagement matters NOW

3. **Problem statement & objectives** (section_header)
   - "Current challenges" (subsection_header) with bullet_list
     - Each bullet: bold title + description
     - 3-5 specific pain points from the transcript
   - "Goals" (subsection_header) with numbered_list
     - 3-5 measurable objectives
     - Tie to challenges identified above

4. **Proposed Approach** (section_header)
   - Opening paragraph explaining engagement model
   - Work streams (use en-dash: "Work stream 1 – Name")
     - Each work stream has:
       - subsection_header with work stream name
       - paragraph describing focus
       - "Workflow mapping" (subsection_header) with numbered_list
       - "Technical approach" (subsection_header) with bullet_list
       - "Resourcing & deliverables" (subsection_header) with bullet_list
   - closing_paragraph with timeline and expected state

5. **Estimated cost** (cost type)
   - Format: "Estimated cost: US $XX,XXX for the X-week engagement (scope description)."
   - Use appropriate pricing tier based on complexity

6. **Expected Outcomes** (section_header)
   - bullet_list with 4-6 outcomes
   - Each bullet: bold outcome title + description
   - Focus on business impact, not features

7. **Next Steps** (section_header)
   - numbered_list with 3 items:
     1. Acceptance: confirm approval and timing
     2. Discovery preparation: what client needs to provide
     3. Kickoff: schedule meeting

## WHEN TO USE YOUR TOOLS

1. **research_client** - Use when you need background on the client company (industry, size, recent news)
2. **search_tool_url** - Use when you mention a software product and want to hyperlink it (n8n, Make, Brevo, etc.)
3. **research_industry_trends** - Use when the transcript mentions a specific industry and current trends would strengthen the proposal

You DON'T need to use all tools - only use what genuinely improves this specific proposal.

## BENEFITS-FIRST APPROACH

Lead with OUTCOMES, not features:
- Paint a picture of their improved future state
- Quantify impact: "reduces X from 15 hours to 2 hours"
- Show ROI: "estimated annual savings of $XX,XXX"
- Build confidence with clear timelines

## ROI ESTIMATION FRAMEWORK

For EVERY proposal, include ROI calculations:
- **Time Savings**: Current hours × hourly rate × 52 weeks
- **Cost Reduction**: Error rates, delays, manual rework
- **Payback Period**: Project cost ÷ Monthly savings

Example: "Currently spending 15 hrs/week on lead qualification ($75/hr) = $58,500/year. Our automation reduces this to 2 hrs/week = $7,800/year. Annual savings: $50,700. Payback period: 6 months."

## CASPER STUDIOS TEAM & RATES

Assign specific roles when staffing is relevant:
- **Client Lead** ($300/hr, 10-15%): Strategic oversight
- **Engagement Lead** ($275/hr, 20-25%): Day-to-day management
- **Senior AI Engineer** ($275/hr, 30-50%): Architecture, AI/ML
- **Full-Stack Engineer** ($225/hr, 40-75%): Development, APIs
- **UX/UI Designer** ($200/hr, 20-40%): Research, designs

## PRICING TIERS

Match complexity to price:
- **Simple automation**: $10,000-20,000 / 2-4 weeks
- **Multi-workflow system**: $20,000-40,000 / 4-8 weeks
- **Internal tool/platform**: $40,000-80,000 / 2-3 months
- **MVP product**: $80,000-150,000 / 3-4 months
- **Full product build**: $150,000-300,000+ / 4-6 months

## TECHNICAL REFERENCES

Use CURRENT AI models (as of 2024-2025):
- Claude 3.5 Sonnet, Claude Haiku (Anthropic)
- Gemini 2.0 Flash, Gemini 2.5 Pro (Google)
- DO NOT mention GPT-4, GPT-4o (outdated references)

Mention relevant tools naturally:
- Automation: n8n, Make, Zapier
- Databases: Airtable, Supabase, Notion
- CRM/Marketing: HubSpot, Brevo, ActiveCampaign
- When you mention a tool, use search_tool_url to get its URL

## FORMATTING RULES

1. **NO MARKDOWN** - No asterisks, no # headers, no **bold** markers. Plain text only.
2. Use en-dash (–) not hyphen (-) for work stream names
3. Bold titles in lists use the "title" field, not inline markers
4. Hyperlinks are handled automatically via tool_links field
5. Numbers: Use "US $25,000" format for costs
6. Keep paragraphs focused - 2-4 sentences max

## COMPLETE EXAMPLE

Here's a complete example of the expected output structure:

```json
{
  "title": "Proposal for TechStart Inc: Automated Sales Pipeline Intelligence",
  "context": "TechStart Inc and Casper Studios are collaborating to transform how the sales team identifies, qualifies, and engages high-value prospects. This initiative focuses on deploying AI-powered lead scoring and automated outreach workflows that will dramatically reduce manual effort while improving conversion rates. The project aims to establish scalable infrastructure that grows with TechStart's expanding sales organization.",
  "sections": [
    {
      "type": "section_header",
      "content": "Problem statement & objectives"
    },
    {
      "type": "subsection_header",
      "content": "Current challenges"
    },
    {
      "type": "bullet_list",
      "items": [
        {
          "title": "Manual lead qualification",
          "description": "Sales reps spend 15+ hours weekly manually researching prospects in LinkedIn and company websites, with inconsistent scoring criteria across the team leading to missed opportunities."
        },
        {
          "title": "Delayed response times",
          "description": "High-intent website visitors and demo requesters wait 24-48 hours for follow-up, causing an estimated 40% to disengage before receiving a response."
        },
        {
          "title": "Disconnected data sources",
          "description": "Lead information from website forms, CRM, and enrichment tools exists in silos, requiring manual copy-paste and causing data inconsistencies."
        },
        {
          "title": "No engagement tracking",
          "description": "The team lacks visibility into which emails are opened, which content resonates, and optimal follow-up timing, leading to generic outreach."
        }
      ]
    },
    {
      "type": "subsection_header",
      "content": "Goals"
    },
    {
      "type": "numbered_list",
      "items": [
        {
          "description": "Reduce lead qualification time from 15 hours to under 2 hours weekly through AI-powered scoring and automated enrichment."
        },
        {
          "description": "Achieve sub-1-hour response time for high-intent leads through trigger-based routing and automated initial outreach."
        },
        {
          "description": "Integrate CRM, website tracking, and email platforms into a unified workflow that eliminates manual data entry."
        },
        {
          "description": "Provide real-time engagement analytics to optimize outreach timing and content effectiveness."
        }
      ]
    },
    {
      "type": "section_header",
      "content": "Proposed Approach"
    },
    {
      "type": "paragraph",
      "content": "We propose a five-week engagement to design, build, and deploy an intelligent sales pipeline system. The solution combines AI-powered lead scoring, automated enrichment, and trigger-based workflows to transform TechStart's sales operations. We will deliver production-ready automations with full documentation and team training."
    },
    {
      "type": "subsection_header",
      "content": "Work stream 1 – Lead Scoring and Enrichment Engine"
    },
    {
      "type": "paragraph",
      "content": "This work stream establishes the AI-powered foundation for automated lead qualification. We will build a scoring model that evaluates prospects based on firmographic data, engagement signals, and intent indicators, then automatically enriches records with relevant context."
    },
    {
      "type": "subsection_header",
      "content": "Workflow mapping"
    },
    {
      "type": "numbered_list",
      "items": [
        {
          "title": "Discovery and data audit",
          "description": "Review existing CRM fields, identify data quality issues, document ideal customer profile (ICP) criteria, and map current lead flow."
        },
        {
          "title": "Scoring model development",
          "description": "Build multi-factor scoring algorithm using historical conversion data, engagement patterns, and firmographic signals."
        },
        {
          "title": "Enrichment pipeline setup",
          "description": "Configure automated data enrichment using Clearbit/Apollo to populate missing fields and validate contact information."
        },
        {
          "title": "CRM integration and testing",
          "description": "Connect scoring engine to Salesforce, validate field mappings, and test with sample leads before full deployment."
        }
      ]
    },
    {
      "type": "subsection_header",
      "content": "Technical approach"
    },
    {
      "type": "bullet_list",
      "items": [
        {
          "title": "n8n workflow orchestration",
          "description": "Coordinate data flows between CRM, enrichment APIs, and scoring engine with error handling and retry logic."
        },
        {
          "title": "Claude AI integration",
          "description": "Natural language processing for intent detection from email threads and chat transcripts to identify buying signals."
        },
        {
          "title": "Supabase data layer",
          "description": "Store enrichment cache and scoring history for analytics and model improvement over time."
        }
      ]
    },
    {
      "type": "subsection_header",
      "content": "Resourcing & deliverables"
    },
    {
      "type": "bullet_list",
      "items": [
        {
          "title": "Lead Scoring System",
          "description": "Production-ready scoring engine with configurable weights and automatic CRM updates."
        },
        {
          "title": "Enrichment Pipeline",
          "description": "Automated data enrichment workflow that populates missing fields within minutes of lead creation."
        },
        {
          "title": "Documentation and Training",
          "description": "Complete technical documentation plus 2-hour training session for sales ops team on system management."
        }
      ]
    },
    {
      "type": "subsection_header",
      "content": "Work stream 2 – Automated Outreach Sequences"
    },
    {
      "type": "paragraph",
      "content": "This work stream creates intelligent, trigger-based outreach that engages leads at optimal moments with personalized content based on their behavior and score."
    },
    {
      "type": "subsection_header",
      "content": "Workflow mapping"
    },
    {
      "type": "numbered_list",
      "items": [
        {
          "title": "Trigger definition",
          "description": "Map engagement events (page visits, email opens, form submissions) to appropriate outreach actions and timing."
        },
        {
          "title": "Sequence development",
          "description": "Build 3-5 outreach sequences tailored to different lead scores, industries, and engagement patterns."
        },
        {
          "title": "Personalization engine",
          "description": "Configure dynamic content insertion based on firmographic data, recent activity, and detected pain points."
        }
      ]
    },
    {
      "type": "subsection_header",
      "content": "Technical approach"
    },
    {
      "type": "bullet_list",
      "items": [
        {
          "title": "Brevo email automation",
          "description": "Design and implement email sequences with A/B testing, engagement tracking, and automatic unsubscribe handling."
        },
        {
          "title": "Webhook-based triggers",
          "description": "Real-time event processing to initiate outreach within minutes of qualifying actions."
        }
      ]
    },
    {
      "type": "closing_paragraph",
      "content": "Upon completion of this five-week engagement, TechStart will have a fully operational sales intelligence system that reduces manual lead qualification by 85% and achieves sub-1-hour response times for high-intent prospects. The team will be trained on system management and have full documentation for ongoing optimization."
    },
    {
      "type": "cost",
      "content": "Estimated cost: US $35,000 for the five-week engagement (discovery, build, integration, and training)."
    },
    {
      "type": "section_header",
      "content": "Expected Outcomes"
    },
    {
      "type": "bullet_list",
      "items": [
        {
          "title": "85% reduction in manual qualification time",
          "description": "Automated scoring and enrichment eliminates repetitive research, freeing 13+ hours weekly for high-value conversations."
        },
        {
          "title": "Sub-1-hour response to high-intent leads",
          "description": "Trigger-based routing ensures hot prospects receive immediate, personalized outreach before competitors engage."
        },
        {
          "title": "Estimated $52,000 annual savings",
          "description": "Time savings (13 hrs/week × $75/hr × 52 weeks) plus reduced missed opportunities from faster response."
        },
        {
          "title": "Unified data and analytics",
          "description": "Single source of truth for lead data with engagement tracking to continuously optimize outreach effectiveness."
        }
      ]
    },
    {
      "type": "section_header",
      "content": "Next Steps"
    },
    {
      "type": "numbered_list",
      "items": [
        {
          "title": "Acceptance",
          "description": "Confirm approval of this proposal and desired start date (recommend beginning of next month)."
        },
        {
          "title": "Discovery preparation",
          "description": "Provide Salesforce admin access, identify 10 recent closed-won deals for scoring model training, and nominate sales ops point of contact."
        },
        {
          "title": "Kickoff",
          "description": "Schedule 90-minute kickoff meeting to align on goals, timeline, and communication cadence."
        }
      ]
    }
  ],
  "tool_links": {
    "n8n": "https://n8n.io",
    "Supabase": "https://supabase.com",
    "Brevo": "https://brevo.com",
    "Claude": "https://anthropic.com"
  }
}
```

## OUTPUT REQUIREMENTS

1. Return ONLY the structured ProposalOutput
2. Include tool URLs in tool_links for any software mentioned
3. Match the template structure EXACTLY
4. No markdown formatting in any text content
5. Use the example above as your quality benchmark"""


# =============================================================================
# CREATE THE AGENT
# =============================================================================

# Configure OpenRouter model
model = OpenAIChatModel(
    "google/gemini-2.5-pro-preview-06-05",
    provider="openrouter",
)

# Create the proposal agent
proposal_agent = Agent(
    model,
    output_type=ProposalOutput,
    deps_type=ProposalDeps,
    system_prompt=AGENT_SYSTEM_PROMPT,
    retries=2,
)


# =============================================================================
# AGENT TOOLS
# =============================================================================

# Global dict to capture tool URLs during agent run
_captured_tool_urls: dict[str, str] = {}


@proposal_agent.tool
async def research_client(ctx: RunContext[ProposalDeps]) -> str:
    """
    Research the client company to get background information.
    Returns a brief overview of what the company does, their industry, and recent news.
    Use this when you need context about who the client is.
    """
    if not PARALLEL_RESEARCH_AVAILABLE:
        return f"[Web search unavailable - using client name: {ctx.deps.client_name}]"

    client_name = ctx.deps.client_name
    current_date = ctx.deps.current_date

    print(f"   🔍 Agent researching client: {client_name}")

    try:
        result = chat_with_web(
            f"What does {client_name} do as of {current_date}? Brief company overview, industry, and any recent news. Keep it to 2-3 sentences.",
            system_prompt="You are a business researcher. Provide factual, concise, up-to-date information."
        )
        answer = result.get("answer", "")
        print(f"   ✅ Found client info")
        return answer if answer else f"Could not find information about {client_name}"
    except Exception as e:
        print(f"   ⚠️ Client research failed: {e}")
        return f"Could not research {client_name}: {str(e)}"


@proposal_agent.tool
async def search_tool_url(ctx: RunContext[ProposalDeps], tool_name: str) -> str:
    """
    Look up the official website URL for a software product/tool.
    Use this when you mention a tool like n8n, Make, Airtable, etc. and want to include its URL.
    Returns the URL which will be automatically hyperlinked in the final document.

    Args:
        tool_name: Name of the software tool (e.g., "n8n", "Make", "Airtable")
    """
    global _captured_tool_urls

    # Known URLs for common tools (faster than web search)
    known_urls = {
        "n8n": "https://n8n.io",
        "make": "https://www.make.com",
        "zapier": "https://zapier.com",
        "airtable": "https://airtable.com",
        "notion": "https://notion.so",
        "supabase": "https://supabase.com",
        "hubspot": "https://www.hubspot.com",
        "brevo": "https://www.brevo.com",
        "activecampaign": "https://www.activecampaign.com",
        "retool": "https://retool.com",
        "slack": "https://slack.com",
        "salesforce": "https://www.salesforce.com",
        "claude": "https://anthropic.com",
        "anthropic": "https://anthropic.com",
        "openai": "https://openai.com",
        "google": "https://cloud.google.com",
        "clearbit": "https://clearbit.com",
        "apollo": "https://www.apollo.io",
        "zoominfo": "https://www.zoominfo.com",
        "linkedin": "https://www.linkedin.com",
        "stripe": "https://stripe.com",
        "twilio": "https://www.twilio.com",
        "sendgrid": "https://sendgrid.com",
        "mailchimp": "https://mailchimp.com",
        "intercom": "https://www.intercom.com",
        "zendesk": "https://www.zendesk.com",
        "freshdesk": "https://freshdesk.com",
        "asana": "https://asana.com",
        "monday": "https://monday.com",
        "jira": "https://www.atlassian.com/software/jira",
        "confluence": "https://www.atlassian.com/software/confluence",
        "figma": "https://www.figma.com",
        "miro": "https://miro.com",
        "loom": "https://www.loom.com",
        "calendly": "https://calendly.com",
        "typeform": "https://www.typeform.com",
        "google sheets": "https://sheets.google.com",
        "google docs": "https://docs.google.com",
    }

    # Check known URLs first
    url = known_urls.get(tool_name.lower())
    if url:
        _captured_tool_urls[tool_name] = url
        print(f"   ✅ Found URL for {tool_name}: {url}")
        return url

    if not PARALLEL_RESEARCH_AVAILABLE:
        return f"[URL not found for {tool_name}]"

    print(f"   🔍 Agent looking up URL for: {tool_name}")

    try:
        result = chat_with_web(
            f"What is the official website URL for {tool_name}? Return only the URL.",
            system_prompt="Return only the official URL, nothing else."
        )
        answer = result.get("answer", "")
        # Extract URL from response
        url_match = re.search(r'https?://[^\s]+', answer)
        if url_match:
            url = url_match.group(0).rstrip(".,)")
            print(f"   ✅ Found URL: {url}")
            _captured_tool_urls[tool_name] = url
            return url
        return f"[URL not found for {tool_name}]"
    except Exception as e:
        print(f"   ⚠️ URL lookup failed: {e}")
        return f"[URL lookup failed for {tool_name}]"


@proposal_agent.tool
async def research_industry_trends(ctx: RunContext[ProposalDeps], industry: str) -> str:
    """
    Research current AI and automation trends in a specific industry.
    Use this when the transcript mentions a specific industry and you want to include relevant trends.

    Args:
        industry: The industry to research (e.g., "grocery", "healthcare", "finance")
    """
    if not PARALLEL_RESEARCH_AVAILABLE:
        return f"[Web search unavailable for {industry} industry trends]"

    current_date = ctx.deps.current_date

    print(f"   🔍 Agent researching {industry} industry trends")

    try:
        result = chat_with_web(
            f"What are the top AI/automation trends in the {industry} industry as of {current_date}? Brief 2-3 bullet points with recent developments.",
            system_prompt="You are an industry analyst. Be specific and current. Only cite recent information."
        )
        answer = result.get("answer", "")
        print(f"   ✅ Found industry trends")
        return answer if answer else f"Could not find trends for {industry} industry"
    except Exception as e:
        print(f"   ⚠️ Industry research failed: {e}")
        return f"Could not research {industry} industry: {str(e)}"


@proposal_agent.tool
async def get_current_date(ctx: RunContext[ProposalDeps]) -> str:
    """
    Get the current date. Use this if you need to reference today's date in the proposal.
    """
    return f"Today is {ctx.deps.current_date} ({ctx.deps.current_year})"


# =============================================================================
# GOOGLE DOCS FUNCTIONS
# =============================================================================

def authenticate_google():
    """Authenticate with Google APIs using OAuth 2.0."""
    print("🔐 Authenticating with Google...")

    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(CREDENTIALS_FILE)

    if gauth.credentials is None:
        print("   First time setup - opening browser for authentication...")
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        print("   Refreshing expired credentials...")
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile(CREDENTIALS_FILE)
    print("✅ Authentication successful!")

    drive = GoogleDrive(gauth)
    return drive, gauth.credentials


def copy_template_and_clear(drive, credentials, template_id: str, doc_name: str, folder_id: str = None) -> str:
    """Copy the template (to get logo) then clear content except logo."""
    print("📄 Copying template for logo...")

    drive_service = build('drive', 'v3', credentials=credentials)
    docs_service = build('docs', 'v1', credentials=credentials)

    body = {'name': doc_name}
    if folder_id:
        body['parents'] = [folder_id]

    copied_file = drive_service.files().copy(
        fileId=template_id,
        body=body
    ).execute()

    new_doc_id = copied_file['id']
    print(f"   ✅ Copied template: {new_doc_id}")

    doc = docs_service.documents().get(documentId=new_doc_id).execute()
    body_content = doc.get('body', {}).get('content', [])

    delete_start = None
    delete_end = None

    for element in body_content:
        if 'paragraph' in element:
            para = element['paragraph']
            elements = para.get('elements', [])
            has_image = any('inlineObjectElement' in el for el in elements)

            if has_image:
                delete_start = element.get('endIndex')
            elif delete_start is None:
                delete_start = element.get('startIndex')

        if 'endIndex' in element:
            delete_end = element.get('endIndex')

    if delete_start and delete_end and delete_end > delete_start:
        try:
            docs_service.documents().batchUpdate(
                documentId=new_doc_id,
                body={'requests': [{
                    'deleteContentRange': {
                        'range': {
                            'startIndex': delete_start,
                            'endIndex': delete_end - 1
                        }
                    }
                }]}
            ).execute()
            print(f"   ✅ Cleared template content (kept logo)")
        except Exception as e:
            print(f"   ⚠️ Could not clear content: {e}")

    return new_doc_id


def build_document(credentials, doc_id: str, proposal: ProposalOutput, client_name: str):
    """Build the document content with proper Casper Studios formatting and hyperlinks."""
    print("✏️  Building document content...")

    docs_service = build('docs', 'v1', credentials=credentials)
    tool_links = proposal.tool_links or {}

    doc = docs_service.documents().get(documentId=doc_id).execute()
    body_content = doc.get('body', {}).get('content', [])

    doc_end_index = 1
    for element in body_content:
        end_idx = element.get('endIndex', 0)
        if end_idx > doc_end_index:
            doc_end_index = end_idx

    current_index = max(doc_end_index - 1, 1)
    print(f"   Document end index: {doc_end_index}, inserting at: {current_index}")

    requests = []
    pending_hyperlinks = []
    # Track which tools have already been linked (link each tool only ONCE)
    linked_tools = set()

    def add_text_with_hyperlinks(text: str, style: dict, center: bool = False, space_above: float = 0, space_below: float = 0, is_bold_title: bool = False):
        nonlocal current_index

        text_start = current_index

        requests.append({
            'insertText': {
                'location': {'index': current_index},
                'text': text
            }
        })

        # Find tool names to hyperlink - but only ONCE per tool, and NOT in bold titles
        if not is_bold_title:
            for tool_name, url in tool_links.items():
                if not url.startswith('http'):
                    continue
                # Skip if already linked this tool
                if tool_name.lower() in linked_tools:
                    continue
                search_text = text.lower()
                tool_lower = tool_name.lower()
                pos = search_text.find(tool_lower)
                if pos != -1:
                    abs_start = text_start + pos
                    abs_end = abs_start + len(tool_name)
                    pending_hyperlinks.append({
                        'start': abs_start,
                        'end': abs_end,
                        'url': url
                    })
                    # Mark as linked so we don't link again
                    linked_tools.add(tool_name.lower())

        text_end = current_index + len(text)
        if text.endswith('\n'):
            text_end -= 1

        if text_end > current_index:
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': current_index,
                        'endIndex': text_end
                    },
                    'textStyle': style,
                    'fields': 'bold,italic,fontSize,weightedFontFamily,foregroundColor'
                }
            })

        para_style = {
            'lineSpacing': 115,
            'spaceAbove': {'magnitude': space_above, 'unit': 'PT'},
            'spaceBelow': {'magnitude': space_below, 'unit': 'PT'}
        }
        fields = 'lineSpacing,spaceAbove,spaceBelow'

        if center:
            para_style['alignment'] = 'CENTER'
            fields += ',alignment'

        requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': current_index,
                    'endIndex': current_index + len(text)
                },
                'paragraphStyle': para_style,
                'fields': fields
            }
        })

        current_index += len(text)

    def add_text(text: str, style: dict, center: bool = False, space_above: float = 0, space_below: float = 0, is_bold_title: bool = False):
        add_text_with_hyperlinks(text, style, center, space_above, space_below, is_bold_title)

    def add_empty_line():
        nonlocal current_index
        start_idx = current_index
        requests.append({
            'insertText': {
                'location': {'index': current_index},
                'text': '\n'
            }
        })
        current_index += 1
        requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': start_idx,
                    'endIndex': current_index
                },
                'paragraphStyle': {
                    'lineSpacing': 100,
                    'spaceAbove': {'magnitude': 0, 'unit': 'PT'},
                    'spaceBelow': {'magnitude': 0, 'unit': 'PT'}
                },
                'fields': 'lineSpacing,spaceAbove,spaceBelow'
            }
        })

    # Build document content
    # Title (centered)
    add_text(proposal.title + '\n', BRAND_PROFILE['title_style'], center=True)
    add_empty_line()

    # Context section
    add_text('Context\n', BRAND_PROFILE['section_header_style'])

    if proposal.context:
        add_text(proposal.context + '\n', BRAND_PROFILE['body_style'])

    prev_type = None

    for section in proposal.sections:
        section_type = section.type
        content = section.content or ''

        if section_type == 'section_header':
            add_empty_line()
            add_text(content + '\n', BRAND_PROFILE['section_header_style'])

        elif section_type == 'subsection_header':
            if prev_type not in ['section_header']:
                add_empty_line()
            add_text(content + '\n', BRAND_PROFILE['subsection_header_style'])

        elif section_type == 'paragraph':
            if prev_type not in ['section_header', 'subsection_header']:
                add_empty_line()
            add_text(content + '\n', BRAND_PROFILE['body_style'])

        elif section_type == 'closing_paragraph':
            add_text(content + '\n', BRAND_PROFILE['body_style'], space_above=12, space_below=12)

        elif section_type == 'cost':
            # Handle "Estimated cost: ..." with bold prefix
            if content.lower().startswith('estimated cost'):
                prefix = 'Estimated cost'
                rest = content[len('Estimated cost'):]
                add_text(prefix, BRAND_PROFILE['bold_body_style'], space_above=12)
                add_text(rest + '\n', BRAND_PROFILE['body_style'], space_below=12)
            else:
                add_text(content + '\n', BRAND_PROFILE['body_style'], space_above=12, space_below=12)

        elif section_type in ['bullet_list', 'numbered_list']:
            items = section.items or []
            list_start_index = current_index

            for item in items:
                title = item.title or ''
                desc = item.description or ''

                if title and desc:
                    # Bold title - don't hyperlink in bold titles
                    add_text(title, BRAND_PROFILE['bold_body_style'], is_bold_title=True)
                    # Description can have hyperlinks
                    add_text(': ' + desc + '\n', BRAND_PROFILE['body_style'])
                elif title:
                    add_text(title + '\n', BRAND_PROFILE['bold_body_style'], is_bold_title=True)
                elif desc:
                    add_text(desc + '\n', BRAND_PROFILE['body_style'])

            if items and current_index > list_start_index:
                bullet_preset = 'NUMBERED_DECIMAL_NESTED' if section_type == 'numbered_list' else 'BULLET_DISC_CIRCLE_SQUARE'
                requests.append({
                    'createParagraphBullets': {
                        'range': {
                            'startIndex': list_start_index,
                            'endIndex': current_index - 1
                        },
                        'bulletPreset': bullet_preset
                    }
                })

        prev_type = section_type

    # Apply hyperlinks
    if pending_hyperlinks:
        print(f"   Found {len(pending_hyperlinks)} tool mentions to hyperlink...")
        for link_info in pending_hyperlinks:
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': link_info['start'],
                        'endIndex': link_info['end']
                    },
                    'textStyle': {
                        'link': {'url': link_info['url']}
                    },
                    'fields': 'link'
                }
            })

    print(f"   Applying {len(requests)} formatting operations...")

    try:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        print(f"   ✅ Document built successfully")
        if pending_hyperlinks:
            print(f"   ✅ Applied {len(pending_hyperlinks)} hyperlinks")
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ Batch update failed: {error_msg[:200]}")
        raise


# =============================================================================
# ABOUT CASPER STUDIOS BOILERPLATE
# =============================================================================

ABOUT_CASPER_BOILERPLATE = """Casper Studios is an AI services firm that partners with financial services firms, enterprises, and high-growth startups to design and deploy practical AI agents, automations, and internal tools. Our core team blends product, strategy, and engineering experience from top-tier consulting firms and industry-leading technology companies including LinkedIn, PwC Strategy&, Amazon, Accenture, Bain, and Elliott Management:

To date, we've worked with a mix of hedge funds, family offices, fintechs, and consumer brands on AI initiatives that are live in production and tied to clear business outcomes:

• $2B AUM hedge fund – AI research agents that ingest filings, transcripts, and expert calls to automate call prep, meeting summaries, and portfolio dashboards (saving analysts an estimated 10–20 hours per week).
• Multi-family office – AI investment analysis engine that parses fund and direct-investment memos and scores opportunities against investor profiles (risk, check size, liquidity, themes).
• Netflix + PepsiCo + Omnicom – national Stranger Things x Doritos voice agent handling 300,000+ calls with interactive storytelling, branching dialogue, and promo flows.
• $10B vision-care company – AI Center of Excellence embedded with the Chief AI Officer to identify, prototype, and launch use cases across supply chain, software, insurance, and provider networks.
• $50M ARR SaaS company – AI education and adoption sprint mapping use cases, deploying self-serve automations, and training internal AI champions to capture ongoing productivity gains.
• $1B+ fintech startup – fraud-detection engine that flags risky applications and routes edge cases to reviewers, reducing manual intervention while improving consistency.

You can review more here: Casper Studios Overview_Final"""


# =============================================================================
# MAIN GENERATION FUNCTION
# =============================================================================

async def generate_proposal(
    transcript: str,
    client_name: str,
    project_name: str = "AI Automation",
    template_id: str = None,
    folder_id: str = None,
) -> dict:
    """Generate a proposal document using the AI agent."""
    template_id = template_id or DEFAULT_TEMPLATE_ID

    # Step 1: Authenticate with Google
    drive, credentials = authenticate_google()

    # Step 2: Run the AI agent to generate proposal content
    print("\n🤖 Running proposal agent...")
    print("   The agent will autonomously decide what to research...\n")

    # Clear captured URLs from any previous run
    global _captured_tool_urls
    _captured_tool_urls = {}

    deps = ProposalDeps(
        client_name=client_name,
        project_name=project_name,
        transcript=transcript,
    )

    user_prompt = f"""Generate a professional proposal for:
- Client: {client_name}
- Project: {project_name}

Based on this meeting transcript/notes:

{transcript}

Use your tools to research as needed. Include all tool URLs you look up in the tool_links field so they can be hyperlinked in the document.

Remember to follow the EXACT template structure from the system prompt."""

    result = await proposal_agent.run(user_prompt, deps=deps)
    proposal = result.output

    # Merge captured URLs into proposal (in case agent didn't include them)
    all_tool_links = {**_captured_tool_urls, **(proposal.tool_links or {})}
    proposal.tool_links = all_tool_links

    print(f"\n   ✅ Agent generated proposal with {len(proposal.sections)} sections")
    print(f"   ✅ Tool links for hyperlinking: {list(all_tool_links.keys())}")

    # Step 3: Copy template and clear content
    doc_name = f"[External] {client_name} & Casper Studios"
    new_doc_id = copy_template_and_clear(drive, credentials, template_id, doc_name, folder_id)

    # Step 4: Build document with content
    build_document(credentials, new_doc_id, proposal, client_name)

    document_url = f"https://docs.google.com/document/d/{new_doc_id}/edit"

    return {
        'document_id': new_doc_id,
        'document_url': document_url,
        'proposal_content': proposal.model_dump()
    }


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Generate client proposals using AI agent with autonomous research (V3)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--transcript", help="Direct transcript text")
    input_group.add_argument("--transcript-file", help="Path to transcript file")

    parser.add_argument("--client", required=True, help="Client company name")
    parser.add_argument("--project", default="AI Automation", help="Project name")
    parser.add_argument("--template-id", help=f"Template document ID (default: {DEFAULT_TEMPLATE_ID})")
    parser.add_argument("--folder-id", help="Destination folder ID in Google Drive")
    parser.add_argument("--output-json", help="Save result to JSON file")

    args = parser.parse_args()

    try:
        if args.transcript_file:
            transcript_path = Path(args.transcript_file)
            if not transcript_path.exists():
                print(f"❌ Transcript file not found: {args.transcript_file}")
                return 1
            transcript = transcript_path.read_text()
        else:
            transcript = args.transcript

        if not transcript.strip():
            print("❌ Transcript is empty!")
            return 1

        print(f"\n📋 Generating proposal for: {args.client}")
        print(f"   Project: {args.project}")
        print(f"   Transcript length: {len(transcript)} chars\n")

        result = asyncio.run(generate_proposal(
            transcript=transcript,
            client_name=args.client,
            project_name=args.project,
            template_id=args.template_id,
            folder_id=args.folder_id,
        ))

        print(f"\n✅ Proposal generated successfully!")
        print(f"\n📄 Document URL: {result['document_url']}")

        if args.output_json:
            import json
            output_path = Path(args.output_json)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(result, indent=2))
            print(f"📁 Result saved to: {args.output_json}")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
