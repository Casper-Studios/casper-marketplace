# Instagram Scraping

## Overview

Comprehensive Instagram scraping capabilities supporting multiple modes: profile data, posts, hashtag discovery, reels, and comments. Each mode uses a specialized Apify actor optimized for that content type.

## Actors Used

| Mode | Apify Actor | Description |
|------|-------------|-------------|
| `profile` | `apify/instagram-profile-scraper` | Profile metadata (bio, followers, posts count) |
| `posts` | `apify/instagram-scraper` | Posts from specific profiles |
| `hashtag` | `apify/instagram-hashtag-scraper` | Posts by hashtag |
| `reels` | `apify/instagram-reel-scraper` | Reels from profiles |
| `comments` | `apify/instagram-comment-scraper` | Comments on specific posts |

## Inputs

### Profile Mode

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `usernames` | list | required | Instagram usernames to scrape |
| `--output` | string | auto | Custom output filename |

### Posts Mode

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `usernames` | list | required | Profiles to scrape posts from |
| `--max-posts` | int | 50 | Maximum posts per profile |
| `--output` | string | auto | Custom output filename |

### Hashtag Mode

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hashtags` | list | required | Hashtags to search (without #) |
| `--max-posts` | int | 100 | Maximum posts per hashtag |
| `--output` | string | auto | Custom output filename |

### Reels Mode

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `usernames` | list | required | Profiles to scrape reels from |
| `--max-reels` | int | 20 | Maximum reels per profile |
| `--output` | string | auto | Custom output filename |

### Comments Mode

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `post_urls` | list | required | Instagram post/reel URLs |
| `--max-comments` | int | 100 | Maximum comments per post |
| `--output` | string | auto | Custom output filename |

## CLI Usage

### Profile Scraping

```bash
# Single profile
python scripts/scrape_instagram.py profile cristiano

# Multiple profiles
python scripts/scrape_instagram.py profile cristiano messi neymarjr

# With custom output
python scripts/scrape_instagram.py profile natgeo --output natgeo_profile.json

# Batch competitor analysis
python scripts/scrape_instagram.py profile competitor1 competitor2 competitor3 --output competitors.json
```

### Posts Scraping

```bash
# Default 50 posts from profile
python scripts/scrape_instagram.py posts username

# Multiple profiles with custom limit
python scripts/scrape_instagram.py posts username1 username2 --max-posts 100

# Quick scan with minimal posts
python scripts/scrape_instagram.py posts natgeo --max-posts 10 --output natgeo_posts.json

# Comprehensive profile posts
python scripts/scrape_instagram.py posts redbull --max-posts 200
```

### Hashtag Scraping

```bash
# Single hashtag
python scripts/scrape_instagram.py hashtag artificialintelligence

# Multiple hashtags
python scripts/scrape_instagram.py hashtag ai ml machinelearning --max-posts 100

# Trending topic research
python scripts/scrape_instagram.py hashtag tech startup entrepreneur --max-posts 50

# Niche discovery
python scripts/scrape_instagram.py hashtag smallbusiness shoplocal --max-posts 200 --output niche_posts.json
```

### Reels Scraping

```bash
# Default 20 reels from profile
python scripts/scrape_instagram.py reels username

# Multiple profiles
python scripts/scrape_instagram.py reels redbull gopro --max-reels 30

# Viral content research
python scripts/scrape_instagram.py reels tiktok_migrants --max-reels 50 --output viral_reels.json
```

### Comments Scraping

```bash
# Single post
python scripts/scrape_instagram.py comments "https://www.instagram.com/p/ABC123/"

# Multiple posts
python scripts/scrape_instagram.py comments "https://www.instagram.com/p/ABC123/" "https://www.instagram.com/p/DEF456/" --max-comments 100

# Reel comments
python scripts/scrape_instagram.py comments "https://www.instagram.com/reel/XYZ789/" --max-comments 200

