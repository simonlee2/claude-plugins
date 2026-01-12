---
name: seedance-video-gen
description: This skill should be used when the user asks to "generate video", "create video", "make a video", "animate image", "image to video", "video with audio", "talking video", or needs AI-powered video generation with synchronized audio, lip-syncing, and cinematic camera controls.
---

# Seedance Video Generation

## Overview

This skill enables AI video generation using ByteDance's Seedance 1.5 Pro model through the Replicate API. Generate videos from text prompts, animate still images, and create content with perfectly synchronized audio and lip-syncing.

## Core Capabilities

### 1. Text-to-Video Generation

Generate videos from natural language descriptions.

**Example requests:**
- "Generate a video of waves crashing on a beach at sunset"
- "Create a video of a cat playing with a ball of yarn"
- "Make a 10-second video of a city skyline timelapse"

**Process:**
1. Extract the scene description from the user's request
2. Determine appropriate duration and aspect ratio
3. Execute `scripts/generate_video.py` with the prompt
4. Save the generated video to the user's working directory

### 2. Image-to-Video Animation

Animate still images into dynamic videos.

**Example requests:**
- "Animate this portrait photo with subtle movements"
- "Turn this landscape image into a video with moving clouds"
- "Make this product image come alive with gentle motion"

**Process:**
1. Ensure the input image is accessible (local file or URL)
2. Upload image to Replicate if needed
3. Execute `scripts/generate_video.py` with the image and prompt
4. Save the animated video to the user's working directory

### 3. Audio-Synchronized Video

Generate videos with perfectly synchronized audio and lip movements.

**Key features:**
- Audio and video generated simultaneously (not sequentially)
- Millisecond-precision lip-sync across multiple languages
- Supported languages: English, Mandarin, Japanese, Korean, Spanish, Portuguese, Indonesian

**Example requests:**
- "Generate a video of a person saying 'Hello, welcome to my channel'"
- "Create a talking head video explaining quantum physics"
- "Make a video with a character singing a song"

### 4. Camera Controls

Apply cinematic camera movements to generated videos.

**Available movements:**
- **Pan** - Horizontal camera sweep
- **Tilt** - Vertical camera movement
- **Zoom** - Move closer or farther from subject
- **Tracking** - Follow a moving subject
- **Orbital** - Circle around the subject

**Example requests:**
- "Generate a video with a slow zoom into the subject"
- "Create a video with the camera panning across a landscape"
- "Make a video with orbital camera movement around the character"

To fix the camera in place, specify "fixed camera" or use the `camera_fixed` parameter.

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | string | required | Scene description |
| `duration` | int | 5 | Video length in seconds (2-12) |
| `aspect_ratio` | string | 16:9 | Output dimensions |
| `image` | file/URL | none | Input image for image-to-video |
| `last_frame_image` | file/URL | none | Target end frame |
| `camera_fixed` | bool | false | Lock camera position |
| `generate_audio` | bool | true | Include synchronized audio |
| `seed` | int | random | For reproducible results |

### Aspect Ratios

- `16:9` - Widescreen (YouTube, presentations)
- `9:16` - Vertical (TikTok, Instagram Reels, Stories)
- `1:1` - Square (Instagram posts)
- `4:3` - Standard (traditional video)
- `3:4` - Portrait
- `21:9` - Ultra-wide (cinematic)
- `9:21` - Ultra-tall

## Using the Generation Script

The `scripts/generate_video.py` script handles all Replicate API interactions.

**Basic text-to-video:**
```bash
python scripts/generate_video.py "a sunset over mountains" --output sunset.mp4
```

**With duration and aspect ratio:**
```bash
python scripts/generate_video.py "a cat playing" \
  --duration 8 \
  --aspect-ratio 9:16 \
  --output cat_playing.mp4
```

**Image-to-video:**
```bash
python scripts/generate_video.py "gentle wind blowing through hair" \
  --image portrait.jpg \
  --output animated_portrait.mp4
```

**Fixed camera:**
```bash
python scripts/generate_video.py "person talking to camera" \
  --camera-fixed \
  --output talking_head.mp4
```

**Without audio:**
```bash
python scripts/generate_video.py "abstract visuals" \
  --no-audio \
  --output silent_video.mp4
```

**Reproducible output:**
```bash
python scripts/generate_video.py "a forest scene" \
  --seed 42 \
  --output forest.mp4
```

## Output Format

- **Format:** MP4 (H.264 video, AAC audio)
- **Frame rate:** 24 fps (fixed)
- **Audio:** Synchronized stereo audio (when enabled)
- **Resolution:** Varies by aspect ratio (typically 1280x720 or similar)

## Environment Setup

Ensure the `REPLICATE_API_KEY` environment variable is set:

```bash
export REPLICATE_API_KEY="your-api-key-here"
```

Get an API key from https://replicate.com/account/api-tokens

## Performance Considerations

- Video generation takes 30 seconds to 3 minutes depending on duration and complexity
- Longer videos (10-12 seconds) require more generation time
- Image-to-video may take slightly longer due to image processing
- The script displays progress updates during generation

## Best Practices

1. **Detailed prompts**: More specific descriptions produce better results
   - Good: "A golden retriever running through a sunlit meadow with wildflowers, slow motion"
   - Less effective: "A dog running"

2. **Match aspect ratio to platform**: Use 9:16 for TikTok/Reels, 16:9 for YouTube

3. **Duration selection**: Start with shorter durations (5s) to iterate quickly, then increase

4. **Camera guidance**: Include camera movement in prompt or use `camera_fixed` for stability

5. **Audio considerations**: Disable audio (`--no-audio`) for videos where you'll add custom music/voiceover

6. **Character consistency**: For multi-clip narratives, use similar prompts and seed values

## Common Use Cases

### Social Media Content
```bash
# TikTok/Reels vertical video
python scripts/generate_video.py "trendy dance moves in neon-lit studio" \
  --aspect-ratio 9:16 --duration 8 --output tiktok_content.mp4
```

### Product Showcase
```bash
# Animate product image
python scripts/generate_video.py "elegant rotation revealing product details" \
  --image product.jpg --duration 6 --output product_showcase.mp4
```

### Talking Head / Avatar
```bash
# Generate speaking video
python scripts/generate_video.py "professional presenter explaining a concept, direct eye contact" \
  --camera-fixed --duration 10 --output presenter.mp4
```

### Cinematic B-Roll
```bash
# Atmospheric footage
python scripts/generate_video.py "aerial view of misty mountains at dawn, slow pan" \
  --aspect-ratio 21:9 --duration 12 --output broll.mp4
```

## Limitations

- Maximum duration: 12 seconds per generation
- Fixed frame rate: 24 fps (cannot be changed)
- Audio is generated, not from external source
- Character consistency across clips requires careful prompting
- Complex scenes with multiple characters may have reduced quality

## Error Handling

The script handles common errors:
- Missing API key: Clear error message with setup instructions
- Invalid image URL/path: Helpful error with troubleshooting steps
- Rate limiting: Automatic retry with backoff
- Generation failures: Detailed error from Replicate API

## Troubleshooting

**Video generation stuck:**
- Check API key is valid and has credits
- Try a shorter duration first
- Simplify the prompt

**Poor lip-sync:**
- Ensure prompt clearly describes speaking/dialogue
- Use `camera_fixed` for talking head videos
- Keep subject centered in frame description

**Unexpected camera movement:**
- Add `camera_fixed` flag for stable shots
- Or specify desired movement explicitly in prompt

**Image-to-video not working:**
- Ensure image is accessible (valid URL or local path)
- Check image format (JPG, PNG supported)
- Try with a simpler, clearer image
