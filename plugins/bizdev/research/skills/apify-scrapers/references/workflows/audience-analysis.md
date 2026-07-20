# Audience Analysis Workflow

## Overview

Comprehensive cross-platform audience analysis tool that scrapes follower demographics, engagement patterns, and content performance across Instagram, Facebook, YouTube, and TikTok. Goes beyond basic metrics to provide actionable insights including quality scores, optimal posting times, and growth trajectories.

## Architecture

```
Input: @username or brand handle
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PLATFORM SCRAPERS                            │
├─────────────────────────────────────────────────────────────────┤
│  Instagram     │  Facebook      │  YouTube       │  TikTok      │
│  - Profile     │  - Page        │  - Channel     │  - Profile   │
│  - Posts       │  - Posts       │  - Videos      │  - Videos    │
│  - Reels       │  - Reviews     │  - Comments    │  - Comments  │
│  - Comments    │  - Engagement  │  - Subscribers │  - Followers │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ANALYSIS ENGINE                              │
├─────────────────────────────────────────────────────────────────┤
│  Engagement Rate Calculation      │  Audience Quality Score    │
│  Best Posting Times Analysis      │  Content Performance Matrix│
│  Industry Benchmarking            │  Growth Trajectory         │
│  Cross-Platform Overlap           │  Sentiment Analysis        │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
Output: Comprehensive Audience Report (JSON/HTML/CSV)
```

## Apify Actors Used

| Platform | Actor ID | Purpose |
|----------|----------|---------|
| Instagram | `apify/instagram-profile-scraper` | Profile demographics |
| Instagram | `apify/instagram-scraper` | Posts and engagement |
| Instagram | `apify/instagram-comment-scraper` | Comment sentiment |
| Instagram | `apify/instagram-reel-scraper` | Reels performance |
| Facebook | `apify/facebook-pages-scraper` | Page metrics |
| Facebook | `apify/facebook-posts-scraper` | Post engagement |
| Facebook | `apify/facebook-reviews-scraper` | Audience sentiment |
| YouTube | `streamers/youtube-channel-scraper` | Channel stats |
| YouTube | `streamers/youtube-comments-scraper` | Comment analysis |
| TikTok | `clockworks/tiktok-scraper` | Profile and videos |

## Key Metrics Calculated

### 1. Engagement Rate
Platform-specific engagement rate formulas:

- **Instagram**: `(likes + comments) / followers * 100`
- **Facebook**: `(reactions + comments + shares) / followers * 100`
- **YouTube**: `(likes + comments) / views * 100`
- **TikTok**: `(likes + comments + shares) / views * 100`

### 2. Audience Quality Score (A-F)
Based on engagement-to-follower ratio compared to industry benchmarks:

| Score | Engagement Rate | Interpretation |
|-------|-----------------|----------------|
| A+ | > 6% | Exceptional, highly engaged niche |
| A | 3-6% | Excellent, loyal community |
| B | 1-3% | Good, healthy engagement |
| C | 0.5-1% | Average, typical for large accounts |
| D | 0.1-0.5% | Below average, possible bot followers |
| F | < 0.1% | Poor, likely fake or dead audience |

### 3. Industry Benchmarks
Pre-loaded benchmarks for common industries:

| Industry | Avg Engagement | Avg Growth/Month |
|----------|----------------|------------------|
| Fashion | 1.5% | 2.3% |
| Tech | 0.8% | 1.5% |
| Food | 2.1% | 2.8% |
| Fitness | 1.9% | 2.1% |
| Beauty | 1.7% | 2.5% |
| Travel | 2.3% | 1.9% |
| B2B | 0.5% | 0.8% |
| Sports | 1.2% | 1.4% |
| Gaming | 1.8% | 3.2% |
| Education | 0.9% | 1.1% |

### 4. Best Posting Times
Analyzes post timestamps and engagement to determine optimal posting windows:

```json
{
  "weekday_best": "Wednesday",
  "weekend_best": "Saturday",
  "best_hours": ["9:00 AM", "12:00 PM", "7:00 PM"],
  "timezone": "UTC",
  "confidence": 0.85
}
```

### 5. Content Performance Matrix
Categorizes content types by performance:

| Content Type | Avg Engagement | Reach | Recommendation |
|--------------|----------------|-------|----------------|
| Reels/Shorts | High | Very High | Prioritize |
| Carousels | High | Medium | Use for education |
| Single Image | Medium | Medium | Use for announcements |
| Text Posts | Low | Low | Minimize |
| Stories | Medium | High | Use for engagement |

### 6. Growth Trajectory
Analyzes follower growth patterns:

- **Accelerating**: Growth rate increasing month-over-month
- **Stable**: Consistent growth rate
- **Decelerating**: Growth rate slowing
- **Declining**: Losing followers
- **Viral**: Sudden spike in growth

## CLI Usage

### Single Account Analysis

```bash
# Basic analysis on all platforms
python scripts/analyze_audience.py @nike

# Specify platforms
python scripts/analyze_audience.py @nike --platforms instagram facebook youtube

# With industry benchmark
python scripts/analyze_audience.py @nike --benchmark sportswear

# Custom output format
python scripts/analyze_audience.py @nike --format html --output nike_report.html
```

### Multi-Account Comparison

