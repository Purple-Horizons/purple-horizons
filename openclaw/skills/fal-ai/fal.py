#!/usr/bin/env python3
"""
fal.ai CLI — powered by official fal-client
Generate images, videos, music, and more using 600+ fal.ai models.
"""

import os
import sys
import json
import urllib.request
import urllib.error
import urllib.parse
from typing import Optional

# ── Helpers ──────────────────────────────────────────────────────────────────

def get_key() -> str:
    key = os.environ.get("FAL_KEY")
    if not key:
        print("Error: FAL_KEY not set", file=sys.stderr)
        sys.exit(1)
    return key

def ensure_client():
    try:
        import fal_client
        return fal_client
    except ImportError:
        print("Error: fal-client not installed. Run: pip3 install fal-client", file=sys.stderr)
        sys.exit(1)

def parse_json(s: str) -> dict:
    try:
        return json.loads(s)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

def on_queue_update(update):
    """Print queue status updates to stderr."""
    if hasattr(update, 'logs') and update.logs:
        for log in update.logs:
            msg = log.get("message", str(log)) if isinstance(log, dict) else str(log)
            print(f"  {msg}", file=sys.stderr)
    status_name = type(update).__name__
    if status_name == "Queued":
        pos = getattr(update, 'position', '?')
        print(f"⏳ Queued (position {pos})", file=sys.stderr)
    elif status_name == "InProgress":
        print(f"⚙️  In progress...", file=sys.stderr)
    elif status_name == "Completed":
        print(f"✅ Done", file=sys.stderr)

def download_file(url: str, path: str):
    """Download a URL to a local file."""
    print(f"Downloading → {path}", file=sys.stderr)
    urllib.request.urlretrieve(url, path)
    print(f"Saved: {path}", file=sys.stderr)

# ── Core Commands ────────────────────────────────────────────────────────────

def cmd_run(model: str, params: dict, timeout: Optional[int] = None):
    """Run a model synchronously (fast models, <30s)."""
    fal = ensure_client()
    os.environ["FAL_KEY"] = get_key()
    kwargs = {"application": model, "arguments": params}
    if timeout:
        kwargs["timeout"] = timeout
    result = fal.run(**kwargs)
    print(json.dumps(result, indent=2))

def cmd_subscribe(model: str, params: dict):
    """Run a model via queue with auto-polling (any model, recommended)."""
    fal = ensure_client()
    os.environ["FAL_KEY"] = get_key()
    result = fal.subscribe(
        model,
        arguments=params,
        with_logs=True,
        on_queue_update=on_queue_update,
    )
    print(json.dumps(result, indent=2))

def cmd_submit(model: str, params: dict):
    """Submit to queue and return handle (for long jobs you want to check later)."""
    fal = ensure_client()
    os.environ["FAL_KEY"] = get_key()
    handle = fal.submit(model, arguments=params)
    print(json.dumps({
        "request_id": handle.request_id,
        "status_url": f"https://queue.fal.run/{model}/requests/{handle.request_id}/status",
        "response_url": f"https://queue.fal.run/{model}/requests/{handle.request_id}",
    }, indent=2))

def cmd_status(model: str, request_id: str):
    """Check status of a submitted job."""
    fal = ensure_client()
    os.environ["FAL_KEY"] = get_key()
    s = fal.status(model, request_id, with_logs=True)
    print(json.dumps({
        "status": type(s).__name__,
        "logs": getattr(s, 'logs', []),
    }, indent=2))

def cmd_result(model: str, request_id: str):
    """Get result of a completed job."""
    fal = ensure_client()
    os.environ["FAL_KEY"] = get_key()
    result = fal.result(model, request_id)
    print(json.dumps(result, indent=2))

def cmd_cancel(model: str, request_id: str):
    """Cancel a queued job."""
    fal = ensure_client()
    os.environ["FAL_KEY"] = get_key()
    fal.cancel(model, request_id)
    print("Cancelled.")

