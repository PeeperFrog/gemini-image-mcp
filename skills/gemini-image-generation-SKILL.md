---
name: gemini-image-generation
description: Generate high-quality AI images using Gemini Imagen for any purpose
---

# Gemini Image Generation

**Purpose:** Generate high-quality AI images using Gemini Imagen 3 and Gemini 2.5 Flash Image for any use case - articles, social media, marketing, presentations, or creative projects.

**Use this skill when:** You need to generate AI images programmatically.

---

## Overview

### Available MCP Tools

- **gemini-custom:generate_image** - Generate single image immediately
- **gemini-custom:add_to_batch** - Queue image for batch generation
- **gemini-custom:view_batch_queue** - View queued images
- **gemini-custom:remove_from_batch** - Remove image from queue by index or filename
- **gemini-custom:run_batch** - Execute batch generation
- **gemini-custom:convert_to_webp** - Convert generated images to WebP format
- **gemini-custom:get_generated_webp_images** - Get base64 data of WebP images for upload

### Image Resolution Options

- **small**: 1K (1024px) - Fast generation, smaller file size
- **medium**: 2K (2048px) - Balanced quality and size
- **large**: 2K (2048px) - Default, best balance for most uses
- **xlarge**: 4K (4096px) - Maximum quality, large files, use sparingly

### Quality Options (Model Selection)

- **pro** (default): Gemini 3 Pro Image Preview
  - Full quality generation up to 4K resolution
  - Supports multiple reference images (default: up to 14, configurable)
  - Best for production content requiring reference images
  - **Handles complex text rendering well**
  - Default resolution: large (2K)
  - Available resolutions: small (1K), medium (2K), large (2K), xlarge (4K)
  
- **fast**: Gemini 2.5 Flash Image
  - Faster generation, cheaper/free tier
  - **Maximum resolution: 1024x1024 pixels** (1K equivalent across all aspect ratios)
  - **NO reference image support** (silently ignored)
  - **Best for minimal text or text-free images** - poor text rendering with large amounts of text
  - Default resolution: small (1K) - cannot be increased
  - Best for: quick tests, abstract concepts without references, cost-effective iterations

**When to use each:**
- Use `quality: "pro"` when:
  - Using reference images (required)
  - Need resolution above 1K (1024px)
  - Creating final production images
  - Need highest quality output
  - **Image contains significant text** (headlines, data labels, multiple text elements)
  
- Use `quality: "fast"` when:
  - Testing prompts quickly
  - Generating abstract/generic images without references
  - Resolution up to 1K (1024px) is sufficient
  - Want faster/cheaper generation
  - Rapid iteration on concepts
  - **Minimal or no text in image** (text-free visualizations, simple one-word labels)

**Important:** If you specify `image_size: "medium"`, `"large"`, or `"xlarge"` with `quality: "fast"`, the output will still be limited to 1024x1024 equivalent. For higher resolutions or complex text rendering, use `quality: "pro"`.

---

## Generation Methods

### Method 1: Immediate Generation (Single Image)

**Use when:** Need one image quickly, real-time feedback required

```javascript
gemini-custom:generate_image({
  prompt: "Your detailed prompt here",
  aspect_ratio: "16:9",
  image_size: "large",
  quality: "pro"  // or "fast"
})
```

**Parameters:**
- `prompt` (required): Detailed image description
- `aspect_ratio`: "1:1", "16:9", "9:16", "4:3", "3:4" (default: "1:1")
- `image_size`: "small", "medium", "large", "xlarge" (default: "large")
  - **Note:** With `quality: "fast"`, maximum output is 1024x1024 pixels regardless of size setting
- `quality`: "pro" or "fast" (default: "pro")
- `reference_image`: File path or JSON array of file paths (optional, pro quality only)

**Output:**
- Image saved to configured images directory (default: `~/Pictures/ai-generated-images/`)
- Filename: Auto-generated with timestamp
- Location configurable via MCP server `config.json`

**Pros:**
- Immediate feedback
- Simple workflow
- Fast quality option for quick tests

