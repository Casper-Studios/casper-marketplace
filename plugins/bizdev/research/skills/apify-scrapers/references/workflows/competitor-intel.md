# Competitor Intelligence Workflow

## Overview
Gather comprehensive intelligence on competitors across social media, reviews, and web presence.

## Workflow Steps

```
Step 1: Map Competitors
├── Google Maps search for industry
├── Identify top players
└── Get website URLs

Step 2: Social Media Analysis
├── Facebook page metrics and posts
├── Instagram presence and engagement
├── LinkedIn company posts
├── Twitter/X activity

Step 3: Review Analysis
├── Google Maps reviews (sentiment, themes)
├── Facebook reviews
└── Identify strengths/weaknesses

Step 4: Content Analysis
├── Scrape competitor websites
├── Extract key messaging
└── Compare offerings

Step 5: Synthesize Report
├── Use parallel-research for analysis
├── Generate competitive report
└── Save to Google Drive
```

## Example Commands

```bash
# Step 1: Find competitors in your space
python scripts/scrape_google_maps.py search "digital marketing agency" --location "Austin, TX" --max-results 20 --output competitors.json

# Step 2a: Facebook presence
python scripts/scrape_facebook.py page "https://facebook.com/competitor1" --output fb_competitor1.json
python scripts/scrape_facebook.py posts "https://facebook.com/competitor1" --max-posts 50 --output fb_posts.json

# Step 2b: Instagram presence
python scripts/scrape_instagram.py profile competitor1 competitor2 --output ig_profiles.json
python scripts/scrape_instagram.py posts competitor1 --max-posts 50 --output ig_posts.json

# Step 3: Reviews analysis
python scripts/scrape_google_maps.py reviews "https://maps.google.com/place/competitor1" --max-reviews 100 --output gmaps_reviews.json
python scripts/scrape_facebook.py reviews "https://facebook.com/competitor1" --max-reviews 50 --output fb_reviews.json

# Step 4: Website content
python scripts/scrape_multi_platform.py website --urls "https://competitor1.com" --max-pages 20 --output website_content.json
```

## Metrics to Compare

| Category | Metrics |
|----------|---------|
| Social Media | Followers, engagement rate, post frequency |
| Reviews | Average rating, review count, sentiment |
| Content | Topics covered, messaging, offers |
| SEO | Keywords targeted, content depth |

## Cost Estimate
- 5 competitors full analysis: ~$10-15
- 20 competitors basic scan: ~$5-10

## Output: Competitive Matrix

| Competitor | Followers | Engagement | Rating | Reviews | Strengths | Weaknesses |
|------------|-----------|------------|--------|---------|-----------|------------|
| Company A | 50K | 3.2% | 4.5 | 200 | Great content | Slow response |
| Company B | 30K | 5.1% | 4.2 | 150 | Fast delivery | Limited range |

## Related Skills
- `parallel-research` - Deep company research
- `content-generation` - Generate competitive report
- `google-workspace` - Save analysis to Drive
