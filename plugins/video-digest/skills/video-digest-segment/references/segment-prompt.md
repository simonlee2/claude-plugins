# SEGMENT a multi-talk video into talks → {ITEM_DIR}/talks.json

One agent. Read the 30s timeline (+ schedule if present), output the ordered talk list.

INPUTS (read):
- {ITEM_DIR}/transcript/timeline_30s.txt — "HH:MM:SS  <text>" per 30s (video offsets).
- {ITEM_DIR}/schedule.txt — authoritative schedule if present (titles, speakers, wall times).
- May grep {ITEM_DIR}/transcript/transcript.tsv (start_ms<TAB>end_ms<TAB>text) for precision.

CONTEXT: {CONTEXT}
(e.g. "Main-stage stream of X conf; the feed can cut away to other stages. Video offset ≈ wall clock − HH:MM; talks drift a few minutes — trust transcript CONTENT over the clock." Paste schedule facts here.)

SIGNALS: speaker self-intros ("I'm X from Y", "please welcome"), applause/transition gaps, topic
shifts matching the next scheduled talk. A long wall of one repeated phrase = applause/non-speech.

TASK: produce the ordered list of REAL talks (exclude pre-roll/breaks/MC filler). For each talk:
- id (1-based video order), start, end ("HH:MM:SS", trim leading applause), slug (kebab),
- title (official exact wording when scheduled; else best content-derived),
- speaker ("Name · Org"),
- kind: "main"|"keynote" (headline) | "fireside" | "talk"/"track" (real talk, not headline) |
  "cutaway" (feed cut to other content — excluded from digest),
- official_time (wall clock or ""), confidence (high|med|low), note (self-intro quote / ambiguity).
Skip pure non-speech; dedupe feed re-shows.

## VERIFY before writing (critical — single-pass reading MISSES talks on braided regions)
Walk the schedule (or your own talk list) in order; for EACH expected talk, grep transcript.tsv
for its speaker's self-intro / distinctive title phrase and confirm it appears — if it does, it
MUST be in talks.json, even if a cutaway overlaps the same window. Overlapping windows are fine
(the feed cut back and forth). Don't drop a scheduled talk because a cutaway is loud in that region.

OUTPUT: write {ITEM_DIR}/talks.json = {"talks":[{id,start,end,slug,title,speaker,kind,official_time,confidence,note},...]}.
Also write {ITEM_DIR}/sessions/boundaries.json with your full reasoning (incl. nonspeech ranges) for audit.
Return a compact table (id, start–end, kind, title, speaker) + note anything ambiguous.
