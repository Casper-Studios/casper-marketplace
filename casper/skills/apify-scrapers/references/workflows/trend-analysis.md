# Trend Analysis Workflow

## Overview

Discover, analyze, and track emerging trends across multiple platforms with enriched insights including velocity scores, lifecycle stages, geographic spread, sentiment analysis, and opportunity scoring.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TREND ANALYSIS ENGINE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐     │
│  │   GOOGLE    │   │  INSTAGRAM  │   │   TIKTOK    │   │   TWITTER   │     │
│  │   TRENDS    │   │  HASHTAGS   │   │  HASHTAGS   │   │  TRENDING   │     │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘     │
│         │                 │                 │                 │            │
│         └────────────┬────┴────────┬────────┴────────┬────────┘            │
│                      │             │                 │                      │
│                      ▼             ▼                 ▼                      │
│              ┌───────────────────────────────────────────┐                  │
│              │           DATA AGGREGATION                │                  │
│              └─────────────────┬─────────────────────────┘                  │
│                                │                                            │
│         ┌──────────────────────┼──────────────────────┐                    │
│         ▼                      ▼                      ▼                    │
│  ┌─────────────┐       ┌─────────────┐       ┌─────────────┐              │
│  │  VELOCITY   │       │  LIFECYCLE  │       │ OPPORTUNITY │              │
│  │   SCORING   │       │   STAGING   │       │   SCORING   │              │
│  └─────────────┘       └─────────────┘       └─────────────┘              │
│         │                      │                      │                    │
│         └──────────────────────┼──────────────────────┘                    │
│                                ▼                                            │
│              ┌───────────────────────────────────────────┐                  │
│              │         ENRICHED TREND REPORT             │                  │
│              └───────────────────────────────────────────┘                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Sources

### Primary Sources (Apify Actors)

| Platform | Actor ID | Data Type | Cost/Item |
|----------|----------|-----------|-----------|
| Google Trends | `apify/google-trends-scraper` | Search interest, related queries | ~$0.01 |
| Instagram | `apify/instagram-hashtag-scraper` | Hashtag posts, engagement | ~$0.002-0.005 |
| TikTok | `clockworks/tiktok-scraper` | Hashtag videos, sounds, views | ~$0.005 |
| Twitter | `kaitoeasyapi/twitter-x-data-tweet-scraper` | Trending topics, tweets | ~$0.00025 |
| Reddit | `trudax/reddit-scraper-lite` | Emerging discussions, upvotes | ~$0.001-0.005 |
| YouTube | `streamers/youtube-scraper` | Trending videos, search trends | ~$0.01-0.05 |

### Trend Types

| Type | Description | Sources |
|------|-------------|---------|
| **Search Trends** | What people are looking for | Google Trends |
| **Social Trends** | Hashtags, topics gaining traction | Instagram, TikTok, Twitter |
| **Content Trends** | Popular formats, styles | TikTok, YouTube, Instagram Reels |
| **Product Trends** | Emerging products, brands | Google Trends, Reddit |
| **Cultural Trends** | Memes, movements, phenomena | All platforms |

## Enrichment Metrics

### 1. Velocity Score (0-100)

Measures how fast a trend is growing.

```
Velocity Score = weighted_average(
    search_growth_rate * 0.3,      # Google Trends week-over-week
    social_growth_rate * 0.25,     # Hashtag usage growth
    content_growth_rate * 0.25,    # New content creation rate
    engagement_growth_rate * 0.2   # Likes/comments acceleration
)
```

| Score Range | Interpretation |
|-------------|----------------|
| 90-100 | Explosive growth (viral) |
| 70-89 | Rapid growth |
| 50-69 | Steady growth |
| 30-49 | Slow growth |
| 0-29 | Stagnant or declining |

### 2. Lifecycle Stage

Based on adoption curve analysis:

| Stage | Characteristics | Strategy |
|-------|-----------------|----------|
| **Emerging** (1-10%) | Early adopters only, low volume, high growth | First-mover advantage |
| **Growing** (10-50%) | Mainstream adoption, high velocity | Scale content quickly |
| **Peak** (50-90%) | Market saturation, velocity slowing | Differentiate or pivot |
| **Declining** (<50% from peak) | Fading interest, negative velocity | Exit or archive |

### 3. Geographic Spread

```json
{
  "origin_region": "United States",
  "spread_pattern": "radial",
  "current_regions": ["US", "UK", "Canada", "Australia"],
  "emerging_regions": ["Germany", "France", "Brazil"],
  "regional_intensity": {
    "US": 100,
    "UK": 85,
    "Canada": 72
  }
}
```

### 4. Related Trends Clustering

```json
{
  "parent_trends": ["artificial intelligence", "automation"],
  "child_trends": ["AI art generators", "ChatGPT alternatives"],
  "sibling_trends": ["machine learning", "neural networks"],
  "competing_trends": ["traditional software", "manual processes"]
}
```

