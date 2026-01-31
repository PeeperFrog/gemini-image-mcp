#!/usr/bin/env python3
"""
Batch image generation using Gemini API - v3.1
UPDATED: Multi-reference images support + config file + quality tiers
"""
import os
import json
import time
import base64
import requests
import subprocess

# Load config from same directory as this script
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.json")

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        cfg = json.load(f)
    for key in ("images_dir", "batch_manager_script"):
        if key in cfg:
            cfg[key] = os.path.expanduser(cfg[key])
    return cfg

CFG = load_config()

def get_mime_type(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif"}
    return mime_map.get(ext, "image/png")

def remove_from_queue(filename):
    cmd = ["python3", CFG["batch_manager_script"], "remove", filename]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  Removed from queue: {filename}")
    else:
        print(f"  Warning: Could not remove from queue: {filename}")

def encode_reference_images(ref_list):
    """Encode a list of reference image paths into inlineData parts."""
    parts = []
    for ref_path_raw in ref_list:
        ref_path = os.path.expanduser(ref_path_raw)
        if not os.path.exists(ref_path):
            raise Exception(f"Reference image not found: {ref_path}")
        with open(ref_path, 'rb') as rf:
            img_b64 = base64.b64encode(rf.read()).decode('utf-8')
        parts.append({"inlineData": {"mimeType": get_mime_type(ref_path), "data": img_b64}})
    return parts

def generate_images_batch(prompts_file, output_dir):
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        return

    with open(prompts_file, 'r') as f:
        data = json.load(f)

    prompts = data.get('prompts', [])
    if not prompts:
        print("No prompts found in file")
        return

    print(f"Generating {len(prompts)} images...")

    models = {
        "pro": "gemini-3-pro-image-preview",
        "fast": "gemini-2.5-flash-image",
    }

    size_map = {"small": "1K", "medium": "2K", "large": "2K", "xlarge": "4K"}
    delay = CFG.get("api_delay_seconds", 3)

    results = []

    for i, prompt_data in enumerate(prompts, 1):
        prompt = prompt_data.get('prompt')
        filename = prompt_data.get('filename', f'image_{i}.png')
        queue_filename = filename
        if not filename.endswith('.png'):
            filename = f"{filename}.png"
        aspect_ratio = prompt_data.get('aspect_ratio', '1:1')
        image_size = prompt_data.get('image_size', 'large')
        quality = prompt_data.get('quality', 'pro')
        if quality not in models:
            quality = 'pro'
        model = models[quality]
        # Reference images only for pro model
        reference_images = []
        if quality == "pro":
            reference_images = prompt_data.get('reference_images', [])
            if not reference_images:
                single = prompt_data.get('reference_image')
                if single:
                    reference_images = [single]

        gemini_size = size_map.get(image_size, '2K')

        print(f"\n[{i}/{len(prompts)}] Generating: {filename} [{quality}]")
        print(f"Prompt: {prompt[:80]}...")
        print(f"Model: {model} | Resolution: {gemini_size} | Aspect Ratio: {aspect_ratio}")
        if reference_images:
            print(f"Reference images: {len(reference_images)}")

        try:
            parts = encode_reference_images(reference_images)
            parts.append({"text": prompt})

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

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

            output_path = os.path.join(output_dir, filename)
            with open(output_path, 'wb') as f:
                f.write(base64.b64decode(image_data))

            result = {
                "filename": filename,
                "status": "success",
                "path": output_path,
                "resolution": gemini_size,
                "aspect_ratio": aspect_ratio,
                "reference_images_used": len(reference_images)
            }
            print(f"Saved to: {output_path}")

            remove_from_queue(queue_filename)

        except Exception as e:
            result = {
                "filename": filename,
                "status": "error",
                "error": str(e)
            }
            print(f"Error: {str(e)}")

        results.append(result)

        if i < len(prompts):
            print(f"Waiting {delay} seconds...")
            time.sleep(delay)

    results_file = os.path.join(output_dir, 'batch_results.json')
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Batch complete!")
    print(f"Total: {len(prompts)} images")
    print(f"Success: {sum(1 for r in results if r['status'] == 'success')}")
    print(f"Failed: {sum(1 for r in results if r['status'] == 'error')}")
    print(f"Results saved to: {results_file}")
    print(f"{'='*60}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 batch_generate.py <prompts.json> [output_dir]")
        sys.exit(1)

    prompts_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(CFG["images_dir"], CFG.get("batch_subdir", "batch"))

    os.makedirs(output_dir, exist_ok=True)

    generate_images_batch(prompts_file, output_dir)