# Sentiment analysis prep
python scripts/scrape_instagram.py comments "https://www.instagram.com/p/ABC123/" --max-comments 500 --output sentiment_data.json
```

## Output Structure

### Profile Output

```json
{
  "scraped_at": "2025-01-15T10:30:00.000Z",
  "platform": "instagram",
  "mode": "profile",
  "total_count": 1,
  "query": ["cristiano"],
  "run_id": "abc123",
  "data": [
    {
      "username": "cristiano",
      "full_name": "Cristiano Ronaldo",
      "biography": "Football player...",
      "external_url": "https://example.com",
      "followers_count": 500000000,
      "following_count": 500,
      "posts_count": 3500,
      "is_verified": true,
      "is_private": false,
      "is_business": true,
      "business_category": "Athlete",
      "profile_pic_url": "https://...",
      "profile_pic_url_hd": "https://...",
      "profile_url": "https://www.instagram.com/cristiano/",
      "id": "12345678"
    }
  ]
}
```

### Posts Output

```json
{
  "scraped_at": "2025-01-15T10:30:00.000Z",
  "platform": "instagram",
  "mode": "posts",
  "total_count": 50,
  "query": ["natgeo"],
  "run_id": "abc123",
  "data": [
    {
      "id": "post_id",
      "shortcode": "ABC123xyz",
      "caption": "Beautiful sunset captured in...",
      "owner_username": "natgeo",
      "timestamp": "2025-01-14T18:00:00.000Z",
      "likes_count": 150000,
      "comments_count": 2500,
      "video_view_count": 0,
      "video_play_count": 0,
      "is_video": false,
      "type": "Image",
      "display_url": "https://...",
      "video_url": "",
      "post_url": "https://www.instagram.com/p/ABC123xyz/",
      "location": "Yellowstone National Park",
      "hashtags": ["nature", "photography", "wildlife"],
      "mentions": ["photographer_name"],
      "engagement_score": 155000
    }
  ]
}
```

### Hashtag Output

```json
{
  "scraped_at": "2025-01-15T10:30:00.000Z",
  "platform": "instagram",
  "mode": "hashtag",
  "total_count": 100,
  "query": ["artificialintelligence"],
  "run_id": "abc123",
  "data": [
    {
      "id": "post_id",
      "shortcode": "XYZ789abc",
      "caption": "The future of AI is here...",
      "owner_username": "tech_influencer",
      "timestamp": "2025-01-14T12:00:00.000Z",
      "likes_count": 5000,
      "comments_count": 150,
      "video_view_count": 0,
      "is_video": false,
      "type": "Sidecar",
      "display_url": "https://...",
      "video_url": "",
      "post_url": "https://www.instagram.com/p/XYZ789abc/",
      "hashtags": ["ai", "artificialintelligence", "tech"],
      "source_hashtag": "artificialintelligence",
      "engagement_score": 5300
    }
  ]
}
```

### Reels Output

```json
{
  "scraped_at": "2025-01-15T10:30:00.000Z",
  "platform": "instagram",
  "mode": "reels",
  "total_count": 20,
  "query": ["redbull"],
  "run_id": "abc123",
  "data": [
    {
      "id": "reel_id",
      "shortcode": "REE123lzz",
      "caption": "Extreme sports at its finest...",
      "owner_username": "redbull",
      "timestamp": "2025-01-13T09:00:00.000Z",
      "likes_count": 250000,
      "comments_count": 5000,
      "play_count": 5000000,
      "view_count": 4500000,
      "duration": 30,
      "video_url": "https://...",
      "thumbnail_url": "https://...",
      "reel_url": "https://www.instagram.com/reel/REE123lzz/",
      "audio_title": "Original Audio",
      "audio_artist": "redbull",
      "hashtags": ["redbull", "extremesports"],
      "engagement_score": 305000
    }
  ]
}
```

### Comments Output

```json
{
  "scraped_at": "2025-01-15T10:30:00.000Z",
  "platform": "instagram",
  "mode": "comments",
  "total_count": 100,
  "query": ["https://www.instagram.com/p/ABC123/"],
  "run_id": "abc123",
  "data": [
    {
      "id": "comment_id",
      "text": "This is amazing! Love this content",
      "owner_username": "commenter_name",
      "owner_profile_pic": "https://...",
      "timestamp": "2025-01-14T19:30:00.000Z",
      "likes_count": 150,
      "replies_count": 5,
      "post_shortcode": "ABC123",
      "post_url": "https://www.instagram.com/p/ABC123/",
      "is_reply": false,
      "parent_comment_id": ""
    }
  ]
}
```

## Cost Estimates

| Mode | Cost per Item | Typical Run (100 items) |
|------|---------------|-------------------------|
| Profile | ~$0.01 per profile | $1.00 (100 profiles) |
| Posts | ~$0.002-0.005 per post | $0.20-0.50 |
| Hashtag | ~$0.002-0.005 per post | $0.20-0.50 |
| Reels | ~$0.003-0.008 per reel | $0.30-0.80 |
| Comments | ~$0.001-0.003 per comment | $0.10-0.30 |

**Notes:**
- Pay-per-result pricing varies by actor and data complexity
- Profile scraping is most expensive due to detailed metadata
- Costs may vary based on Apify pricing changes
- Set `maxCostPerRun` in actor options to prevent runaway costs

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid or expired Apify API token | Verify `APIFY_TOKEN` in .env, regenerate token in Apify console |
| `402 Payment Required` | Insufficient Apify credits | Add credits to Apify account |
| `Private profile` | User account is private | Cannot scrape private profiles; use alternative public accounts |
| `Profile not found` | Username does not exist or changed | Verify username is correct, check for typos |
| `Rate limited` | Too many requests to Instagram | Wait 5-10 minutes, reduce request frequency |
| `Actor timeout` | Too many items requested | Reduce `--max-posts/reels/comments`, use smaller batches |
| `Blocked by Instagram` | IP or account flagged | Actor handles proxy rotation automatically; wait and retry |
| `Invalid URL` | Malformed post/reel URL | Ensure URL matches `instagram.com/p/` or `instagram.com/reel/` format |
| `No results found` | Hashtag too niche or typo | Verify hashtag spelling, try broader terms |
| `Login required` | Content requires authentication | Some content unavailable without login; actor handles when possible |

### Recovery Strategies

1. **Automatic retry**: Implement exponential backoff (30s, 60s, 120s) for transient failures
2. **Graceful degradation**: If profile fails, continue with remaining profiles
3. **Batch splitting**: For large requests, split into chunks of 10-20 items
4. **Cost protection**: Set `maxCostPerRun` in actor options
5. **Fallback actors**: Some actors have alternatives with different pricing/capabilities

## Testing Checklist

### Pre-flight

- [ ] `APIFY_TOKEN` set in `.env` (note: uses `APIFY_TOKEN`, not `APIFY_API_TOKEN`)
- [ ] Dependencies installed (`pip install apify-client python-dotenv`)
- [ ] Network connectivity to `api.apify.com`
- [ ] Sufficient Apify credits available
- [ ] `.tmp/` directory exists or can be created

### Smoke Tests

```bash
# Profile: Quick test with known public profile
python scripts/scrape_instagram.py profile natgeo --output test_profile.json

