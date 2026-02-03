# Competitor Ads Intelligence Workflow

## Overview

Comprehensive competitor advertising intelligence across Facebook/Meta Ads Library and Google Ads Transparency Center. This workflow extracts, analyzes, and benchmarks competitor advertising strategies with rich analytics and comparison capabilities.

**What This Does:**
- Scrape competitor ads from Meta Ads Library (Facebook, Instagram, Messenger, Audience Network)
- Extract Google Ads Transparency Center data (Search, YouTube, Display)
- Generate spend estimates and performance insights
- Compare multiple competitors side-by-side
- Extract messaging themes and creative strategies

**Why This is Enriched (Beyond Basic Apify Skills):**
- Aggregated summary analytics across all scraped ads
- Multi-competitor benchmarking with relative rankings
- Creative type distribution analysis
- Messaging theme extraction and categorization
- Platform focus comparison
- Historical trend insights

## Workflow Architecture

```
                    +-----------------+
                    |   CLI Input     |
                    | (competitors,   |
                    |  platforms,     |
                    |  options)       |
                    +--------+--------+
                             |
            +----------------+----------------+
            |                                 |
    +-------v-------+               +---------v---------+
    |  Facebook Ads |               |  Google Ads       |
    |  Library      |               |  Transparency     |
    |  Scraper      |               |  Center Scraper   |
    +-------+-------+               +---------+---------+
            |                                 |
            +----------------+----------------+
                             |
                    +--------v--------+
                    |   Data Fusion   |
                    |   & Enrichment  |
                    +--------+--------+
                             |
                    +--------v--------+
                    |   Analytics     |
                    |   Engine        |
                    +--------+--------+
                             |
            +----------------+----------------+
            |                |                |
    +-------v-------+ +------v------+ +-------v-------+
    |  Summary      | | Comparison  | |   Trends      |
    |  Statistics   | | Matrix      | |   Analysis    |
    +---------------+ +-------------+ +---------------+
                             |
                    +--------v--------+
                    |   JSON Output   |
                    |   with Rich     |
                    |   Analytics     |
                    +--------+--------+
```

## Apify Actors Used

| Platform | Actor ID | Purpose | Cost |
|----------|----------|---------|------|
| **Facebook/Meta Ads** | `apify/facebook-ads-scraper` | Official Meta Ads Library scraper | ~$0.75/1K ads |
| **Facebook Ads (alt)** | `curious_coder/facebook-ads-library-scraper` | Lightweight alternative | ~$0.50/1K ads |
| **Google Ads** | `lexis-solutions/google-ads-scraper` | Google Ads Transparency Center | ~$1.00/1K ads |
| **Google Ads (alt)** | `xtech/google-ad-transparency-scraper` | Full/Lite modes with batch | ~$0.80/1K ads |

## Input Parameters

### Competitor Targeting

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `competitors` | list | required | Competitor names, domains, or page URLs |
| `--search` | string | null | Keyword-based discovery mode |
| `--country` | string | "US" | Target country (ISO code) |
| `--platforms` | list | ["facebook"] | Platforms: facebook, google, both |
| `--days` | int | 30 | Lookback period for ads |
| `--max-ads` | int | 100 | Maximum ads per competitor |

### Filtering Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--status` | string | "active" | Ad status: active, inactive, all |
| `--media-types` | list | all | Filter: image, video, carousel, text |
| `--min-spend` | int | null | Minimum spend estimate (USD) |
| `--languages` | list | null | Ad language filter |
| `--exclude-political` | bool | true | Exclude political/issue ads |

### Output Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--output` | string | auto | Output filename (JSON) |
| `--compare` | flag | false | Enable comparison mode |
| `--include-creatives` | bool | false | Download ad creative assets |
| `--format` | string | "json" | Output format: json, csv |

## CLI Usage Examples

### Basic Usage

```bash
# Single competitor analysis
python scripts/scrape_competitor_ads.py "Nike" --platforms facebook google --country US --days 30

# Multiple competitor names
python scripts/scrape_competitor_ads.py "Nike" "Adidas" "Puma" --platforms facebook --max-ads 200

# Using domain names
python scripts/scrape_competitor_ads.py "nike.com" "adidas.com" --platforms google
```

### Comparison Mode

```bash
# Side-by-side comparison of competitors
python scripts/scrape_competitor_ads.py "Nike" "Adidas" "Puma" --compare --output comparison.json

# Full benchmark with all metrics
python scripts/scrape_competitor_ads.py "Shopify" "BigCommerce" "WooCommerce" \
  --compare \
  --platforms facebook google \
  --days 60 \
  --output ecommerce_comparison.json
```

### Keyword Discovery

