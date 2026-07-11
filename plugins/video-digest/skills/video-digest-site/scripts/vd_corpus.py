#!/usr/bin/env python3
"""Synthesis-essay corpus: every included talk's summary + takeaway, with [[sid]]
citation keys matching vd_site.py numbering. Feed the corpus to a strong model to
write narrative.json. Usage: vd_corpus.py [project_dir]"""
import json, os, sys
from pathlib import Path

PROJ = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
def included(k): return k not in ("cutaway", "nonspeech")

out, cites, n = [], {}, 0
for gdir in sorted((PROJ / "groups").iterdir()):
    if not (gdir / "group.json").exists(): continue
    gj = json.loads((gdir / "group.json").read_text()); gk = gj["key"]
    idirs = [d for d in gdir.iterdir() if d.is_dir() and (d / "manifest.json").exists()]
    forder = gj.get("order")
    idirs = sorted(idirs, key=(lambda d: forder.index(d.name)) if forder else (lambda d: d.name))
    out.append(f"\n\n{'='*70}\n# {gj['label']}\n{'='*70}")
    for idir in idirs:
        if not (idir / "highlights.json").exists(): continue
        sj = json.loads((idir / "source.json").read_text()) if (idir / "source.json").exists() else {"key": idir.name}
        data = json.loads((idir / "highlights.json").read_text())
        order = [os.path.splitext(os.path.basename(t["clip"]))[0]
                 for t in json.loads((idir / "manifest.json").read_text())["talks"]]
        inc = [s for s in order if included(data[s]["program"]["kind"])]
        for seq, stem in enumerate(inc, 1):
            tk = data[stem]; sid = f"{gk}-{sj['key']}-t{seq}"
            cites[sid] = {"speaker": tk["speaker"], "title": tk["title"], "day": gj["label"]}
            out.append(f"\n\n### [[{sid}]] {tk['title']} — {tk['speaker']}  (kind={tk['program']['kind']})")
            md = idir / "sessions" / f"{stem}.md"
            if md.exists(): out.append(md.read_text().strip())
            tf = idir / "sessions" / f"{stem}.take.json"
            if tf.exists(): out.append("TAKEAWAY: " + json.dumps(json.loads(tf.read_text()), ensure_ascii=False))
            n += 1

(PROJ / "narrative_corpus.md").write_text("\n".join(out))
(PROJ / "narrative_cite_index.txt").write_text(
    "\n".join(f"[[{s}]] = {c['speaker']} — {c['title']} ({c['day']})" for s, c in cites.items()))
print(f"corpus: {n} talks → narrative_corpus.md, narrative_cite_index.txt")
