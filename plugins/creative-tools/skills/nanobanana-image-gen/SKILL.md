---
name: nanobanana-image-gen
description: Generate and edit images using Google's Nanobanana model via Replicate API. Use this skill when users request image generation from text descriptions, image-to-image transformations, style transfers, or any creative image editing tasks. Supports multiple input images, custom aspect ratios, and various output formats.
---

# Nanobanana Image Generation

## Overview

This skill enables image generation and editing using Google's Nanobanana model (google/nano-banana) through the Replicate API. Generate images from text prompts, transform existing images, apply style transfers, or create variations with precise control over aspect ratios and output formats.

## Core Capabilities

### 1. Text-to-Image Generation

Generate images from natural language descriptions.

**Example requests:**
- "Generate an image of a sunset over snow-capped mountains"
- "Create a portrait of a cat wearing a bow tie in a Victorian setting"
- "Make me an abstract image with blue and purple swirls"

**Process:**
1. Extract the text description from the user's request
2. Determine appropriate aspect ratio (default: 1:1 for general images, 16:9 for landscapes, 2:3 for portraits)
3. Execute `scripts/generate_image.py` with the prompt
4. Save the generated image to the user's working directory

### 2. Image-to-Image Transformation

Transform or edit existing images using text prompts.

**Example requests:**
- "Make this photo look like a watercolor painting"
- "Transform this image to black and white with high contrast"
- "Turn this photo into an anime-style illustration"
- "Edit this image to make it look like it was taken at golden hour"

**Process:**
1. Ensure the input image is accessible (local file or URL)
2. If local file, it must be uploaded to a publicly accessible URL first (use appropriate upload method)
3. Extract the transformation instructions from the user's request
4. Execute `scripts/generate_image.py` with both prompt and image input
5. Save the transformed image to the user's working directory

### 3. Multi-Image Input

Use multiple images as references or inputs for generation.

**Example requests:**
- "Combine the style of this painting with the subject of this photo"
- "Generate an image that merges elements from these three images"
- "Create a variation that incorporates aspects from both of these images"

**Process:**
1. Ensure all input images are accessible as URLs
2. Provide all image URLs in the `image_input` array parameter
3. Execute `scripts/generate_image.py` with the prompt and multiple image inputs

### 4. Aspect Ratio Control

Generate images with specific dimensions for different use cases.

**Available aspect ratios:**
- `1:1` - Square (social media posts, profile pictures)
- `16:9` - Widescreen (presentations, YouTube thumbnails)
- `9:16` - Vertical (mobile stories, TikTok)
- `4:3` - Standard (traditional photos)
- `3:4` - Portrait orientation
- `21:9` - Ultra-wide (cinematic)
- `4:5` - Instagram portrait
- `5:4` - Medium format
- `2:3` - Portrait photos
- `3:2` - Landscape photos
- `match_input_image` - Match input image dimensions (default when image input provided)

**Example requests:**
- "Generate a 16:9 banner image of a forest"
- "Create a square profile picture of a logo"
- "Make a vertical 9:16 image for Instagram stories"

## Using the Generation Script

The `scripts/generate_image.py` script handles all Replicate API interactions with proper error handling and polling.

**Basic usage:**
```bash
python scripts/generate_image.py "a sunset over mountains" --output sunset.jpg
```

**With image input:**
```bash
python scripts/generate_image.py "make this look like a watercolor" \
  --image-input https://example.com/photo.jpg \
  --output watercolor.jpg
```

**With multiple images:**
```bash
python scripts/generate_image.py "combine these styles" \
  --image-input https://example.com/img1.jpg \
  --image-input https://example.com/img2.jpg \
  --output combined.jpg
```

**Custom aspect ratio:**
```bash
python scripts/generate_image.py "a wide landscape" \
  --aspect-ratio 21:9 \
  --output landscape.jpg
```

**PNG output:**
```bash
python scripts/generate_image.py "transparent logo concept" \
  --output-format png \
  --output logo.png
```

## Important Implementation Details

### Image URL Requirements

Replicate requires images to be uploaded to their file hosting service. The script automatically handles this:

1. If the input is a URL from any domain, the script downloads and re-uploads to Replicate
2. If the input is a local file path, the script reads and uploads to Replicate
3. This ensures compatibility with the Nanobanana model's requirements

### Error Handling

The script includes comprehensive error handling:
- API authentication failures (missing or invalid `REPLICATE_API_KEY`)
- Network timeouts and connection errors
- Invalid image URLs or file paths
- Model execution failures with helpful error messages

### Output Files

Generated images are saved to the specified output path. If no output path is specified, the script saves to `./generated_image_{timestamp}.jpg` in the current directory.

### Performance Considerations

- Image generation typically takes 5-15 seconds depending on complexity
- The script uses polling with appropriate intervals (configurable)
- Progress indicators show generation status
- Timeout is set to 5 minutes by default to handle complex generations

## API Reference

For detailed information about the Nanobanana model parameters, capabilities, and best practices, refer to `references/nanobanana-api.md`.

## Environment Setup

Ensure the `REPLICATE_API_KEY` environment variable is set:

```bash
export REPLICATE_API_KEY="your-api-key-here"
```

Get an API key from https://replicate.com/account/api-tokens

## Common Pitfalls

1. **Image URLs not publicly accessible**: Ensure input images are either publicly accessible URLs or properly uploaded to Replicate's file hosting
2. **Missing API key**: The script will fail if `REPLICATE_API_KEY` is not set in the environment
3. **Aspect ratio mismatch**: When using `match_input_image`, ensure at least one input image is provided
4. **File path issues**: Always use absolute paths or properly resolve relative paths for local image files

## Best Practices

1. **Descriptive prompts**: More detailed prompts generally produce better results (e.g., "a serene mountain lake at sunset with pine trees in the foreground" vs "a lake")
2. **Appropriate aspect ratios**: Choose aspect ratios that match the intended use case
3. **Image quality**: When using image inputs, higher quality source images generally produce better results
4. **Iterative refinement**: Generate multiple variations by adjusting prompts to find the best result
5. **Output format**: Use PNG for images requiring transparency, JPG for photographs and general images (smaller file size)
