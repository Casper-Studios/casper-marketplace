# Multi-Platform Scraping (TikTok & YouTube)

## Script
`scripts/scrape_multi_platform.py`

## TikTok

### Actor
`clockworks/tiktok-scraper`

### Inputs
| Parameter | Type | Description |
|-----------|------|-------------|
| `hashtags` | list | Hashtags to search |
| `max_videos` | int | Maximum videos |

### Usage
```bash
python scripts/scrape_multi_platform.py tiktok --hashtags "AI,tech" --max-videos 50
```

## YouTube

### Actor
`streamers/youtube-scraper`

### Inputs
| Parameter | Type | Description |
|-----------|------|-------------|
| `search_query` | string | Search term |
| `max_results` | int | Maximum videos |
| `download_subtitles` | bool | Include transcripts |

### Usage
```bash
python scripts/scrape_multi_platform.py youtube --query "AI tutorial" --max-results 20

# With subtitles
python scripts/scrape_multi_platform.py youtube --query "AI" --subtitles
```

## Output Structure

### TikTok
```json
{
  "videos": [
    {
      "id": "video_id",
      "description": "caption",
      "author": "username",
      "likes": 0,
      "comments": 0,
      "shares": 0,
      "video_url": "url"
    }
  ]
}
```

### YouTube
```json
{
  "videos": [
    {
      "id": "video_id",
      "title": "Video Title",
      "channelName": "Channel",
      "viewCount": 0,
      "likeCount": 0,
      "description": "...",
      "subtitles": "transcript text"
    }
  ]
}
```

## Cost Estimates
- TikTok: ~$0.005 per video
- YouTube: ~$0.01-0.05 per video (more with subtitles)

## Testing Checklist

### Pre-flight
- [ ] `APIFY_API_TOKEN` set in `.env`
- [ ] Dependencies installed (`pip install apify-client python-dotenv`)
- [ ] Network connectivity to `api.apify.com`

### Smoke Test
```bash
# Test TikTok with a simple hashtag
python scripts/scrape_multi_platform.py tiktok --hashtags "tech" --max-videos 5

# Test YouTube with a simple search
python scripts/scrape_multi_platform.py youtube --query "AI tutorial" --max-results 5

# Test YouTube with subtitles
python scripts/scrape_multi_platform.py youtube --query "Python basics" --max-results 3 --subtitles
```

### Validation

#### TikTok
- [ ] Response contains `videos` array with expected fields (`id`, `description`, `author`, `likes`)
- [ ] Video URLs are accessible
- [ ] Engagement metrics present (`likes`, `comments`, `shares`)
- [ ] Cost estimate: ~$0.025 for 5 videos

#### YouTube
- [ ] Response contains `videos` array with expected fields (`id`, `title`, `channelName`, `viewCount`)
- [ ] Video IDs are valid YouTube video IDs
- [ ] `subtitles` field populated when `--subtitles` flag used
- [ ] Channel names and descriptions present
- [ ] Cost estimate: ~$0.05-0.25 for 5 videos (more with subtitles)

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid or expired Apify API token | Verify `APIFY_API_TOKEN` in .env, regenerate token |
| `402 Payment Required` | Insufficient Apify credits | Add credits to Apify account |
| `Actor timeout` | Too many videos or subtitle extraction | Reduce `max_videos`, disable `download_subtitles` |
| `Hashtag not found` | TikTok hashtag doesn't exist | Verify hashtag spelling, try without # prefix |
| `Video unavailable` | Video was deleted or made private | Skip and continue with remaining videos |
| `Subtitles unavailable` | YouTube video has no captions | Continue without subtitles, log for manual review |
| `Region restricted` | Content not available in actor's region | Some content may be inaccessible - skip and log |
| `Rate limited` | Platform detected scraping | Wait 5 minutes, reduce batch size |

### Recovery Strategies

1. **Automatic retry**: Implement exponential backoff (60s, 120s, 240s) for rate limits
2. **Graceful degradation**: If subtitles fail, return video metadata without transcript
3. **Platform fallback**: If one platform fails entirely, continue with successful platforms
4. **Batch processing**: Limit to 20 videos per run to avoid timeouts
5. **Cost monitoring**: Track per-platform costs and set alerts at thresholds

## Performance Tips

### Batch Processing
- Combine multiple URLs in single actor run
- Use `maxItems` to limit results when testing
- Process results as they stream (if supported)

### Rate Limit Handling
- Implement exponential backoff between requests
- Use proxies to distribute load
- Respect platform rate limits (Twitter: 300/15min)

### Cost Optimization
- Start with `maxItems: 10` for testing
- Use date filters to reduce volume
- Cache results locally to avoid re-scraping

### Memory Usage
- Process large result sets in chunks
- Stream to file instead of memory for >1000 items
