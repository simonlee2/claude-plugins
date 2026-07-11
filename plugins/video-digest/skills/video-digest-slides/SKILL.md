---
name: video-digest-slides
description: Extract and select slide images for a video digest - grab candidate frames at each highlight timestamp (-5s/exact/+5s), build labeled montages, then vision-pick and verify the frame that actually shows a slide. Stage 4 of the video-digest pipeline, after summarize. Use when pairing talk highlights with the speaker's slides.
---

# video-digest-slides

Input: `<item_dir>` with `manifest.json` + `sessions/*.md` (highlights with timestamps). Requires Pillow (`uv run --with pillow` if missing).

## 1. Deterministic (scripts/)

```
python3 scripts/vd_frames.py <item_dir>    # frames/<stem>/hNN_{0,1,2}.jpg + highlights.json
python3 scripts/vd_montage.py <item_dir>   # montages/<stem>_pN.jpg + montages/index.json
```
Frames at 960px wide, offsets −5/0/+5s per highlight. Montage grid: rows = highlights, 3 columns of candidates, labeled `hNN:j  HH:MM:SS`, 8 rows/page.

## 2. Vision LLM steps (fan out ~5 talks/agent, CHEAP models)

1. **Select** (`references/select-prompt.md`, haiku/sonnet): read montages, pick per highlight the candidate j (0/1/2) that is a clean readable slide of THIS talk, or null (speaker/audience/transition/sponsor wall). Writes `frames/sel_<stem>.json` = `{"0": j|null, ...}`.
2. **Verify** (`references/verify-prompt.md`, sonnet): full-res re-check each pick against the highlight text; fix or null. Overwrites `sel_<stem>.json`. Don't skip — the cheap select pass overpicks.

Fireside chats / no-slides talks: all-null is correct; the digest renders text-only points.
