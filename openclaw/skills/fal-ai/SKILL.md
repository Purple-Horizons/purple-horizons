---
name: fal-ai
description: Generate images, videos, music, and more using fal.ai's 600+ model library. Powered by official fal-client with auto-queue, file uploads, streaming, and smart defaults.
homepage: https://fal.ai
metadata: {"openclaw":{"emoji":"🎨","requires":{"env":["FAL_KEY"],"pip":["fal-client"]}}}
---

# fal-ai

Universal CLI for [fal.ai](https://fal.ai) — access 600+ AI models for image generation, video, music, upscaling, and more. Built on the official `fal-client` with auto-queue polling, file uploads, and streaming.

## Setup

1. Get your API key at https://fal.ai/dashboard/keys
2. Set the environment variable:
   ```bash
   export FAL_KEY="your-key-here"
   ```
3. Install the client:
   ```bash
   pip3 install fal-client
   ```

## Quick Commands

```bash
# Generate an image (default: nano-banana-pro / Google Imagen 3)
python3 fal.py image "vibrant Miami sunset over Brickell"

# Save to file
python3 fal.py image "logo design" --save logo.png

# Use a different model
python3 fal.py image "abstract art" --model fal-ai/flux-pro/v1.1

# Change size (square_hd, landscape_4_3, portrait_4_3, landscape_16_9, portrait_16_9)
python3 fal.py image "headshot" --size square_hd

# Generate a video
python3 fal.py video "ocean waves crashing" --save waves.mp4

# Image-to-video
python3 fal.py video "slow zoom in" --image https://example.com/photo.jpg
```

## Core Commands

```bash
# Run any model with auto-queue + polling (recommended for everything)
python3 fal.py subscribe <model> '<json_params>'

# Run directly (fast models only, <30s)
python3 fal.py run <model> '<json_params>'

# Submit and get request_id (check later)
python3 fal.py submit <model> '<json_params>'
python3 fal.py status <model> <request_id>
python3 fal.py result <model> <request_id>
python3 fal.py cancel <model> <request_id>

# Stream results (SSE-compatible models)
python3 fal.py stream <model> '<json_params>'

# Upload a local file → get fal URL
python3 fal.py upload ./my-photo.jpg
```

## Discovery

```bash
# Search for models
python3 fal.py models "video generation"

# Get model schema (see required/optional params)
python3 fal.py schema fal-ai/nano-banana-pro
```

## Popular Models

### Image Generation
| Model | Cost | Notes |
|-------|------|-------|
| `fal-ai/nano-banana-pro` | $0.15 | **Default** — Google Imagen 3, bright/vibrant, great typography |
| `fal-ai/flux/schnell` | $0.003 | Fast, good quality |
| `fal-ai/flux-pro/v1.1` | $0.05 | Best quality FLUX |
| `fal-ai/stable-diffusion-v3-medium` | $0.035 | SD3 |

### Video Generation
| Model | Cost | Notes |
|-------|------|-------|
| `fal-ai/minimax-video/video-01-live` | ~$0.50 | MiniMax video |
| `fal-ai/kling-video/v1.5/pro` | ~$0.30 | Kling video |
| `fal-ai/luma-dream-machine` | ~$0.30 | Luma Labs |
| `fal-ai/wan/v2.1/1.3b/text-to-video` | varies | WAN 2.1 |

### Video Upscaling
| Model | Cost | Notes |
|-------|------|-------|
| `fal-ai/flashvsr/upscale/video` | $0.0005/MP | Fast upscale |
| `fal-ai/bytedance-upscaler/upscale/video` | ~$0.007/s | ByteDance, up to 4K |

### Music & Audio
| Model | Cost | Notes |
|-------|------|-------|
| `fal-ai/elevenlabs/music` | varies | ElevenLabs text-to-music |
| `fal-ai/minimax-music/v2` | varies | MiniMax music generation |

### Speech & Transcription
| Model | Cost | Notes |
|-------|------|-------|
| `fal-ai/whisper` | varies | Speech-to-text |

### LLMs
| Model | Cost | Notes |
|-------|------|-------|
| `fal-ai/any-llm` | varies | Use any LLM via fal |

## Legacy Aliases

`generate` and `generate-queue` still work — both map to `subscribe`.

## File Uploads

For models that need image/video/audio input, upload first:

```bash
# Upload local file
python3 fal.py upload ./photo.jpg
# Returns: {"url": "https://fal.media/files/..."}

# Use the URL as input
python3 fal.py subscribe fal-ai/flux/dev/image-to-image '{"image_url": "https://fal.media/files/...", "prompt": "oil painting style"}'
```

## Workflows

Chain models by using output URLs as inputs:

```bash
# 1. Generate image
python3 fal.py image "cyberpunk city" --save city.png

# 2. Upload it
python3 fal.py upload ./city.png

# 3. Animate it
python3 fal.py video "camera slowly panning across" --image "https://fal.media/files/..."
```
