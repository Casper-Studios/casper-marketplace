#!/usr/bin/env python3
"""
fal.ai Image Generation - Professional Workflows
Supports Nano Banana Pro (text-to-image + edit) and FLUX-2 models.

Usage:
    # Nano Banana Pro - Text to Image
    python execution/generate_images.py nano-banana "A professional product photo" --aspect-ratio 16:9 --resolution 2K

    # Nano Banana Pro - Edit
    python execution/generate_images.py nano-banana-edit "Change color to blue" --images image1.jpg image2.jpg --resolution 2K

    # FLUX-2 - Text to Image
    python execution/generate_images.py flux "Vibrant lifestyle photo" --size landscape_4_3 --guidance 2.5

    # Advanced options
    python execution/generate_images.py nano-banana "Brand campaign image" --num-images 4 --resolution 4K --seed 42

    # FLUX-2 with custom dimensions
    python execution/generate_images.py flux "Product shot" --width 1024 --height 1536 --steps 35 --guidance 3.5
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import requests
from urllib.parse import urljoin

# Load environment variables
load_dotenv()

# Configuration
FAL_API_KEY = os.getenv("FAL_API_KEY")
OUTPUT_DIR = Path(__file__).parent.parent / ".tmp" / "generated_images"

# API Endpoints
ENDPOINTS = {
    "nano-banana": "fal-ai/nano-banana-pro",
    "nano-banana-edit": "fal-ai/nano-banana-pro/edit",
    "flux": "fal-ai/flux-2"
}

# Model Capabilities
NANO_BANANA_ASPECTS = ["21:9", "16:9", "3:2", "4:3", "5:4", "1:1", "4:5", "3:4", "2:3", "9:16"]
NANO_BANANA_RESOLUTIONS = ["1K", "2K", "4K"]
FLUX_SIZES = ["square_hd", "square", "portrait_4_3", "portrait_16_9", "landscape_4_3", "landscape_16_9"]
OUTPUT_FORMATS = ["jpeg", "png", "webp"]

def validate_environment():
    """Validate required environment variables."""
    if not FAL_API_KEY:
        raise ValueError(
            "FAL_API_KEY not found in environment. "
            "Please add it to your .env file.\n"
            "Get your key from: https://fal.ai/dashboard/keys"
        )

def submit_request(endpoint, payload):
    """
    Submit image generation request to fal.ai (queue-based).

    Args:
        endpoint: Model endpoint ID
        payload: Request payload dict

    Returns:
        dict: Response with request_id
    """
    url = f"https://queue.fal.run/{endpoint}"
    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json"
    }

    print(f"🚀 Submitting request to {endpoint}...")

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"   Response: {e.response.text}")
        raise

def poll_status(endpoint, request_id, max_wait=300):
    """
    Poll for request completion.

    Args:
        endpoint: Model endpoint ID
        request_id: Request ID from submission
        max_wait: Maximum seconds to wait

    Returns:
        dict: Completed response with images
    """
    status_url = f"https://queue.fal.run/{endpoint}/requests/{request_id}/status"
    headers = {
        "Authorization": f"Key {FAL_API_KEY}"
    }

    print(f"⏳ Waiting for generation to complete...")
    start_time = time.time()
    last_status = None

    while (time.time() - start_time) < max_wait:
        try:
            response = requests.get(status_url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            status = data.get("status")
            if status != last_status:
                print(f"   Status: {status}")
                last_status = status

            if status == "COMPLETED":
                print(f"✅ Generation completed in {time.time() - start_time:.1f}s")
                return data.get("response_url") or data

            elif status in ["FAILED", "CANCELLED"]:
                error_msg = data.get("error", "Unknown error")
                raise Exception(f"Generation failed: {error_msg}")

            time.sleep(2)  # Poll every 2 seconds

        except requests.exceptions.RequestException as e:
            print(f"⚠️  Poll error: {str(e)}, retrying...")
            time.sleep(2)

    raise TimeoutError(f"Generation exceeded {max_wait}s timeout")

def fetch_result(response_url):
    """Fetch final result from response URL."""
    headers = {
        "Authorization": f"Key {FAL_API_KEY}"
    }

    response = requests.get(response_url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()

def download_images(images, output_dir):
    """
    Download generated images.

    Args:
        images: List of image dicts with 'url' field
        output_dir: Directory to save images

    Returns:
        list: Paths to downloaded images
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    downloaded = []

    print(f"\n📥 Downloading {len(images)} image(s)...")

    for i, image_data in enumerate(images, 1):
        image_url = image_data.get("url")
        if not image_url:
            print(f"⚠️  Image {i}: No URL found, skipping")
            continue

        # Determine filename
        file_name = image_data.get("file_name") or f"generated_{i}.png"
        output_path = output_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_name}"

        try:
            response = requests.get(image_url, timeout=60)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                f.write(response.content)

            print(f"   ✅ Image {i}: {output_path}")
            downloaded.append(str(output_path))

        except Exception as e:
            print(f"   ❌ Image {i} download failed: {str(e)}")

    return downloaded

