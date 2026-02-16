#!/usr/bin/env python3
"""
fal.ai CLI v2 — powered by official fal-client + Platform APIs
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

# ── Platform API (https://api.fal.ai/v1/) ───────────────────────────────────

PLATFORM_BASE = "https://api.fal.ai/v1"

def platform_get(path: str, params: Optional[dict] = None, auth: bool = True) -> dict:
    """GET request to fal Platform API."""
    url = f"{PLATFORM_BASE}{path}"
    if params:
        qs = urllib.parse.urlencode(params, doseq=True)
        url += f"?{qs}"
    headers = {"Content-Type": "application/json"}
    if auth:
        headers["Authorization"] = f"Key {get_key()}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"API Error [{e.code}]: {body}", file=sys.stderr)
        sys.exit(1)

def platform_post(path: str, data: dict, auth: bool = True) -> dict:
    """POST request to fal Platform API."""
    url = f"{PLATFORM_BASE}{path}"
    headers = {"Content-Type": "application/json"}
    if auth:
        headers["Authorization"] = f"Key {get_key()}"
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"API Error [{e.code}]: {body}", file=sys.stderr)
        sys.exit(1)

# ── Core Generation Commands ─────────────────────────────────────────────────

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

def cmd_job_status(model: str, request_id: str):
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

# ── Quick Shortcuts ──────────────────────────────────────────────────────────

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

    images = result.get("images", [])
    if save and images:
        download_file(images[0]["url"], save)

    print(json.dumps(result, indent=2))

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

# ── Platform API Commands ────────────────────────────────────────────────────

def cmd_models(query: Optional[str] = None, category: Optional[str] = None,
               limit: int = 20, raw: bool = False):
    """Search/list models via Platform API."""
    params = {"limit": limit, "status": "active"}
    if query:
        params["q"] = query
    if category:
        params["category"] = category

    result = platform_get("/models", params)

    if raw:
        print(json.dumps(result, indent=2))
        return

    models = result.get("models", [])
    if not models:
        print("No models found.")
        return

    # Pretty table output
    print(f"{'Model':55s} {'Category':20s} {'Name'}")
    print("-" * 110)
    for m in models:
        eid = m.get("endpoint_id", "?")
        meta = m.get("metadata", {})
        name = meta.get("display_name", "")
        cat = meta.get("category", "")
        tags = meta.get("tags", [])
        pinned = "📌 " if meta.get("pinned") else ""
        highlighted = "⭐ " if meta.get("highlighted") else ""
        print(f"{eid:55s} {cat:20s} {highlighted}{pinned}{name}")

    if result.get("has_more"):
        print(f"\n... more results available (use --limit N or --raw for pagination)")

def cmd_pricing(*endpoint_ids: str, raw: bool = False):
    """Get live pricing for models."""
    if not endpoint_ids:
        print("Usage: pricing <model1> [model2] ...", file=sys.stderr)
        sys.exit(1)

    result = platform_get("/models/pricing", {"endpoint_id": list(endpoint_ids)})

    if raw:
        print(json.dumps(result, indent=2))
        return

    prices = result.get("prices", [])
    if not prices:
        print("No pricing found.")
        return

    print(f"{'Model':55s} {'Price':>10s}  {'Unit':20s} {'Currency'}")
    print("-" * 100)
    for p in prices:
        eid = p.get("endpoint_id", "?")
        price = p.get("unit_price", 0)
        unit = p.get("unit", "?")
        currency = p.get("currency", "USD")
        print(f"{eid:55s} ${price:>8.5f}  per {unit:16s} {currency}")

def cmd_estimate(estimate_type: str, endpoints_json: str):
    """Estimate costs before running.

    Examples:
      estimate unit_price '{"fal-ai/nano-banana-pro": 10}'
      estimate historical '{"fal-ai/flux/dev": 100}'
    """
    endpoints_raw = parse_json(endpoints_json)

    if estimate_type in ("unit_price", "unit"):
        data = {
            "estimate_type": "unit_price",
            "endpoints": {k: {"unit_quantity": v} for k, v in endpoints_raw.items()}
        }
    elif estimate_type in ("historical", "historical_api_price"):
        data = {
            "estimate_type": "historical_api_price",
            "endpoints": {k: {"call_quantity": int(v)} for k, v in endpoints_raw.items()}
        }
    else:
        print(f"Unknown estimate type: {estimate_type}. Use 'unit_price' or 'historical'", file=sys.stderr)
        sys.exit(1)

    result = platform_post("/models/pricing/estimate", data)
    total = result.get("total_cost", 0)
    currency = result.get("currency", "USD")
    print(f"Estimated cost: ${total:.4f} {currency}")
    if result.get("endpoints"):
        print(json.dumps(result, indent=2))

def cmd_usage(endpoint_id: Optional[str] = None, start: Optional[str] = None,
              end: Optional[str] = None, limit: int = 20, raw: bool = False):
    """View usage records."""
    params = {"limit": limit}
    if endpoint_id:
        params["endpoint_id"] = endpoint_id
    if start:
        params["start"] = start
    if end:
        params["end"] = end

    result = platform_get("/models/usage", params)

    if raw:
        print(json.dumps(result, indent=2))
        return

    series = result.get("time_series", [])
    has_data = False
    for bucket in series:
        results = bucket.get("results", [])
        if results:
            has_data = True
            print(f"\n📅 {bucket['bucket']}")
            for r in results:
                eid = r.get("endpoint_id", "?")
                qty = r.get("unit_quantity", 0)
                unit = r.get("unit", "")
                cost = r.get("cost", 0)
                print(f"  {eid:50s} {qty:>8.2f} {unit:15s} ${cost:.4f}")

    if not has_data:
        print("No usage data in this period.")

def cmd_analytics(endpoint_id: str, start: Optional[str] = None,
                  end: Optional[str] = None, raw: bool = False):
    """View analytics (request counts, latency, error rates)."""
    params = {
        "endpoint_id": endpoint_id,
        "expand": ["request_count", "success_count", "error_count",
                    "p50_duration", "p90_duration"],
    }
    if start:
        params["start"] = start
    if end:
        params["end"] = end

    result = platform_get("/models/analytics", params)

    if raw:
        print(json.dumps(result, indent=2))
        return

    series = result.get("time_series", [])
    has_data = False
    for bucket in series:
        results = bucket.get("results", [])
        if results:
            has_data = True
            print(f"\n📅 {bucket['bucket']}")
            for r in results:
                reqs = r.get("request_count", 0)
                ok = r.get("success_count", 0)
                errs = r.get("error_count", 0)
                p50 = r.get("p50_duration", 0)
                p90 = r.get("p90_duration", 0)
                print(f"  requests: {reqs}  success: {ok}  errors: {errs}  p50: {p50:.1f}s  p90: {p90:.1f}s")

    if not has_data:
        print("No analytics data in this period.")

def cmd_schema(model: str):
    """Get model input/output schema via Platform API."""
    result = platform_get("/models", {"endpoint_id": model, "expand": "openapi-3.0"})
    models = result.get("models", [])
    if models and models[0].get("openapi"):
        print(json.dumps(models[0]["openapi"], indent=2))
    elif models:
        print(json.dumps(models[0], indent=2))
    else:
        print(f"Model not found: {model}", file=sys.stderr)
        sys.exit(1)

def cmd_info(model: str):
    """Get model metadata (name, category, tags, status)."""
    result = platform_get("/models", {"endpoint_id": model})
    models = result.get("models", [])
    if not models:
        print(f"Model not found: {model}", file=sys.stderr)
        sys.exit(1)

    m = models[0]
    meta = m.get("metadata", {})

    # Also fetch pricing
    try:
        pricing = platform_get("/models/pricing", {"endpoint_id": model})
        prices = pricing.get("prices", [])
    except:
        prices = []

    print(f"Model:    {m.get('endpoint_id', '?')}")
    print(f"Name:     {meta.get('display_name', '?')}")
    print(f"Category: {meta.get('category', '?')}")
    print(f"Status:   {meta.get('status', '?')}")
    if meta.get("description"):
        print(f"Desc:     {meta['description']}")
    if meta.get("tags"):
        print(f"Tags:     {', '.join(meta['tags'])}")
    if meta.get("license_type"):
        print(f"License:  {meta['license_type']}")
    if meta.get("thumbnail_url"):
        print(f"Thumb:    {meta['thumbnail_url']}")
    if prices:
        p = prices[0]
        print(f"Price:    ${p['unit_price']:.5f} per {p['unit']} ({p['currency']})")

def cmd_latest(category: Optional[str] = None, limit: int = 10):
    """Show newest/trending models."""
    params = {"limit": limit, "status": "active"}
    if category:
        params["category"] = category

    result = platform_get("/models", params)
    models = result.get("models", [])

    if not models:
        print("No models found.")
        return

    # Sort by highlighted/pinned first, then by date
    print(f"{'Model':55s} {'Category':20s} {'Name'}")
    print("-" * 110)
    for m in models:
        eid = m.get("endpoint_id", "?")
        meta = m.get("metadata", {})
        name = meta.get("display_name", "")
        cat = meta.get("category", "")
        pinned = "📌 " if meta.get("pinned") else ""
        highlighted = "⭐ " if meta.get("highlighted") else ""
        new = "🆕 " if meta.get("is_new") else ""
        print(f"{eid:55s} {cat:20s} {new}{highlighted}{pinned}{name}")

# ── CLI Dispatcher ───────────────────────────────────────────────────────────

USAGE = """
fal.ai CLI v2 (official fal-client + Platform APIs)