### 5. Opportunity Score (0-100)

Composite score for actionability:

```
Opportunity Score = weighted_average(
    content_opportunity * 0.35,    # Ease of content creation
    commercial_opportunity * 0.35, # Monetization potential
    timing_opportunity * 0.30     # Window of opportunity
)
```

| Score Range | Recommendation |
|-------------|----------------|
| 80-100 | High priority - act now |
| 60-79 | Good opportunity - plan action |
| 40-59 | Moderate - worth monitoring |
| 20-39 | Low priority - limited potential |
| 0-19 | Not recommended |

### 6. Sentiment Analysis

```json
{
  "overall_sentiment": "positive",
  "sentiment_score": 0.72,
  "distribution": {
    "positive": 65,
    "neutral": 25,
    "negative": 10
  },
  "controversy_score": 15,
  "emotion_breakdown": {
    "excitement": 45,
    "curiosity": 30,
    "skepticism": 15,
    "fear": 10
  }
}
```

### 7. Historical Comparison

```json
{
  "similar_past_trends": [
    {
      "trend": "blockchain",
      "similarity_score": 78,
      "peak_year": 2021,
      "trajectory": "hype_cycle",
      "current_status": "plateau_of_productivity"
    }
  ],
  "predicted_trajectory": "sustained_growth",
  "confidence": 75
}
```

## CLI Usage

### Basic Commands

```bash
# Analyze specific topic
python analyze_trends.py "artificial intelligence" --sources google instagram tiktok --days 90

# Discover trending topics in category
python analyze_trends.py --category technology --discover --top 50

# Compare multiple trends
python analyze_trends.py "AI" "blockchain" "metaverse" --compare --chart

# Regional analysis
python analyze_trends.py "fashion trends" --regions US UK FR DE --compare

# Real-time monitoring mode
python analyze_trends.py --category fitness --monitor --alert-threshold 50

# Export trend report
python analyze_trends.py "sustainable fashion" --format html --output trend_report.html
```

### Command Reference

| Flag | Description | Default |
|------|-------------|---------|
| `--sources` | Platforms to analyze | `google instagram tiktok` |
| `--days` | Analysis period | `30` |
| `--category` | Topic category filter | None |
| `--discover` | Find trending topics | False |
| `--top` | Number of trends to discover | `20` |
| `--compare` | Compare multiple trends | False |
| `--chart` | Generate visualization | False |
| `--regions` | Geographic regions to analyze | `US` |
| `--monitor` | Continuous monitoring mode | False |
| `--alert-threshold` | Velocity score for alerts | `70` |
| `--format` | Output format (json/html/csv) | `json` |
| `--output` | Custom output filename | Auto-generated |
| `--enrich` | Enrichment level (basic/full) | `full` |

## Workflow Steps

### Step 1: Data Collection

```bash
# Collect trend data from all sources
python analyze_trends.py "AI agents" --sources google instagram tiktok reddit youtube --days 90
```

Internal process:
1. Query Google Trends for search interest
2. Scrape Instagram hashtag metrics
3. Collect TikTok hashtag data
4. Gather Twitter mentions
5. Analyze Reddit discussions
6. Check YouTube search trends

### Step 2: Data Aggregation

Raw data from each platform is normalized:
- Standardize date formats
- Normalize engagement metrics
- Map regional data to ISO codes
- Extract common entities

### Step 3: Enrichment Analysis

Calculate all enrichment metrics:
- Velocity scoring
- Lifecycle staging
- Geographic mapping
- Trend clustering
- Opportunity scoring
- Sentiment analysis
- Historical comparison

### Step 4: Report Generation

```bash
# Generate comprehensive report
python analyze_trends.py "sustainable living" --format html --enrich full
```

## Output Format

### JSON Output Structure

