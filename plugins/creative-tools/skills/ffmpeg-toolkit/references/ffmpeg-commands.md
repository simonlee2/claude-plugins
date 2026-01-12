# FFmpeg Command Reference

Detailed reference for ffmpeg flags, options, and advanced usage.

## Command Structure

```
ffmpeg [global_options] {[input_options] -i input} ... {[output_options] output} ...
```

## Global Options

| Option | Description |
|--------|-------------|
| `-hide_banner` | Suppress printing banner |
| `-y` | Overwrite output without asking |
| `-n` | Never overwrite output |
| `-v quiet` | Suppress all output except errors |
| `-stats` | Print encoding progress/statistics |

## Input Options

| Option | Description | Example |
|--------|-------------|---------|
| `-ss` | Seek to position | `-ss 00:01:30` or `-ss 90` |
| `-t` | Duration to process | `-t 00:00:30` or `-t 30` |
| `-to` | Stop at position | `-to 00:02:00` |
| `-r` | Set input framerate | `-r 30` |
| `-f` | Force input format | `-f concat` |

### Position Notes
- `-ss` before `-i`: Fast seek (may be inaccurate)
- `-ss` after `-i`: Slow seek (frame-accurate)
- Use seconds or HH:MM:SS.ms format

## Output Options

### Video Codec Options

| Option | Description | Example |
|--------|-------------|---------|
| `-c:v` | Video codec | `-c:v libx264` |
| `-c:v copy` | Copy video stream | No re-encoding |
| `-vn` | No video | Discard video |
| `-vf` | Video filter | `-vf "scale=1280:-1"` |

### Common Video Codecs

| Codec | Library | Notes |
|-------|---------|-------|
| H.264 | `libx264` | Most compatible |
| H.265/HEVC | `libx265` | Better compression |
| VP9 | `libvpx-vp9` | WebM format |
| AV1 | `libaom-av1` | Best compression, slow |
| ProRes | `prores_ks` | Editing codec |

### Audio Codec Options

| Option | Description | Example |
|--------|-------------|---------|
| `-c:a` | Audio codec | `-c:a aac` |
| `-c:a copy` | Copy audio stream | No re-encoding |
| `-an` | No audio | Discard audio |
| `-af` | Audio filter | `-af "volume=2"` |
| `-b:a` | Audio bitrate | `-b:a 192k` |

### Common Audio Codecs

| Codec | Library | Notes |
|-------|---------|-------|
| AAC | `aac` | Default MP4 audio |
| MP3 | `libmp3lame` | Universal support |
| Opus | `libopus` | Best quality/size |
| FLAC | `flac` | Lossless |
| PCM | `pcm_s16le` | Uncompressed |

## Quality Control

### CRF (Constant Rate Factor)

H.264/libx264:
```bash
-c:v libx264 -crf 23
```
- Range: 0-51 (0 = lossless, 51 = worst)
- 18: Visually lossless
- 23: Default
- 28: Low quality, small file

H.265/libx265:
```bash
-c:v libx265 -crf 28
```
- Range: 0-51
- 28: Equivalent to x264 CRF 23

VP9:
```bash
-c:v libvpx-vp9 -crf 31 -b:v 0
```
- Range: 0-63
- 31: Good quality
- Must set `-b:v 0` to use CRF mode

### Presets (Speed vs Compression)

```bash
-preset ultrafast  # Fastest, largest file
-preset superfast
-preset veryfast
-preset faster
-preset fast
-preset medium     # Default
-preset slow
-preset slower
-preset veryslow   # Slowest, smallest file
```

### Bitrate Control

| Mode | Flags | Notes |
|------|-------|-------|
| CBR | `-b:v 5M` | Constant bitrate |
| VBR | `-crf 23` | Variable, quality-based |
| Capped VBR | `-crf 23 -maxrate 5M -bufsize 10M` | Quality with cap |

## Video Filters (-vf)

### Scaling
```bash
scale=1920:1080           # Exact size
scale=1280:-1             # Width 1280, auto height
scale=-1:720              # Auto width, height 720
scale=iw/2:ih/2           # Half size
scale='min(1920,iw)':'-1' # Max width 1920
```

### Cropping
```bash
crop=640:480:100:50       # width:height:x:y
crop=in_w:in_h-100        # Remove 100px from bottom
crop=iw:ih-100:0:0        # Remove 100px from bottom
```

### Padding
```bash
pad=1920:1080:(ow-iw)/2:(oh-ih)/2  # Center in 1920x1080
pad=iw:ih+100:0:50:black          # Add 50px top/bottom
```

### Rotation
```bash
transpose=0  # 90° CCW + vertical flip
transpose=1  # 90° clockwise
transpose=2  # 90° counterclockwise
transpose=3  # 90° CW + vertical flip
hflip        # Horizontal flip
vflip        # Vertical flip
```

### Speed/Tempo
```bash
setpts=0.5*PTS   # 2x speed (video)
setpts=2*PTS     # 0.5x speed (video)
```

### Color/Effects
```bash
eq=brightness=0.1:saturation=1.5    # Adjust brightness/saturation
colorbalance=rs=0.3                  # Color correction
curves=preset=lighter                # Preset curves
hue=h=90                             # Rotate hue
```