QUICK COMMANDS:
  image <prompt> [--model M] [--size S] [--save path] [--extra '{}']
  video <prompt> [--model M] [--image URL] [--save path] [--extra '{}']

GENERATION:
  subscribe <model> <json>       Run with auto-queue + polling (recommended)
  run <model> <json>             Run directly (fast models only)
  submit <model> <json>          Submit to queue, get request_id
  status <model> <request_id>    Check job status
  result <model> <request_id>    Get completed result
  cancel <model> <request_id>    Cancel a job
  stream <model> <json>          Stream results (SSE models)
  upload <file_path>             Upload file, get fal URL

DISCOVERY:
  models [query] [--category C] [--limit N] [--raw]
      Search/list models. Categories: text-to-image, image-to-video,
      text-to-video, image-to-image, text-to-speech, speech-to-text, etc.
  latest [--category C] [--limit N]
      Show newest/trending models
  info <model>                   Model details + live pricing
  schema <model>                 Full OpenAPI schema

PRICING & USAGE:
  pricing <model1> [model2] ...  Live pricing for models
  estimate unit_price '{"model": qty}'     Estimate cost by units
  estimate historical '{"model": calls}'   Estimate cost by API calls
  usage [--endpoint M] [--start DATE] [--end DATE]   Your usage records
  analytics <model> [--start DATE] [--end DATE]      Performance metrics