**Cons:**
- Cannot generate multiple images at once
- No filename control

### Method 2: Batch Generation (Multiple Images)

**Use when:** Need multiple images, want custom filenames, can wait for batch processing

**Step 1: Add images to queue**
```javascript
gemini-custom:add_to_batch({
  prompt: "Your detailed prompt here",
  aspect_ratio: "16:9",
  image_size: "large",
  quality: "pro",  // Optional, defaults to "pro"
  filename: "custom-name-20260131-120000",  // Optional but recommended
  description: "Hero image"  // Optional note for your reference
})
```

**Step 2: View queue (optional)**
```javascript
gemini-custom:view_batch_queue()
```

**Step 3: Execute batch**
```javascript
gemini-custom:run_batch()
```

**Output:**
- Images saved to configured batch directory (default: `~/Pictures/ai-generated-images/batch/`)
- Filenames: Your custom names or auto-generated
- Locations configurable via MCP server `config.json`

**Pros:**
- Generate multiple images efficiently
- Custom filenames with timestamps
- Review queue before generating
- Cost-effective for multiple images

**Cons:**
- Must wait for full batch
- No immediate feedback per image

### Method 3: Using Reference Images

**Use when:** Need to base generation on existing product images, photos, or visual references

**CRITICAL: Reference images require `quality: "pro"`**

Reference images are ONLY supported with Gemini 3 Pro Image Preview. If you use `quality: "fast"`, reference images will be silently ignored.

**Workflow:**

1. **Locate reference images** in your accessible directories (e.g., `/home/yourusername/reference-images/`)

2. **CRITICAL: Get user approval before using references**
   - Present found references to user
   - Example: "I found [filename.png] that matches [product/topic]. Would you like me to use this as a reference?"
   - Wait for explicit approval
   - Do NOT proceed with reference images without user confirmation
   - Exception: If user says "use any available references" or similar blanket approval

3. **Generate with approved references:**

**Single reference image:**
```javascript
gemini-custom:generate_image({
  prompt: "Product name (see reference image) in modern setting, professional photography, well-lit",
  reference_image: "/path/to/reference-image.png",
  aspect_ratio: "16:9",
  image_size: "large",
  quality: "pro"  // REQUIRED for reference images
})
```

**Multiple reference images:**
Pass as JSON array string:
```javascript
gemini-custom:add_to_batch({
  prompt: "Product A (see reference image 1) next to Product B (see reference image 2) in comparison shot",
  reference_image: "[\"/path/to/reference1.png\", \"/path/to/reference2.png\"]",
  quality: "pro",  // REQUIRED for reference images
  filename: "product-comparison-20260131-120000"
})
```

**Prompt style with references:**
- Cite references: "Product name (see reference image) doing action"
- Don't describe details: Let reference provide visual information
- Focus on: Scene, setting, action, lighting, composition
- Skip: Physical descriptions, colors, materials (reference provides these)

**Example:**
```
❌ Without reference: "Humanoid robot with gray metallic finish, 1.9m tall, articulated hands..."
✅ With reference: "Robot (see reference image) performing assembly task in factory"
```

**Pros:**
- Much more accurate product representation
- Reduces hallucination of product details
- Better for technical/product-focused images
- Supports multiple reference images (default: up to 14, configurable)

**Cons:**
- Requires finding good reference images
- May constrain creative interpretation
- Only works with pro quality

---

## Prompt Engineering

### General Best Practices

**Effective prompts include:**
- Clear subject/concept description
- Visual style (photorealistic, illustrated, abstract, artistic)
- Lighting conditions (well-lit, dramatic, natural, studio)
- Setting/environment description
- Composition guidance (cinematic, centered, dynamic, balanced)
- Color palette or mood (optional)

**Standard Prompt Template:**
```
[Main subject/concept] in [style], [lighting description], [setting], [quality/composition specifications]
```

### Example Prompts

**Product Photography:**
```
Modern smartphone on minimalist white surface, professional product photography, soft diffused lighting, clean composition, photorealistic, high resolution
```

