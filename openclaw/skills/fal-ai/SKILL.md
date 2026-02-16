---
name: fal-ai
description: Generate images, videos, music, and more using fal.ai's 600+ model library. Powered by official fal-client + Platform APIs for live pricing, usage tracking, cost estimates, and model discovery.
homepage: https://fal.ai
metadata: {"openclaw":{"emoji":"🎨","requires":{"env":["FAL_KEY"],"pip":["fal-client"]}}}
---

# fal-ai

Universal CLI for [fal.ai](https://fal.ai) — access 600+ AI models for image generation, video, music, upscaling, and more. Built on the official `fal-client` + Platform APIs.

## Setup

1. Get your API key at https://fal.ai/dashboard/keys
2. Set: `export FAL_KEY="your-key-here"`
3. Install: `pip3 install fal-client`

## Quick Commands

```bash
# Generate an image (default: nano-banana-pro / Google Imagen 3)
python3 fal.py image "vibrant Miami sunset over Brickell"
python3 fal.py image "logo design" --save logo.png
python3 fal.py image "abstract art" --model fal-ai/flux-pro/v1.1
python3 fal.py image "headshot" --size square_hd

# Generate a video
python3 fal.py video "ocean waves crashing" --save waves.mp4
python3 fal.py video "slow zoom in" --image https://example.com/photo.jpg
```

## Model Discovery

```bash
# Search models by keyword
python3 fal.py models "video generation"

# Filter by category
python3 fal.py models --category text-to-image
python3 fal.py models --category text-to-video
python3 fal.py models --category image-to-video

# See newest/trending models
python3 fal.py latest
python3 fal.py latest --category text-to-image --limit 5

# Model details + live price
python3 fal.py info fal-ai/nano-banana-pro

# Full OpenAPI schema (see all params)
python3 fal.py schema fal-ai/nano-banana-pro
```

**Categories:** text-to-image, image-to-image, text-to-video, image-to-video, text-to-speech, speech-to-text, training, and more.

## Live Pricing & Cost Estimates

No more stale price tables — pull live data:

```bash
# Get current pricing for any models
python3 fal.py pricing fal-ai/nano-banana-pro fal-ai/flux/dev fal-ai/kling-video/v1.5/pro

# Estimate cost before running (by output units)
python3 fal.py estimate unit_price '{"fal-ai/nano-banana-pro": 10}'

# Estimate cost by number of API calls (uses historical average)
python3 fal.py estimate historical '{"fal-ai/flux/dev": 100}'
```

## Usage & Analytics

```bash
# View your usage records
python3 fal.py usage
python3 fal.py usage --endpoint fal-ai/nano-banana-pro --start 2026-02-01

# Performance analytics (request counts, latency, error rates)
python3 fal.py analytics fal-ai/nano-banana-pro --start 2026-02-01
```

## Core Generation Commands

```bash
# Run any model with auto-queue + polling (recommended)
python3 fal.py subscribe <model> '<json_params>'

# Run directly (fast models only, <30s)
python3 fal.py run <model> '<json_params>'

# Submit and check later
python3 fal.py submit <model> '<json_params>'
python3 fal.py status <model> <request_id>
python3 fal.py result <model> <request_id>
python3 fal.py cancel <model> <request_id>

# Stream results (SSE-compatible models)
python3 fal.py stream <model> '<json_params>'

# Upload local file → fal URL
python3 fal.py upload ./my-photo.jpg
```

## Workflows (chaining models)

```bash
# 1. Generate image
python3 fal.py image "cyberpunk city" --save city.png

# 2. Upload it
python3 fal.py upload ./city.png

# 3. Animate it
python3 fal.py video "camera slowly panning" --image "https://fal.media/files/..."
```

## Image Sizes

`square_hd`, `landscape_4_3`, `portrait_4_3`, `landscape_16_9`, `portrait_16_9`

## Legacy Aliases

`generate`, `generate-queue`, and `search` still work for backwards compatibility.