EXAMPLES:
  python3 fal.py image "vibrant Miami sunset over Brickell"
  python3 fal.py image "logo" --model fal-ai/flux-pro/v1.1 --save logo.png
  python3 fal.py models "video" --category text-to-video
  python3 fal.py latest --category text-to-image --limit 5
  python3 fal.py info fal-ai/nano-banana-pro
  python3 fal.py pricing fal-ai/nano-banana-pro fal-ai/flux/dev
  python3 fal.py estimate unit_price '{"fal-ai/nano-banana-pro": 10}'
  python3 fal.py usage --start 2026-02-01
  python3 fal.py analytics fal-ai/nano-banana-pro --start 2026-02-01
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
        elif args[i].startswith("--"):
            # Flag without value (e.g. --raw)
            key = args[i][2:]
            opts[key] = True
            i += 1
        else:
            i += 1
    return opts

def main():
    if len(sys.argv) < 2:
        print(USAGE)
        return

    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    # ── Quick shortcuts ──
    if cmd == "image":
        if not args:
            print("Usage: image <prompt> [--model M] [--size S] [--save path]", file=sys.stderr); sys.exit(1)
        prompt = args[0]
        opts = parse_extras(args[1:])
        extra = parse_json(opts["extra"]) if "extra" in opts else None
        cmd_image(prompt, model=opts.get("model", "fal-ai/nano-banana-pro"),
                  size=opts.get("size", "landscape_4_3"), save=opts.get("save"), extra=extra)

    elif cmd == "video":
        if not args:
            print("Usage: video <prompt> [--model M] [--image URL] [--save path]", file=sys.stderr); sys.exit(1)
        prompt = args[0]
        opts = parse_extras(args[1:])
        extra = parse_json(opts["extra"]) if "extra" in opts else None
        cmd_video(prompt, model=opts.get("model", "fal-ai/minimax-video/video-01-live"),
                  image_url=opts.get("image"), save=opts.get("save"), extra=extra)

    # ── Generation ──
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
        cmd_job_status(args[0], args[1])

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

    # ── Discovery ──
    elif cmd == "models":
        opts = parse_extras(args)
        # First non-flag arg is the query
        query = args[0] if args and not args[0].startswith("--") else opts.get("q")
        cmd_models(query=query, category=opts.get("category"),
                   limit=int(opts.get("limit", 20)), raw=bool(opts.get("raw")))

    elif cmd == "latest":
        opts = parse_extras(args)
        cmd_latest(category=opts.get("category"), limit=int(opts.get("limit", 10)))

    elif cmd == "info":
        if not args:
            print("Usage: info <model>", file=sys.stderr); sys.exit(1)
        cmd_info(args[0])

    elif cmd == "schema":
        if not args:
            print("Usage: schema <model>", file=sys.stderr); sys.exit(1)
        cmd_schema(args[0])

    # ── Pricing & Usage ──
    elif cmd == "pricing":
        if not args:
            print("Usage: pricing <model1> [model2] ...", file=sys.stderr); sys.exit(1)
        raw = "--raw" in args
        endpoint_ids = [a for a in args if not a.startswith("--")]
        cmd_pricing(*endpoint_ids, raw=raw)

    elif cmd == "estimate":
        if len(args) < 2:
            print("Usage: estimate unit_price '{\"model\": qty}'", file=sys.stderr); sys.exit(1)
        cmd_estimate(args[0], args[1])

    elif cmd == "usage":
        opts = parse_extras(args)
        cmd_usage(endpoint_id=opts.get("endpoint"), start=opts.get("start"),
                  end=opts.get("end"), limit=int(opts.get("limit", 20)),
                  raw=bool(opts.get("raw")))

    elif cmd == "analytics":
        if not args:
            print("Usage: analytics <model> [--start DATE] [--end DATE]", file=sys.stderr); sys.exit(1)
        model = args[0]
        opts = parse_extras(args[1:])
        cmd_analytics(model, start=opts.get("start"), end=opts.get("end"),
                      raw=bool(opts.get("raw")))

    # ── Legacy aliases ──
    elif cmd in ("generate", "generate-queue"):
        if len(args) < 2:
            print("Usage: generate <model> <json>", file=sys.stderr); sys.exit(1)
        cmd_subscribe(args[0], parse_json(args[1]))

    elif cmd == "search":
        # Legacy alias for models
        query = args[0] if args else None
        cmd_models(query=query)

    elif cmd in ("help", "-h", "--help"):
        print(USAGE)

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print(USAGE)
        sys.exit(1)

if __name__ == "__main__":
    main()
