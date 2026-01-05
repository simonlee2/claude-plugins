# creative-tools

AI-powered creative tools plugin for Claude Code featuring image generation and manipulation using Google's Nanobanana model.

## Features

### Skill: nanobanana-image-gen

Automatically activates when you request image generation or manipulation tasks.

**Capabilities:**

#### Text-to-Image Generation
Generate images from natural language descriptions.

```
"Generate an image of a sunset over mountains"
"Create a portrait of a cat wearing a bow tie"
"Make me an abstract image with blue and purple swirls"
```

#### Image-to-Image Transformation
Transform existing images using text prompts.

```
"Make this photo look like a watercolor painting"
"Transform this image to black and white"
"Turn this photo into an anime-style illustration"
```

#### Multi-Image Input
Combine multiple images as references.

```
"Combine the style of this painting with the subject of this photo"
"Generate an image that merges elements from these three images"
```

#### Custom Aspect Ratios
Generate images with specific dimensions for different use cases.

**Supported ratios:**
- `1:1` - Square (social media posts, profile pictures)
- `16:9` - Widescreen (presentations, YouTube thumbnails)
- `9:16` - Vertical (mobile stories, TikTok)
- `4:3` - Standard (traditional photos)
- `3:4` - Portrait orientation
- `21:9` - Ultra-wide (cinematic)
- `4:5` - Instagram portrait
- `2:3` / `3:2` - Photo formats
- `match_input_image` - Match input dimensions

## Installation

### Prerequisites

**Required:**
- Replicate API key (get yours at https://replicate.com/account/api-tokens)

Set your API key as an environment variable:
```bash
export REPLICATE_API_KEY="your-api-key-here"
```

### From marketplace (once published):
```bash
/plugin marketplace add simon-username/claude-plugins
/plugin install creative-tools@simon-plugins
```

### Local testing:
```bash
/plugin marketplace add ~/Developer/claude-plugins
/plugin install creative-tools@simon-plugins
```

## Usage

The skill activates automatically when you request image-related tasks. No slash commands needed.

### Examples

**Simple generation:**
```
User: "Generate a 16:9 banner image of a forest at night"
Claude: [Activates nanobanana-image-gen skill]
        Generating image...
        [Saves to working directory]
```

**Image transformation:**
```
User: "Make this photo look like a vintage poster"
Claude: [Activates nanobanana-image-gen skill]
        Transforming image...
        [Saves result to working directory]
```

**Style transfer:**
```
User: "Apply the style of this artwork to my photo"
Claude: [Activates nanobanana-image-gen skill]
        Processing images...
        [Saves styled image]
```

## Configuration

### Environment Variables

**REPLICATE_API_KEY** (required)
Your Replicate API token for accessing the Nanobanana model.

```bash
# Add to your ~/.zshrc or ~/.bashrc
export REPLICATE_API_KEY="r8_your_api_key_here"
```

### Default Settings

- **Default aspect ratio**: 1:1 (square)
- **Landscape images**: Automatically use 16:9
- **Portrait requests**: Automatically use 2:3
- **Output format**: JPG (use PNG for transparency needs)
- **Generation timeout**: 5 minutes

## Components

- `skills/nanobanana-image-gen/` - Image generation skill
  - `SKILL.md` - Skill definition and capabilities
  - `scripts/generate_image.py` - Image generation script
  - `references/nanobanana-api.md` - API reference and best practices

## Troubleshooting

### "Missing REPLICATE_API_KEY"
Ensure you've set the environment variable and restarted your terminal.

### "Image URL not accessible"
Input images must be publicly accessible URLs or local files. The script automatically uploads local files to Replicate.

### "Generation timeout"
Complex images may take longer. The script waits up to 5 minutes by default.

### "API rate limit"
Check your Replicate account usage limits and plan.

## Best Practices

1. **Descriptive prompts**: More detail produces better results
   - Good: "a serene mountain lake at sunset with pine trees in the foreground"
   - Weak: "a lake"

2. **Appropriate aspect ratios**: Choose ratios matching your use case
   - Social media: 1:1 or 4:5
   - Presentations: 16:9
   - Stories: 9:16

3. **Image quality**: Higher quality source images produce better transformations

4. **Iterative refinement**: Generate multiple variations by adjusting prompts

5. **Output format**:
   - Use JPG for photographs (smaller files)
   - Use PNG for images requiring transparency

## Performance

- **Generation time**: 5-15 seconds for typical images
- **Complex generations**: Up to 1-2 minutes
- **Polling interval**: Optimized for minimal API calls
- **Timeout**: 5 minutes maximum

## Contributing

This is a personal plugin collection. Feel free to fork and adapt for your needs.

## License

MIT License - see LICENSE file for details

## Support

For issues or questions, open an issue in the repository.

---

**Note:** This plugin requires a Replicate API key. Usage is subject to Replicate's pricing and terms of service.
