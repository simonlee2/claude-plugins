# SELECT the slide frame per highlight (vision) → frames/sel_<name>.json
# (fan out ~5 talks/agent; CHEAP model: haiku or sonnet)

INPUTS: montages {ITEM_DIR}/montages/<name>_pN.jpg (page names in montages/index.json);
highlight text in {ITEM_DIR}/highlights.json. Each montage row is one highlight; the 3 columns
are candidates labeled "hII:j  HH:MM:SS" where j=0 is −5s, 1 is exact, 2 is +5s.

For EACH highlight i, choose the candidate j (0/1/2) whose image is a CLEAN, readable slide
belonging to THIS talk (text/bullets/chart/diagram/code/title). Choose **null** if none is a
usable slide (speaker/host/audience/wide stage, sponsor-logo wall, black/transition frame, or
clearly a DIFFERENT talk's slide). Tie-breakers: best match to the highlight text; most readable;
prefer j=1 (exact) when equal. Firesides/demo-only talks: null is expected.

Read each montage with the Read tool. WRITE {ITEM_DIR}/frames/sel_<name>.json =
{"0": j-or-null, "1": ...} including EVERY highlight index. Return one line per talk (e.g. "7/9 slides").
