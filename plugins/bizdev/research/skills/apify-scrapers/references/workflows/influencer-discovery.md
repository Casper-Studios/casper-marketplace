# Influencer Discovery Workflow

## Overview

Comprehensive multi-platform influencer discovery system with scoring algorithms, tier classification, fake follower detection, brand safety analysis, and contact extraction. Find and evaluate influencers across Instagram, TikTok, YouTube, and Twitter/X for partnerships, collaborations, or outreach campaigns.

## Key Features

- **Multi-Platform Discovery**: Instagram, TikTok, YouTube, Twitter/X
- **Influencer Scoring Algorithm**: Weighted scoring based on 5 factors
- **Tier Classification**: Nano to Mega influencer categorization
- **Fake Follower Detection**: Heuristic-based authenticity scoring
- **Brand Safety Analysis**: Content sentiment and risk flagging
- **Contact Extraction**: Email, website, and link-in-bio extraction
- **Cost Estimation**: Estimated post rates and CPM by tier

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      INFLUENCER DISCOVERY WORKFLOW                   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
     ┌──────────────────────────────┼──────────────────────────────┐
     ▼                              ▼                              ▼
┌─────────────┐            ┌─────────────┐            ┌─────────────┐
│  DISCOVERY  │            │  ENRICHMENT │            │   OUTPUT    │
│   SOURCES   │            │   ENGINES   │            │   FORMATS   │
├─────────────┤            ├─────────────┤            ├─────────────┤
│ Hashtags    │───────────▶│ Scoring     │───────────▶│ JSON        │
│ Keywords    │            │ Authenticity│            │ CSV         │
│ Competitors │            │ Brand Safety│            │ Sheets      │
│ Similar Acc │            │ Contacts    │            │ CRM         │
│ Location    │            │ Categories  │            │             │
└─────────────┘            └─────────────┘            └─────────────┘
```

---

## Workflow Steps

```
Step 1: Configure Discovery Parameters
├── Choose platform(s): instagram, tiktok, youtube, twitter
├── Set discovery method: hashtag, keyword, competitor, similar
├── Define filters: tier, engagement, followers, location
└── Set result limits and output format

Step 2: Scrape Platform Data
├── Instagram: hashtag posts → extract creator handles
├── TikTok: hashtag videos → extract author profiles
├── YouTube: search results → extract channel data
└── Twitter: search tweets → extract user profiles

Step 3: Extract Unique Influencers
├── Deduplicate creators from posts
├── Aggregate engagement metrics
├── Calculate averages per creator
└── Build initial influencer profiles

Step 4: Enrich & Score Influencers
├── Calculate engagement rate
├── Estimate authenticity score
├── Analyze brand safety
├── Extract contact information
├── Categorize content types
├── Calculate overall influencer score
└── Classify tier and estimate rates

Step 5: Filter & Rank Results
├── Apply tier filters
├── Apply engagement thresholds
├── Apply follower range filters
├── Sort by influencer score
└── Generate distribution analytics

Step 6: Export for Outreach
├── JSON: Full data for processing
├── CSV: Spreadsheet-ready format
├── Google Sheets: Direct import
└── CRM: Attio/HubSpot ready
```

---

## Influencer Scoring Algorithm

### Weighted Scoring Model

| Factor | Weight | Description |
|--------|--------|-------------|
| Engagement Rate | 30% | (likes + comments) / followers |
| Follower Authenticity | 25% | Estimated real follower % |
| Content Relevance | 20% | Match to target hashtags/topics |
| Posting Consistency | 15% | Regular posting frequency |
| Growth Rate | 10% | Follower growth trend |

### Score Calculation

```python
# Engagement normalized (5% = perfect 100)
engagement_score = min(100, (engagement_rate / 5) * 100)

# Posting normalized (7 posts/week = 100)
posting_score = min(100, (posts_per_week / 7) * 100)

