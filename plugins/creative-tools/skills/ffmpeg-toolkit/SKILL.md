---
name: ffmpeg-toolkit
description: This skill should be used when the user asks to "convert video", "trim video", "cut video", "extract audio", "compress video", "resize video", "create gif", "merge videos", "combine videos", "add audio to video", or needs help with ffmpeg commands for video and audio processing.
---

# FFmpeg Toolkit

Comprehensive guide for video and audio processing with ffmpeg.

## Overview

This skill provides guidance on using ffmpeg for common video and audio operations. ffmpeg is a powerful command-line tool for processing multimedia files - converting formats, trimming, resizing, extracting audio, creating GIFs, and much more.

## Core Principles

### Always Use These Flags
- `-hide_banner` - Suppress ffmpeg version info for cleaner output
- `-y` - Overwrite output file without asking (for automation)

### When to Use `-c copy` (Stream Copy)
Use `-c copy` when you want to:
- Preserve original quality (no re-encoding)
- Process quickly (10-100x faster than re-encoding)
- Keep file size similar to source

**Limitation:** Stream copy cannot change codec, resolution, or apply filters.

### When to Re-encode
Re-encode when you need to:
- Change resolution or aspect ratio
- Apply filters (crop, rotate, overlay)
- Change codec (e.g., HEVC to H.264)
- Adjust quality/bitrate
- Frame-accurate trimming

## Common Operations

### 1. Format Conversion

**Basic conversion (re-encodes):**
```bash
ffmpeg -hide_banner -i input.mkv output.mp4
```

**Lossless remux (no re-encoding):**
```bash
ffmpeg -hide_banner -i input.mkv -c copy output.mp4
```

**Convert to web-optimized MP4:**
```bash
ffmpeg -hide_banner -i input.mov -c:v libx264 -crf 23 -c:a aac -movflags faststart output.mp4
```

### 2. Trimming/Cutting

**Fast trim (no re-encoding, may have keyframe issues):**
```bash
ffmpeg -hide_banner -ss 00:01:30 -i input.mp4 -t 00:00:30 -c copy output.mp4
```
- `-ss 00:01:30` - Start at 1 minute 30 seconds
- `-t 00:00:30` - Duration of 30 seconds

**Frame-accurate trim (requires re-encoding):**
```bash
ffmpeg -hide_banner -i input.mp4 -ss 00:01:30 -t 00:00:30 -c:v libx264 -c:a aac output.mp4
```

**Trim to end of file:**
```bash
ffmpeg -hide_banner -ss 00:05:00 -i input.mp4 -c copy output.mp4
```

### 3. Audio Operations

**Extract audio to MP3:**
```bash
ffmpeg -hide_banner -i video.mp4 -vn -c:a libmp3lame -q:a 2 audio.mp3
```

**Extract audio to WAV (lossless):**
```bash
ffmpeg -hide_banner -i video.mp4 -vn audio.wav
```

**Remove audio from video:**
```bash
ffmpeg -hide_banner -i input.mp4 -an -c:v copy output.mp4
```

**Add audio to video:**
```bash
ffmpeg -hide_banner -i video.mp4 -i audio.mp3 -c:v copy -c:a aac -map 0:v -map 1:a output.mp4
```

**Replace audio in video:**
```bash
ffmpeg -hide_banner -i video.mp4 -i new_audio.mp3 -c:v copy -c:a aac -map 0:v -map 1:a -shortest output.mp4
```

### 4. Resizing/Scaling

**Scale to specific resolution:**
```bash
ffmpeg -hide_banner -i input.mp4 -vf "scale=1920:1080" -c:a copy output.mp4
```

**Scale maintaining aspect ratio (width 1280, auto height):**
```bash
ffmpeg -hide_banner -i input.mp4 -vf "scale=1280:-1" -c:a copy output.mp4
```

