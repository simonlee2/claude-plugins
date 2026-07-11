---
name: video-digest-site
description: Build and publish the digest website from processed video-digest content - overview card grid, per-talk detail pages with slides and takeaways, YouTube deep links, optional EN/Traditional-Chinese toggle and a cited synthesis essay. Stage 5 (final) of the video-digest pipeline. Use when rendering or publishing a video digest site, or refreshing it after new talks.
---

# video-digest-site

Input: project dir with `digest.json` + processed `groups/<group>/<item>/` (manifest, highlights, sel_*, take.json; optional zh.json). Needs Pillow.

## Build

```
python3 scripts/vd_site.py <project>                 # single-file digest.html (data-URI images)
python3 scripts/vd_site.py <project> --dist <project>/dist   # folder site (index.html + assets/)
```

- **Single file**: for the claude.ai Artifact tool. HARD CAP ~8 MB — over ~10 MB hosted artifacts truncate/403. Size is slide-count-bound; levers: `slide_cap` in digest.json, IMG_W/IMG_Q in the script. Big events → use dist mode instead.
- **Dist folder**: crisp 900px slides as separate files; publish with the `here-now` skill:
  `bash ~/.claude/skills/here-now/scripts/publish.sh <project>/dist --slug <slug> --client claude` (re-publish to the SAME slug to update). here.now fails >1000 files — check `ls dist/assets | wc -l`; if near, lower `slide_cap`.
- Talks/highlights link to YouTube (`source.json` url) at the right timestamp automatically.

## Verify before publishing

Open the built file in a browser (or agent-browser skill): check a card → detail → slide captions render, hash routing works (#back button), no horizontal scroll, and (if zh) the toggle.

## Optional: synthesis essay (extra tab)

1. `python3 scripts/vd_corpus.py <project>` → `narrative_corpus.md` + `narrative_cite_index.txt`.
2. STRONG model reads both, writes `<project>/narrative.json`:
   `{title,dek,reading_time,sections:[{kicker,heading,blocks:[{type:"para"|"pull",text}]}],coda}` —
   thesis + 3-5 themed sections + coda; inline `[[sid]]` citations ONLY from the cite index (rendered as numbered superscript links + "Talks cited" list).
3. Optional `narrative.zh.json` (same shape, `[[sid]]` preserved verbatim).
4. Rebuild — the essay tab appears automatically when narrative.json exists. Config: digest.json `essay_tab` (tab/CTA label), `essay: {kicker, byline}`.

## digest.json knobs used here

`title, brand, kicker, headline, lede, footer` (string or `{en,zh}`), `languages` (zh enables toggle), `slide_cap`, `kinds` (pill class/labels), `essay_tab`, `essay`. See the `video-digest` umbrella skill.