# Final weighted score
influencer_score = (
    engagement_score * 0.30 +
    authenticity_score * 0.25 +
    relevance_score * 0.20 +
    posting_score * 0.15 +
    growth_score * 0.10
)
```

### Score Interpretation

| Score | Rating | Recommendation |
|-------|--------|----------------|
| 80-100 | Excellent | Highly recommended for partnerships |
| 60-79 | Good | Strong candidate, verify content fit |
| 40-59 | Average | Review manually before outreach |
| 20-39 | Below Average | Consider only if niche-specific |
| 0-19 | Poor | Not recommended |

---

## Tier Classification

| Tier | Follower Range | Typical Engagement | Estimated Post Rate |
|------|----------------|-------------------|---------------------|
| **Nano** | 1K - 10K | 5-10% | $50 - $250 |
| **Micro** | 10K - 100K | 3-5% | $250 - $1,500 |
| **Mid** | 100K - 500K | 2-3% | $1,500 - $5,000 |
| **Macro** | 500K - 1M | 1.5-2% | $5,000 - $15,000 |
| **Mega** | 1M+ | 1-1.5% | $15,000 - $100,000+ |

### CPM Estimates by Platform

| Platform | Nano CPM | Micro CPM | Mid CPM | Macro CPM |
|----------|----------|-----------|---------|-----------|
| Instagram | $2-5 | $5-15 | $15-30 | $30-50 |
| TikTok | $1.5-4 | $4-12 | $12-24 | $24-40 |
| YouTube | $3-7.5 | $7.5-22 | $22-45 | $45-75 |
| Twitter | $1.5-3.5 | $3.5-10 | $10-21 | $21-35 |

---

## Fake Follower Detection

### Authenticity Heuristics

```
HIGH AUTHENTICITY (80-100%):
├── Engagement rate matches tier expectations
├── Diverse commenters (many unique users)
├── Thoughtful comments (avg length > 50 chars)
└── Consistent engagement across posts

MEDIUM AUTHENTICITY (50-79%):
├── Slightly below-expected engagement
├── Some comment diversity
└── Mixed comment quality

LOW AUTHENTICITY (0-49%):
├── Very low engagement for follower count
├── Same users commenting repeatedly
├── Short, generic comments ("Nice!", "Amazing!")
├── Sudden follower spikes
└── Engagement/follower ratio anomalies
```

### Detection Algorithm

```python
# Expected engagement by tier
expected = {"nano": 5.0, "micro": 3.0, "mid": 2.0, "macro": 1.5, "mega": 1.0}

# Penalize low engagement
if engagement < expected * 0.3:
    score -= 40  # Major red flag
elif engagement < expected * 0.5:
    score -= 25

# Penalize suspiciously high engagement
if engagement > expected * 5:
    score -= 30  # Possible fake engagement

# Bonus for quality comments
if avg_comment_length > 50:
    score += 5

# Bonus for diverse commenters
if unique_commenters / total_comments > 0.8:
    score += 10
```

---

## Brand Safety Analysis

### Risk Levels

| Level | Status | Description |
|-------|--------|-------------|
| Green | Safe | No significant brand safety concerns |
| Yellow | Caution | Some potentially risky content |
| Red | Risk | Multiple high-risk content flags |

### Flagged Categories

**Red Flags (High Risk):**
- Controversial topics
- Political content
- NSFW/Adult content
- Gambling
- Violence
- Drug/Alcohol promotion
- Tobacco
- Weapons

**Yellow Flags (Moderate Risk):**
- Strong opinions
- Rant content
- Debate/Drama
- Call-out content
- "Beef" between creators

### Analysis Output

```json
{
  "status": "yellow",
  "description": "Some potentially risky content",
  "red_flags": 1,
  "yellow_flags": 2,
  "flagged_terms": [
    {"term": "controversial", "severity": "red"},
    {"term": "opinion", "severity": "yellow"}
  ]
}
```

---

## Contact Extraction

### Extracted Data Points

| Field | Source | Pattern |
|-------|--------|---------|
| Email | Bio text | Standard email regex |
| Business Email | Bio text | "business:", "collab:", "inquiry:" prefixes |
| Website | Profile URL | External link field |
| Linktree | Bio text | linktr.ee/username |
| Other Links | Bio text | beacons.ai, stan.store, bio.link |

### Email Extraction Patterns

```python
# Standard email
[\w.+-]+@[\w-]+\.[\w.-]+

# Business email patterns
business[\s:]+([^\s]+@[\w-]+\.[\w.-]+)
collab[\s:]+([^\s]+@[\w-]+\.[\w.-]+)
inquiry[\s:]+([^\s]+@[\w-]+\.[\w.-]+)
contact[\s:]+([^\s]+@[\w-]+\.[\w.-]+)
```

---

## CLI Commands

### Basic Discovery

```bash
# Discover by hashtag on Instagram
python scripts/discover_influencers.py --hashtags fitness health --platform instagram

# Discover by topic (auto-converts to hashtags)
python scripts/discover_influencers.py --topic "sustainable fashion" --platform instagram

# Multi-platform discovery
python scripts/discover_influencers.py --topic "AI" --platforms instagram tiktok youtube
```

### Filtered Discovery

```bash
# Filter by tier
python scripts/discover_influencers.py --hashtags tech --tier micro mid

# Filter by engagement rate
python scripts/discover_influencers.py --hashtags beauty --min-engagement 3.0