def generate_nano_banana(args):
    """Generate images with Nano Banana Pro."""
    # Build payload
    payload = {
        "prompt": args.prompt,
        "num_images": args.num_images,
        "aspect_ratio": args.aspect_ratio,
        "resolution": args.resolution,
        "output_format": args.output_format
    }

    if args.seed:
        payload["seed"] = args.seed

    if args.enable_web_search:
        payload["enable_web_search"] = True
        print("⚠️  Web search enabled (+$0.015 per image)")

    # Validate
    if args.aspect_ratio not in NANO_BANANA_ASPECTS:
        print(f"⚠️  Invalid aspect ratio, using 1:1")
        payload["aspect_ratio"] = "1:1"

    if args.resolution not in NANO_BANANA_RESOLUTIONS:
        print(f"⚠️  Invalid resolution, using 1K")
        payload["resolution"] = "1K"

    # Cost estimate
    base_cost = 0.15
    if args.resolution == "4K":
        base_cost = 0.30
    web_search_cost = 0.015 if args.enable_web_search else 0
    total_cost = (base_cost + web_search_cost) * args.num_images
    print(f"💰 Estimated cost: ${total_cost:.2f} ({args.num_images} images @ ${base_cost + web_search_cost:.3f} each)")

    return payload

def generate_nano_banana_edit(args):
    """Generate edited images with Nano Banana Pro Edit."""
    if not args.images:
        raise ValueError("--images required for edit mode (up to 14 images)")

    if len(args.images) > 14:
        print("⚠️  Maximum 14 images, using first 14")
        args.images = args.images[:14]

    # Convert local paths to URLs if needed (upload to temporary hosting)
    image_urls = []
    for img_path in args.images:
        if img_path.startswith("http"):
            image_urls.append(img_path)
        else:
            # For local files, user needs to upload them first
            print(f"⚠️  Local file detected: {img_path}")
            print(f"   Please upload to public URL first (e.g., imgur, imgbb)")
            raise ValueError(f"Local files not supported yet: {img_path}")

    payload = {
        "prompt": args.prompt,
        "image_urls": image_urls,
        "num_images": args.num_images,
        "resolution": args.resolution,
        "aspect_ratio": args.aspect_ratio or "auto",
        "output_format": args.output_format
    }

    print(f"🔧 Editing {len(image_urls)} input image(s)")

    # Cost estimate
    base_cost = 0.15 if args.resolution != "4K" else 0.30
    total_cost = base_cost * args.num_images
    print(f"💰 Estimated cost: ${total_cost:.2f}")

    return payload