# Posts: Minimal posts from public account
python scripts/scrape_instagram.py posts natgeo --max-posts 5 --output test_posts.json

# Hashtag: Popular hashtag with few results
python scripts/scrape_instagram.py hashtag photography --max-posts 5 --output test_hashtag.json

# Reels: Minimal reels from active account
python scripts/scrape_instagram.py reels redbull --max-reels 5 --output test_reels.json

# Comments: Popular post with many comments
python scripts/scrape_instagram.py comments "https://www.instagram.com/p/KNOWN_POST_ID/" --max-comments 10 --output test_comments.json
```

### Validation Checklist

#### Profile Mode
- [ ] Response contains `data` array with profile objects
- [ ] Each profile has `username`, `followers_count`, `posts_count`
- [ ] `is_verified` and `is_private` flags present
- [ ] `profile_url` is valid Instagram URL
- [ ] `scraped_at` timestamp is present and valid

#### Posts Mode
- [ ] Response contains `data` array sorted by `engagement_score` (descending)
- [ ] Each post has `shortcode`, `caption`, `likes_count`, `comments_count`
- [ ] `post_url` is valid and matches shortcode
- [ ] `owner_username` matches requested profile
- [ ] `hashtags` and `mentions` arrays present

#### Hashtag Mode
- [ ] Response contains `data` array sorted by `engagement_score`
- [ ] `source_hashtag` field matches requested hashtag
- [ ] Posts are from various users (not just one account)
- [ ] `total_count` respects `--max-posts` limit

#### Reels Mode
- [ ] Response contains `data` array with reel objects
- [ ] Each reel has `play_count`, `view_count`, `duration`
- [ ] `video_url` and `thumbnail_url` present
- [ ] `audio_title` and `audio_artist` populated when available

#### Comments Mode
- [ ] Response contains `data` array sorted by `likes_count`
- [ ] Each comment has `text`, `owner_username`, `likes_count`
- [ ] `is_reply` flag distinguishes top-level vs reply comments
- [ ] `post_shortcode` matches input URL

## Performance Tips

### Batch Processing

- **Batch usernames**: Combine multiple usernames in single run
  ```bash
  python scripts/scrape_instagram.py profile user1 user2 user3 user4 user5
  ```
- **Parallel hashtags**: Search multiple related hashtags together
  ```bash
  python scripts/scrape_instagram.py hashtag ai ml deeplearning neuralnetworks
  ```
- **Limit for testing**: Use small limits during development
  ```bash
  python scripts/scrape_instagram.py posts username --max-posts 10
  ```

### Cost Optimization

- Start with minimal items (`--max-posts 10`) for testing
- Use profile mode first to verify account exists before scraping posts
- Cache results locally to avoid re-scraping unchanged profiles
- Use hashtag mode for discovery, then target specific profiles

### Discovery Strategy

1. **Find influencers**: Use hashtag mode to find active accounts in a niche
2. **Analyze profiles**: Scrape profiles to compare follower counts and engagement
3. **Deep dive**: Scrape posts from top performers to analyze content strategy
4. **Engagement analysis**: Scrape comments to understand audience sentiment

### Rate Limit Handling

- Space out large requests (wait 60s between batches)
- Use smaller batches for sensitive accounts
- Monitor Apify run status for rate limit warnings
- The actors handle proxy rotation automatically

### Memory Usage

- For >500 items, consider splitting into multiple runs
- Process results in chunks when analyzing large datasets
- Stream results to file instead of holding in memory

## Related Skills

| Skill | Use Case |
|-------|----------|
| `content-generation` | Summarize scraped posts, generate reports |
| `google-workspace` | Save results to Google Sheets or Docs |
| `parallel-research` | Cross-reference Instagram data with web research |
| `slack-automation` | Send scraping results to Slack channels |

### Example Workflow

```bash
# 1. Discover accounts via hashtag
python scripts/scrape_instagram.py hashtag sustainablefashion --max-posts 100

# 2. Identify top accounts from results
# (manually or via script analysis)

# 3. Get detailed profile data
python scripts/scrape_instagram.py profile account1 account2 account3

# 4. Analyze their best content
python scripts/scrape_instagram.py posts account1 --max-posts 50

# 5. Understand audience sentiment
python scripts/scrape_instagram.py comments "https://instagram.com/p/top_post/" --max-comments 200

# 6. Generate report (using content-generation skill)
# 7. Save to Google Drive (using google-workspace skill)
```
