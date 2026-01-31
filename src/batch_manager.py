#!/usr/bin/env python3
"""
Batch image queue manager - v3.0
UPDATED: Multi-reference images support + config file
"""
import os
import json
from datetime import datetime

# Load config from same directory as this script
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.json")

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        cfg = json.load(f)
    cfg["images_dir"] = os.path.expanduser(cfg["images_dir"])
    cfg["queue_file"] = os.path.join(cfg["images_dir"], cfg.get("queue_filename", "batch_queue.json"))
    return cfg

CFG = load_config()
QUEUE_FILE = CFG["queue_file"]

def ensure_queue_exists():
    os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
    if not os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'w') as f:
            json.dump({"prompts": []}, f)

def add_to_queue(prompt, filename=None, aspect_ratio="16:9", image_size="large", description="", reference_images=None, quality="pro"):
    """Add an image request to the batch queue

    Args:
        prompt: Text description of image
        filename: Output filename (auto-generated if None)
        aspect_ratio: Aspect ratio (1:1, 16:9, etc.)
        image_size: Resolution - "small" (1K), "medium" (2K), "large" (2K), "xlarge" (4K)
        description: Optional description/note
        reference_images: Optional list of file paths to reference images (max 14, pro only)
        quality: Quality tier - "pro" or "fast"
    """
    ensure_queue_exists()

    with open(QUEUE_FILE, 'r') as f:
        queue = json.load(f)

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"batch_image_{timestamp}.png"

    entry = {
        "prompt": prompt,
        "filename": filename,
        "aspect_ratio": aspect_ratio,
        "image_size": image_size,
        "quality": quality,
        "description": description,
        "added_at": datetime.now().isoformat()
    }
    if reference_images:
        entry["reference_images"] = reference_images
    queue["prompts"].append(entry)

    with open(QUEUE_FILE, 'w') as f:
        json.dump(queue, f, indent=2)

    return {
        "success": True,
        "queue_size": len(queue["prompts"]),
        "added": {
            "filename": filename,
            "resolution": image_size,
            "aspect_ratio": aspect_ratio,
            "reference_images": len(reference_images) if reference_images else 0,
            "description": description or prompt[:50]
        }
    }

def remove_from_queue(identifier):
    ensure_queue_exists()

    with open(QUEUE_FILE, 'r') as f:
        queue = json.load(f)

    original_count = len(queue["prompts"])

    try:
        index = int(identifier)
        if index < 0 or index >= original_count:
            return {"success": False, "error": f"Index {index} out of range (0-{original_count-1})"}
        removed = queue["prompts"].pop(index)
        removed_files = [removed["filename"]]
    except ValueError:
        filename = str(identifier)
        removed_files = []
        for i in reversed(range(len(queue["prompts"]))):
            if queue["prompts"][i]["filename"] == filename:
                removed = queue["prompts"].pop(i)
                removed_files.append(removed["filename"])
        if not removed_files:
            return {"success": False, "error": f"Filename '{filename}' not found in queue"}

    with open(QUEUE_FILE, 'w') as f:
        json.dump(queue, f, indent=2)

    return {
        "success": True,
        "removed_count": len(removed_files),
        "removed_files": removed_files,
        "queue_size": len(queue["prompts"]),
        "message": f"Removed {len(removed_files)} item(s) from queue"
    }

def view_queue():
    ensure_queue_exists()
    with open(QUEUE_FILE, 'r') as f:
        queue = json.load(f)
    return {"total": len(queue["prompts"]), "prompts": queue["prompts"]}

def clear_queue():
    ensure_queue_exists()
    with open(QUEUE_FILE, 'w') as f:
        json.dump({"prompts": []}, f)
    return {"success": True, "message": "Queue cleared"}

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Add to queue:    python3 batch_manager.py add 'prompt' [filename] [aspect_ratio] [image_size] ['[\"ref1.png\",\"ref2.png\"]']")
        print("  Remove by index: python3 batch_manager.py remove 0")
        print("  Remove by name:  python3 batch_manager.py remove 'filename.png'")
        print("  View queue:      python3 batch_manager.py view")
        print("  Clear queue:     python3 batch_manager.py clear")
        print("\nImage sizes: small (1K), medium (2K), large (2K default), xlarge (4K)")
        sys.exit(1)

    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) < 3:
            print("Error: Prompt required")
            sys.exit(1)
        prompt = sys.argv[2]
        filename = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else None
        aspect_ratio = sys.argv[4] if len(sys.argv) > 4 else "16:9"
        image_size = sys.argv[5] if len(sys.argv) > 5 else "large"
        # Reference images come as JSON-encoded list
        reference_images = None
        if len(sys.argv) > 6:
            try:
                reference_images = json.loads(sys.argv[6])
                if isinstance(reference_images, str):
                    reference_images = [reference_images]
            except json.JSONDecodeError:
                reference_images = [sys.argv[6]]
        # Quality tier
        quality = sys.argv[7] if len(sys.argv) > 7 else "pro"
        result = add_to_queue(prompt, filename, aspect_ratio, image_size, "", reference_images, quality)
        print(json.dumps(result, indent=2))

    elif command == "remove":
        if len(sys.argv) < 3:
            print("Error: Index or filename required")
            sys.exit(1)
        result = remove_from_queue(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif command == "view":
        result = view_queue()
        print(json.dumps(result, indent=2))

    elif command == "clear":
        result = clear_queue()
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
