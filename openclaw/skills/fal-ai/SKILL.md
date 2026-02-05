---
name: fal-ai
description: Generate images, videos, music, and more using fal.ai's model library. Supports 100+ models including Flux, Stable Diffusion, video generation, upscaling, and audio.
homepage: https://fal.ai
metadata: {"openclaw":{"emoji":"🎨","requires":{"env":["FAL_KEY"]}}}
---

# fal-ai

Universal wrapper for [fal.ai](https://fal.ai) — access 100+ AI models for image generation, video, music, upscaling, and more.

## Setup

1. Get your API key at https://fal.ai/dashboard/keys
2. Set the environment variable:
   ```bash
   export FAL_KEY="your-key-here"
   ```

## Usage

```bash
# Generate an image
python3 fal.py generate "fal-ai/flux/schnell" '{"prompt": "a robot reading a book"}'

# Generate music
python3 fal.py generate "fal-ai/minimax-music/v2" '{"prompt": "upbeat electronic track"}'

# Upscale a video
python3 fal.py generate-queue "fal-ai/flashvsr/upscale/video" '{"video_url": "https://..."}'

# Search for models
python3 fal.py search "video generation"

# Get model schema (see required parameters)
python3 fal.py schema "fal-ai/flux/schnell"
```

## Popular Models

### Image Generation
| Model | Cost | Notes |
|-------|------|-------|
| `fal-ai/flux/schnell` | $0.003 | Fast, great quality |
| `fal-ai/flux-pro/v1.1` | $0.05 | Best quality |
| `fal-ai/nano-banana-pro` | $0.15 | Google Imagen 3, great typography |
| `fal-ai/stable-diffusion-v3-medium` | $0.035 | SD3 |

### Video Generation
| Model | Cost | Notes |
|-------|------|-------|
| `fal-ai/minimax-video/video-01-live` | ~$0.50 | MiniMax video |
| `fal-ai/kling-video/v1.5/pro` | ~$0.30 | Kling video |
| `fal-ai/luma-dream-machine` | ~$0.30 | Luma Labs |

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

## Commands

| Command | Description |
|---------|-------------|
| `generate <model> <json>` | Run model directly (fast, small jobs) |
| `generate-queue <model> <json>` | Run via queue (longer jobs) |
| `models` | List all available models |
| `search <keywords>` | Search for models |
| `schema <model>` | Get model's input schema |
| `status <url>` | Check queued job status |
| `result <url>` | Get completed job result |
| `cancel <url>` | Cancel queued job |

## Examples

### Generate an image and save it
```bash
# Generate
python3 fal.py generate "fal-ai/flux/schnell" '{"prompt": "cyberpunk cityscape at night"}' > result.json

# Extract URL (the response includes image URLs)
cat result.json | jq -r '.images[0].url'
```

### Queue a long video job
```bash
# Submit to queue
python3 fal.py generate-queue "fal-ai/minimax-video/video-01-live" \
  '{"prompt": "a cat playing piano"}' > queue.json

# Check status
python3 fal.py status "$(cat queue.json | jq -r '.status_url')"

# Get result when done
python3 fal.py result "$(cat queue.json | jq -r '.response_url')"
```

### Reference image (image-to-image)
```bash
python3 fal.py generate "fal-ai/flux/dev/image-to-image" '{
  "prompt": "make it look like a watercolor painting",
  "image_url": "https://example.com/photo.jpg",
  "strength": 0.7
}'
```

## Tips

- Use `generate` for fast models (< 30s)
- Use `generate-queue` for slow models (video, large images)
- Check `schema` to see required/optional parameters
- Most image models return `images[0].url` in the response
- Video models typically return `video.url`

## Links

- [fal.ai Model Library](https://fal.ai/models)
- [fal.ai Pricing](https://fal.ai/pricing)
- [API Docs](https://fal.ai/docs)
