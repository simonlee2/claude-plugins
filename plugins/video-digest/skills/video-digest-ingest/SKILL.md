---
name: video-digest-ingest
description: Acquire videos and transcribe them for a video digest project - probe/enumerate a YouTube playlist, channel streams tab, or local folder; download at 720p; extract audio; transcribe with mlx-whisper; emit a 30s timeline. Stage 1 of the video-digest pipeline. Use when ingesting videos for a digest, or when asked to download+transcribe talk videos.
---

# video-digest-ingest

Deterministic stage 1. See `video-digest` (umbrella) for the project layout.

## Scripts (in `scripts/`, all take explicit paths — no env vars)

### Probe a source (ALWAYS do this first; supports pilot-first)
```
python3 scripts/vd_probe.py <playlist_or_channel_url | /path/to/folder>
```
Prints a worklist table (id, duration, title) + totals and time/disk estimates. Add `--json out.json` to save the worklist. Skips unavailable/private entries (duration null). For a channel's live streams use the `/streams` tab URL; entries without a duration are still-live → NOT ingestable yet.

### Ingest one item (download/link + transcribe + timeline)
```
bash scripts/vd_ingest.sh <item_dir> <youtube_url | /path/to/video.ext> [lang]
```
- Creates `<item_dir>`, downloads ≤720p mp4 (`video.mp4`, symlinked as `source.mp4`) or symlinks a local file.
- Extracts 16k mono wav → transcribes via `uvx --from mlx-whisper mlx_whisper` (large-v3-turbo) with `--condition-on-previous-text False` (**critical: prevents hallucinated repeat-loops erasing real content**).
- `lang` optional (e.g. `en`); omit to autodetect.
- Idempotent: skips download/transcribe if outputs exist.

### Author metadata for a single-talk item (playlist entry / lone video)
```
python3 scripts/vd_single.py <item_dir> --title "T" --speaker "Name · Org" [--kind talk] [--url <video_url>]
```
Reads real duration via ffprobe → writes 1-talk `talks.json` (00:00:00 → duration), plus `source.json` (label=title, subtitle=speaker, url). Skip this for multi-talk streams — use `video-digest-segment` instead, and write `source.json` by hand.

## Batch workflow (playlist / folder)

1. `vd_probe.py <url>` → worklist. Derive title/speaker per video from its YouTube title (e.g. "Talk Name, Speaker | Event" → split; verify against transcript later).
2. Pilot ONE item end-to-end through all stages before batching.
3. Batch **serially** (concurrent Whisper exhausts RAM):
   for each entry → `vd_ingest.sh groups/<group>/NN-<slug> <url> [lang] < /dev/null` then `vd_single.py ...`.
   `NN-` prefix (01, 02…) = playlist order = digest order.
   **In a `while read` loop you MUST redirect the ingest call's stdin (`< /dev/null`)** — ffmpeg/yt-dlp otherwise eat the loop's input and mangle subsequent lines.
   **TSV worklists read by `bash read`: never leave a field empty** (tab is IFS whitespace, so consecutive tabs collapse and fields shift). Use a placeholder like `-` for unknown speaker and translate it in the consumer.
4. Create `groups/<group>/group.json` `{"key":"<group>","label":"..."}` once.

## Gotchas

- **yt-dlp 403 / "challenge solving failed"** (falls back to audio-only): YouTube rotated its player; fix `python3 -m pip install -U --pre "yt-dlp[default]"`, verify `yt-dlp -F <url>`.
- 720p is intentional — video is only used for audio + slide frames (extracted at 960px). Don't download best quality.
- Audio in downloaded mp4 may be Opus (plays in Chrome/VLC, not QuickTime) — irrelevant to the pipeline.
- Whisper quality check: grep the transcript for a phrase repeated many times in a row → if found early, the loop bug hit; confirm the `--condition-on-previous-text False` flag was used.