# Filter by follower count
python scripts/discover_influencers.py --hashtags travel --min-followers 10000 --max-followers 100000

# Combined filters
python scripts/discover_influencers.py \
  --hashtags fitness health nutrition \
  --platform instagram \
  --tier micro \
  --min-engagement 3.0 \
  --min-followers 10000 \
  --max-results 200
```

### Enriched Discovery

```bash
# Fetch detailed profile data (slower, more accurate)
python scripts/discover_influencers.py --hashtags beauty --platform instagram --fetch-profiles

# Extract contact information
python scripts/discover_influencers.py --hashtags tech --extract-contacts --output contacts.json
```

### Export Options

```bash
# Export as JSON (default)
python scripts/discover_influencers.py --topic "AI" --output influencers.json

# Export as CSV for spreadsheets
python scripts/discover_influencers.py --topic "AI" --format csv --output outreach_list.csv

# Full outreach list with contacts
python scripts/discover_influencers.py \
  --hashtags tech AI startup \
  --tier micro mid \
  --min-engagement 2.0 \
  --extract-contacts \
  --format csv \
  --output tech_influencers_outreach.csv
```

---

## Output Format

### JSON Output Structure

```json
{
  "query": {
    "hashtags": ["fitness", "health"],
    "platforms": ["instagram"],
    "tiers": ["micro"],
    "min_engagement": 3.0,
    "min_followers": 10000
  },
  "discovered_at": "2024-01-15T10:30:00",
  "total_found": 150,
  "influencers": [
    {
      "username": "@fitnessguru",
      "platform": "instagram",
      "full_name": "John Fitness",
      "followers": 85000,
      "engagement_rate": 4.2,
      "influencer_score": 87,
      "tier": "micro",
      "tier_label": "Micro (10K-100K)",
      "authenticity_score": 92,
      "verified": false,
      "estimated_post_rate": "$250-1.5K",
      "cpm_estimate": "$5-15",
      "contact": {
        "email": "business@fitnessguru.com",
        "website": "https://fitnessguru.com",
        "linktree": "https://linktr.ee/fitnessguru"
      },
      "top_hashtags": ["fitness", "workout", "gym", "health", "gains"],
      "content_categories": ["fitness", "health", "lifestyle"],
      "brand_safety": "green",
      "brand_safety_detail": {
        "status": "green",
        "description": "No significant brand safety concerns",
        "red_flags": 0,
        "yellow_flags": 0
      },
      "profile_url": "https://www.instagram.com/fitnessguru/",
      "bio": "Certified PT | Transform your body | Business: business@fitnessguru.com",
      "sample_posts_analyzed": 25,
      "avg_likes": 3500,
      "avg_comments": 125
    }
  ],
  "tier_distribution": {
    "nano": 45,
    "micro": 78,
    "mid": 20,
    "macro": 5,
    "mega": 2
  },
  "platform_breakdown": {
    "instagram": 150
  },
  "scoring_weights": {
    "engagement_rate": 0.30,
    "follower_authenticity": 0.25,
    "content_relevance": 0.20,
    "posting_consistency": 0.15,
    "growth_rate": 0.10
  }
}
```

### CSV Output Columns

| Column | Description |
|--------|-------------|
| username | @handle |
| platform | Social platform |
| full_name | Display name |
| followers | Follower count |
| engagement_rate | Engagement % |
| influencer_score | Overall score (0-100) |
| tier | Tier classification |
| authenticity_score | Authenticity % |
| verified | Verified badge |
| estimated_post_rate | Estimated cost |
| email | Extracted email |
| website | Profile website |
| categories | Content categories |
| top_hashtags | Top 5 hashtags |
| brand_safety | Safety status |
| profile_url | Direct profile link |
| bio | Bio snippet |

---

## Platform-Specific Actors

### Instagram

| Actor | Purpose | Cost/1000 |
|-------|---------|-----------|
| `apify/instagram-hashtag-scraper` | Hashtag discovery | ~$0.50 |
| `apify/instagram-profile-scraper` | Profile details | ~$1.00 |
| `apify/instagram-scraper` | Posts from profiles | ~$0.50 |
| `apify/instagram-comment-scraper` | Comment analysis | ~$1.00 |

### TikTok

| Actor | Purpose | Cost/1000 |
|-------|---------|-----------|
| `clockworks/tiktok-scraper` | Hashtag/profile | ~$0.50 |

### YouTube

| Actor | Purpose | Cost/1000 |
|-------|---------|-----------|
| `streamers/youtube-scraper` | Search results | ~$1.00 |
| `streamers/youtube-channel-scraper` | Channel details | ~$1.50 |

### Twitter/X

| Actor | Purpose | Cost/1000 |
|-------|---------|-----------|
| `kaitoeasyapi/twitter-x-data-tweet-scraper` | Search/profile | ~$1.00 |

---

## Cost Estimation

### Per Discovery Run

| Configuration | Est. Cost |
|---------------|-----------|
| Single platform, 100 posts | $0.50 - $1.00 |
| Single platform + profiles (50) | $1.50 - $2.50 |
| Multi-platform (3), 100 each | $2.00 - $4.00 |
| Multi-platform + profiles | $4.00 - $7.00 |
| Full enrichment + contacts | $5.00 - $10.00 |

### Optimization Tips

1. **Start narrow**: Use specific hashtags, not broad topics
2. **Limit results**: Start with 50-100, increase if needed
3. **Skip profiles initially**: Only fetch if you need bio data
4. **Use tier filters**: Narrow by tier before enriching
5. **Batch similar searches**: Combine related hashtags

---

## Integration Workflows

### Outreach Campaign Pipeline

```
1. Discover influencers
   python scripts/discover_influencers.py --topic "AI" --tier micro mid --format csv