```bash
# Find advertisers by keyword/topic
python scripts/scrape_competitor_ads.py --search "running shoes" --country US --max-ads 200

# Discover competitors in a niche
python scripts/scrape_competitor_ads.py --search "AI writing assistant" --platforms facebook google --days 14

# Industry-specific discovery
python scripts/scrape_competitor_ads.py --search "CRM software small business" --country GB
```

### Advanced Filtering

```bash
# Video ads only from active campaigns
python scripts/scrape_competitor_ads.py "Netflix" "Disney+" "HBO Max" \
  --media-types video \
  --status active \
  --days 7

# High-spend advertisers only
python scripts/scrape_competitor_ads.py "Salesforce" "HubSpot" "Zoho" \
  --min-spend 10000 \
  --platforms facebook

# Non-English markets
python scripts/scrape_competitor_ads.py "Mercado Libre" "Amazon" \
  --country MX \
  --languages es
```

## Output Structure

### Full Output Schema

```json
{
  "metadata": {
    "scraped_at": "2024-01-15T10:30:00Z",
    "competitors_analyzed": ["Nike", "Adidas", "Puma"],
    "platforms": ["facebook", "google"],
    "country": "US",
    "date_range": {
      "start": "2023-12-15",
      "end": "2024-01-15"
    },
    "filters_applied": {
      "status": "active",
      "media_types": "all",
      "exclude_political": true
    }
  },

  "competitors": [
    {
      "name": "Nike",
      "identifier": "nike",
      "facebook_page_id": "123456789",
      "google_advertiser_id": "AR123456789",
      "platforms": {
        "facebook": {
          "total_ads": 145,
          "active_ads": 98,
          "inactive_ads": 47,
          "spend_estimate": {
            "lower_bound_usd": 50000,
            "upper_bound_usd": 250000,
            "currency": "USD"
          },
          "reach_estimate": {
            "lower_bound": 5000000,
            "upper_bound": 25000000
          },
          "platform_distribution": {
            "facebook": 60,
            "instagram": 45,
            "messenger": 15,
            "audience_network": 25
          },
          "media_breakdown": {
            "image": 45,
            "video": 55,
            "carousel": 30,
            "collection": 15
          },
          "ads": [
            {
              "id": "ad_123456",
              "status": "active",
              "start_date": "2024-01-01",
              "end_date": null,
              "creative": {
                "type": "video",
                "headline": "Just Do It",
                "body_text": "Explore the new Nike Air Max collection...",
                "call_to_action": "Shop Now",
                "landing_url": "https://nike.com/air-max",
                "media_urls": ["https://..."]
              },
              "targeting": {
                "age_range": "18-54",
                "gender": "all",
                "locations": ["United States"],
                "interests": ["Running", "Fitness", "Sports"]
              },
              "impressions_estimate": {
                "lower_bound": 100000,
                "upper_bound": 500000
              },
              "spend_estimate": {
                "lower_bound_usd": 5000,
                "upper_bound_usd": 25000
              }
            }
          ]
        },
        "google": {
          "total_ads": 78,
          "formats": {
            "text": 45,
            "image": 20,
            "video": 13
          },
          "regions_targeted": ["United States", "Canada"],
          "ads": [...]
        }
      }
    }
  ],

  "summary": {
    "total_ads_analyzed": 523,
    "total_competitors": 3,
    "total_spend_estimate": {
      "lower_bound_usd": 150000,
      "upper_bound_usd": 750000
    },
    "platform_distribution": {
      "facebook": 245,
      "instagram": 120,
      "google_search": 80,
      "google_display": 45,
      "youtube": 33
    },
    "creative_breakdown": {
      "video": 180,
      "image": 220,
      "carousel": 75,
      "text": 48
    },
    "status_breakdown": {
      "active": 380,
      "inactive": 143
    },
    "top_messaging_themes": [
      {
        "theme": "Performance/Speed",
        "frequency": 45,
        "keywords": ["fast", "performance", "speed", "run"]
      },
      {
        "theme": "Innovation/Technology",
        "frequency": 38,
        "keywords": ["new", "technology", "innovation", "advanced"]
      },
      {
        "theme": "Lifestyle/Culture",
        "frequency": 32,
        "keywords": ["style", "culture", "life", "everyday"]
      }
    ],
    "top_call_to_actions": [
      {"cta": "Shop Now", "count": 180},
      {"cta": "Learn More", "count": 95},
      {"cta": "Sign Up", "count": 45}
    ],
    "avg_ad_duration_days": 21,
    "ads_per_competitor_avg": 174.3
  },

  "comparison": {
    "spend_ranking": [
      {"competitor": "Nike", "spend_estimate_mid": 150000, "rank": 1},
      {"competitor": "Adidas", "spend_estimate_mid": 120000, "rank": 2},
      {"competitor": "Puma", "spend_estimate_mid": 45000, "rank": 3}
    ],
    "activity_ranking": [
      {"competitor": "Nike", "total_ads": 223, "active_rate": 0.68, "rank": 1},
      {"competitor": "Adidas", "total_ads": 185, "active_rate": 0.72, "rank": 2},
      {"competitor": "Puma", "total_ads": 115, "active_rate": 0.61, "rank": 3}
    ],
    "platform_focus": {
      "Nike": {"primary": "facebook", "secondary": "instagram", "facebook_pct": 0.45},
      "Adidas": {"primary": "instagram", "secondary": "facebook", "instagram_pct": 0.52},
      "Puma": {"primary": "facebook", "secondary": "google", "facebook_pct": 0.55}
    },
    "creative_strategy": {
      "Nike": {"primary_format": "video", "video_pct": 0.55},
      "Adidas": {"primary_format": "carousel", "carousel_pct": 0.48},
      "Puma": {"primary_format": "image", "image_pct": 0.62}
    },
    "messaging_overlap": {
      "shared_themes": ["performance", "style", "innovation"],
      "unique_to_nike": ["athlete endorsement", "competition"],
      "unique_to_adidas": ["sustainability", "collaboration"],
      "unique_to_puma": ["affordability", "streetwear"]
    }
  },

  "trends": {
    "ad_volume_by_week": [
      {"week": "2023-W51", "ads_launched": 45},
      {"week": "2024-W01", "ads_launched": 78},
      {"week": "2024-W02", "ads_launched": 62}
    ],
    "spend_trend": "increasing",
    "format_trend": "video_growing",
    "platform_shift": "instagram_focus_increasing"
  }
}
```

