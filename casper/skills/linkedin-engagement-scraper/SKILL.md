---
name: linkedin-engagement-scraper
description: >
  Scrape LinkedIn post commenters and export Lemlist-ready CSVs, with optional ICP filtering.
  Use this skill when the user wants to scrape engagement from a LinkedIn post, extract commenters,
  build a lead list from LinkedIn post interactions, generate a CSV for Lemlist import, or filter
  scraped contacts against an Ideal Customer Profile. Triggers on "scrape LinkedIn post",
  "get commenters", "LinkedIn engagement", "post engagers", "Lemlist CSV", "who commented on this post",
  "ICP filter", "ideal customer profile", or "filter leads".
---

# LinkedIn Engagement Scraper

Scrape everyone who engaged with a LinkedIn post and produce two Lemlist-ready outputs:

1. **All engagers** — everyone who commented, ready for Lemlist import
2. **ICP matches** — only the people who match your Ideal Customer Profile

## Pipeline

```
LinkedIn post URL
        ↓
scrape_engagers.py (PhantomBuster API)
        ↓
    ┌───┴───┐
    │       │
    ▼       ▼
All CSV   engagers.json
(Lemlist)     │
              ▼
        filter_icp.py (define ICP → score → filter)
              │
              ▼
        ICP Matches CSV
          (Lemlist)
```

## Prerequisites

| Requirement | Details |
|-------------|---------|
| `PHANTOMBUSTER_API_KEY` | [Settings → API](https://phantombuster.com/settings#api) |
| `PHANTOMBUSTER_AGENT_ID` | From phantom URL: `phantombuster.com/phantoms/<ID>/...` |
| Python packages | `pip install requests python-dotenv` |

Set the env vars in a `.env` file in the working directory.
See `references/phantombuster-setup.md` for full PhantomBuster setup instructions.

## Step 1: Scrape Engagers

```bash
python <skill-path>/scripts/scrape_engagers.py "<linkedin_post_url>"
```

This launches PhantomBuster, waits for results, and outputs:

| File | Purpose |
|------|---------|
| `output/all_engagers_YYYY-MM-DD_HHMMSS.csv` | All contacts, Lemlist-ready. Import directly. |
| `output/engagers.json` | Full contact data with seniority tagging. Feed to Step 2. |

## Step 2: Filter by ICP (Optional)

```bash
python <skill-path>/scripts/filter_icp.py output/engagers.json
```

The script prompts you to define your ICP interactively:

```
--- Define your Ideal Customer Profile ---

Segment 1:
  Industries (comma-separated, or blank for any): saas, fintech
  Target titles/keywords (comma-separated, or blank for any): vp, head of, director
  Minimum seniority [c_suite / vp / director / manager / senior_ic / any]: director
  Company name keywords (comma-separated, or blank for any):

  Add another segment? (y/n): n
```

Or reuse a saved ICP:

```bash
python <skill-path>/scripts/filter_icp.py output/engagers.json --icp output/icp_criteria.json
```

Output:

| File | Purpose |
|------|---------|
| `output/icp_matches_YYYY-MM-DD_HHMMSS.csv` | Strong + likely ICP matches, Lemlist-ready |
| `output/icp_criteria.json` | Your saved ICP (reuse on future scrapes) |

## ICP Matching Logic

Each contact is scored against your ICP segments on four dimensions:

| Dimension | Source | What it checks |
|-----------|--------|----------------|
| **Title keywords** | LinkedIn headline | Does their title contain your target keywords? |
| **Company keywords** | LinkedIn headline | Does their company match your targets? |
| **Seniority** | Parsed from title | Are they at or above your minimum seniority level? |
| **Industry** | LinkedIn headline | Does their company/headline match your target industries? |

Fit ratings:
- **Strong fit** — Matches all active criteria
- **Likely fit** — Matches all but one criterion
- **Weak fit** — Partial match
- **No fit** — Doesn't match

The ICP CSV includes strong + likely fits. Weak fits are output as a fallback if no strong/likely matches exist.

## Seniority Levels

Parsed automatically from job titles:

| Level | Example titles |
|-------|---------------|
| `c_suite` | CEO, CTO, Founder, Chief __ Officer |
| `vp` | VP, SVP, Head of, Partner |
| `director` | Director, Senior Director, Managing Director |
| `manager` | Manager, Senior Manager, Product Manager |
| `senior_ic` | Principal, Staff, Lead, Architect |
| `individual_contributor` | Everything else |

See `references/icp-parsing-guide.md` for detailed parsing rules.

## Lemlist CSV Columns

Both output CSVs use the same Lemlist-compatible format:

| Column | Description |
|--------|-------------|
| `email` | Blank — Lemlist enriches from LinkedIn URL on import |
| `firstName` | First name |
| `lastName` | Last name |
| `companyName` | Company (extracted from LinkedIn headline) |
| `linkedinUrl` | LinkedIn profile URL |
| `jobTitle` | Job title (extracted from LinkedIn headline) |
| `icebreaker` | Comment text — use `{{icebreaker}}` in Lemlist templates |
| `icpFit` | _(ICP CSV only)_ strong_fit or likely_fit |

## Importing into Lemlist

1. Open Lemlist → your campaign → Import
2. Upload the CSV (either `all_engagers` or `icp_matches`)
3. Lemlist auto-enriches emails from the LinkedIn URLs
4. Use `{{icebreaker}}` in your email template for personalization

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `412 Precondition Failed` on launch | Enable auto-launch in PhantomBuster phantom settings |
| `403` or auth errors | Check `PHANTOMBUSTER_API_KEY` in `.env` |
| 0 contacts returned | Post has no comments, or PhantomBuster session cookie expired |
| Missing company/title | Person's headline doesn't follow "Title at Company" format |
| 0 ICP matches | Broaden criteria — try fewer keywords or lower seniority minimum |