**Scale to fit within bounds (won't exceed 1920x1080):**
```bash
ffmpeg -hide_banner -i input.mp4 -vf "scale='min(1920,iw)':'min(1080,ih)'" -c:a copy output.mp4
```

### 5. Compression

**Constant Rate Factor (CRF) - Recommended:**
```bash
ffmpeg -hide_banner -i input.mp4 -c:v libx264 -crf 23 -c:a aac output.mp4
```
- CRF 18: Visually lossless
- CRF 23: Default, good balance
- CRF 28: Smaller file, lower quality

**Target bitrate:**
```bash
ffmpeg -hide_banner -i input.mp4 -c:v libx264 -b:v 2M -c:a aac -b:a 128k output.mp4
```

**Two-pass encoding (best quality for target size):**
```bash
ffmpeg -hide_banner -i input.mp4 -c:v libx264 -b:v 2M -pass 1 -f null /dev/null
ffmpeg -hide_banner -i input.mp4 -c:v libx264 -b:v 2M -pass 2 output.mp4
```

### 6. Creating GIFs

**Basic GIF:**
```bash
ffmpeg -hide_banner -i input.mp4 -vf "fps=10,scale=480:-1" output.gif
```

**High-quality GIF with palette:**
```bash
ffmpeg -hide_banner -i input.mp4 -vf "fps=10,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" output.gif
```

**GIF from specific section:**
```bash
ffmpeg -hide_banner -ss 00:00:05 -t 3 -i input.mp4 -vf "fps=15,scale=320:-1:flags=lanczos" output.gif
```

### 7. Combining Videos

**Concatenate videos (same codec):**

First create a file list (`videos.txt`):
```
file 'video1.mp4'
file 'video2.mp4'
file 'video3.mp4'
```

Then concatenate:
```bash
ffmpeg -hide_banner -f concat -safe 0 -i videos.txt -c copy output.mp4
```

**Concatenate with re-encoding (different codecs/resolutions):**
```bash
ffmpeg -hide_banner -f concat -safe 0 -i videos.txt -c:v libx264 -c:a aac output.mp4
```

### 8. Rotation

**Rotate 90° clockwise:**
```bash
ffmpeg -hide_banner -i input.mp4 -vf "transpose=1" output.mp4
```

Transpose values:
- `0` - 90° counterclockwise + vertical flip
- `1` - 90° clockwise
- `2` - 90° counterclockwise
- `3` - 90° clockwise + vertical flip

**Rotate 180°:**
```bash
ffmpeg -hide_banner -i input.mp4 -vf "transpose=1,transpose=1" output.mp4
```

### 9. Cropping

**Crop to specific dimensions:**
```bash
ffmpeg -hide_banner -i input.mp4 -vf "crop=640:480:100:50" output.mp4
```
Format: `crop=width:height:x:y`

**Crop center square:**
```bash
ffmpeg -hide_banner -i input.mp4 -vf "crop=min(iw\,ih):min(iw\,ih)" output.mp4
```

### 10. Speed Adjustment

**Speed up video 2x:**
```bash
ffmpeg -hide_banner -i input.mp4 -vf "setpts=0.5*PTS" -af "atempo=2.0" output.mp4
```

**Slow down video 0.5x:**
```bash
ffmpeg -hide_banner -i input.mp4 -vf "setpts=2*PTS" -af "atempo=0.5" output.mp4
```

**Speed up without audio:**
```bash
ffmpeg -hide_banner -i input.mp4 -vf "setpts=0.5*PTS" -an output.mp4
```

## Advanced Operations

### Add Subtitles

**Burn subtitles into video:**
```bash
ffmpeg -hide_banner -i input.mp4 -vf "subtitles=subs.srt" output.mp4
```

**Burn ASS subtitles (styled):**
```bash
ffmpeg -hide_banner -i input.mp4 -vf "ass=subs.ass" output.mp4
```

### Add Watermark/Overlay

**Image overlay (top-right corner):**
```bash
ffmpeg -hide_banner -i input.mp4 -i logo.png -filter_complex "overlay=W-w-10:10" output.mp4
```

### Extract Frames

**Extract all frames:**
```bash
ffmpeg -hide_banner -i input.mp4 frame_%04d.png
```

**Extract 1 frame per second:**
```bash
ffmpeg -hide_banner -i input.mp4 -vf "fps=1" frame_%04d.png
```

**Extract single frame at timestamp:**
```bash
ffmpeg -hide_banner -ss 00:00:10 -i input.mp4 -frames:v 1 thumbnail.png
```

### Create Video from Images

**Images to video:**
```bash
ffmpeg -hide_banner -framerate 30 -i frame_%04d.png -c:v libx264 -pix_fmt yuv420p output.mp4
```

### Change Metadata

**Set title:**
```bash
ffmpeg -hide_banner -i input.mp4 -c copy -metadata title="My Video" output.mp4
```

**Remove all metadata:**
```bash
ffmpeg -hide_banner -i input.mp4 -c copy -map_metadata -1 output.mp4
```

### Hardware Acceleration (NVIDIA)

**Encode with NVENC:**
```bash
ffmpeg -hide_banner -i input.mp4 -c:v h264_nvenc -preset fast -b:v 5M output.mp4
```

**Decode and encode with GPU:**
```bash
ffmpeg -hide_banner -hwaccel cuda -i input.mp4 -c:v h264_nvenc output.mp4
```

## Quick Reference

| Task | Command |
|------|---------|
| Get info | `ffmpeg -i input.mp4` |
| Convert format | `ffmpeg -i in.mkv out.mp4` |
| Remux (fast) | `ffmpeg -i in.mkv -c copy out.mp4` |
| Trim | `ffmpeg -ss 00:01:00 -t 30 -i in.mp4 -c copy out.mp4` |
| Extract audio | `ffmpeg -i in.mp4 -vn out.mp3` |
| Remove audio | `ffmpeg -i in.mp4 -an -c:v copy out.mp4` |
| Scale | `ffmpeg -i in.mp4 -vf "scale=1280:-1" out.mp4` |
| Compress | `ffmpeg -i in.mp4 -crf 28 out.mp4` |
| To GIF | `ffmpeg -i in.mp4 -vf "fps=10,scale=320:-1" out.gif` |
| Rotate 90° | `ffmpeg -i in.mp4 -vf "transpose=1" out.mp4` |

## Best Practices

1. **Always test on a short clip first** before processing large files
2. **Use `-c copy` when possible** for speed and quality preservation
3. **Add `-movflags faststart`** for web-optimized MP4s
4. **Use CRF for quality-based encoding** instead of fixed bitrate
5. **Check input info first** with `ffmpeg -i input.mp4` to understand source
6. **Use two-pass encoding** when targeting specific file size

## Common Pitfalls

- **Audio/video sync issues after trim**: Use re-encoding instead of `-c copy`
- **Black frames at start**: Add `-avoid_negative_ts make_zero`
- **Incompatible codec in container**: Check container format supports codec
- **GIF too large**: Reduce FPS, scale down, or shorten duration

## Additional Resources

For detailed command reference, see `references/ffmpeg-commands.md`.