def cmd_upload(file_path: str):
    """Upload a local file and get a fal URL for use as input."""
    fal = ensure_client()
    os.environ["FAL_KEY"] = get_key()
    url = fal.upload_file(file_path)
    print(json.dumps({"url": url}, indent=2))

def cmd_stream(model: str, params: dict):
    """Stream results from a model (SSE)."""
    fal = ensure_client()
    os.environ["FAL_KEY"] = get_key()
    events = []
    for event in fal.stream(model, arguments=params):
        events.append(event)
        print(json.dumps(event), file=sys.stderr)
    print(json.dumps(events, indent=2))

# ── Image shortcut ───────────────────────────────────────────────────────────

def cmd_image(prompt: str, model: str = "fal-ai/nano-banana-pro", size: str = "landscape_4_3",
              save: Optional[str] = None, extra: Optional[dict] = None):
    """Quick image generation with sensible defaults."""
    params = {"prompt": prompt, "image_size": size}
    if extra:
        params.update(extra)

    fal = ensure_client()
    os.environ["FAL_KEY"] = get_key()
    result = fal.subscribe(
        model,
        arguments=params,
        with_logs=True,
        on_queue_update=on_queue_update,
    )

    # Auto-download if save path given
    images = result.get("images", [])
    if save and images:
        download_file(images[0]["url"], save)

    print(json.dumps(result, indent=2))

# ── Video shortcut ───────────────────────────────────────────────────────────

def cmd_video(prompt: str, model: str = "fal-ai/minimax-video/video-01-live",
              image_url: Optional[str] = None, save: Optional[str] = None, extra: Optional[dict] = None):
    """Quick video generation."""
    params = {"prompt": prompt}
    if image_url:
        params["image_url"] = image_url
    if extra:
        params.update(extra)

    fal = ensure_client()
    os.environ["FAL_KEY"] = get_key()
    result = fal.subscribe(
        model,
        arguments=params,
        with_logs=True,
        on_queue_update=on_queue_update,
    )

    video = result.get("video", {})
    if save and video.get("url"):
        download_file(video["url"], save)

    print(json.dumps(result, indent=2))

# ── Model discovery (raw API, no client needed) ─────────────────────────────

def _api_get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

def cmd_models(keywords: Optional[str] = None):
    """List/search models."""
    url = "https://fal.ai/api/models"
    if keywords:
        url += f"?keywords={urllib.parse.quote(keywords)}"
    result = _api_get(url)
    print(json.dumps(result, indent=2))

def cmd_schema(model: str):
    """Get model input/output schema."""
    url = f"https://fal.ai/api/openapi/queue/openapi.json?endpoint_id={urllib.parse.quote(model)}"
    result = _api_get(url)
    print(json.dumps(result, indent=2))

# ── CLI Dispatcher ───────────────────────────────────────────────────────────

USAGE = """
fal.ai CLI (v2 — official fal-client)

QUICK COMMANDS:
  image <prompt> [--model M] [--size S] [--save path] [--extra '{}']
      Generate an image (default: nano-banana-pro / Imagen 3)

  video <prompt> [--model M] [--image URL] [--save path] [--extra '{}']
      Generate a video (default: minimax-video)

CORE COMMANDS:
  subscribe <model> <json>    Run model with auto-queue + polling (recommended)
  run <model> <json>          Run model directly (fast models only)
  submit <model> <json>       Submit to queue, get request_id back
  status <model> <request_id> Check job status
  result <model> <request_id> Get completed result
  cancel <model> <request_id> Cancel a job
  stream <model> <json>       Stream results (SSE models)
  upload <file_path>          Upload file, get fal URL

DISCOVERY:
  models [keywords]           List/search available models
  schema <model>              Get model input/output schema

EXAMPLES:
  python3 fal.py image "vibrant Miami sunset over Brickell"
  python3 fal.py image "logo design" --model fal-ai/flux-pro/v1.1 --save logo.png
  python3 fal.py subscribe fal-ai/nano-banana-pro '{"prompt":"a cat"}'
  python3 fal.py video "ocean waves" --save waves.mp4
  python3 fal.py upload ./my-photo.jpg
  python3 fal.py models "video generation"
"""

