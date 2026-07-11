#!/usr/bin/env python3
"""Extract candidate frames per highlight (offsets -5s/0/+5s) so a vision pass can
pick the one showing a slide. Writes frames/<stem>/hNN_{0,1,2}.jpg + highlights.json.
Usage: vd_frames.py <item_dir>"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
SRC = str(ROOT / "source.mp4")
FRAMES = ROOT / "frames"
OFFSETS = [-5, 0, 5]
man = json.loads((ROOT / "manifest.json").read_text())["talks"]

def to_s(t): h, m, s = map(int, t.split(":")); return h*3600 + m*60 + s

def parse_highlights(md):
    out = []
    for ln in md.read_text().splitlines():
        m = re.match(r"\s*[-*]\s*\*\*\[(\d\d:\d\d:\d\d)\]\*\*\s*(.+)", ln)
        if m:
            text = re.sub(r"\*\*", "", m.group(2)).strip()
            w = 1.0
            mk = re.match(r"^[★⭐]\s*(.+)", text)   # leading star = key slide, wins when space is tight
            if mk: w, text = 2.0, mk.group(1).strip()
            out.append((to_s(m.group(1)), m.group(1), text, w))
    return out

data = {}
for tk in man:
    stem = Path(tk["clip"]).stem
    a, b = to_s(tk["start"]), to_s(tk["end"])
    d = FRAMES / stem; d.mkdir(parents=True, exist_ok=True)
    items = []
    for i, (tsec, ts, text, w) in enumerate(parse_highlights(ROOT / "sessions" / f"{stem}.md")):
        files = []
        for j, off in enumerate(OFFSETS):
            tt = min(max(tsec + off, a + 1), b - 1)
            fn = d / f"h{i:02d}_{j}.jpg"
            subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", str(tt),
                "-i", SRC, "-frames:v", "1", "-q:v", "3", "-vf", "scale=960:-1", str(fn)], check=False)
            if fn.exists() and fn.stat().st_size > 0:
                files.append(fn.name)
        hl = {"i": i, "ts": ts, "sec": tsec, "text": text, "files": files}
        if w != 1.0: hl["weight"] = w
        items.append(hl)
    data[stem] = {"id": tk["id"], "title": tk["title"], "start": tk["start"],
                  "speaker": tk["speaker"], "program": tk["program"], "highlights": items}
    print(f"{stem}: {len(items)} highlights")

(ROOT / "highlights.json").write_text(json.dumps(data, indent=2))
print("wrote highlights.json")
