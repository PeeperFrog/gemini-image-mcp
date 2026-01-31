#!/usr/bin/env python3
"""
GEMINI IMAGE GENERATION MCP SERVER - v3.1
Multiple reference images (up to 14), external config file, and quality tiers

CHANGES FROM v3.0:
1. Added quality parameter: "pro" (default, Gemini 3 Pro) or "fast" (Gemini 2.0 Flash)
2. Fast mode: cheaper/free, quicker generation — no reference image support
3. Reference images silently ignored when quality="fast"
"""

import sys
import json
import os
import base64
import requests
import subprocess
from datetime import datetime

# --- Configuration ---
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.json")

def load_config():
    """Load configuration from config.json next to this script"""
    with open(CONFIG_PATH, 'r') as f:
        cfg = json.load(f)
    # Expand ~ in all path values
    for key in ("images_dir", "batch_manager_script", "batch_generate_script", "webp_convert_script"):
        if key in cfg:
            cfg[key] = os.path.expanduser(cfg[key])
    # Derived paths
    cfg["batch_dir"] = os.path.join(cfg["images_dir"], cfg.get("batch_subdir", "batch"))
    cfg["queue_file"] = os.path.join(cfg["images_dir"], cfg.get("queue_filename", "batch_queue.json"))
    return cfg

CFG = load_config()
MAX_REF_IMAGES = CFG.get("max_reference_images", 14)

# Model endpoints by quality tier
MODELS = {
    "pro": "gemini-3-pro-image-preview",
    "fast": "gemini-2.5-flash-image",
}

# --- MCP protocol ---
def send_message(message):
    json_str = json.dumps(message)
    sys.stdout.write(json_str + '\n')
    sys.stdout.flush()

def read_message():
    line = sys.stdin.readline()
    if not line:
        return None
    return json.loads(line)

