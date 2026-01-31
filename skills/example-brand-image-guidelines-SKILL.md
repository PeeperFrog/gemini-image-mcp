---
name: example-brand-image-guidelines
description: Example template for creating brand-specific image generation guidelines
---

# Example Brand Image Guidelines

**Purpose:** Template for creating brand-specific visual identity, aesthetic guidelines, and branding requirements for image generation.

**Use this skill when:** Generating images for [YOUR BRAND] content.

**Dependencies:** Use with **gemini-image-generation** skill for technical implementation.

**Note:** This is an EXAMPLE template. Copy and customize for your own brand.

---

## Brand Aesthetic

### Visual Identity

**Core Aesthetic:**
- [Your primary visual style - e.g., minimalist, bold, vintage, futuristic]
- [Background preferences - e.g., light, dark, gradient, textured]
- [Lighting style - e.g., dramatic, soft, natural, neon]
- [Imagery themes - e.g., nature, technology, human-centered]

**Color Palette:**
- **Primary**: [Color 1] (#HEXCODE), [Color 2] (#HEXCODE)
- **Secondary**: [Color 3] (#HEXCODE), [Color 4] (#HEXCODE)
- **Accents**: [Accent colors] (#HEXCODE)
- **Backgrounds**: [Background colors/styles]

**Typography Style:**
- **Primary font**: [Font name or style - e.g., Bold sans-serif, Modern geometric]
- **Secondary font**: [Font name or style]
- **Text treatment**: [Bold, italic, outlined, shadowed, etc.]

### Standard Prompt Template

```
[Main subject/concept] in [YOUR BRAND STYLE], [YOUR LIGHTING], [YOUR BACKGROUND], [YOUR QUALITY SPECIFICATIONS]
```

**Example:**
```
[Subject] in minimalist modern style, soft natural lighting, clean white background, professional photography, high resolution
```

### Prompt Guidelines

**DO:**
- Use consistent style keywords
- Specify your brand colors
- Include your lighting preferences
- Request your preferred composition style
- Maintain visual consistency across images

**DON'T:**
- Use conflicting style directions
- Forget brand color specifications
- Skip lighting/mood descriptors
- Use styles that conflict with brand identity

---

## Branding Requirements

### Logo/Watermark Placement

**Option 1: Include watermark on all images**

**Branding Format:**
- Text: "[YourBrand.com]" or your logo text
- Placement: [Location - e.g., bottom right, top left, centered bottom]
- Orientation: [Normal, rotated, angled]
- Style: [Font, size, color, effects]
- Appearance: [Small, subtle, prominent]

**Prompt Language for Branding:**
```
[Your watermark text] in [font style], positioned at [location], [size description], [color/styling details], [additional specifications]
```

**Example:**
```
Small text watermark "YourBrand.com" in modern sans-serif font, positioned in bottom right corner, white text with subtle drop shadow, unobtrusive but readable
```

**Option 2: Selective watermarking**

Define which image types require branding:
- Hero images (16:9): [YES/NO]
- Social media squares (1:1): [YES/NO]
- Social media stories (9:16): [YES/NO]
- Product images: [YES/NO]
- Marketing materials: [YES/NO]

---

## Content-Specific Guidelines

### [Content Type 1 - e.g., Blog Hero Images]

**Format:** 16:9, [NO/WITH] branding

**Style specifications:**
- [Specific style for this content type]
- [Composition preferences]
- [Color treatment]
- [Text overlays if any]

**Example prompt:**
```
[Your specific prompt template for this content type]
```

### [Content Type 2 - e.g., Social Media Posts]

**Format:** 1:1, [NO/WITH] branding

**Style specifications:**
- [Style for social content]
- [Visual hierarchy]
- [Text treatment]
- [Brand elements]

**Example prompt:**
```
[Your social media prompt template]
```

### [Content Type 3 - e.g., Marketing Materials]

**Format:** [Aspect ratio], [NO/WITH] branding

**Style specifications:**
- [Marketing visual style]
- [Emphasis areas]
- [Call-to-action visual elements]

**Example prompt:**
```
[Your marketing prompt template]
```

---

## Use Cases & Examples

### Product Photography Style

```
[Product name] (see reference image if available) on [your background style], [your lighting], [your photography style], professional product photography, [brand color accents]
```

### Concept Visualization

```
Abstract representation of [concept] in [your brand style], [your color palette], [composition style], modern and clean
```

### Data Visualization

```
[Graph/chart type] showing [data], [headline text style], [your brand colors for data], [background style], professional infographic aesthetic
```

### Social Media Graphics

```
[Content description], [your brand style], [text treatment], [brand colors], eye-catching composition for [platform]
```

---

## Integration with gemini-image-generation

When using **gemini-image-generation** skill for [YOUR BRAND] content:

1. **Apply brand aesthetic** to all prompts
2. **Add branding watermark** where specified
3. **Use brand colors** consistently
4. **Follow content-specific patterns** for each use case
5. **Use reference images** when available (get user approval first)

**Example workflow:**

```javascript
// Hero image - Apply brand style
gemini-custom:add_to_batch({
  prompt: "[Apply brand aesthetic + content-specific pattern]",
  aspect_ratio: "16:9",
  image_size: "large",
  quality: "pro",
  filename: "topic-hero-20260131-120000"
})

// Social square - Include branding if required
gemini-custom:add_to_batch({
  prompt: "[Apply brand aesthetic + branding watermark if required]",
  aspect_ratio: "1:1",
  image_size: "large",
  quality: "pro",
  filename: "topic-social-20260131-120001"
})

gemini-custom:run_batch()
```

---

## Quality Control Checklist

**Before generation:**
- [ ] Brand aesthetic applied
- [ ] Brand colors specified
- [ ] Branding watermark included (if required)
- [ ] Correct content-specific pattern used
- [ ] Reference images identified (if needed)
- [ ] User approval obtained for reference images

**After generation:**
- [ ] Visual style matches brand identity
- [ ] Colors are on-brand
- [ ] Watermark placed correctly (if included)
- [ ] Text legible and accurate
- [ ] Overall quality meets brand standards
- [ ] Image appropriate for intended use

---

## Customization Instructions

To adapt this template for your brand:

1. **Replace all [PLACEHOLDERS] with your actual:**
   - Brand name
   - Style descriptors
   - Color codes
   - Font specifications
   - Content types

2. **Define your visual identity:**
   - Choose 3-5 consistent style keywords
   - Specify exact color hex codes
   - Document lighting preferences
   - Define composition rules

3. **Create content-specific sections:**
   - Add sections for your actual content types
   - Write specific prompt templates
   - Include example outputs

4. **Document branding requirements:**
   - Decide watermark placement
   - Specify which content gets branded
   - Write exact branding prompt language

5. **Add real examples:**
   - Include actual prompts you've tested
   - Document successful outputs
   - Note what works and what doesn't

6. **Save as:**
   - `[your-brand-name]-image-guidelines/SKILL.md`
   - Reference alongside `gemini-image-generation` skill

---

## Related Skills

- **gemini-image-generation** - Technical implementation and tool usage
- [Your other brand-related skills]

---

## Example: Minimal Modern Brand

Here's a complete minimal example:

**Brand:** CleanTech (hypothetical)

**Visual Identity:**
- Minimalist modern style
- White/light gray backgrounds
- Soft natural lighting
- Blue (#0066CC) and green (#00CC66) accents

**Standard Prompt:**
```
[Subject] in minimalist modern style, soft natural lighting, clean white background, blue and green color accents, professional photography
```

**Branding:**
- Small "CleanTech.co" text in bottom right
- Blue color, simple sans-serif
- No watermark on hero images, yes on social

**Hero Image Example:**
```
Modern electric vehicle charging station in minimalist modern style, soft natural lighting, clean white background with blue and green accent lighting, professional photography, high resolution
```

**Social Square Example:**
```
Bold headline text "THE FUTURE IS ELECTRIC" in modern sans-serif, minimalist composition with blue and green gradient accent bars, clean white background. Small text "CleanTech.co" in bottom right corner, blue color.
```

---

**Remember:** This is a template. Customize everything for your actual brand identity!
