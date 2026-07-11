---
name: video-digest-segment
description: Segment a long multi-talk video (conference stream, all-day recording) into individual talks by reading its transcript timeline - produces talks.json for the video-digest pipeline. Stage 2; skip for single-talk videos (video-digest-ingest's vd_single.py handles those). Use when a digest source video contains multiple talks/sessions.
---

# video-digest-segment

LLM stage — no scripts. Input: `<item_dir>/transcript/timeline_30s.txt` (from ingest). Output: `<item_dir>/talks.json`.

## This is the fragile stage — read this before running

A single pass over a braided feed (stream cutting between stages, re-shows, MC filler) **drops real talks**. Always run the verification pass below.

## Procedure

1. If an authoritative schedule exists (conference program page, description chapters, `chapters.txt`), save it to `<item_dir>/schedule.txt` — titles/speakers/times in order. It's reconciliation ground truth. No schedule → derive talks purely from content.
2. Run the segmentation prompt: `references/segment-prompt.md` (fill `{ITEM_DIR}`, `{CONTEXT}`, paste schedule facts). One agent for the whole stream.
3. **VERIFY (mandatory)**: walk the schedule (or the talk list you produced) in order; for EACH expected talk, grep `transcript/transcript.tsv` for the speaker's self-intro or a distinctive title phrase and confirm a matching entry exists in talks.json. A scheduled talk braided with cutaways must still appear (kind main/talk) even if windows overlap. Timestamps drift — trust transcript CONTENT over scheduled clock times.
4. Sanity-check output: talks ordered by start; `start`/`end` "HH:MM:SS"; leading applause trimmed; kinds valid.

## talks.json schema

```json
{"talks":[{"id":1,"start":"00:12:30","end":"00:31:05","slug":"kebab-slug",
  "title":"...","speaker":"Name · Org","kind":"main",
  "official_time":"9:15am|","confidence":"high|med|low","note":"self-intro quote / ambiguity"}]}
```
kinds: `main`/`keynote` (headline), `fireside`, `track`/`talk` (regular), `cutaway` (feed cut to other content — excluded from digest), `nonspeech` (excluded). Exclude pure breaks/pre-roll entirely; dedupe re-shows.
