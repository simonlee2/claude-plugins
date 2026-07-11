---
name: video-digest
description: Build a shareable web digest (per-talk TL;DR, takeaways, slides paired with narration) from videos. Sources - a long multi-talk stream (YouTube or file), a YouTube playlist, a single video, or a local folder of videos. Umbrella skill - routes to composable stage skills (ingest, segment, summarize, slides, site). Use when asked to "make a digest / recap / summary site" from talks, a conference, a playlist, or recorded videos.
---

# video-digest — orchestrator

Turn videos into a digest site: overview card grid → per-talk detail (TL;DR, "take this to work", slides with captions), optional bilingual toggle + synthesis essay. Generalized from the AIE WF2026 pipeline.

## Stage skills (mix & match)

| Stage | Skill | In → Out |
|---|---|---|
| 1. Ingest | `video-digest-ingest` | source (URL/playlist/folder) → `video.mp4`, transcript, 30s timeline per item |
| 2. Segment | `video-digest-segment` | ONLY multi-talk streams: timeline → `talks.json`. Single-video items: auto (1-talk talks.json, done by ingest) |
| 3. Summarize | `video-digest-summarize` | transcript slices → `sessions/*.md`, `*.take.json`, optional `zh.json` |
| 4. Slides | `video-digest-slides` | highlights → candidate frames → montages → vision-picked `frames/sel_*.json` |
| 5. Site | `video-digest-site` | everything → `index.html`/`dist/` (+ optional essay), publish via here-now or Artifact |

Routing by source shape:
- **YouTube playlist / folder of videos** → ingest each video as its own item (skip segment). One group per playlist/folder.
- **Long multi-talk stream** → one item, then segment.
- **Single talk video** → one item, skip segment.

## Project layout

```
<project>/
├── digest.json                  # config (below)
├── groups/<group>/              # group = a tab/section (a day, a track, or the whole event)
│   ├── group.json               # {key,label,date?,hours?}  key MUST be kebab [a-z0-9-]
│   └── <item>/                  # item = ONE source video; prefix NN- for order (01-opening-keynote)
│       ├── source.json          # {key,label,subtitle,url?}  url → YouTube deep links in the digest
│       ├── video.mp4 source.mp4 # gitignored; source.mp4 = symlink
│       ├── transcript/          # transcript.{tsv,txt,srt...}, timeline_30s.txt, *.clean.txt
│       ├── talks.json manifest.json highlights.json zh.json
│       ├── sessions/ frames/ montages/ clips/
├── dist/                        # published site (site skill)
└── narrative.json narrative.zh.json   # optional essay
```

## digest.json (project config)

All text fields accept a string (EN-only) or `{"en":..., "zh":...}`. Minimal example:

```json
{
  "key": "compile26",
  "title": "Cursor Compile 2026 · Digest",
  "brand": "CURSOR · COMPILE 26",
  "kicker": "Cursor Compile 2026",
  "headline": "The conference, in slides & takeaways.",
  "lede": "Skim the talks, then open any one for the slides, the thesis, and what it means for your work.",
  "footer": "Transcripts auto-generated (Whisper) then cleaned; names ~95% accurate.",
  "audience": "an engineer building with AI",
  "whisper_language": "en",
  "languages": ["en"],
  "slide_cap": 8,
  "glossary": [["\\bKursor\\b", "Cursor"]],
  "nonspeech": ["thank you."]
}
```

- `audience` — steers takeaway prompts ("what should X do because of this talk").
- `languages` — add `"zh"` to enable the 繁中 toggle (translate step becomes required).
- `slide_cap` — max embedded slides/talk. here.now publishes fail >1000 files; cap = (1000 − overhead) / talks.
- `glossary`/`nonspeech` — transcript corrections; start empty, fill after reading the pilot transcript.
- Optional `kinds` — extra talk-kind pills: `{"demo": {"class":"fire","en":"Demo","zh":"示範"}}`. Built-ins: main/keynote (green), fireside (purple), track/talk (blue); `cutaway`+`nonspeech` are always excluded from the digest.

## Workflow

1. **Scope**: probe the source first (`video-digest-ingest` has probe scripts) — count videos, total duration. Estimate: download ~2–5 min/hour of video (≤720p); mlx-whisper large-v3-turbo ≈ 10–15× realtime on Apple Silicon; disk ~0.5–1 GB/hour.
2. **PILOT FIRST** on batches: run ONE item end-to-end (ingest → summarize → slides → site), inspect the output, fix config (glossary, kinds, prompts), then batch the rest. Never fan out 50 downloads before one full-path validation.
3. Batch: ingest serially (concurrent Whisper exhausts RAM). LLM stages fan out ~5 talks/agent — **on cheap models** (table below).
4. **Essay (default, every digest)**: after all talks are processed, run the site skill's corpus step and write the synthesis essay (`narrative.json`) with the STRONGEST model — plus `narrative.zh.json` if bilingual. Simon wants this on every digest.
5. Site: build, eyeball in browser, publish (here-now skill for folders, Artifact for single-file ≤8MB).
5. Register done items in `<project>/ingested.json` `{"items":{"<videoId>":{"group","item"}}}` so re-runs skip them.

## Model tiers — delegate grunt work to cheaper models

Fan-out LLM steps run as subagents; pick the model per stage (Agent tool `model` param):

| Stage | Model | Why |
|---|---|---|
| segment + verify | strong (session model) | fragile; drops talks if sloppy |
| summarize, takeaway | sonnet | mechanical per-talk text work |
| slide-select | haiku/sonnet | simple vision matching |
| slide-verify | sonnet | adversarial check of the cheap pass |
| translate | sonnet | routine; use opus only if quality complaints |
| essay synthesis | strongest available | cross-talk judgment, the flagship text |
| site build/publish | (scripts, no LLM) | — |

## Ops notes

- Every stage is idempotent per item — safe to re-run one item without touching others.
- LLM steps write files the next deterministic step reads; you can re-run any LLM step alone and rebuild the site.
- New talks appearing over time (ongoing playlist/channel): re-probe, ingest only unregistered items, rebuild site, republish to the same slug/URL.
