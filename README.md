# Gemini Image MCP Server

An MCP (Model Context Protocol) server that provides AI image generation tools using Google's Gemini models. Supports single and batch image generation, multiple reference images, WebP conversion, and direct WordPress upload.

## Features

- **Two quality tiers** -- Pro (Gemini 3 Pro Image Preview, up to 4K) and Fast (Gemini 2.5 Flash Image, 1K max)
- **Reference images** -- up to 14 reference images per generation (Pro mode)
- **Batch generation** -- queue multiple images, review, then generate in one run
- **WebP conversion** -- convert PNG/JPG to WebP for web optimization
- **WordPress upload** -- upload WebP images directly to WordPress media library
- **Configurable** -- all paths, limits, and delays via `config.json`

## Tools Provided

| Tool | Description |
|------|-------------|
| `generate_image` | Generate a single image immediately |
| `add_to_batch` | Queue an image for batch generation |
| `remove_from_batch` | Remove from queue by index or filename |
| `view_batch_queue` | View queued images |
| `run_batch` | Generate all queued images |
| `convert_to_webp` | Convert generated images to WebP |
| `upload_to_wordpress` | Upload WebP images to WordPress |
| `get_generated_webp_images` | Get base64 data of WebP images |

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/YOUR_USERNAME/gemini-image-mcp.git
cd gemini-image-mcp

# Create config from example
cp config.json.example config.json
cp .env.example .env
```

### 2. Set your API key

Edit `.env`:

```
GEMINI_API_KEY=your-gemini-api-key-here
```

### 3. Edit config.json

Update paths in `config.json` to match your system. The `images_dir` path supports `~` expansion.

### 4. Install dependencies

```bash
pip install requests
```

WebP conversion also requires [uv](https://github.com/astral-sh/uv) and Pillow (handled automatically by uv).

### 5. Add to your MCP client

#### Claude Code (`~/.claude/settings.json`)

```json
{
  "mcpServers": {
    "gemini-custom": {
      "command": "python3",
      "args": ["/path/to/gemini-image-mcp/src/gemini_image_server.py"],
      "env": {
        "GEMINI_API_KEY": "your-key-here"
      }
    }
  }
}
```

#### Or run as a systemd service

See `docs/systemd-service.example` for a template.

## Project Structure

```
gemini-image-mcp/
├── src/
│   ├── gemini_image_server.py   # Main MCP server
│   ├── batch_manager.py         # Batch queue management
│   └── batch_generate.py        # Batch image generation
├── scripts/
│   └── webp-convert.py          # PNG/JPG to WebP converter
├── skills/
│   ├── gemini-image-generation-SKILL.md        # Claude skill file
│   └── example-brand-image-guidelines-SKILL.md # Brand template skill
├── docs/
│   └── systemd-service.example  # Systemd service template
├── config.json.example          # Configuration template
├── .env.example                 # Environment variable template
├── .gitignore
├── LICENSE
└── README.md
```

## Configuration

`config.json` fields:

| Field | Description | Default |
|-------|-------------|---------|
| `images_dir` | Base output directory for images | `~/Pictures/ai-generated-images` |
| `batch_subdir` | Subdirectory for batch output | `batch` |
| `queue_filename` | Batch queue file name | `batch_queue.json` |
| `batch_manager_script` | Path to batch manager | `./src/batch_manager.py` |
| `batch_generate_script` | Path to batch generator | `./src/batch_generate.py` |
| `webp_convert_script` | Path to WebP converter | `./scripts/webp-convert.py` |
| `max_reference_images` | Max reference images per generation | `14` |
| `api_delay_seconds` | Delay between batch API calls | `3` |

## Claude Skills

The `skills/` directory contains Claude Code skill files:

- **gemini-image-generation-SKILL.md** -- comprehensive guide for using the image generation tools, prompt engineering, workflows, and troubleshooting
- **example-brand-image-guidelines-SKILL.md** -- template for creating brand-specific image generation guidelines

Copy these to your Claude Code skills directory to give Claude detailed knowledge of how to use this server.

## Quality Tiers

| | Pro | Fast |
|---|---|---|
| Model | Gemini 3 Pro Image Preview | Gemini 2.5 Flash Image |
| Max resolution | 4K (4096px) | 1K (1024px) |
| Reference images | Up to 14 | Not supported |
| Text rendering | Good | Poor with complex text |
| Best for | Production content | Quick tests, iterations |

## License

MIT
