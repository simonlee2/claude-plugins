#!/usr/bin/env python3
"""Probe a digest source: YouTube playlist/channel URL or a local folder of videos.
Prints a worklist (idx, id, duration, title) + totals and ingest estimates.
Usage: vd_probe.py <url|folder> [--json out.json]"""
import json, subprocess, sys
from pathlib import Path

VIDEO_EXT = {".mp4", ".mkv", ".webm", ".mov", ".m4v", ".avi"}

def probe_url(url):
    r = subprocess.run(["yt-dlp", "--flat-playlist", "-J", url],
                       capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    entries = d.get("entries") or [d]  # single video → treat as 1-entry list
    items = []
    for i, e in enumerate(entries, 1):
        items.append({"idx": i, "id": e.get("id"), "title": e.get("title"),
                      "duration": e.get("duration"),
                      "url": e.get("url") or f"https://youtu.be/{e.get('id')}"})
    return d.get("title") or url, items

def probe_folder(folder):
    items = []
    files = sorted(p for p in Path(folder).iterdir() if p.suffix.lower() in VIDEO_EXT)
    for i, p in enumerate(files, 1):
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "default=nk=1:nw=1", str(p)], capture_output=True, text=True)
        try: dur = float(r.stdout.strip())
        except ValueError: dur = None
        items.append({"idx": i, "id": p.stem, "title": p.stem,
                      "duration": dur, "url": str(p.resolve())})
    return str(folder), items

def main():
    src = sys.argv[1]
    title, items = probe_folder(src) if Path(src).is_dir() else probe_url(src)
    ok = [x for x in items if x["duration"]]
    skipped = [x for x in items if not x["duration"]]
    print(f"SOURCE: {title}\nITEMS: {len(ok)} usable, {len(skipped)} unavailable/live (skipped)")
    for x in ok:
        m = int(x["duration"] // 60)
        print(f"  {x['idx']:3d}. [{m:3d}m] {x['id']}  {x['title']}")
    for x in skipped:
        print(f"  ---. [ ? ] {x['id']}  {x['title']}  (SKIP)")
    tot_h = sum(x["duration"] for x in ok) / 3600
    print(f"\nTOTAL: {tot_h:.1f} h of video")
    print(f"ESTIMATES: download ~{tot_h*3:.0f}–{tot_h*5:.0f} min · "
          f"transcribe ~{tot_h*60/12:.0f} min (mlx-whisper ≈12× realtime, serial) · "
          f"disk ~{tot_h*0.7:.1f} GB")
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        Path(out).write_text(json.dumps({"source": title, "items": ok}, indent=2))
        print(f"worklist → {out}")

if __name__ == "__main__":
    main()