def generate_flux(args):
    """Generate images with FLUX-2."""
    # Build payload
    payload = {
        "prompt": args.prompt,
        "guidance_scale": args.guidance,
        "num_inference_steps": args.steps,
        "output_format": args.output_format
    }

    # Handle image size
    if args.width and args.height:
        # Custom dimensions
        if not (512 <= args.width <= 2048 and 512 <= args.height <= 2048):
            print("⚠️  Dimensions must be 512-2048px, adjusting...")
            args.width = max(512, min(2048, args.width))
            args.height = max(512, min(2048, args.height))

        payload["image_size"] = {"width": args.width, "height": args.height}
        megapixels = (args.width * args.height) / 1_000_000
    else:
        # Predefined size
        if args.size not in FLUX_SIZES:
            print(f"⚠️  Invalid size, using square")
            args.size = "square"

        payload["image_size"] = args.size
        # Estimate megapixels (approximate)
        size_mp = {
            "square": 1.05, "square_hd": 2.1,
            "portrait_4_3": 1.05, "portrait_16_9": 1.05,
            "landscape_4_3": 1.05, "landscape_16_9": 1.05
        }
        megapixels = size_mp.get(args.size, 1.0)

    if args.seed:
        payload["seed"] = args.seed

    if args.enable_safety_checker is not None:
        payload["enable_safety_checker"] = args.enable_safety_checker

    if args.enable_prompt_expansion:
        payload["enable_prompt_expansion"] = True

    # LoRAs support (advanced)
    if args.loras:
        loras = []
        for lora_spec in args.loras:
            # Format: path:scale or just path (scale=1.0)
            if ':' in lora_spec:
                path, scale = lora_spec.rsplit(':', 1)
                loras.append({"path": path, "scale": float(scale)})
            else:
                loras.append({"path": lora_spec, "scale": 1.0})
        payload["loras"] = loras
        print(f"🎨 Using {len(loras)} LoRA(s)")

    # Image-to-image editing
    if args.images:
        if len(args.images) > 3:
            print("⚠️  FLUX-2 supports max 3 images, using first 3")
            args.images = args.images[:3]

        image_urls = []
        for img_path in args.images:
            if img_path.startswith("http"):
                image_urls.append(img_path)
            else:
                print(f"⚠️  Local file: {img_path} - upload to public URL first")
                raise ValueError(f"Local files not supported: {img_path}")

        payload["image_urls"] = image_urls
        print(f"🖼️  Using {len(image_urls)} reference image(s)")

    # Cost estimate
    cost_per_mp = 0.012
    total_cost = cost_per_mp * megapixels * args.num_images
    print(f"💰 Estimated cost: ${total_cost:.4f} ({megapixels:.2f}MP x {args.num_images} images)")

    # Note: num_images not directly supported in FLUX-2 API, need to make multiple requests
    if args.num_images > 1:
        print(f"ℹ️  Note: Generating {args.num_images} images requires {args.num_images} separate requests")

    return payload

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Generate images with fal.ai (Nano Banana Pro or FLUX-2)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Required arguments
    parser.add_argument(
        "model",
        choices=["nano-banana", "nano-banana-edit", "flux"],
        help="Model to use"
    )
    parser.add_argument(
        "prompt",
        help="Image generation or edit prompt"
    )

    # Common options
    parser.add_argument("--num-images", type=int, default=1, help="Number of images (1-4)")
    parser.add_argument("--output-format", choices=OUTPUT_FORMATS, default="png", help="Output format")
    parser.add_argument("--seed", type=int, help="Seed for reproducibility")
    parser.add_argument("--output-dir", help="Custom output directory")

    # Nano Banana options
    parser.add_argument("--aspect-ratio", choices=NANO_BANANA_ASPECTS, default="1:1", help="Aspect ratio (Nano Banana)")
    parser.add_argument("--resolution", choices=NANO_BANANA_RESOLUTIONS, default="1K", help="Resolution (Nano Banana)")
    parser.add_argument("--enable-web-search", action="store_true", help="Enable web search (+$0.015)")
    parser.add_argument("--images", nargs="+", help="Input images for editing (URLs or paths)")

    # FLUX-2 options
    parser.add_argument("--size", choices=FLUX_SIZES, default="square", help="Image size preset (FLUX-2)")
    parser.add_argument("--width", type=int, help="Custom width 512-2048px (FLUX-2)")
    parser.add_argument("--height", type=int, help="Custom height 512-2048px (FLUX-2)")
    parser.add_argument("--guidance", type=float, default=2.5, help="Guidance scale 0-20 (FLUX-2)")
    parser.add_argument("--steps", type=int, default=28, help="Inference steps 4-50 (FLUX-2)")
    parser.add_argument("--enable-safety-checker", type=bool, help="Enable safety checker (FLUX-2)")
    parser.add_argument("--enable-prompt-expansion", action="store_true", help="Auto-expand prompt (FLUX-2)")
    parser.add_argument("--loras", nargs="+", help="LoRA paths (format: url:scale or url)")

    args = parser.parse_args()

    try:
        # Validate environment
        validate_environment()

        print(f"🎨 fal.ai Image Generation")
        print(f"   Model: {args.model}")
        print(f"   Prompt: {args.prompt[:80]}{'...' if len(args.prompt) > 80 else ''}")

        # Build payload based on model
        if args.model == "nano-banana":
            payload = generate_nano_banana(args)
        elif args.model == "nano-banana-edit":
            payload = generate_nano_banana_edit(args)
        elif args.model == "flux":
            payload = generate_flux(args)

        # Get endpoint
        endpoint = ENDPOINTS[args.model]

        # Submit request
        result = submit_request(endpoint, payload)

        # Handle response based on type
        if isinstance(result, dict) and "request_id" in result:
            # Queue-based response
            request_id = result["request_id"]
            print(f"   Request ID: {request_id}")

            # Poll for completion
            response = poll_status(endpoint, request_id)

            # If response is URL, fetch it
            if isinstance(response, str):
                response = fetch_result(response)
        else:
            # Direct response
            response = result

        # Extract images
        images = response.get("images", [])
        if not images:
            print("⚠️  No images in response")
            print(f"   Response: {json.dumps(response, indent=2)}")
            return 1

        # Download images
        output_dir = Path(args.output_dir) if args.output_dir else OUTPUT_DIR
        downloaded_paths = download_images(images, output_dir)

        # Save metadata
        metadata = {
            "model": args.model,
            "prompt": args.prompt,
            "parameters": vars(args),
            "response": response,
            "downloaded_files": downloaded_paths,
            "generated_at": datetime.now().isoformat()
        }

        metadata_path = output_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"\n✅ Generation complete!")
        print(f"   Images: {len(downloaded_paths)}")
        print(f"   Metadata: {metadata_path}")

        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
