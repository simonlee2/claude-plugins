# Nanobanana Model API Reference

## Model Information

**Model ID**: `google/nano-banana`
**Provider**: Replicate
**Type**: Image generation and editing
**Documentation**: https://replicate.com/google/nano-banana

## Model Capabilities

Nanobanana is Google's fast image generation model that excels at:

1. **Text-to-image generation** - Creating images from natural language descriptions
2. **Image-to-image transformation** - Editing and transforming existing images
3. **Style transfer** - Applying artistic styles to images
4. **Multi-image input** - Using multiple reference images to guide generation
5. **Aspect ratio control** - Precise control over output dimensions

## Input Parameters

### Required Parameters

#### `prompt` (string)
- **Description**: Text description of the desired image or transformation
- **Best practices**:
  - Be specific and descriptive
  - Include details about style, mood, lighting, composition
  - For transformations, clearly describe the desired changes
- **Examples**:
  - "A serene mountain landscape at sunset with pine trees in the foreground, photorealistic, 8k quality"
  - "Transform this photo into a watercolor painting with soft pastel colors"
  - "A futuristic cityscape with neon lights, cyberpunk style, rainy night"

### Optional Parameters

#### `image_input` (array of URLs)
- **Description**: Input images to transform or use as reference
- **Type**: Array of strings (image URLs)
- **Default**: `[]` (empty array for text-to-image)
- **Format**: Publicly accessible URLs or Replicate file URLs
- **Multiple images**: Supports multiple reference images
- **Use cases**:
  - Image-to-image transformation
  - Style transfer
  - Image variation generation
  - Multi-image composition

**Important**: Images must be uploaded to Replicate's file hosting service. The generation script handles this automatically.

#### `aspect_ratio` (string)
- **Description**: Aspect ratio of the generated image
- **Type**: String enum
- **Default**: `"match_input_image"` (when images provided), `"1:1"` (for text-to-image)
- **Available options**:
  - `"match_input_image"` - Match dimensions of input image (requires image input)
  - `"1:1"` - Square (1024x1024) - Best for: profile pictures, social posts
  - `"16:9"` - Widescreen (1344x768) - Best for: YouTube thumbnails, presentations, banners
  - `"9:16"` - Vertical (768x1344) - Best for: Stories, TikTok, mobile wallpapers
  - `"4:3"` - Standard (1152x896) - Best for: Traditional photos, presentations
  - `"3:4"` - Portrait (896x1152) - Best for: Portrait photos
  - `"21:9"` - Ultra-wide (1536x640) - Best for: Cinematic, ultra-wide displays
  - `"4:5"` - Instagram portrait (1024x1280) - Best for: Instagram posts
  - `"5:4"` - Medium format (1280x1024) - Best for: Medium format photography
  - `"2:3"` - Portrait (896x1344) - Best for: Portrait photography
  - `"3:2"` - Landscape (1344x896) - Best for: Landscape photography

#### `output_format` (string)
- **Description**: Format of the output image
- **Type**: String enum
- **Default**: `"jpg"`
- **Available options**:
  - `"jpg"` - JPEG format, smaller file size, no transparency
  - `"png"` - PNG format, larger file size, supports transparency
- **When to use PNG**: Logos, graphics requiring transparency, images with text
- **When to use JPG**: Photographs, general images, when file size matters

## Output

The model returns a single output object with a `url()` method that provides the generated image URL.

**Output structure**:
```python
output = {
    "url": lambda: "https://replicate.delivery/pbxt/..."
}
```

**Accessing the image**:
```python
image_url = output.url()
```

## Performance Characteristics

### Generation Times
- **Simple prompts**: 5-10 seconds
- **Complex prompts**: 10-15 seconds
- **Image-to-image**: 8-12 seconds
- **Multi-image input**: 12-18 seconds

### Polling Configuration
- **Recommended interval**: 1000ms (1 second)
- **Timeout**: 300 seconds (5 minutes)
- **Mode**: Poll mode with intervals

## Best Practices

### Prompt Engineering

1. **Be specific and descriptive**
   - Good: "A majestic lion with a golden mane sitting on a rocky outcrop at sunset, dramatic lighting, photorealistic, 8k"
   - Poor: "A lion"

2. **Include style modifiers**
   - Examples: "photorealistic", "oil painting", "watercolor", "anime style", "cyberpunk", "impressionist"