```bash
# Compare competitors
python scripts/analyze_audience.py @nike @adidas @puma --compare

# Compare with CSV output
python scripts/analyze_audience.py @nike @adidas --compare --format csv --output comparison.csv
```

### Advanced Options

```bash
# Full analysis with all enrichments
python scripts/analyze_audience.py @brand \
  --platforms instagram facebook youtube tiktok \
  --benchmark fashion \
  --max-posts 100 \
  --include-comments \
  --format html \
  --output full_report.html

# Quick summary (profile only, no posts)
python scripts/analyze_audience.py @brand --quick

# JSON for programmatic use
python scripts/analyze_audience.py @brand --format json --output data.json
```

## Output Formats

### JSON (Default)

```json
{
  "analysis_timestamp": "2025-01-31T10:30:00Z",
  "account": "@nike",
  "platforms": {
    "instagram": {
      "username": "nike",
      "followers": 250000000,
      "following": 150,
      "posts_count": 2500,
      "engagement_rate": 1.2,
      "quality_score": "B",
      "follower_following_ratio": 1666666.7,
      "avg_likes_per_post": 2500000,
      "avg_comments_per_post": 15000,
      "best_posting_times": {
        "weekday": "Wednesday",
        "hours": ["9:00 AM", "6:00 PM"]
      },
      "top_content_types": [
        {"type": "Reels", "engagement": 1.8},
        {"type": "Carousel", "engagement": 1.3},
        {"type": "Single Image", "engagement": 0.9}
      ],
      "recent_growth": {
        "monthly_rate": 0.5,
        "trajectory": "stable"
      },
      "top_hashtags": ["#nike", "#justdoit", "#sports"],
      "sentiment_score": 0.72
    },
    "facebook": { ... },
    "youtube": { ... },
    "tiktok": { ... }
  },
  "cross_platform_summary": {
    "total_reach": 520000000,
    "avg_engagement_rate": 1.35,
    "strongest_platform": "instagram",
    "weakest_platform": "facebook",
    "overall_quality_score": "B+",
    "growth_trend": "stable",
    "estimated_audience_overlap": 0.25
  },
  "benchmark_comparison": {
    "industry": "sportswear",
    "engagement_vs_benchmark": "+15%",
    "growth_vs_benchmark": "-5%",
    "position": "above average"
  },
  "recommendations": [
    "Increase TikTok posting frequency to match Instagram engagement",
    "YouTube engagement below benchmark - consider more community posts",
    "Reels performing 50% better than static posts - prioritize video content",
    "Best posting time is Wednesday 9AM - consider scheduling around this"
  ]
}
```

### HTML Report

Generates a styled HTML report with:
- Executive summary dashboard
- Platform-by-platform breakdown with charts
- Engagement timeline visualization
- Content performance heatmap
- Competitive comparison (if multiple accounts)
- Actionable recommendations

### CSV Export

For spreadsheet analysis:
```csv
account,platform,followers,engagement_rate,quality_score,growth_rate
nike,instagram,250000000,1.2,B,0.5
nike,facebook,35000000,0.8,C,0.2
nike,youtube,1500000,2.1,B+,0.8
```

## Cost Estimates

| Analysis Type | Est. Time | Est. Cost |
|---------------|-----------|-----------|
| Quick (profile only) | 30s | $0.01 |
| Standard (50 posts) | 2-3 min | $0.10 |
| Deep (100 posts + comments) | 5-10 min | $0.50 |
| Multi-platform full | 10-15 min | $1.00 |
| Competitor comparison (5) | 15-20 min | $2.50 |

## Integration with Other Skills

### With parallel-research
```bash
# Deep research on brand + audience analysis
python scripts/analyze_audience.py @brand --output .tmp/audience.json
python parallel-research/scripts/research.py "Analyze {brand} marketing strategy" --context .tmp/audience.json
```

### With content-generation
```bash
# Generate social media strategy based on analysis
python scripts/analyze_audience.py @client --output .tmp/analysis.json
python content-generation/scripts/generate.py "social media strategy" --data .tmp/analysis.json
```

### With google-workspace
```bash
# Save report to Google Drive
python scripts/analyze_audience.py @brand --format html --output .tmp/report.html
python google-workspace/scripts/upload.py .tmp/report.html --folder "Client Reports"
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `APIFY_TOKEN not found` | Missing API key | Add to .env file |
| `Account not found` | Private or invalid handle | Verify account exists and is public |
| `Rate limited` | Too many requests | Wait 60s and retry |
| `Timeout` | Large account, slow scrape | Use --quick flag or increase timeout |
| `No posts found` | New account or scraping blocked | Try different platform |

## Environment Variables

```bash
# Required
APIFY_TOKEN=your_apify_token

# Optional
AUDIENCE_ANALYSIS_MAX_POSTS=50
AUDIENCE_ANALYSIS_TIMEOUT=300
```

## Related Workflows

- [competitor-intel.md](./competitor-intel.md) - Full competitor analysis
- [influencer-discovery.md](./influencer-discovery.md) - Find influencers by criteria
- [lead-generation.md](./lead-generation.md) - Extract leads from social

## Changelog

- **v1.0** - Initial release with 4-platform support
- **v1.1** - Added industry benchmarks and quality scores
- **v1.2** - Added HTML report generation
- **v1.3** - Added multi-account comparison mode