### Text Overlay
```bash
drawtext=text='Hello':fontsize=24:fontcolor=white:x=10:y=10
drawtext=textfile=text.txt:reload=1:fontsize=24:y=h-th-10
```

### Timestamps
```bash
drawtext=text='%{pts\:hms}':fontsize=24:x=10:y=10
```

## Audio Filters (-af)

### Volume
```bash
volume=2           # Double volume
volume=0.5         # Half volume
volume=10dB        # Increase by 10dB
loudnorm           # Normalize loudness
```

### Speed/Tempo
```bash
atempo=2.0         # 2x speed (0.5-2.0 range)
atempo=2.0,atempo=2.0  # 4x speed (chain for >2x)
```

### Fade
```bash
afade=t=in:st=0:d=3     # Fade in 3s at start
afade=t=out:st=57:d=3   # Fade out starting at 57s
```

### Channels
```bash
pan=mono|c0=0.5*c0+0.5*c1  # Convert to mono
channelsplit                # Split stereo to two mono
```

## Stream Selection (-map)

```bash
-map 0        # All streams from first input
-map 0:v      # All video from first input
-map 0:a      # All audio from first input
-map 0:v:0    # First video stream from first input
-map 0:a:1    # Second audio stream from first input
-map 1:a      # All audio from second input
```

### Examples

**Replace audio:**
```bash
ffmpeg -i video.mp4 -i audio.mp3 -map 0:v -map 1:a -c copy output.mp4
```

**Keep video, remove audio:**
```bash
ffmpeg -i input.mp4 -map 0:v -c copy output.mp4
```

**Select specific streams:**
```bash
ffmpeg -i input.mkv -map 0:v:0 -map 0:a:1 -c copy output.mp4
```

## Concatenation

### Concat Demuxer (Same Codec)

Create `files.txt`:
```
file 'video1.mp4'
file 'video2.mp4'
```

```bash
ffmpeg -f concat -safe 0 -i files.txt -c copy output.mp4
```

### Concat Filter (Different Codecs)

```bash
ffmpeg -i v1.mp4 -i v2.mp4 -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1" output.mp4
```

## Hardware Acceleration

### NVIDIA (NVENC/NVDEC)

**Decode with GPU:**
```bash
-hwaccel cuda
-hwaccel_output_format cuda
```

**Encode with GPU:**
```bash
-c:v h264_nvenc
-c:v hevc_nvenc
```

**Full GPU pipeline:**
```bash
ffmpeg -hwaccel cuda -hwaccel_output_format cuda -i input.mp4 -c:v h264_nvenc output.mp4
```

### Intel QuickSync

```bash
-c:v h264_qsv
-c:v hevc_qsv
```

### Apple VideoToolbox

```bash
-c:v h264_videotoolbox
-c:v hevc_videotoolbox
```

## Container Formats

| Extension | Format | Video Codecs | Audio Codecs |
|-----------|--------|--------------|--------------|
| .mp4 | MPEG-4 | H.264, H.265 | AAC, MP3 |
| .mkv | Matroska | Any | Any |
| .webm | WebM | VP8, VP9, AV1 | Vorbis, Opus |
| .mov | QuickTime | H.264, ProRes | AAC, PCM |
| .avi | AVI | Many | Many |
| .gif | GIF | GIF | None |

## Useful Flags

| Flag | Description |
|------|-------------|
| `-movflags faststart` | Web-optimized MP4 |
| `-pix_fmt yuv420p` | Compatibility pixel format |
| `-shortest` | End when shortest input ends |
| `-avoid_negative_ts make_zero` | Fix timestamps |
| `-vsync vfr` | Variable framerate |
| `-async 1` | Sync audio to video |

## Getting Information

**Full info:**
```bash
ffmpeg -i input.mp4
```

**JSON output:**
```bash
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4
```

**Duration only:**
```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.mp4
```

**Resolution:**
```bash
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 input.mp4
```

## Common Patterns

### Web-Ready MP4
```bash
ffmpeg -i input.mov -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k -movflags faststart -pix_fmt yuv420p output.mp4
```

### Thumbnail Generation
```bash
ffmpeg -i input.mp4 -ss 00:00:05 -frames:v 1 -q:v 2 thumbnail.jpg
```

### Preview/Proxy
```bash
ffmpeg -i input.mp4 -vf "scale=640:-1" -c:v libx264 -crf 28 -preset veryfast -c:a aac -b:a 64k proxy.mp4
```

### Audio Normalization
```bash
ffmpeg -i input.mp4 -af loudnorm -c:v copy output.mp4
```

### Batch Processing
```bash
for f in *.mp4; do ffmpeg -i "$f" -c:v libx264 -crf 23 "converted_$f"; done
```

## Error Solutions

| Error | Solution |
|-------|----------|
| "Non-monotonous DTS" | Add `-fflags +genpts` |
| "Discarding NAL unit" | Re-encode video |
| "Invalid data found" | Check file integrity |
| "Audio sync issues" | Use `-async 1` or re-encode |
| "Avi header overlong" | Add `-max_muxing_queue_size 1024` |

## Resources

- Official documentation: https://ffmpeg.org/documentation.html
- FFmpeg wiki: https://trac.ffmpeg.org/wiki
- CLI guidelines: https://clig.dev/
