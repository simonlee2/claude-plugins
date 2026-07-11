# TRANSLATE an item's digest text to Traditional Chinese → {ITEM_DIR}/zh.json
# (one agent per item or ~5 talks/agent; cheap model: sonnet)

Produce zh-Hant (繁體中文, Taiwan usage) translations of every INCLUDED talk's user-facing text.

INPUTS (read):
- {ITEM_DIR}/highlights.json — per stem: title, program.kind, highlights[] (each has `i` + `text`).
- {ITEM_DIR}/sessions/<stem>.take.json — tldr, takeaway.
- {ITEM_DIR}/manifest.json — talk order.
INCLUDED = program.kind NOT "cutaway"/"nonspeech". Translate ONLY those.

TRANSLATE: title, tldr, takeaway, every highlight `text`.
DO NOT translate: speaker/company/product names, well-known acronyms (RAG, MCP, GPU, API, SDK,
LLM, PR, CI…), code in `backticks`, proper nouns. Preserve **bold** and `code` markup exactly.
Tight, idiomatic technical Chinese a senior TW/HK engineer would write — not a literal gloss;
leave English jargon where translating reduces clarity.

OUTPUT — write {ITEM_DIR}/zh.json keyed by stem exactly as in highlights.json:
{"<stem>": {"title":"…","tldr":"…","takeaway":"…","hl":{"0":"…","1":"…", …every highlight i}}, …}
Every included stem present; every highlight index present under "hl". Valid JSON only.
Return a one-line count (talks × strings).
