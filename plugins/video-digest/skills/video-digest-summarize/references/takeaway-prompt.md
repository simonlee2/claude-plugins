# TL;DR + practical takeaway → sessions/<name>.take.json   (fan out ~5 talks/agent, cheap model: sonnet)

INPUT: {ITEM_DIR}/sessions/<name>.md (summary + highlights).

For each WRITE {ITEM_DIR}/sessions/<name>.take.json = {"tldr": "...", "takeaway": "..."}:
- tldr: 1–2 punchy sentences capturing the core thesis. No fluff, no "in this talk".
- takeaway: 2–3 sentences on what {AUDIENCE} should DO or remember because of this talk —
  a concrete decision, practice, tool, or mental model. Specific to the content, not generic.
Ground strictly in the summary; don't invent. Return a one-line-per-talk confirmation.
