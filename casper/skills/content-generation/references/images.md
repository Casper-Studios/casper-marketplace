# Image Generation (fal.ai)

## Models

### Nano Banana Pro
- **Best for:** Brand images, complex scenes, text in images
- **Cost:** $0.15 (1K), $0.30 (4K)

### FLUX-2
- **Best for:** High volume, fast iteration, LoRA support
- **Cost:** $0.012/megapixel

## Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | string | required | Image description |
| `model` | string | nano-banana-pro | Model choice |
| `aspect_ratio` | string | 1:1 | 21:9, 16:9, 4:3, 1:1, 9:16, etc. |
| `resolution` | string | 1K | 1K, 2K, 4K (Nano only) |
| `num_images` | int | 1 | 1-4 variations |

## CLI Usage

```bash
# Nano Banana Pro
python scripts/generate_images.py "Professional headshot" --model nano-banana-pro --ratio 1:1

# FLUX-2 batch
python scripts/generate_images.py "Social media graphic" --model flux-2 --size square_hd --count 4

# 4K output
python scripts/generate_images.py "Print-quality photo" --model nano-banana-pro --resolution 4K
```

## Python Usage

### Install SDK
```bash
pip install fal-client
```

### Basic Image Generation
```python
import fal_client

result = fal_client.subscribe(
    "fal-ai/flux/schnell",
    arguments={
        "prompt": "A futuristic cityscape at sunset",
        "image_size": "landscape_16_9",
        "num_images": 1
    }
)

print(result["images"][0]["url"])
```

### With Progress Callback
```python
def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        print(f"Progress: {update.logs}")

result = fal_client.subscribe(
    "fal-ai/flux/dev",
    arguments={"prompt": "..."},
    with_logs=True,
    on_queue_update=on_queue_update
)
```

### Nano Banana Pro (Higher Quality)
```python
import fal_client

result = fal_client.subscribe(
    "fal-ai/nano-banana-pro",
    arguments={
        "prompt": "Professional headshot, studio lighting",
        "aspect_ratio": "1:1",
        "resolution": "2K"
    }
)

# Download image
import requests
image_url = result["images"][0]["url"]
response = requests.get(image_url)
with open("output.png", "wb") as f:
    f.write(response.content)
```

### Batch Generation
```python
import fal_client

prompts = [
    "Social media graphic for tech company",
    "Abstract blue pattern background",
    "Professional office workspace"
]

for i, prompt in enumerate(prompts):
    result = fal_client.subscribe(
        "fal-ai/flux/schnell",
        arguments={
            "prompt": prompt,
            "image_size": "square_hd",
            "num_images": 1
        }
    )
    print(f"Image {i+1}: {result['images'][0]['url']}")
```

## Model Comparison

### fal.ai Image Models

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| `flux/schnell` | Fast (2-4s) | Good | $0.003 | Drafts, iterations |
| `flux/dev` | Medium (8-15s) | High | $0.025 | Production images |
| `flux-pro` | Slow (15-30s) | Highest | $0.05 | Premium content |
| `flux-realism` | Medium | Photorealistic | $0.025 | Product photos |
| `stable-diffusion-v3` | Fast | Good | $0.002 | General purpose |
| `nano-banana-pro` | Medium (5-15s) | Highest | $0.15-0.30 | Brand campaigns, text |
| `flux-2` | Fast (2-5s) | Good | $0.012/MP | High volume batches |

### When to Use Each
- **Quick iterations**: flux/schnell - test prompts fast
- **Final assets**: flux/dev or flux-pro - higher quality
- **Photos**: flux-realism - realistic human faces, products
- **Budget**: stable-diffusion-v3 - lowest cost
- **Brand campaigns**: nano-banana-pro - best text rendering, highest quality
- **High volume (50+)**: flux-2 - cost-effective at scale

### LoRA/Fine-tuning
Some models support LoRA for style customization:
```python
result = fal_client.subscribe(
    "fal-ai/flux/dev",
    arguments={
        "prompt": "A portrait in custom style",
        "loras": [{"path": "https://...", "scale": 0.8}]
    }
)
```

## Model Selection

| Use Case | Model | Why |
|----------|-------|-----|
| Brand campaign | Nano Banana Pro 2K | Best quality, text rendering |
| Social batch (50+) | FLUX-2 | Cost ($0.012 vs $0.15) |
| Product edit | Nano Banana Pro Edit | Multi-image blending |
| Custom style (LoRA) | FLUX-2 + LoRA | LoRA support |
| Print materials | Nano Banana Pro 4K | Highest resolution |