## Workflow Steps

### Step 1: Configure Analysis Parameters

```bash
# Define your competitive set
COMPETITORS=("Nike" "Adidas" "Puma" "Under Armour" "New Balance")

# Set analysis parameters
COUNTRY="US"
PLATFORMS="facebook google"
DAYS=30
MAX_ADS=200
```

### Step 2: Run Competitor Ads Scraper

```bash
# Execute the scraper
python scripts/scrape_competitor_ads.py \
  "${COMPETITORS[@]}" \
  --platforms $PLATFORMS \
  --country $COUNTRY \
  --days $DAYS \
  --max-ads $MAX_ADS \
  --compare \
  --output competitor_ads_analysis.json
```

### Step 3: Review Summary Statistics

The script outputs key metrics to console:

```
=== Competitor Ads Analysis Complete ===

Total Ads Analyzed: 523
Competitors: 5
Platforms: Facebook, Google

Spend Ranking:
  1. Nike - $100K-$250K
  2. Adidas - $75K-$200K
  3. Under Armour - $50K-$150K
  4. New Balance - $40K-$120K
  5. Puma - $30K-$100K

Top Creative Formats:
  - Video: 38%
  - Image: 35%
  - Carousel: 18%
  - Text: 9%

Results saved to: .tmp/competitor_ads_analysis.json
```

### Step 4: Deep Dive Analysis (Optional)

```bash
# Focus on specific competitor with more details
python scripts/scrape_competitor_ads.py "Nike" \
  --platforms facebook \
  --max-ads 500 \
  --include-creatives \
  --output nike_deep_dive.json

# Keyword-based discovery to find new competitors
python scripts/scrape_competitor_ads.py \
  --search "athletic footwear" \
  --country US \
  --max-ads 300 \
  --output athletic_footwear_landscape.json
```

### Step 5: Export and Share

```bash
# Upload results to Google Drive
python ~/.claude/skills/google-workspace/scripts/upload_to_drive.py \
  .tmp/competitor_ads_analysis.json \
  --folder "Competitive Intelligence"

# Generate report with parallel-research
python ~/.claude/skills/parallel-research/scripts/parallel_research.py \
  chat "Analyze this competitor advertising data and provide strategic recommendations: $(cat .tmp/competitor_ads_analysis.json | head -1000)"
```

## Analytics Features (Enriched)

### 1. Spend Estimation

The script aggregates spend estimates from Meta Ads Library (which provides lower/upper bounds) and normalizes across competitors:

- **Lower Bound**: Conservative minimum spend estimate
- **Upper Bound**: Maximum possible spend estimate
- **Midpoint**: Calculated average for ranking
- **Relative Spend**: Percentage of total competitive spend

### 2. Creative Strategy Analysis

Automatic categorization of creative approaches:

