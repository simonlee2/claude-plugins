#!/usr/bin/env python3
"""Author metadata for a SINGLE-talk item (playlist entry / lone video): 1-talk
talks.json spanning the real duration + source.json. Multi-talk streams: don't
use this — run the segment stage instead.
Usage: vd_single.py <item_dir> --title T --speaker "Name · Org" [--kind talk] [--url U]"""
import argparse, json, re, subprocess
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("item_dir"); ap.add_argument("--title", required=True)
ap.add_argument("--speaker", default=""); ap.add_argument("--kind", default="talk")
ap.add_argument("--url", default="")
a = ap.parse_args()
d = Path(a.item_dir)

dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
    "-of", "default=nk=1:nw=1", str(d / "source.mp4")], capture_output=True, text=True,
    check=True).stdout.strip())
end = f"{int(dur//3600):02d}:{int(dur%3600//60):02d}:{int(dur%60):02d}"

slug = re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", a.title.lower())).strip("-")[:48] or d.name
(d / "source.json").write_text(json.dumps(
    {"key": d.name, "label": a.title[:80], "subtitle": a.speaker, "url": a.url}, indent=2))
(d / "talks.json").write_text(json.dumps({"talks": [{
    "id": 1, "start": "00:00:00", "end": end, "slug": slug, "title": a.title,
    "speaker": a.speaker, "kind": a.kind, "official_time": "", "confidence": "high",
    "note": ""}]}, indent=2))
print(f"{d.name}: 1 talk, 00:00:00–{end}")