## Prompting Best Practices

### Prompt Structure
1. **Subject**: Main focus of the image
2. **Style**: Art style, medium, aesthetic
3. **Details**: Specific attributes, colors, lighting
4. **Quality modifiers**: Resolution, detail level

### Effective Prompts
```
# Basic structure
[subject] in [style], [details], [quality]

# Example
"A serene mountain lake at sunset, oil painting style,
warm golden light reflecting on water, misty atmosphere,
highly detailed, 8k resolution"
```

### Style Modifiers
| Category | Examples |
|----------|----------|
| Art Style | oil painting, watercolor, digital art, photorealistic, anime |
| Lighting | golden hour, dramatic lighting, soft diffused light, neon |
| Mood | serene, dramatic, whimsical, dystopian, ethereal |
| Quality | highly detailed, 8k, masterpiece, professional |

### Negative Prompts
Use to exclude unwanted elements:
```
"blurry, low quality, distorted, watermark, text, logo"
```

### Aspect Ratio Guidelines
| Use Case | Ratio | fal.ai Value |
|----------|-------|--------------|
| Social media post | 1:1 | square |
| Landscape/banner | 16:9 | landscape_16_9 |
| Portrait/mobile | 9:16 | portrait_16_9 |
| Widescreen | 21:9 | landscape_4_3 |

### Common Mistakes
1. Vague prompts: "a nice picture"
2. Too many subjects: "a cat and dog and bird and..."
3. Conflicting styles: "realistic cartoon"
4. Specific and focused prompts work best

## Output Location
`.tmp/generated_images/`

## Testing Checklist

### Pre-flight
- [ ] `FAL_API_KEY` set in `.env`
- [ ] Dependencies installed (`pip install fal-client python-dotenv`)
- [ ] Network connectivity to `fal.run`
- [ ] Sufficient fal.ai credits

### Smoke Test
```bash
# Test Nano Banana Pro (default)
python scripts/generate_images.py "A simple red apple on white background" --model nano-banana-pro --ratio 1:1

# Test FLUX-2 (faster/cheaper)
python scripts/generate_images.py "Abstract blue pattern" --model flux-2 --size square_hd

# Test batch generation
python scripts/generate_images.py "Professional headshot" --model flux-2 --count 2

# Test high resolution (4K)
python scripts/generate_images.py "Mountain landscape" --model nano-banana-pro --resolution 4K
```

### Validation
- [ ] Image file saved to `.tmp/generated_images/`
- [ ] Image URL is accessible (if returned)
- [ ] Image dimensions match requested aspect ratio/resolution
- [ ] `--count` produces correct number of images
- [ ] Text in images renders correctly (Nano Banana Pro)
- [ ] No artifacts or obvious generation errors
- [ ] Cost tracking: Nano ~$0.15 (1K), ~$0.30 (4K); FLUX ~$0.012/megapixel
- [ ] Generation time: Nano ~5-15s, FLUX ~2-5s

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid or missing API key | Verify `FAL_API_KEY` in .env |
| `402 Payment Required` | Insufficient fal.ai credits | Add credits at fal.ai/billing |
| `429 Rate Limited` | Too many concurrent requests | Wait and retry with exponential backoff |
| `Model unavailable` | Selected model is down | Try alternative model (Nano <-> FLUX) |
| `Content policy violation` | Prompt contains prohibited content | Modify prompt to comply with content policy |
| `Generation timeout` | Image took too long to generate | Retry, or use faster model (FLUX) |
| `Invalid aspect ratio` | Unsupported ratio for model | Use standard ratios (1:1, 16:9, 4:3, 9:16) |
| `Resolution too high` | 4K not supported by model | Use lower resolution or Nano Banana Pro |
| `Download failed` | Could not save generated image | Check disk space, verify output path |

### Recovery Strategies

1. **Automatic retry**: Implement exponential backoff (5s, 10s, 20s) for transient failures
2. **Model fallback**: If Nano fails, try FLUX-2; if FLUX fails, try Nano
3. **Prompt sanitization**: Pre-validate prompts against known blocked terms
4. **Resolution fallback**: If 4K fails, retry at 2K then 1K
5. **Batch chunking**: For multiple images, generate in smaller batches (2-4 at a time)
6. **Cost protection**: Set maximum cost per request and abort if exceeded
