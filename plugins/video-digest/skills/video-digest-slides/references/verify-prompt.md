# VERIFY each chosen frame matches its highlight (vision) → overwrite frames/sel_<name>.json
# (fan out ~5 talks/agent; model: sonnet — this is the check on the cheap select pass)

INPUTS: current picks {ITEM_DIR}/frames/sel_<name>.json; text in {ITEM_DIR}/highlights.json.
Candidate files: {ITEM_DIR}/frames/<name>/h<II>_<j>.jpg (II = 2-digit highlight index, j = 0/1/2).

For EACH highlight with a non-null pick: Read that chosen frame full-res. Does the slide clearly
support the highlight text (same topic / the stat/chart/diagram/title it refers to)?
- YES → keep. NO (speaker, unrelated/generic title, another talk's slide) → Read the other 2
  candidates and pick the best match; if none matches → null.
For null picks: Read the exact-time candidate (j=1); set it only if it's a matching slide, else leave null.
Be strict: keep only if a viewer would agree the slide goes with the point. When torn, prefer null.

Overwrite {ITEM_DIR}/frames/sel_<name>.json (every highlight index present). Return a concise
changelog of CHANGED highlights + reason, and kept/changed/nulled counts.