# --- Helpers ---
def get_mime_type(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    mime_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    return mime_map.get(ext, "image/png")

def _normalize_reference_images(reference_images=None, reference_image=None):
    """Accept either a list or a single path, return validated list (max MAX_REF_IMAGES)."""
    paths = []
    if reference_images:
        if isinstance(reference_images, str):
            paths = [reference_images]
        else:
            paths = list(reference_images)
    elif reference_image:
        paths = [reference_image]
    if len(paths) > MAX_REF_IMAGES:
        raise Exception(f"Too many reference images ({len(paths)}). Maximum is {MAX_REF_IMAGES}.")
    return paths

def _encode_reference_images(paths):
    """Return list of inlineData parts for the given image paths."""
    parts = []
    for p in paths:
        ref_path = os.path.expanduser(p)
        if not os.path.exists(ref_path):
            raise Exception(f"Reference image not found: {ref_path}")
        with open(ref_path, 'rb') as f:
            img_b64 = base64.b64encode(f.read()).decode('utf-8')
        parts.append({
            "inlineData": {
                "mimeType": get_mime_type(ref_path),
                "data": img_b64
            }
        })
    return parts

# --- Core functions ---
def generate_image(prompt, aspect_ratio="1:1", image_size="large", reference_image=None, reference_images=None, quality="pro"):
    """Generate image using Gemini API with resolution control, multiple reference images, and quality tiers"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise Exception("GEMINI_API_KEY not set")

    quality = quality if quality in MODELS else "pro"
    model = MODELS[quality]

    size_map = {"small": "1K", "medium": "2K", "large": "2K", "xlarge": "4K"}
    # Fast mode defaults to small if not explicitly set
    if quality == "fast" and image_size == "large":
        image_size = "small"
    gemini_size = size_map.get(image_size, "2K")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    # Reference images only supported on pro model
    ref_paths = []
    if quality == "pro":
        ref_paths = _normalize_reference_images(reference_images, reference_image)
    parts = _encode_reference_images(ref_paths)
    parts.append({"text": prompt})

    # Build generationConfig — fast model doesn't support imageSize
    image_config = {"aspectRatio": aspect_ratio}
    if quality == "pro":
        image_config["imageSize"] = gemini_size

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": image_config
        }
    }

    response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")

    data = response.json()
    # Response may contain text and image parts; find the image part
    image_data = None
    for part in data['candidates'][0]['content']['parts']:
        if 'inlineData' in part:
            image_data = part['inlineData']['data']
            break
    if not image_data:
        raise Exception("No image data in API response")

    output_dir = CFG["images_dir"]
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/gemini_image_{timestamp}.png"

    with open(filename, 'wb') as f:
        f.write(base64.b64decode(image_data))

    return {
        "success": True,
        "image_path": filename,
        "resolution": gemini_size,
        "aspect_ratio": aspect_ratio,
        "quality": quality,
        "model": model,
        "reference_images_used": len(ref_paths),
        "message": f"Image generated successfully ({quality} mode): {filename}"
    }

def add_to_batch(prompt, filename=None, aspect_ratio="16:9", image_size="large", description="", reference_image=None, reference_images=None, quality="pro"):
    """Add image to batch queue with multiple reference image support and quality tier"""
    quality = quality if quality in MODELS else "pro"
    # Reference images only on pro
    ref_paths = _normalize_reference_images(reference_images, reference_image) if quality == "pro" else []
    # Fast mode defaults to small
    if quality == "fast" and image_size == "large":
        image_size = "small"

    cmd = ["python3", CFG["batch_manager_script"], "add", prompt]
    if filename:
        cmd.append(filename)
    else:
        cmd.append("")
    cmd.append(aspect_ratio or "16:9")
    cmd.append(image_size or "large")
    # Pass reference images as JSON-encoded list
    if ref_paths:
        cmd.append(json.dumps(ref_paths))
    else:
        cmd.append("[]")
    # Pass quality tier
    cmd.append(quality)

    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

def remove_from_batch(identifier):
    cmd = ["python3", CFG["batch_manager_script"], "remove", str(identifier)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

def view_batch_queue():
    cmd = ["python3", CFG["batch_manager_script"], "view"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

def run_batch():
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return {"success": False, "error": "GEMINI_API_KEY not set"}

    env = os.environ.copy()
    env['GEMINI_API_KEY'] = api_key

    cmd = ["python3", CFG["batch_generate_script"], CFG["queue_file"], CFG["batch_dir"]]
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)

    return {
        "success": result.returncode == 0,
        "output": result.stdout,
        "error": result.stderr if result.returncode != 0 else None
    }

def convert_to_webp(quality=85, force=False):
    cmd = ["uv", "run", CFG["webp_convert_script"], CFG["images_dir"], "--batch", "--recursive", "--quality", str(quality)]
    if force:
        cmd.append("--force")
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "success": result.returncode == 0,
        "output": result.stdout,
        "error": result.stderr if result.returncode != 0 else None
    }

def upload_to_wordpress(wp_url, wp_user, wp_password, directory="batch", limit=10):
    from pathlib import Path
    batch_dir = os.path.join(CFG["images_dir"], directory)
    uploaded = []
    failed = []

    image_files = sorted(Path(batch_dir).glob("*.webp"), key=os.path.getmtime, reverse=True)[:limit]

    for img_path in image_files:
        try:
            filename = img_path.name
            with open(img_path, 'rb') as f:
                files = {'file': (filename, f, 'image/webp')}
                response = requests.post(
                    f"{wp_url}/wp-json/wp/v2/media",
                    auth=(wp_user, wp_password),
                    files=files
                )
                if response.status_code == 201:
                    media_data = response.json()
                    uploaded.append({
                        "filename": filename,
                        "media_id": media_data['id'],
                        "url": media_data['source_url'],
                        "title": media_data['title']['rendered']
                    })
                else:
                    failed.append({"filename": filename, "error": f"HTTP {response.status_code}: {response.text}"})
        except Exception as e:
            failed.append({"filename": img_path.name, "error": str(e)})

    return {"success": len(failed) == 0, "uploaded": uploaded, "failed": failed, "total": len(uploaded) + len(failed)}

def get_generated_webp_images(directory="batch", limit=10):
    from pathlib import Path
    batch_dir = os.path.join(CFG["images_dir"], directory)
    images = []

    image_files = sorted(Path(batch_dir).glob("*.webp"), key=os.path.getmtime, reverse=True)[:limit]
    for img_path in image_files:
        with open(img_path, 'rb') as f:
            images.append({
                "filename": img_path.name,
                "base64": base64.b64encode(f.read()).decode('utf-8'),
                "path": str(img_path),
                "size": os.path.getsize(img_path)
            })

    return {"success": True, "images": images, "count": len(images)}

# --- MCP handlers ---
def handle_initialize(request_id):
    send_message({
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "gemini-image-generator", "version": "3.1.0"}
        }
    })

def handle_tools_list(request_id):
    send_message({
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "tools": [
                {
                    "name": "get_generated_webp_images",
                    "description": "Get base64 data of recently generated WebP images for uploading",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "directory": {"type": "string", "description": "Directory to scan (default: batch)", "default": "batch"},
                            "limit": {"type": "integer", "description": "Maximum number of images to return", "default": 10}
                        },
                        "required": []
                    }
                },
                {
                    "name": "generate_image",
                    "description": "Generate a single image immediately using Gemini. Use quality='pro' (default) for high-quality with reference image support, or quality='fast' for cheaper/quicker social media images (no reference images).",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "Text description of the image to generate"},
                            "aspect_ratio": {"type": "string", "description": "Aspect ratio (1:1, 16:9, 9:16, 4:3, 3:4)", "default": "1:1"},
                            "image_size": {"type": "string", "description": "Image resolution: 'small' (1K/1024px), 'medium' (2K/2048px), 'large' (2K/2048px default for pro, small default for fast), 'xlarge' (4K/4096px)", "enum": ["small", "medium", "large", "xlarge"], "default": "large"},
                            "quality": {"type": "string", "description": "Quality tier: 'pro' (Gemini 3 Pro, high quality, reference images supported) or 'fast' (Gemini 2.0 Flash, cheaper/quicker, no reference images)", "enum": ["pro", "fast"], "default": "pro"},
                            "reference_image": {"type": "string", "description": "Optional single reference image file path (pro mode only)"},
                            "reference_images": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": f"Optional list of reference image file paths, max {MAX_REF_IMAGES} (pro mode only)",
                                "maxItems": MAX_REF_IMAGES
                            }
                        },
                        "required": ["prompt"]
                    }
                },
                {
                    "name": "add_to_batch",
                    "description": "Add an image to the batch queue for later generation with resolution control and quality tier",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "Text description of the image to generate"},
                            "filename": {"type": "string", "description": "Optional filename for the image"},
                            "aspect_ratio": {"type": "string", "description": "Aspect ratio (1:1, 16:9, 9:16, 4:3, 3:4)", "default": "16:9"},
                            "image_size": {"type": "string", "description": "Image resolution: 'small' (1K), 'medium' (2K), 'large' (2K default for pro, small for fast), 'xlarge' (4K)", "enum": ["small", "medium", "large", "xlarge"], "default": "large"},
                            "quality": {"type": "string", "description": "Quality tier: 'pro' (default) or 'fast' (cheaper, no reference images)", "enum": ["pro", "fast"], "default": "pro"},
                            "description": {"type": "string", "description": "Optional description/note for this image"},
                            "reference_image": {"type": "string", "description": "Optional single reference image file path (pro mode only)"},
                            "reference_images": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": f"Optional list of reference image file paths, max {MAX_REF_IMAGES} (pro mode only)",
                                "maxItems": MAX_REF_IMAGES
                            }
                        },
                        "required": ["prompt"]
                    }
                },
                {
                    "name": "remove_from_batch",
                    "description": "Remove an image from the batch queue by index (0, 1, 2...) or filename",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "identifier": {"type": "string", "description": "Either an integer index (0 for first item, 1 for second, etc.) or a filename string"}
                        },
                        "required": ["identifier"]
                    }
                },
                {
                    "name": "view_batch_queue",
                    "description": "View all images currently queued for batch generation",
                    "inputSchema": {"type": "object", "properties": {}, "required": []}
                },
                {
                    "name": "run_batch",
                    "description": "Execute batch generation for all queued images",
                    "inputSchema": {"type": "object", "properties": {}, "required": []}
                },
                {
                    "name": "convert_to_webp",
                    "description": "Convert generated images to WebP format for WordPress optimization. Scans images directory recursively and converts PNG/JPG to WebP.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "quality": {"type": "integer", "description": "WebP quality (0-100). Default 85", "default": 85, "minimum": 0, "maximum": 100},
                            "force": {"type": "boolean", "description": "Force reconversion even if .webp files already exist", "default": False}
                        },
                        "required": []
                    }
                },
                {
                    "name": "upload_to_wordpress",
                    "description": "Upload WebP images directly to WordPress media library",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "wp_url": {"type": "string", "description": "WordPress site URL (e.g., https://example.com)"},
                            "wp_user": {"type": "string", "description": "WordPress username"},
                            "wp_password": {"type": "string", "description": "WordPress application password"},
                            "directory": {"type": "string", "description": "Directory containing images (default: batch)", "default": "batch"},
                            "limit": {"type": "integer", "description": "Maximum number of images to upload", "default": 10}
                        },
                        "required": ["wp_url", "wp_user", "wp_password"]
                    }
                }
            ]
        }
    })

def handle_tool_call(request_id, tool_name, arguments):
    try:
        if tool_name == "generate_image":
            result = generate_image(
                arguments.get("prompt"),
                arguments.get("aspect_ratio", "1:1"),
                arguments.get("image_size", "large"),
                arguments.get("reference_image"),
                arguments.get("reference_images"),
                arguments.get("quality", "pro")
            )
        elif tool_name == "add_to_batch":
            result = add_to_batch(
                arguments.get("prompt"),
                arguments.get("filename"),
                arguments.get("aspect_ratio", "16:9"),
                arguments.get("image_size", "large"),
                arguments.get("description", ""),
                arguments.get("reference_image"),
                arguments.get("reference_images"),
                arguments.get("quality", "pro")
            )
        elif tool_name == "remove_from_batch":
            result = remove_from_batch(arguments.get("identifier"))
        elif tool_name == "view_batch_queue":
            result = view_batch_queue()
        elif tool_name == "run_batch":
            result = run_batch()
        elif tool_name == "convert_to_webp":
            result = convert_to_webp(arguments.get("quality", 85), arguments.get("force", False))
        elif tool_name == "get_generated_webp_images":
            result = get_generated_webp_images(arguments.get("directory", "batch"), arguments.get("limit", 10))
        elif tool_name == "upload_to_wordpress":
            result = upload_to_wordpress(
                arguments.get("wp_url"),
                arguments.get("wp_user"),
                arguments.get("wp_password"),
                arguments.get("directory", "batch"),
                arguments.get("limit", 10)
            )
        else:
            raise Exception(f"Unknown tool: {tool_name}")

        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"content": [{"type": "text", "text": json.dumps(result)}]}
        }
    except Exception as e:
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32000, "message": str(e)}
        }
    send_message(response)

def main():
    sys.stderr.write("Gemini Image MCP Server v3.1 - Pro/Fast Quality Tiers\n")
    sys.stderr.flush()

    while True:
        try:
            message = read_message()
            if message is None:
                break

            method = message.get("method")
            request_id = message.get("id")

            if method == "initialize":
                handle_initialize(request_id)
            elif method == "tools/list":
                handle_tools_list(request_id)
            elif method == "tools/call":
                params = message.get("params", {})
                handle_tool_call(request_id, params.get("name"), params.get("arguments", {}))
            elif method == "notifications/initialized":
                pass

        except Exception as e:
            sys.stderr.write(f"Error: {str(e)}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    main()
