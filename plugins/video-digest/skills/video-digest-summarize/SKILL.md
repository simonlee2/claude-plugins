---
name: video-digest-summarize
description: Turn segmented talk transcripts into digest text - per-talk transcript slices, cleaned transcripts, summary docs with timestamped highlights, TL;DR + practical takeaway JSON, and optional Traditional Chinese translation. Stage 3 of the video-digest pipeline, after ingest (and segment for multi-talk streams). Use when summarizing talks for a video digest.
---

# video-digest-summarize

Input: `<item_dir>` with `talks.json` + `transcript/transcript.tsv`. See `video-digest` for layout/config.

## 1. Deterministic prep (scripts/)

```
python3 scripts/vd_sessions.py <item_dir> [--clips]   # slices + manifest.json (+ per-talk clips)
python3 scripts/vd_clean.py <item_dir>                # cleaned transcript, glossary from digest.json
```
- `vd_sessions.py`: per talk `sessions/NN_slug.txt` ("[HH:MM:SS] text" lines, video offsets) + `manifest.json`. `--clips` also cuts lossless per-talk mp4s (only useful for multi-talk streams; skipped automatically when a talk spans the whole video).
- `vd_clean.py`: collapses Whisper loop/applause runs, applies `glossary`/`nonspeech` from the project's `digest.json` (walks up from item_dir) → `transcript/transcript.clean.txt`, `sessions/*.clean.txt`, `transcript/corrections.md`.

## 2. LLM steps (prompts in `references/`; fan out ~5 talks per agent)

| Prompt | Reads | Writes |
|---|---|---|
| `summarize-prompt.md` | `sessions/<name>.txt` | `sessions/<name>.md` (Summary, timestamped Highlights, quotes) |
| `takeaway-prompt.md` | `sessions/<name>.md` | `sessions/<name>.take.json` `{"tldr","takeaway"}` |
| `translate-prompt.md` | highlights.json + take.json | `zh.json` — only if project `languages` includes `"zh"`; run AFTER the slides stage (needs highlights.json) |

Fill `{ITEM_DIR}` and `{AUDIENCE}` (from digest.json `audience`) in prompts.

## Order note

summarize → takeaway can run right after this stage's scripts; the slides stage then extracts frames at each highlight timestamp. Translation last (it reads highlights.json from the slides stage).

## Glossary loop

After the pilot item, read `transcript/corrections.md` + skim a `sessions/*.md` for recurring ASR errors (product names, speaker names) → add regex pairs to `digest.json.glossary`, re-run `vd_clean.py`. Only unambiguous fixes; never risky common-word swaps.