**Concept Visualization:**
```
Abstract representation of cloud computing with interconnected nodes and data streams, modern digital art style, vibrant blue and purple gradient, balanced composition
```

**Technical/Scientific:**
```
Detailed cross-section visualization of lithium-ion battery, technical diagram style with labels, clean professional aesthetic, educational clarity, white background
```

**Marketing/Hero:**
```
Luxury sports car on mountain road at sunset, dramatic golden hour lighting, dynamic low angle shot, photorealistic, cinematic composition, depth of field
```

**Social Media:**
```
Bold text design with motivational quote, modern typography, vibrant gradient background, high contrast, eye-catching composition for Instagram post
```

### Prompt Guidelines

**DO:**
- Be specific about subject and style
- Specify lighting conditions
- Include desired composition style
- Mention quality level (photorealistic, high resolution, etc.)
- Use reference images when available

**DON'T:**
- Be vague or generic
- Assume Gemini knows your brand colors/style
- Rely solely on text for complex products (use references)
- Forget to specify aspect ratio for intended use

### Text in Images

**Text rendering limitations:**
- Gemini may duplicate words randomly (e.g., "AI, AI" instead of "AI")
- May misspell or jumble text
- More common with short words, punctuation, special characters

**Mitigation strategies:**
1. Keep text simple and clear
2. Avoid complex punctuation
3. Add "Verify all text matches the prompt exactly" at end of prompts
4. Review generated images for text accuracy
5. Regenerate if text is garbled
6. For critical text: Consider creating text-free base image and adding text in post-processing

---

## Reference Images

### When to Use Reference Images

**✅ Use reference images when:**
- Generating images of specific named products
- Technical visualizations requiring accuracy
- When you have reference materials available
- Product comparisons or before/after scenarios
- Need to match existing visual style

**❌ Don't use reference images for:**
- Abstract concepts or generic visualizations
- When no suitable reference exists
- Quick tests (use fast quality instead)

### Finding and Managing Reference Images

1. **Check accessible directories** for existing references
2. **Download or capture** reference images if needed
3. **Save to organized location** for reuse
4. **Present to user** for approval before using (if applicable)
5. **Cite in prompts** - e.g., "Product (see reference image) in setting"

### Reference Image Best Practices

1. Use high-quality reference images
2. Match reference to the version/model being discussed
3. Combine reference with text descriptions of scene/setting
4. Use reference for accuracy, not to copy style
5. Can use multiple references (default limit: 14, configurable in server config)
6. Always use `quality: "pro"` when using references

---

## Workflows

### Workflow 1: Quick Single Image

```javascript
gemini-custom:generate_image({
  prompt: "Mountain landscape at sunset, dramatic lighting, photorealistic",
  aspect_ratio: "16:9",
  image_size: "large"
})
```

### Workflow 2: Batch Generation

```javascript
// Queue multiple images
gemini-custom:add_to_batch({
  prompt: "Product shot angle 1",
  filename: "product-front-20260131-120000"
})

gemini-custom:add_to_batch({
  prompt: "Product shot angle 2",
  filename: "product-side-20260131-120001"
})

gemini-custom:add_to_batch({
  prompt: "Product shot angle 3",
  filename: "product-top-20260131-120002"
})

// Generate all at once
gemini-custom:run_batch()
```

### Workflow 3: Batch Management

```javascript
// View current queue
gemini-custom:view_batch_queue()

// Remove specific item (by index or filename)
gemini-custom:remove_from_batch({
  identifier: "2"  // or "product-side-20260131-120001"
})

// Execute remaining batch
gemini-custom:run_batch()
```

### Workflow 4: Using Reference Images

```javascript
// Step 1: Check directory for reference images
Filesystem:list_directory({ path: "/path/to/references" })

// Step 2: MANDATORY - Present to user and get approval
// "Found product-specs.png. Would you like me to use this as a reference?"
// WAIT for user response before proceeding

// Step 3: Generate with reference (ONLY after user approval)
gemini-custom:generate_image({
  prompt: "Product (see reference image) in modern setting, professional photography",
  reference_image: "/path/to/product-specs.png",
  aspect_ratio: "16:9",
  quality: "pro"  // Required for references
})
```

