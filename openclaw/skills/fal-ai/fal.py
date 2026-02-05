#!/usr/bin/env python3
"""
fal.ai CLI for Clawdbot
Generate images and content using fal.ai models
"""

import os
import sys
import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any

# API endpoints
FAL_BASE_URL = "https://fal.ai/api"
FAL_QUEUE_URL = "https://queue.fal.run"
FAL_DIRECT_URL = "https://fal.run"

def get_api_key() -> str:
    """Get FAL_KEY from environment"""
    key = os.environ.get("FAL_KEY")
    if not key:
        print("Error: FAL_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    return key

def api_request(url: str, method: str = "GET", data: Optional[Dict] = None, auth: bool = True) -> Dict:
    """Make API request to fal.ai"""
    headers = {"Content-Type": "application/json"}
    if auth:
        headers["Authorization"] = f"Key {get_api_key()}"
    
    req_data = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"API Error [{e.code}]: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Request Error: {e.reason}", file=sys.stderr)
        sys.exit(1)

def cmd_models(page: Optional[int] = None, total: Optional[int] = None):
    """List available models"""
    url = f"{FAL_BASE_URL}/models"
    params = []
    if page is not None:
        params.append(f"page={page}")
    if total is not None:
        params.append(f"total={total}")
    if params:
        url += "?" + "&".join(params)
    
    result = api_request(url, auth=False)
    print(json.dumps(result, indent=2))

def cmd_search(keywords: str):
    """Search for models"""
    url = f"{FAL_BASE_URL}/models?keywords={urllib.parse.quote(keywords)}"
    result = api_request(url, auth=False)
    print(json.dumps(result, indent=2))

def cmd_schema(model_id: str):
    """Get model schema"""
    url = f"{FAL_BASE_URL}/openapi/queue/openapi.json?endpoint_id={urllib.parse.quote(model_id)}"
    result = api_request(url, auth=False)
    print(json.dumps(result, indent=2))

def cmd_generate(model: str, parameters: str, queue: bool = False):
    """Generate content using a model"""
    try:
        params = json.loads(parameters)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON parameters: {e}", file=sys.stderr)
        sys.exit(1)
    
    if queue:
        url = f"{FAL_QUEUE_URL}/{model}"
    else:
        url = f"{FAL_DIRECT_URL}/{model}"
    
    result = api_request(url, method="POST", data=params)
    print(json.dumps(result, indent=2))

def cmd_status(status_url: str):
    """Check queue status"""
    result = api_request(status_url)
    print(json.dumps(result, indent=2))

def cmd_result(response_url: str):
    """Get queued result"""
    result = api_request(response_url)
    print(json.dumps(result, indent=2))

def cmd_cancel(cancel_url: str):
    """Cancel queued request"""
    result = api_request(cancel_url, method="PUT")
    print(json.dumps(result, indent=2))

def cmd_help():
    """Show help"""
    print("""
fal.ai CLI - Generate images and content

Commands:
  models [page] [total]     List available models
  search <keywords>         Search for models
  schema <model_id>         Get model schema
  generate <model> <json>   Generate content (direct mode)
  generate-queue <model> <json>  Generate content (queue mode)
  status <url>              Check queue status
  result <url>              Get queued result
  cancel <url>              Cancel queued request

Examples:
  # Generate image with Flux Schnell (fast)
  python3 fal.py generate "fal-ai/flux/schnell" '{"prompt": "a robot"}'

  # Search for image models
  python3 fal.py search "image generation"

  # Queue a slow job
  python3 fal.py generate-queue "fal-ai/flux-pro" '{"prompt": "detailed art"}'
""")

def main():
    import urllib.parse
    
    if len(sys.argv) < 2:
        cmd_help()
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == "models":
        page = int(sys.argv[2]) if len(sys.argv) > 2 else None
        total = int(sys.argv[3]) if len(sys.argv) > 3 else None
        cmd_models(page, total)
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: search <keywords>", file=sys.stderr)
            sys.exit(1)
        cmd_search(sys.argv[2])
    elif cmd == "schema":
        if len(sys.argv) < 3:
            print("Usage: schema <model_id>", file=sys.stderr)
            sys.exit(1)
        cmd_schema(sys.argv[2])
    elif cmd == "generate":
        if len(sys.argv) < 4:
            print("Usage: generate <model> <json_parameters>", file=sys.stderr)
            sys.exit(1)
        cmd_generate(sys.argv[2], sys.argv[3], queue=False)
    elif cmd == "generate-queue":
        if len(sys.argv) < 4:
            print("Usage: generate-queue <model> <json_parameters>", file=sys.stderr)
            sys.exit(1)
        cmd_generate(sys.argv[2], sys.argv[3], queue=True)
    elif cmd == "status":
        if len(sys.argv) < 3:
            print("Usage: status <status_url>", file=sys.stderr)
            sys.exit(1)
        cmd_status(sys.argv[2])
    elif cmd == "result":
        if len(sys.argv) < 3:
            print("Usage: result <response_url>", file=sys.stderr)
            sys.exit(1)
        cmd_result(sys.argv[2])
    elif cmd == "cancel":
        if len(sys.argv) < 3:
            print("Usage: cancel <cancel_url>", file=sys.stderr)
            sys.exit(1)
        cmd_cancel(sys.argv[2])
    elif cmd == "help":
        cmd_help()
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        cmd_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