3. **Specify lighting and mood**
   - Examples: "golden hour lighting", "dramatic shadows", "soft diffused light", "neon glow"

4. **Add quality indicators**
   - Examples: "8k quality", "highly detailed", "professional photography", "cinematic"

5. **For transformations, be clear about desired changes**
   - Good: "Transform this photo into a watercolor painting with soft pastel colors and visible brush strokes"
   - Poor: "Make it look artistic"

### Image Input Best Practices

1. **Image quality**: Higher quality source images produce better results
2. **Image size**: Optimal input size is 1024px on the longest side
3. **Multiple images**: When using multiple inputs, ensure they're thematically related
4. **URL accessibility**: Ensure image URLs are publicly accessible

### Aspect Ratio Selection

Choose aspect ratios based on the intended use:
- **Social media**: 1:1 (Instagram), 9:16 (Stories), 4:5 (Instagram portrait)
- **Video thumbnails**: 16:9 (YouTube, streaming platforms)
- **Photography**: 3:2 (landscape), 2:3 (portrait), 4:3 (standard)
- **Cinematic**: 21:9 (ultra-wide)
- **Presentations**: 16:9 (modern), 4:3 (traditional)

### Error Handling

Common errors and solutions:

1. **"Invalid image URL"**
   - Ensure image URLs are publicly accessible
   - Upload images to Replicate's file hosting first

2. **"API key not found"**
   - Set the `REPLICATE_API_KEY` environment variable
   - Verify the API key is valid

3. **"Request timeout"**
   - Increase timeout duration for complex generations
   - Simplify the prompt or reduce image input count

4. **"Model prediction failed"**
   - Check prompt for inappropriate content
   - Verify input images are valid and accessible
   - Try with a simpler prompt

## Rate Limits

Replicate enforces rate limits based on account tier:
- **Free tier**: Limited concurrent predictions
- **Pro tier**: Higher concurrency limits
- **Enterprise**: Custom limits

Handle rate limits by:
- Implementing exponential backoff
- Queueing requests
- Monitoring API response headers

## Cost Considerations

Pricing is based on:
- **Prediction run time**: Billed per second
- **Input image size**: Larger inputs may cost more
- **Output resolution**: Higher resolutions may increase cost

Check current pricing at: https://replicate.com/google/nano-banana

## Example API Calls

### Text-to-Image
```python
import replicate

output = replicate.run(
    "google/nano-banana",
    input={
        "prompt": "A majestic mountain landscape at sunset",
        "aspect_ratio": "16:9",
        "output_format": "jpg"
    }
)
image_url = output.url()
```

### Image-to-Image Transformation
```python
output = replicate.run(
    "google/nano-banana",
    input={
        "prompt": "Transform into a watercolor painting",
        "image_input": ["https://replicate.delivery/pbxt/..."],
        "aspect_ratio": "match_input_image",
        "output_format": "jpg"
    }
)
image_url = output.url()
```

### Multi-Image Input
```python
output = replicate.run(
    "google/nano-banana",
    input={
        "prompt": "Combine the style from the first image with the subject from the second",
        "image_input": [
            "https://replicate.delivery/pbxt/style.jpg",
            "https://replicate.delivery/pbxt/subject.jpg"
        ],
        "aspect_ratio": "1:1",
        "output_format": "jpg"
    }
)
image_url = output.url()
```

## Troubleshooting

### Common Issues

1. **Slow generation times**
   - Normal for complex prompts
   - Use simpler prompts or fewer input images
   - Check Replicate status page for service issues

2. **Poor quality results**
   - Add quality modifiers to prompt ("8k", "highly detailed")
   - Use higher quality input images
   - Be more specific in the prompt

3. **Unexpected style or content**
   - Refine the prompt with more specific details
   - Add negative prompts if supported in future versions
   - Adjust aspect ratio to match intended composition

4. **File upload failures**
   - Verify image files are valid
   - Check file size limits (typically 10MB max)
   - Ensure network connectivity

## Additional Resources

- **Replicate Documentation**: https://replicate.com/docs
- **Nanobanana Model Page**: https://replicate.com/google/nano-banana
- **API Reference**: https://replicate.com/docs/reference/http
- **Python Client**: https://github.com/replicate/replicate-python
- **Rate Limits**: https://replicate.com/docs/topics/rate-limits