def parse_extras(args: list) -> dict:
    """Parse --key value pairs from args list."""
    opts = {}
    i = 0
    while i < len(args):
        if args[i].startswith("--") and i + 1 < len(args):
            key = args[i][2:]
            opts[key] = args[i + 1]
            i += 2
        else:
            i += 1
    return opts

def main():
    if len(sys.argv) < 2:
        print(USAGE)
        return

    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    if cmd == "image":
        if not args:
            print("Usage: image <prompt> [--model M] [--size S] [--save path] [--extra '{}']", file=sys.stderr)
            sys.exit(1)
        prompt = args[0]
        opts = parse_extras(args[1:])
        extra = parse_json(opts["extra"]) if "extra" in opts else None
        cmd_image(prompt, model=opts.get("model", "fal-ai/nano-banana-pro"),
                  size=opts.get("size", "landscape_4_3"), save=opts.get("save"), extra=extra)

    elif cmd == "video":
        if not args:
            print("Usage: video <prompt> [--model M] [--image URL] [--save path]", file=sys.stderr)
            sys.exit(1)
        prompt = args[0]
        opts = parse_extras(args[1:])
        extra = parse_json(opts["extra"]) if "extra" in opts else None
        cmd_video(prompt, model=opts.get("model", "fal-ai/minimax-video/video-01-live"),
                  image_url=opts.get("image"), save=opts.get("save"), extra=extra)

    elif cmd == "subscribe":
        if len(args) < 2:
            print("Usage: subscribe <model> <json>", file=sys.stderr); sys.exit(1)
        cmd_subscribe(args[0], parse_json(args[1]))

    elif cmd == "run":
        if len(args) < 2:
            print("Usage: run <model> <json>", file=sys.stderr); sys.exit(1)
        opts = parse_extras(args[2:])
        timeout = int(opts["timeout"]) if "timeout" in opts else None
        cmd_run(args[0], parse_json(args[1]), timeout=timeout)

    elif cmd == "submit":
        if len(args) < 2:
            print("Usage: submit <model> <json>", file=sys.stderr); sys.exit(1)
        cmd_submit(args[0], parse_json(args[1]))

    elif cmd == "status":
        if len(args) < 2:
            print("Usage: status <model> <request_id>", file=sys.stderr); sys.exit(1)
        cmd_status(args[0], args[1])

    elif cmd == "result":
        if len(args) < 2:
            print("Usage: result <model> <request_id>", file=sys.stderr); sys.exit(1)
        cmd_result(args[0], args[1])

    elif cmd == "cancel":
        if len(args) < 2:
            print("Usage: cancel <model> <request_id>", file=sys.stderr); sys.exit(1)
        cmd_cancel(args[0], args[1])

    elif cmd == "stream":
        if len(args) < 2:
            print("Usage: stream <model> <json>", file=sys.stderr); sys.exit(1)
        cmd_stream(args[0], parse_json(args[1]))

    elif cmd == "upload":
        if not args:
            print("Usage: upload <file_path>", file=sys.stderr); sys.exit(1)
        cmd_upload(args[0])

    elif cmd == "models":
        cmd_models(args[0] if args else None)

    elif cmd == "schema":
        if not args:
            print("Usage: schema <model>", file=sys.stderr); sys.exit(1)
        cmd_schema(args[0])

    # Legacy aliases
    elif cmd == "generate":
        if len(args) < 2:
            print("Usage: generate <model> <json>", file=sys.stderr); sys.exit(1)
        cmd_subscribe(args[0], parse_json(args[1]))

    elif cmd == "generate-queue":
        if len(args) < 2:
            print("Usage: generate-queue <model> <json>", file=sys.stderr); sys.exit(1)
        cmd_subscribe(args[0], parse_json(args[1]))

    elif cmd in ("help", "-h", "--help"):
        print(USAGE)

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print(USAGE)
        sys.exit(1)

if __name__ == "__main__":
    main()
