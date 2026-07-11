#!/usr/bin/env python3
"""Clean the Whisper transcript: collapse loop/applause runs, drop empties, apply the
project glossary (digest.json, found by walking up from item_dir). Non-destructive
(*.clean.* outputs). Usage: vd_clean.py <item_dir>"""
import csv, json, re, sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
TSV = ROOT / "transcript" / "transcript.tsv"

CFG = {}
for p in ROOT.parents:
    if (p / "digest.json").exists():
        CFG = json.loads((p / "digest.json").read_text()); break
GLOSSARY = [(g[0], g[1]) for g in CFG.get("glossary", [])]
NONSPEECH = {s.lower() for s in CFG.get("nonspeech", [])} | {"thank you."}

def hms(ms):
    s = ms // 1000
    return f"{s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}"

def dedupe_internal(t):
    parts = [p.strip() for p in re.split(r'(?<=[.!?])\s+', t.strip()) if p.strip()]
    if len(parts) > 1 and len(set(p.lower() for p in parts)) == 1:
        return parts[0]
    toks = [p.strip() for p in re.split(r'[,.!?]+', t) if p.strip()]
    if len(toks) >= 8 and len(set(tok.lower() for tok in toks)) <= 3:
        seen, keep = set(), []
        for tok in toks:
            k = tok.lower()
            if k not in seen:
                seen.add(k); keep.append(tok)
        return ", ".join(keep) + f". ⟨⚠ transcription glitch: phrase repeated ×{len(toks)}⟩"
    return t.strip()

rows = []
with open(TSV) as f:
    r = csv.reader(f, delimiter="\t"); next(r, None)
    for x in r:
        if len(x) < 3: continue
        try: rows.append((int(x[0]), int(x[1]), dedupe_internal(x[2])))
        except ValueError: pass

counts = {}
def apply_glossary(text):
    for pat, repl in GLOSSARY:
        text, n = re.subn(pat, repl, text, flags=re.IGNORECASE)
        if n: counts[repl] = counts.get(repl, 0) + n
    return text

ne = [(s, e, t) for (s, e, t) in rows if t]
dropped_empty = len(rows) - len(ne)
segs, i = [], 0
while i < len(ne):
    s, e, t = ne[i]; j = i
    while j + 1 < len(ne) and ne[j + 1][2].strip().lower() == t.strip().lower():
        j += 1
    segs.append((s, apply_glossary(t), j - i + 1)); i = j + 1

def render(seg):
    s, t, run = seg
    if run >= 10 and t.strip().lower() in NONSPEECH:
        return f"[{hms(s)}] ⟨applause / hold — non-speech (“{t}” ×{run})⟩"
    if run >= 10: return f"[{hms(s)}] {t}  ⟨⚠ transcription glitch: repeated ×{run}⟩"
    if run >= 3: return f"[{hms(s)}] {t}  ⟨×{run}⟩"
    return f"[{hms(s)}] {t}"

(ROOT / "transcript" / "transcript.clean.txt").write_text("\n".join(render(x) for x in segs) + "\n")

def to_s(t):
    h, m, sec = map(int, t.split(":")); return h*3600 + m*60 + sec
n_slices = 0
if (ROOT / "manifest.json").exists():
    for talk in json.loads((ROOT / "manifest.json").read_text())["talks"]:
        a, b = to_s(talk["start"])*1000, to_s(talk["end"])*1000
        sl = [x for x in segs if a <= x[0] <= b]
        (ROOT / "sessions" / f"{Path(talk['clip']).stem}.clean.txt").write_text(
            "\n".join(render(x) for x in sl) + "\n")
        n_slices += 1

rep = ["# Transcript cleanup report", "",
       f"- Raw segments: **{len(rows):,}**",
       f"- Empty dropped: **{dropped_empty:,}** · after collapsing: **{len(segs):,}**",
       f"- Cleaned slices: **{n_slices}**", "", "## Term corrections applied"]
rep += [f"- {t}: {c}" for t, c in sorted(counts.items(), key=lambda kv: -kv[1])] or ["- (none)"]
(ROOT / "transcript" / "corrections.md").write_text("\n".join(rep) + "\n")
print(f"raw={len(rows)} clean={len(segs)} slices={n_slices} corrections={sum(counts.values())}")