**Important:** Never use reference images without explicit user approval, unless the user has given blanket permission (e.g., "use any available references").

### Workflow 5: Convert to WebP

```javascript
// After generating images, convert to WebP for web use
gemini-custom:convert_to_webp({
  quality: 85  // Optional, default is 85
})
```

---

## Aspect Ratio Selection

**16:9 (Landscape):**
- Website featured images
- Hero images for articles
- Video thumbnails
- Wide social media posts

**1:1 (Square):**
- Instagram posts
- Social media thumbnails
- Profile images
- Most social platforms

**9:16 (Portrait):**
- Instagram/TikTok stories
- Mobile-optimized graphics
- Vertical video thumbnails

**4:3 (Standard):**
- Traditional photography
- Presentation slides
- Some print materials

**3:4 (Portrait Standard):**
- Portrait photography
- Print materials
- Some mobile displays

---

## File Management

### Output Locations

Output directories are configurable via the MCP server's `config.json` file:

**Default locations:**
- **Immediate generation**: `~/Pictures/ai-generated-images/`
- **Batch generation**: `~/Pictures/ai-generated-images/batch/`
- **WebP conversions**: Same directory as source images with `.webp` extension

**Configuration parameters** (in `config.json`):
- `images_dir`: Base directory for all generated images
- `batch_subdir`: Subdirectory name for batch generations
- `queue_filename`: Batch queue file name
- `max_reference_images`: Maximum number of reference images (default: 14)
- `api_delay_seconds`: Delay between API calls in batch (default: 3)

Check your MCP server configuration if images are saving to unexpected locations.

### Naming Conventions

**Batch Generation (Custom Names with Timestamps):**
- Format: `[descriptive-name]-[YYYYMMDD-HHMMSS]`
- Examples:
  - `product-hero-20260131-120000`
  - `social-square-20260131-120001`
  - `comparison-chart-20260131-120002`

**Best Practice:**
Always include timestamp in filename when using batch generation to avoid overwriting previous versions and maintain version history.

### Output Locations

Output directories are configurable via the MCP server's `config.json` file.

**Default locations:**
- **Immediate generation**: `~/Pictures/ai-generated-images/`
- **Batch generation**: `~/Pictures/ai-generated-images/batch/`
- **WebP conversions**: Same directory as source images with `.webp` extension

Check your MCP server configuration if images are saving to unexpected locations.

---

## WebP Conversion

Convert generated PNG images to WebP format for optimized web use:

```javascript
gemini-custom:convert_to_webp({
  quality: 85,  // Optional: 0-100, default 85
  force: false  // Optional: reconvert even if .webp exists
})
```

**Features:**
- Scans image directory recursively
- Converts PNG/JPG to WebP
- Skips existing .webp files (unless force=true)
- Typically achieves 80-90% file size reduction
- Maintains visual quality

---

## Quality Control Checklist

**Before Generation:**
- [ ] Prompt is clear and detailed
- [ ] Correct aspect ratio for intended use
- [ ] Appropriate image size selected
- [ ] Quality setting correct (pro for references, fast for tests)
- [ ] Reference images ready (if using)
- [ ] Custom filename included (for batch)

**After Generation:**
- [ ] Image matches prompt intent
- [ ] Text is accurate (no duplications, typos)
- [ ] Quality is sufficient for intended use
- [ ] Aspect ratio correct
- [ ] If using references: Product appearance accurate

---

## Known Issues

### Quality Parameter Limitations

**Fast Quality (`quality: "fast"`) - Gemini 2.5 Flash Image:**
- **Maximum resolution: 1024x1024 pixels** (1K equivalent)
  - This applies regardless of `image_size` parameter
  - Cannot generate 2K or 4K images
  - All aspect ratios limited to 1024px on longest dimension
- **Poor text rendering with large amounts of text**
  - Use minimal text only (simple labels, single words)
  - For headlines, paragraphs, or multiple text elements, use `quality: "pro"`
  - More prone to text duplication and spelling errors
