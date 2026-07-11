#!/usr/bin/env python3
"""Per-talk transcript slices + manifest.json (optionally lossless clips), driven by
talks.json. Usage: vd_sessions.py <item_dir> [--clips]"""
import csv, json, subprocess, sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
CLIPS_ON = "--clips" in sys.argv
SRC = ROOT / "source.mp4"
SESS = ROOT / "sessions"; SESS.mkdir(exist_ok=True)

def hms(t):
    h, m, s = map(int, t.split(":")); return h*3600 + m*60 + s

talks = json.loads((ROOT / "talks.json").read_text())["talks"]

segs = []
with open(ROOT / "transcript" / "transcript.tsv") as f:
    r = csv.reader(f, delimiter="\t"); next(r, None)
    for row in r:
        if len(row) < 3: continue
        try: segs.append((int(row[0]), int(row[1]), row[2]))
        except ValueError: pass

def slice_text(a, b):
    a, b = a*1000, b*1000; out = []
    for s, e, t in segs:
        if e < a or s > b: continue
        ts = s // 1000
        out.append(f"[{ts//3600:02d}:{(ts%3600)//60:02d}:{ts%60:02d}] {t.strip()}")
    return "\n".join(out)

whole_dur = hms(talks[-1]["end"]) if talks else 0
manifest = []
for t in talks:
    name = f"{t['id']:02d}_{t['slug']}"
    a, b = hms(t["start"]), hms(t["end"])
    kind = t["kind"]
    manifest.append({"id": t["id"], "start": t["start"], "end": t["end"], "duration_s": b - a,
        "title": t["title"], "speaker": t["speaker"], "confidence": t.get("confidence", ""),
        "program": {"kind": kind, "official_time": t.get("official_time", ""),
                    "on_main_stage_schedule": kind in ("main", "fireside", "keynote")},
        "reconciliation_note": t.get("note", ""), "clip": f"clips/{name}.mp4",
        "summary": f"sessions/{name}.md"})
    (SESS / f"{name}.txt").write_text(slice_text(a, b))
    whole = len(talks) == 1 and a == 0
    if CLIPS_ON and not whole:
        (ROOT / "clips").mkdir(exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", t["start"],
            "-to", t["end"], "-i", str(SRC), "-c", "copy", "-movflags", "+faststart",
            str(ROOT / "clips" / f"{name}.mp4")], check=True)
        print(f"cut {name}.mp4")

(ROOT / "manifest.json").write_text(json.dumps({"talks": manifest}, indent=2))
print(f"{ROOT.name}: {len(manifest)} talk(s), slices in sessions/")
