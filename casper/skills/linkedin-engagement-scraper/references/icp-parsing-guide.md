# ICP Parsing Guide

How to turn natural language into structured ICP segments.

## Core Concept: Segments

An ICP is composed of one or more **segments**. Each segment defines a target pocket of the market.
Users almost always think in segments even if they don't use that word — they'll say "I also want..."
or "and then for healthcare..." which signals a new segment.

## Parsing Rules

### 1. Identify Segment Boundaries

Listen for these signals that the user is defining a new segment:
- Industry shift: "...and then for healthcare companies..."
- Conjunction with new criteria: "Also interested in..."
- Contrasting criteria: "But for smaller companies, I want..."

If the user describes one set of criteria with no segment signals, treat it as a single segment.

### 2. Extract Criteria Per Segment

For each segment, extract whatever the user provides from these dimensions:

| Dimension | Examples | Notes |
|---|---|---|
| **Industry** | Financial services, healthcare, SaaS, manufacturing | Map to standard industry categories |
| **Company size** | Revenue range, AUM, employee count, funding stage | Capture the metric AND the range |
| **Company tier** | Fortune 500/1000/2000, Inc 5000, public vs. private | These are separate from size |
| **Geography** | US-based, EMEA, specific states/countries | Often implied (e.g., Fortune 2000 implies US-centric) |
| **Target titles** | Head of AI, VP Engineering, CTO, Director of Data | See title normalization below |
| **Seniority level** | C-suite, VP+, Director+, Manager+ | Sometimes given as a floor |
| **Other qualifiers** | "Companies currently hiring for AI roles", "Recently raised Series B+" | Capture as free-text criteria |

### 3. Handle Implied Criteria

Users often leave things implicit. Common patterns:

- **"Fortune 2000"** implies large US-centric companies, typically $1B+ revenue
- **"Head of AI"** without seniority context implies VP-equivalent or above
- **"AUM"** only applies to financial services — if the user mentions AUM for a non-financial segment, clarify
- **"Startups"** typically means Series A–C, <500 employees, unless they specify otherwise

When criteria are implied, include them in your confirmation but mark them as inferred:
> "I'm assuming Fortune 2000 means US-centric companies — is that right?"

### 4. Handle Ambiguity

If the user says something genuinely ambiguous, ask. Common ambiguities:

- **"Big companies"** — What's big? Revenue? Headcount? Give them options.
- **"Tech leaders"** — Title (CTO, VP Eng) or companies that are tech leaders?
- **"AI people"** — People who work in AI, or people at AI companies?

Don't over-ask though. If you can reasonably infer intent, confirm your interpretation rather than
asking an open-ended question.

## Title Normalization

Job titles on LinkedIn are messy. Here's how to map common titles to seniority levels:

### C-Suite
CEO, CTO, CIO, CDO (Chief Data Officer), CAIO (Chief AI Officer), CFO, COO, CMO,
Chief [Anything] Officer, Co-Founder, Founder

### VP Level
VP, Vice President, SVP, Senior Vice President, EVP, Executive Vice President,
Head of [Department], Global Head of [Department]

### Director Level
Director, Senior Director, Managing Director (context-dependent — in banking this is more senior),
Group Director, Associate Director (borderline — include if user says "Director+")

### Manager Level
Manager, Senior Manager, Program Manager, Product Manager, Engineering Manager

### Individual Contributor (Senior)
Principal, Staff, Senior [Role], Lead [Role], Architect

### Mapping Rules
- "VP+" means VP Level and above (C-Suite + VP)
- "Director+" means Director Level and above
- Treat "Head of" as VP-equivalent regardless of whether it says VP
- "Partner" at consulting/law/VC firms is C-Suite equivalent
- "Managing Director" at banks/financial firms is senior (VP+ equivalent)
- When in doubt, include the contact and note the ambiguity

## Output Format

After parsing, structure the ICP as:

```json
{
  "segments": [
    {
      "name": "Financial Services",
      "industry": ["financial services", "banking", "asset management", "insurance"],
      "company_size": {
        "metric": "aum",
        "min": 1000000000,
        "max": 10000000000
      },
      "company_tier": ["Fortune 2000"],
      "target_titles": {
        "keywords": ["AI", "ML", "machine learning", "data", "artificial intelligence"],
        "min_seniority": "vp"
      },
      "geography": null,
      "other_qualifiers": []
    }
  ]
}
```

This structure is for your internal use during filtering — don't show the raw JSON to the user.
Show them the human-readable confirmation table instead.
