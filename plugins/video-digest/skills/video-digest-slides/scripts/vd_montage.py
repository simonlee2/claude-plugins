#!/usr/bin/env python3
"""Labeled montage grids per talk (rows=highlights, cols=3 candidates) for the vision
select pass. Writes montages/<stem>_pN.jpg + montages/index.json.
Usage: vd_montage.py <item_dir>   (needs Pillow: uv run --with pillow)"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(sys.argv[1]).resolve()
FRAMES = ROOT / "frames"
MON = ROOT / "montages"; MON.mkdir(exist_ok=True)
data = json.loads((ROOT / "highlights.json").read_text())

TW, TH, LBL, PAD, ROWS = 300, 169, 20, 6, 8
try: font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 14)
except Exception: font = ImageFont.load_default()

def load(stem, fn):
    p = FRAMES / stem / fn
    if not p.exists(): return None
    try: return Image.open(p).convert("RGB").resize((TW, TH))
    except Exception: return None

index = {}
for stem, tk in data.items():
    hls = tk["highlights"]
    pages = [hls[i:i+ROWS] for i in range(0, len(hls), ROWS)]
    pnames = []
    for pi, group in enumerate(pages):
        W = 3*TW + 4*PAD
        H = len(group)*(TH+LBL+PAD) + PAD
        canvas = Image.new("RGB", (W, H), (18, 20, 26))
        dr = ImageDraw.Draw(canvas)
        for r, hl in enumerate(group):
            y = PAD + r*(TH+LBL+PAD)
            for j in range(3):
                x = PAD + j*(TW+PAD)
                fn = hl["files"][j] if j < len(hl["files"]) else None
                tile = load(stem, fn) if fn else None
                dr.rectangle([x, y, x+TW, y+LBL], fill=(40, 44, 54))
                dr.text((x+4, y+2), f"h{hl['i']:02d}:{j}  {hl['ts']}", fill=(230, 233, 239), font=font)
                if tile: canvas.paste(tile, (x, y+LBL))
                else: dr.rectangle([x, y+LBL, x+TW, y+LBL+TH], fill=(30, 30, 30))
        name = f"{stem}_p{pi}.jpg"
        canvas.save(MON / name, quality=85)
        pnames.append(name)
    index[stem] = pnames
    print(f"{stem}: {len(pnames)} page(s), {len(hls)} highlights")

(MON / "index.json").write_text(json.dumps(index, indent=2))
print("done")