2. Import to Google Sheets (use google-workspace skill)
   # Creates filterable spreadsheet

3. Review and shortlist manually
   # Add "Status" column, filter top candidates

4. Enrich with Parallel Research (use parallel-research skill)
   # Get additional company/personal intel

5. Add to CRM (use attio-crm skill)
   # Create contacts with tags

6. Launch outreach sequence
   # Use email automation or manual outreach
```

### Competitor Follower Mining

```
1. Find competitor's top posts
   python scripts/scrape_instagram.py posts @competitor --max-posts 50

2. Extract commenters (power users)
   # Parse comments for engaged followers

3. Filter for influencer-level accounts
   python scripts/discover_influencers.py --profiles [list] --min-followers 10000

4. Analyze and score
   # Full enrichment on filtered list
```

### Brand Partnership Qualification

```
1. Initial discovery with broad filters
   python scripts/discover_influencers.py --hashtags [industry] --max-results 500

2. Apply strict brand safety filter
   # Keep only "green" status

3. Filter by authenticity
   # Keep only 70%+ authenticity

4. Export qualified leads
   python scripts/discover_influencers.py [...] --min-authenticity 70 --format csv
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Low results | Niche hashtags | Add more related hashtags |
| High fake followers | Inflated accounts | Increase authenticity threshold |
| Missing emails | Not in bio | Try linktree extraction |
| Platform errors | Rate limits | Reduce batch size, add delays |
| Inaccurate scores | Limited post data | Enable `--fetch-profiles` |

### Rate Limits

- Instagram: ~100 profiles/hour without proxy
- TikTok: ~200 videos/hour
- YouTube: ~100 videos/hour
- Twitter: ~150 tweets/hour

### Data Quality

- **Engagement rate accuracy**: Based on sample posts, may vary
- **Authenticity score**: Heuristic estimate, not definitive
- **Contact extraction**: Depends on bio content quality
- **Brand safety**: Keyword-based, not sentiment analysis

---

## Best Practices

### For Discovery

1. **Use niche hashtags**: `#veganrecipes` > `#food`
2. **Combine related terms**: 3-5 hashtags per search
3. **Start with micro tier**: Best engagement/cost ratio
4. **Check recent activity**: Filter for active creators
5. **Verify content fit**: Review actual posts before outreach

### For Outreach

1. **Personalize messages**: Reference specific content
2. **Start with email**: More professional than DMs
3. **Clear value proposition**: What's in it for them?
4. **Respect rates**: Don't lowball based on estimates
5. **Build relationships**: Long-term > one-off

### For Campaigns

1. **Mix tiers**: Nano for authenticity, Macro for reach
2. **Platform match**: Choose platform for audience fit
3. **Content guidelines**: Clear but not restrictive
4. **Track performance**: Unique codes/links per influencer
5. **Measure ROI**: CPM, CPA, engagement lift

---

## Related Skills

- **google-workspace**: Export to Google Sheets
- **attio-crm**: Add influencers as CRM contacts
- **parallel-research**: Deep research on top candidates
- **content-generation**: Create outreach templates
- **slack-automation**: Alert on new discoveries

---

## References

- [Apify Instagram Scraper](https://apify.com/apify/instagram-scraper)
- [Apify TikTok Scraper](https://apify.com/clockworks/tiktok-scraper)
- [Apify YouTube Scraper](https://apify.com/streamers/youtube-scraper)
- [Influencer Marketing Hub - Rate Calculator](https://influencermarketinghub.com/instagram-money-calculator/)
