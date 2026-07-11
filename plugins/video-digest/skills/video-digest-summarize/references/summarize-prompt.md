# SUMMARIZE each talk → sessions/<name>.md   (fan out ~5 talks/agent, cheap model: sonnet)

INPUT: {ITEM_DIR}/sessions/<name>.txt — lines "[HH:MM:SS] text" (video offsets).
Auto-transcribed (Whisper): silently fix obvious ASR errors (names/products) from context; don't invent.

For each assigned talk WRITE {ITEM_DIR}/sessions/<name>.md EXACTLY:

# <Title>
**Speaker:** <speaker/org>
**Segment:** [<first ts>–<last ts>]

## Summary
3–5 sentences, concrete (what it argued/covered). For a fireside/long talk, up to 6.

## Highlights
- **[HH:MM:SS]** point   (6–9 bullets; 9–12 for a long talk/fireside; real timestamps from the slice, in order)
- Prefix the 2–4 most essential highlights with `★ ` (e.g. `- **[00:12:30]** ★ point`) — the ones whose slide is core to the thesis/takeaway. These win when slide space is tight. Star sparingly; most bullets stay unmarked.

## Notable quotes
> "quote" — [HH:MM:SS]
(1–3; omit the section if nothing quotable; clean filler but keep faithful)

If a slice is degraded/short add at top: "> ⚠️ Note: audio partially garbled; summary approximate."
Return only a short list of files written.