```json
{
  "query": "artificial intelligence",
  "analysis_period": {
    "start": "2024-11-01",
    "end": "2025-01-31"
  },
  "generated_at": "2025-01-31T10:30:00Z",
  "overall_trend": {
    "direction": "growing",
    "velocity_score": 85,
    "lifecycle_stage": "growing",
    "opportunity_score": 78,
    "sentiment": "positive",
    "controversy_score": 12
  },
  "by_platform": {
    "google": {
      "search_interest": 85,
      "trend_direction": "+25% vs last quarter",
      "related_queries": [
        {"query": "AI tools", "growth": "breakout"},
        {"query": "ChatGPT", "growth": "+150%"}
      ],
      "rising_topics": ["AI agents", "LLMs", "AI automation"]
    },
    "instagram": {
      "hashtag_posts": 5000000,
      "weekly_growth": "12%",
      "top_content_formats": ["reels", "carousel"],
      "avg_engagement_rate": 3.2,
      "top_creators": ["@ai_explained", "@tech_daily"]
    },
    "tiktok": {
      "hashtag_views": 50000000000,
      "trending_sounds": [
        {"name": "AI Voice", "uses": 1500000},
        {"name": "Robot Future", "uses": 800000}
      ],
      "creator_adoption": "high",
      "viral_videos": 450
    },
    "reddit": {
      "active_discussions": 15000,
      "avg_upvotes": 850,
      "top_subreddits": ["r/MachineLearning", "r/artificial", "r/ChatGPT"],
      "sentiment_score": 0.68
    },
    "youtube": {
      "trending_videos": 120,
      "avg_views": 500000,
      "top_channels": ["Two Minute Papers", "AI Explained"],
      "content_types": ["tutorials", "news", "reviews"]
    }
  },
  "geographic_analysis": {
    "hottest_regions": ["US", "UK", "India"],
    "emerging_regions": ["Brazil", "Indonesia", "Vietnam"],
    "regional_variations": {
      "US": {"focus": "enterprise AI", "sentiment": "optimistic"},
      "EU": {"focus": "AI regulation", "sentiment": "cautious"},
      "Asia": {"focus": "AI development", "sentiment": "enthusiastic"}
    }
  },
  "related_trends": {
    "parent": ["technology", "automation", "digital transformation"],
    "child": ["AI art", "AI writing", "AI coding assistants"],
    "sibling": ["machine learning", "data science", "robotics"],
    "competing": ["traditional software", "human expertise"]
  },
  "predictions": {
    "peak_timing": "Q2 2025",
    "longevity": "sustained",
    "confidence": 75,
    "risk_factors": ["regulatory changes", "market saturation"]
  },
  "recommendations": [
    {
      "action": "Create educational content now",
      "priority": "high",
      "rationale": "High search volume, growing interest, content gap exists"
    },
    {
      "action": "Focus on practical applications",
      "priority": "high",
      "rationale": "Users seeking actionable content, not theory"
    },
    {
      "action": "Target emerging markets",
      "priority": "medium",
      "rationale": "Brazil and Indonesia showing rapid adoption"
    }
  ]
}
```

## Cost Estimates

### Per Analysis Run

| Sources Used | Estimated Cost |
|--------------|----------------|
| Single platform | $0.05-0.15 |
| 3 platforms | $0.15-0.50 |
| All 6 platforms | $0.50-1.50 |
| Full enrichment | +$0.10-0.30 |

### Monitoring Mode (per hour)

| Check Frequency | Cost/Hour |
|-----------------|-----------|
| Every 15 min | $0.50-1.00 |
| Every 30 min | $0.25-0.50 |
| Every hour | $0.15-0.30 |

## Integration Patterns

### Trend Analysis + Content Generation

```bash
# 1. Analyze trends
python analyze_trends.py "AI productivity" --format json --output trend_data.json

# 2. Generate content based on trends
# Use content-generation skill with trend_data.json as input
```

### Trend Analysis + Competitor Intel

```bash
# 1. Find trending topics in your industry
python analyze_trends.py --category "SaaS marketing" --discover --top 20

# 2. Analyze competitor coverage of those trends
# Use competitor-intel workflow
```

### Automated Trend Reports

```bash
# Weekly trend digest
python analyze_trends.py --category technology --discover --top 30 \
  --format html --output weekly_trends.html

# Upload to Google Drive
# Use google-workspace skill
```

## Best Practices

### 1. Start Broad, Then Focus

```bash
# First: Discover what's trending
python analyze_trends.py --category "your-industry" --discover --top 50

# Then: Deep dive on promising trends
python analyze_trends.py "specific trend" --sources all --enrich full
```

### 2. Monitor Velocity, Not Volume

- High volume + low velocity = mature trend (saturated)
- Low volume + high velocity = emerging trend (opportunity)

### 3. Geographic Timing

- Trends often spread: US -> UK -> Europe -> Asia
- Get ahead by monitoring origin regions

### 4. Sentiment Matters

- High velocity + negative sentiment = controversy (risky)
- High velocity + positive sentiment = opportunity (safe)

### 5. Historical Context

- Similar past trends help predict trajectory
- Learn from what worked and failed before

## Troubleshooting

### No Results for Query

**Cause:** Query too specific or not trending
**Solution:** Try broader terms or check spelling

### Missing Platform Data

**Cause:** Platform blocking or rate limiting
**Solution:** Reduce request frequency, check proxy settings

### Inaccurate Velocity Scores

**Cause:** Insufficient historical data
**Solution:** Extend analysis period (--days 90)

### High Cost Runs

**Cause:** Too many sources or high result limits
**Solution:** Focus on 2-3 most relevant platforms

## Related Skills

- **apify-scrapers** - Raw data collection from platforms
- **parallel-research** - Deep research on specific trends
- **content-generation** - Create trend-based content
- **google-workspace** - Export reports to Drive/Sheets