- Does NOT support reference images - they will be silently ignored
- Optimized for speed over quality
- Best for rapid iteration and testing, not final production

**Always use `quality: "pro"` when:**
- Using any reference images
- Need resolution above 1K (1024px)
- **Image contains significant text** (headlines, data visualizations, infographics, multiple labels)
- Creating production content for articles, marketing, or professional use
- Need consistent high-quality output

### Gemini Text Rendering

Gemini's text rendering can be unpredictable:
- May duplicate words randomly
- May misspell or jumble text
- More common with short words, punctuation, special characters

**Workflow requirement:**
After image generation, always review for:
- Text accuracy (matches prompt exactly)
- Spelling errors or duplications
- Text legibility at intended viewing size

---

## Advanced Usage

### Brand-Specific Workflows

For brand-specific aesthetics, colors, and branding requirements, create a separate skill that extends these generic guidelines.

**Example structure:**
1. Create `your-brand-image-guidelines` skill
2. Define your brand colors, aesthetic, logo placement
3. Reference this skill alongside `gemini-image-generation`
4. Apply brand guidelines to prompts

**See example:** `example-brand-image-guidelines` skill (included) shows how to extend this generic skill with brand-specific requirements.

### Content-Driven Patterns

**Pattern A: Data Visualization**

For charts and graphs with overlaid text:
1. Headline (20-30% top): Key insight in plain language
2. Graph (50-60% center): Visual data with clear labels
3. Supporting data (10-15%): Secondary context
4. Background: Clean or atmospheric

**Pattern B: Text-Forward Design**

For attention-grabbing graphics:
- Dominant headline (60%+ of space)
- High contrast text
- Simple background
- Bold typography

**Pattern C: Product Focus**

For featuring products:
- Use reference images when possible
- Simple prompt: "Product (see reference) in [setting]"
- Focus on composition and lighting
- Let reference handle product details

---

## Integration with Other Tools

### WordPress/CMS Upload

After generating and converting to WebP:

```javascript
// Get base64 data for upload
gemini-custom:get_generated_webp_images({
  directory: "batch",
  limit: 10
})

// Use with WordPress REST API or other CMS
```

### Automation Workflows

Combine with other MCP servers for complete automation:
1. Research topics (Perplexity)
2. Generate content (writing tools)
3. Create images (this skill)
4. Publish (WordPress/CMS tools)

---

## Troubleshooting

**Images not generating:**
- Check MCP server is running
- Verify API credentials configured
- Check network connectivity
- Review error messages in output

**Reference images not working:**
- Ensure using `quality: "pro"`
- Verify file paths are correct
- Check reference images exist and are accessible
- Confirm file format is supported (PNG, JPG)

**Text rendering issues:**
- Keep text simple
- Add "Verify all text matches the prompt exactly"
- Review and regenerate if needed
- Consider text-free images with text added in post

**Poor image quality:**
- Use `quality: "pro"` instead of "fast"
- Increase `image_size` to "xlarge" (pro quality only)
- Improve prompt detail and specificity
- Use reference images when appropriate

**Image resolution lower than expected:**
- Check if using `quality: "fast"` - limited to 1024x1024 pixels maximum
- For higher resolutions (2K, 4K), use `quality: "pro"`
- Verify `image_size` parameter is set correctly

---

## Related Skills

Extend this skill with brand-specific skills for:
- Brand aesthetics and visual identity
- Logo and watermark placement
- Color palette specifications
- Typography guidelines
- Content-specific patterns

**Example:** See `example-brand-image-guidelines` skill (included) for how to create brand-specific extensions.

---

## Version History

- v1.0: Initial release
  - Immediate and batch generation workflows
  - Reference image support (multiple images, configurable limit)
  - Two quality tiers:
    - Pro: Gemini 3 Pro Image Preview (up to 4K, reference images, good text rendering)
    - Fast: Gemini 2.5 Flash Image (max 1K, no references, minimal text only)
  - WebP conversion support
  - Configurable paths and limits via `config.json`