- **Format Distribution**: Video vs. image vs. carousel vs. text
- **Primary Format**: Most-used creative type per competitor
- **Format Trend**: Whether video/carousel usage is increasing
- **A/B Testing Signals**: Multiple creatives with similar messaging

### 3. Messaging Theme Extraction

Natural language analysis of ad copy to identify:

- **Top Themes**: Most common messaging categories
- **Theme Keywords**: Words associated with each theme
- **Unique Positioning**: Themes used by only one competitor
- **Shared Territory**: Common messaging across all competitors

### 4. Platform Strategy

Cross-platform analysis including:

- **Primary Platform**: Where competitor focuses most spend
- **Platform Mix**: Distribution across FB/IG/Google/YouTube
- **Platform Shift**: Changes in platform focus over time
- **Cross-Platform Consistency**: Same ads across platforms

### 5. Competitive Benchmarking

Comparison metrics when `--compare` flag is used:

- **Spend Ranking**: Competitors ranked by estimated spend
- **Activity Ranking**: By total number of ads
- **Active Rate**: Percentage of ads currently running
- **Creative Innovation Score**: Variety of formats/messaging

## Cost Estimates

| Scenario | Ads Scraped | Estimated Cost |
|----------|-------------|----------------|
| Single competitor, 100 ads | 100 | ~$0.10 |
| 3 competitors, 200 ads each | 600 | ~$0.60 |
| 5 competitors, full analysis | 1,000 | ~$1.00 |
| Keyword discovery, 500 ads | 500 | ~$0.50 |
| Deep dive, 1,000 ads | 1,000 | ~$1.00 |

**Cost Optimization Tips:**
- Use `--max-ads` to limit per-competitor extraction
- Focus on `--status active` to skip inactive ads
- Use single platform when cross-platform isn't needed
- Cache results and only refresh weekly

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `Competitor not found` | Invalid name/domain | Verify competitor exists on platform |
| `No ads in date range` | Competitor not advertising | Extend `--days` parameter |
| `Rate limited` | Too many requests | Wait 5 minutes, reduce scope |
| `Invalid country code` | Wrong ISO code | Use 2-letter ISO code (US, GB, DE) |
| `Platform unavailable` | API issues | Retry or use alternate platform |
| `Spend estimate unavailable` | Meta limitation | Some ads don't have spend data |

## Integration Patterns

### Pattern 1: Weekly Competitive Report

```bash
#!/bin/bash
# weekly_competitor_report.sh

# Scrape competitor ads
python scripts/scrape_competitor_ads.py \
  "Competitor1" "Competitor2" "Competitor3" \
  --compare \
  --platforms facebook google \
  --days 7 \
  --output weekly_ads.json

# Generate report with AI
python ~/.claude/skills/parallel-research/scripts/parallel_research.py \
  chat "Create a weekly competitive advertising report from: $(cat .tmp/weekly_ads.json)"

# Upload to Drive
python ~/.claude/skills/google-workspace/scripts/upload_to_drive.py \
  .tmp/weekly_ads.json \
  --folder "Weekly Reports"
```

### Pattern 2: New Competitor Discovery

```bash
# Find who's advertising in your space
python scripts/scrape_competitor_ads.py \
  --search "your product category" \
  --country US \
  --max-ads 500 \
  --output landscape.json

# Extract unique advertisers
cat .tmp/landscape.json | jq '.summary.unique_advertisers'
```

### Pattern 3: Campaign Launch Monitoring

```bash
# Before your campaign launch, benchmark competitors
python scripts/scrape_competitor_ads.py \
  "MainCompetitor" \
  --platforms facebook \
  --days 1 \
  --status active \
  --output pre_launch_baseline.json

# After launch, compare activity changes
python scripts/scrape_competitor_ads.py \
  "MainCompetitor" \
  --platforms facebook \
  --days 1 \
  --status active \
  --output post_launch_snapshot.json
```

## Related Workflows

| Workflow | Use Case | Link |
|----------|----------|------|
| Competitor Intel | Full competitive analysis | `workflows/competitor-intel.md` |
| Lead Generation | Find leads from advertiser lists | `workflows/lead-generation.md` |
| Content Generation | Create competitive reports | `~/.claude/skills/content-generation/SKILL.md` |
| Google Workspace | Save results to Drive/Sheets | `~/.claude/skills/google-workspace/SKILL.md` |

## Security Notes

- Ad data is public (from official transparency libraries)
- No authentication required for Meta Ads Library
- No authentication required for Google Ads Transparency
- Respect rate limits to avoid IP blocks
- Store results locally (not transmitted to third parties)

## Changelog

- **v1.0.0** - Initial release with Facebook and Google support
- Includes summary analytics, comparison mode, and theme extraction
- Enriched beyond basic Apify skill with comprehensive benchmarking
