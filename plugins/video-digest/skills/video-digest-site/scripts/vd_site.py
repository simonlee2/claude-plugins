#!/usr/bin/env python3
"""Merge groups/<group>/<item>/ into ONE digest site: overview grid of session cards
→ per-session detail (TL;DR, takeaway, slides). Hash-routed, deep-linkable. Optional
EN/繁中 toggle (zh.json / narrative.zh.json) and synthesis-essay tab (narrative.json).
Branding/labels from <project>/digest.json.

Usage: vd_site.py [project_dir] [--dist <out_dir>]
  default: single self-contained HTML (data-URI images) → <project>/digest.html
  --dist:  external image files (crisp, not size-capped)  → <out_dir>/index.html
Needs Pillow (uv run --with pillow)."""
import base64, html, io, json, re, sys
from pathlib import Path
from PIL import Image

args = [a for a in sys.argv[1:]]
DIST = None
if "--dist" in args:
    i = args.index("--dist"); DIST = Path(args[i + 1]).resolve(); del args[i:i + 2]
PROJ = Path(args[0]).resolve() if args else Path.cwd()

CFG = json.loads((PROJ / "digest.json").read_text()) if (PROJ / "digest.json").exists() else {}
def cfg_t(key, default=""):
    v = CFG.get(key, default)
    if isinstance(v, dict): return v.get("en", default), v.get("zh", "")
    return v, ""

GROUPS = sorted(d for d in (PROJ / "groups").iterdir() if d.is_dir() and (d / "group.json").exists())
IMG_W, IMG_Q = (900, 62) if DIST else (600, 50)
THUMB_W, THUMB_Q = (480, 58) if DIST else (400, 52)
# Slide budget (see _allocate_slides). No flat per-talk cap: keep every distinct slide up
# to SLIDE_CEILING; trim only when the total exceeds SLIDE_BUDGET, and then globally.
# DIST is file-count bound (here.now ~1000 files), so it's effectively uncapped; the
# single-file artifact is size bound (~8MB of data-URIs), so it gets a real budget.
SLIDE_CEILING = CFG.get("slide_ceiling", 40)          # per-talk safety ceiling
SLIDE_FLOOR   = CFG.get("slide_floor", 3)             # min slides a talk keeps when trimming
SLIDE_BUDGET  = CFG.get("slide_budget", 10_000 if DIST else 300)
DEDUP_THRESH  = CFG.get("dedup_threshold", 2.0)       # mean abs diff (0-255) on 16x16 gray; <=0 disables

# kind -> (color class, EN label, ZH label); digest.json "kinds" can add/override
PB = {"main": ("main", "Main Stage", "主舞台"), "keynote": ("main", "Keynote", "主題演講"),
      "fireside": ("fire", "Fireside", "爐邊對談"), "track": ("cut", "Talk", "議程"),
      "talk": ("cut", "Talk", "議程")}
for k, v in CFG.get("kinds", {}).items():
    PB[k] = (v.get("class", "cut"), v.get("en", k.title()), v.get("zh", v.get("en", k.title())))
def included_kind(k): return k not in ("cutaway", "nonspeech")

_ASSET_N = 0
def _img(path, w, q):
    global _ASSET_N
    im = Image.open(path).convert("RGB")
    if im.width > w: im = im.resize((w, round(im.height * w / im.width)))
    if DIST:
        (DIST / "assets").mkdir(parents=True, exist_ok=True)
        _ASSET_N += 1; name = f"s{_ASSET_N:04d}.jpg"
        im.save(DIST / "assets" / name, "JPEG", quality=q, optimize=True)
        return f"assets/{name}"
    b = io.BytesIO(); im.save(b, "JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
def data_uri(p): return _img(p, IMG_W, IMG_Q)
def thumb_uri(p): return _img(p, THUMB_W, THUMB_Q)

# --- near-duplicate slide detection: 16x16 grayscale, mean abs per-pixel diff (0-255) ---
_SIG = {}
def _sig(path):
    k = str(path)
    if k not in _SIG:
        _SIG[k] = list(Image.open(path).convert("L").resize((16, 16)).getdata())
    return _SIG[k]
def _delta(a, b):
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a) if len(a) == len(b) else float("inf")
def _is_dup(path, kept):
    """True if `path` matches an already-kept slide in this talk; else record it and return False."""
    if DEDUP_THRESH <= 0: return False
    sig = _sig(path)
    if any(_delta(sig, k) <= DEDUP_THRESH for k in kept): return True
    kept.append(sig); return False

def fmt(s):
    s = html.escape(s or ""); s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", s)
def esc(s): return html.escape(s or "")

def _load(p):
    try: return json.loads(p.read_text()) if p.exists() else None
    except Exception: return None
ESSAY = _load(PROJ / "narrative.json")
ESSAY_ZH = _load(PROJ / "narrative.zh.json")
HAS_ZH = "zh" in CFG.get("languages", ["en"]) or ESSAY_ZH is not None

def T(en, zh=None):
    """Bilingual span pair (already-rendered HTML); zh falls back to en."""
    if not HAS_ZH: return en
    z = zh if (zh not in (None, "")) else en
    return f'<span class="t-en">{en}</span><span class="t-zh">{z}</span>'

def ytlink(url, sec):
    if not url: return ""
    return f"{url}{'&' if '?' in url else '?'}t={int(sec)}s"

# --- essay citations: [[sid]] -> numbered superscript link ---
CITE_META = {}; CITES = {}; CITE_ORDER = []
def _cite_sub(m):
    sid = m.group(1)
    if sid not in CITES: CITE_ORDER.append(sid); CITES[sid] = len(CITE_ORDER)
    c = CITE_META.get(sid)
    t = esc(c["speaker"] + " — " + c["title"]) if c else sid
    return f'<sup class="cn"><a href="#{sid}" title="{t}">{CITES[sid]}</a></sup>'
def rich(x): return re.sub(r"\[\[([a-z0-9\-]+)\]\]", _cite_sub, fmt(x))

def build_item(group_key, sdir):
    meta = _load(sdir / "source.json") or {"key": sdir.name, "label": sdir.name.title(), "subtitle": ""}
    skey = meta["key"]; url = meta.get("url", "")
    data = json.loads((sdir / "highlights.json").read_text())
    zh = _load(sdir / "zh.json") or {}
    man = json.loads((sdir / "manifest.json").read_text())["talks"]
    order = [Path(t["clip"]).stem for t in man]
    inc = [s for s in order if included_kind(data[s]["program"]["kind"])]
    items = []
    for seq, stem in enumerate(inc, 1):
        tk = data[stem]; prog = tk["program"]; sid = f"{group_key}-{skey}-t{seq}"
        zt = zh.get(stem, {}); zhl = zt.get("hl", {}) or {}
        sel = _load(sdir / "frames" / f"sel_{stem}.json") or {}
        take = _load(sdir / "sessions" / f"{stem}.take.json") or {}
        pc, pl_en, pl_zh = PB.get(prog["kind"], ("cut", "Talk", "議程"))
        # Collect candidate slides only (dedup within the talk); images are materialized
        # later in _allocate_slides once the global total is known. `_src`/`_w` are temp.
        beats = []; kept_sigs = []
        for hl in tk["highlights"]:
            j = sel.get(str(hl["i"])); en = fmt(hl["text"])
            zx = zhl.get(str(hl["i"])); zb = fmt(zx) if zx else None
            beat = {"img": None, "en": en, "zh": zb, "ts": hl["ts"], "link": ytlink(url, hl["sec"]),
                    "_src": None, "_w": float(hl.get("weight", 1.0))}
            if isinstance(j, int) and 0 <= j < len(hl["files"]):
                fp = sdir / "frames" / stem / hl["files"][j]
                if fp.exists() and not _is_dup(fp, kept_sigs):
                    beat["_src"] = fp
            beats.append(beat)
        h, m, s = map(int, tk["start"].split(":"))
        items.append({"sid": sid, "seq": seq, "kind": prog["kind"], "pc": pc, "pl_en": pl_en,
            "pl_zh": pl_zh, "time": prog.get("official_time", ""), "title": tk["title"],
            "title_zh": zt.get("title", ""), "speaker": tk["speaker"],
            "tldr": take.get("tldr", ""), "tldr_zh": zt.get("tldr", ""),
            "takeaway": take.get("takeaway", ""), "takeaway_zh": zt.get("takeaway", ""),
            "beats": beats, "thumb": "", "n_slides": 0,
            "watch": ytlink(url, h*3600 + m*60 + s)})
    return items

def build_group(gdir):
    gmeta = json.loads((gdir / "group.json").read_text())
    idirs = [d for d in gdir.iterdir() if d.is_dir() and (d / "highlights.json").exists()]
    forder = gmeta.get("order")
    idirs = sorted(idirs, key=(lambda d: forder.index(d.name)) if forder else (lambda d: d.name))
    items = [it for d in idirs for it in build_item(gmeta["key"], d)]
    return {"meta": gmeta, "key": gmeta["key"], "items": items,
            "n_talks": len(items), "n_slides": 0}

def _allocate_slides(groups):
    """Decide how many slides each talk keeps, then materialize them.

    No flat per-talk cap. If every distinct (deduped) slide fits under SLIDE_BUDGET, keep
    them all (capped per talk only by SLIDE_CEILING). Otherwise trim GLOBALLY: each talk
    keeps a floor, the remaining budget is shared proportional to each talk's distinct
    slide count (long/dense talks earn more), and within a talk the highest-weight
    (★-marked) slides win. Cross-talk share is by size (calibrated); which slides survive
    inside a talk is by weight (value)."""
    items = [it for g in groups for it in g["items"]]
    for it in items:
        it["_cands"] = [b for b in it["beats"] if b["_src"] is not None]
    cap = {id(it): min(len(it["_cands"]), SLIDE_CEILING) for it in items}
    total = sum(len(it["_cands"]) for it in items)
    if total <= SLIDE_BUDGET:
        keep = dict(cap)
    else:
        keep = {id(it): min(SLIDE_FLOOR, cap[id(it)]) for it in items}
        remaining = SLIDE_BUDGET - sum(keep.values())
        extra = {id(it): cap[id(it)] - keep[id(it)] for it in items}
        pool = sum(extra.values())
        if remaining > 0 and pool > 0:                      # largest-remainder apportionment
            raw = {k: remaining * extra[k] / pool for k in extra}
            add = {k: min(int(raw[k]), extra[k]) for k in raw}
            leftover = remaining - sum(add.values())
            frac = sorted((k for k in raw if add[k] < extra[k]),
                          key=lambda k: raw[k] - int(raw[k]), reverse=True)
            for k in frac[:max(0, leftover)]: add[k] += 1
            for k in keep: keep[k] += add[k]
    for it in items:
        order = sorted(range(len(it["_cands"])),
                       key=lambda idx: (-it["_cands"][idx]["_w"], idx))   # weight desc, then order
        keepset = set(order[:keep[id(it)]])
        for idx, b in enumerate(it["_cands"]):
            if idx in keepset: b["img"] = data_uri(b["_src"])             # materialize kept only
        it["thumb"] = next((b["img"] for b in it["beats"] if b["img"]), "")
        it["n_slides"] = sum(1 for b in it["beats"] if b["img"])
        for b in it["beats"]: b.pop("_src", None); b.pop("_w", None)
        it.pop("_cands", None)
    for g in groups:
        g["n_slides"] = sum(it["n_slides"] for it in g["items"])
    kept = sum(g["n_slides"] for g in groups); mode = "dist" if DIST else "single-file"
    if total > kept:
        print(f"slide budget ({mode}): kept {kept}/{total} distinct slides — trimmed {total - kept} to fit budget {SLIDE_BUDGET}")
    else:
        print(f"slides ({mode}): {kept} distinct kept (dedup≤{DEDUP_THRESH}, no budget trim)")
    if DIST and kept > 900:
        print(f"WARNING: {kept} slide files — here.now caps ~1000; consider splitting per day/group")

groups = [g for g in (build_group(d) for d in GROUPS) if g["items"]]
if not groups:
    raise SystemExit("no talks found under groups/<group>/<item>/")
multi = len(groups) > 1
_allocate_slides(groups)
tot_talks = sum(g["n_talks"] for g in groups)
tot_slides = sum(g["n_slides"] for g in groups)
for _g in groups:
    for _it in _g["items"]:
        CITE_META[_it["sid"]] = {"speaker": _it["speaker"], "title": _it["title"],
                                 "title_zh": _it["title_zh"], "day": _g["meta"]["label"]}

def render_essay(nar, narz):
    narz = narz or {}
    zsecs = narz.get("sections", [])
    body = []
    for i, sec in enumerate(nar.get("sections", [])):
        z = zsecs[i] if i < len(zsecs) else {}
        zblk = z.get("blocks", [])
        blk = []
        for j, b in enumerate(sec.get("blocks", [])):
            zt = zblk[j].get("text") if j < len(zblk) else None
            cap = T(rich(b.get("text", "")), rich(zt) if zt else None)
            if b.get("type") == "pull":
                blk.append(f'<blockquote class="pull"><p>{cap}</p></blockquote>')
            else:
                blk.append(f'<p>{cap}</p>')
        body.append(f'<section class="esec"><p class="ekick">{T(esc(sec.get("kicker", "")), esc(z.get("kicker", "")))}</p>'
                    f'<h2>{T(esc(sec.get("heading", "")), esc(z.get("heading", "")))}</h2>{"".join(blk)}</section>')
    coda = nar.get("coda"); codaz = narz.get("coda")
    if coda:
        paras = coda if isinstance(coda, list) else [coda]
        parz = (codaz if isinstance(codaz, list) else [codaz]) if codaz else []
        cb = "".join(f"<p>{T(rich(p), rich(parz[k]) if k < len(parz) else None)}</p>" for k, p in enumerate(paras))
        body.append(f'<section class="esec coda">{cb}</section>')
    src = ""
    for sid in CITE_ORDER:
        c = CITE_META.get(sid, {})
        src += (f'<li id="src-{CITES[sid]}"><span class="sn">{CITES[sid]}</span>'
                f'<a href="#{sid}">{esc(c.get("speaker", ""))} — '
                f'{T(esc(c.get("title", sid)), esc(c.get("title_zh", "")))}</a>'
                f'<span class="sd">{esc(c.get("day", ""))}</span></li>')
    srcbox = f'<section class="sources"><h2>{T("Talks cited", "引用的演講")}</h2><ol>{src}</ol></section>' if src else ""
    ecfg = CFG.get("essay", {})
    kick_en = ecfg.get("kicker", "Synthesis"); by_en = ecfg.get("byline", "")
    rt = T(esc(nar.get("reading_time", "")), esc(narz.get("reading_time", "")))
    meta_en = f"read across {tot_talks} talks"; meta_zh = f"綜觀 {tot_talks} 場演講"
    if by_en: meta_en += f" · {by_en}"; meta_zh += f" · {ecfg.get('byline_zh', by_en)}"
    head = (f'<header class="ehead"><p class="ekicker">{T(esc(kick_en), esc(ecfg.get("kicker_zh", "綜合評析")))}</p>'
            f'<h1>{T(esc(nar.get("title", "")), esc(narz.get("title", "")))}</h1>'
            f'<p class="edek">{T(esc(nar.get("dek", "")), esc(narz.get("dek", "")))}</p>'
            f'<p class="emeta">{rt} · {T(meta_en, meta_zh)}</p></header>')
    return f'<article class="essay" id="essay">{head}{"".join(body)}{srcbox}</article>'

def pill(pc, en, zh): return f'<span class="pill {pc}">{T(en, zh)}</span>'

def card(it):
    thumb = (f'<span class="thumb"><img loading="lazy" src="{it["thumb"]}" alt=""></span>'
             if it["thumb"] else f'<span class="thumb none"><span>{T("No slides shown", "無投影片")}</span></span>')
    time = f'<span class="ctime">{esc(it["time"])}</span>' if it["time"] else ""
    return (f'<a class="card kb-{it["pc"]}" href="#{it["sid"]}">{thumb}'
            f'<span class="cbody"><span class="cmeta">{pill(it["pc"], it["pl_en"], it["pl_zh"])}{time}</span>'
            f'<span class="ctitle">{T(esc(it["title"]), esc(it["title_zh"]))}</span>'
            f'<span class="cspk">{esc(it["speaker"])}</span>'
            f'<span class="ctldr">{T(fmt(it["tldr"]), fmt(it["tldr_zh"]))}</span></span></a>')

def panel(it, grp, prev, nxt):
    lbl = esc(grp["meta"]["label"])
    no_en = f'No.&nbsp;{it["seq"]:02d}'; no_zh = f'第&nbsp;{it["seq"]:02d}&nbsp;場'
    eye = [f'<span class="no">{T(no_en, no_zh)}</span>']
    if it["time"]: eye.append(f'<span class="sep">·</span><span>{esc(it["time"])}</span>')
    eye.append(f'<span class="sep">·</span>{pill(it["pc"], it["pl_en"], it["pl_zh"])}')
    if it["watch"]:
        eye.append(f'<span class="sep">·</span><a class="watch" href="{esc(it["watch"])}" target="_blank" rel="noopener">{T("▶ Watch", "▶ 觀看影片")}</a>')
    tldr = f'<p class="tldr">{T(fmt(it["tldr"]), fmt(it["tldr_zh"]))}</p>' if it["tldr"] else ""
    tw_lab = T("Take this to work", "帶進你的工作")
    tw = (f'<div class="takeaway"><p class="lab">{tw_lab}</p>'
          f'<p>{T(fmt(it["takeaway"]), fmt(it["takeaway_zh"]))}</p></div>') if it["takeaway"] else ""
    bh = []
    for b in it["beats"]:
        tsl = f'<a class="ts" href="{esc(b["link"])}" target="_blank" rel="noopener">{b["ts"]}</a> ' if b["link"] else ""
        cap = tsl + T(b["en"], b["zh"])
        if b["img"]:
            bh.append(f'<figure class="slide"><img loading="lazy" src="{b["img"]}" alt="slide"><figcaption>{cap}</figcaption></figure>')
        else:
            bh.append(f'<div class="point">{cap}</div>')
    pv = (f'<a class="pn prev" href="#{prev["sid"]}"><span class="pnl">{T("‹ Prev", "‹ 上一場")}</span>'
          f'<span class="pnt">{T(esc(prev["title"]), esc(prev["title_zh"]))}</span></a>') if prev else '<span class="pn"></span>'
    nx = (f'<a class="pn next" href="#{nxt["sid"]}"><span class="pnl">{T("Next ›", "下一場 ›")}</span>'
          f'<span class="pnt">{T(esc(nxt["title"]), esc(nxt["title_zh"]))}</span></a>') if nxt else '<span class="pn"></span>'
    back_en = f'‹ {lbl} overview'; back_zh = f'‹ 返回{lbl}總覽'
    return (f'<article class="session" id="{it["sid"]}" data-day="{grp["key"]}">'
            f'<a class="back" href="#{grp["key"]}">{T(back_en, back_zh)}</a>'
            f'<div class="eyebrow">{"".join(eye)}</div>'
            f'<h2>{T(esc(it["title"]), esc(it["title_zh"]))}</h2>'
            f'<p class="spk">{esc(it["speaker"])}</p>{tldr}{tw}'
            f'<div class="beats">{"".join(bh)}</div><nav class="dpn">{pv}{nx}</nav></article>')

essay_title_en, essay_title_zh = cfg_t("essay_tab", "✦ Synthesis")
if multi:
    daytabs = "".join(
        f'<a class="daytab" data-day="{g["key"]}" data-tab="{g["key"]}" href="#{g["key"]}">{esc(g["meta"]["label"])} <span class="n">{g["n_talks"]}</span></a>'
        for g in groups)
elif ESSAY:
    # single group + essay: still need a tab back to the talks, else essay is a dead-end
    ov_en, ov_zh = cfg_t("overview_tab", "Talks")
    g = groups[0]
    daytabs = (f'<a class="daytab" data-day="{g["key"]}" data-tab="{g["key"]}" href="#{g["key"]}">'
               f'{T(esc(ov_en), esc(ov_zh) or "演講")} <span class="n">{g["n_talks"]}</span></a>')
else:
    daytabs = ""
essay_tab = f'<a class="daytab essaytab" data-tab="essay" href="#essay">{T(esc(essay_title_en), esc(essay_title_zh))}</a>' if ESSAY else ""
essay_html = f'<div class="essaywrap">{render_essay(ESSAY, ESSAY_ZH)}</div>' if ESSAY else ""
essay_cta = f'<p><a class="herocta" href="#essay">{T(esc(essay_title_en) + " ›", esc(essay_title_zh) + " ›")}</a></p>' if ESSAY else ""
langsw = ('<div class="langsw" role="group" aria-label="Language">'
          '<button type="button" data-lang="en">EN</button>'
          '<button type="button" data-lang="zh">中文</button></div>') if HAS_ZH else ""

ovwrap = []
for g in groups:
    cards = "".join(card(it) for it in g["items"])
    dd = esc(g["meta"].get("date", ""))
    pre = f'{dd}{" · " if dd else ""}'
    meta_line = T(f'{pre}{g["n_talks"]} talks · {g["n_slides"]} slides',
                  f'{pre}{g["n_talks"]} 場演講 · {g["n_slides"]} 張投影片')
    ovwrap.append(f'<section class="ovgrid" data-day="{g["key"]}"><header class="ovhead">'
                  f'<h2>{esc(g["meta"]["label"])}</h2><p>{meta_line}</p>'
                  f'</header><div class="grid">{cards}</div></section>')

panels = []
for g in groups:
    its = g["items"]
    for i, it in enumerate(its):
        panels.append(panel(it, g, its[i - 1] if i > 0 else None, its[i + 1] if i + 1 < len(its) else None))

used = {}
for g in groups:
    for it in g["items"]:
        used[it["pc"]] = (it["pl_en"], it["pl_zh"])
legend = "".join(f'<span><span class="dot {pc}"></span>{T(en, zh)}</span>' for pc, (en, zh) in used.items()) if len(used) > 1 else ""

CSS = """
:root{--paper:#FBFAF8;--ink:#191A1E;--slate:#5E626B;--line:#E6E2DB;--accent:#2A43C0;
 --tint:#F1EFE8;--main:#1C7A44;--fire:#6D3BD1;--cut:#3A5BB0;
 --serif:"Iowan Old Style","Charter",Georgia,"Times New Roman","Songti TC","Noto Serif CJK TC",serif;
 --mono:ui-monospace,"SF Mono","Cascadia Code",Menlo,Consolas,monospace;
 --sans:-apple-system,system-ui,"Segoe UI",Roboto,Helvetica,Arial,"PingFang TC","Noto Sans CJK TC","Microsoft JhengHei",sans-serif;}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);line-height:1.6;-webkit-font-smoothing:antialiased}
img{max-width:100%}
.wrap{max-width:1120px;margin:0 auto;padding:0 clamp(18px,4vw,40px)}
a{color:inherit}
.t-zh{display:none!important}
body.lang-zh .t-zh{display:inline!important}
body.lang-zh .t-en{display:none!important}
body.lang-zh{line-height:1.75}
.topbar{position:sticky;top:0;z-index:7;background:var(--paper);display:flex;align-items:center;gap:12px;padding:12px 0}
.topbar .brand{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--slate)}
.langsw{margin-left:auto;display:inline-flex;border:1px solid var(--line);border-radius:999px;overflow:hidden}
.langsw button{font-family:var(--mono);font-size:12px;padding:6px 13px;border:0;background:transparent;color:var(--slate);cursor:pointer;line-height:1}
.langsw button.active{background:var(--ink);color:#fff}
.pill{font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;padding:2px 8px;border-radius:20px;white-space:nowrap}
.pill.main{color:var(--main);background:#EAF4EE}.pill.fire{color:var(--fire);background:#F0EAFB}.pill.cut{color:var(--cut);background:#EAEFF8}
.dot{width:7px;height:7px;border-radius:50%;display:inline-block}
.dot.main{background:var(--main)}.dot.fire{background:var(--fire)}.dot.cut{background:var(--cut)}
code{font-family:var(--mono);font-size:.87em;background:#ECEAE3;padding:1px 5px;border-radius:4px;overflow-wrap:anywhere}
strong{font-weight:600}
.masthead{padding:60px 0 30px}
.masthead .kick{font-family:var(--mono);font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin:0 0 14px}
.masthead h1{font-family:var(--serif);font-weight:600;font-size:clamp(30px,5vw,46px);line-height:1.05;letter-spacing:-.015em;margin:0 0 14px;text-wrap:balance}
.masthead .lede{font-size:18px;color:var(--slate);max-width:56ch;margin:0}
.masthead .stats{display:flex;gap:24px;margin-top:20px;font-family:var(--mono);font-size:12px;color:var(--slate);flex-wrap:wrap}
.masthead .stats b{color:var(--ink)}
.masthead .legend{display:flex;gap:16px;margin-top:12px;font-family:var(--mono);font-size:11px;color:var(--slate);flex-wrap:wrap}
.masthead .legend>span{display:inline-flex;gap:6px;align-items:center}
body[data-view=detail] .masthead{display:none}
.tabs{position:sticky;top:46px;z-index:5;display:flex;gap:6px;flex-wrap:wrap;padding:12px 0;background:var(--paper);border-bottom:1px solid var(--line)}
.tabs:empty{display:none}
.daytab{font-family:var(--mono);font-size:13px;text-decoration:none;color:var(--slate);padding:7px 14px;border-radius:999px;border:1px solid var(--line)}
.daytab .n{opacity:.6;font-size:11px}
.daytab:hover{background:var(--tint);color:var(--ink)}
.daytab.active{background:var(--ink);color:#fff;border-color:var(--ink)}
.daytab.active .n{opacity:.7}
.ovgrid{display:none}.ovgrid.active{display:block}
body[data-view=detail] .ovwrap{display:none}
.ovhead{padding:34px 0 6px}
.ovhead h2{font-family:var(--serif);font-size:26px;font-weight:600;margin:0}
.ovhead p{font-family:var(--mono);font-size:12px;color:var(--slate);margin:4px 0 0;text-transform:uppercase;letter-spacing:.04em}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,270px),1fr));gap:20px;padding:18px 0 40px}
.card{display:flex;flex-direction:column;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:#fff;text-decoration:none;color:inherit;transition:border-color .15s,transform .15s}
.card:hover{border-color:var(--accent);transform:translateY(-2px)}
.card:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.thumb{display:block;aspect-ratio:16/9;background:var(--tint);border-bottom:1px solid var(--line)}
.thumb img{width:100%;height:100%;object-fit:cover;display:block}
.thumb.none{display:flex;align-items:center;justify-content:center}
.thumb.none span{font-family:var(--mono);font-size:11px;color:var(--slate);letter-spacing:.06em;text-transform:uppercase}
.kb-main{border-top:3px solid var(--main)}.kb-fire{border-top:3px solid var(--fire)}.kb-cut{border-top:3px solid var(--line)}
.cbody{display:flex;flex-direction:column;gap:4px;padding:14px 16px 16px}
.cmeta{display:flex;gap:8px;align-items:center;font-family:var(--mono);font-size:11px;color:var(--slate)}
.cmeta .ctime{margin-left:auto}
.ctitle{font-family:var(--serif);font-weight:600;font-size:18px;line-height:1.18;letter-spacing:-.01em;text-wrap:balance;overflow-wrap:anywhere}
.cspk{font-size:12.5px;color:var(--slate);overflow-wrap:anywhere}
.ctldr{font-size:13.5px;line-height:1.5;color:var(--ink);margin-top:4px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;overflow-wrap:anywhere}
body[data-view=overview] .detailwrap{display:none}
.session{display:none;max-width:760px;margin:0 auto;padding:26px 0 40px}
.session.active{display:block}
.back{display:inline-block;font-family:var(--mono);font-size:12px;color:var(--accent);text-decoration:none;margin-bottom:22px}
.back:hover{text-decoration:underline}
.eyebrow{display:flex;gap:9px;align-items:center;font-family:var(--mono);font-size:12px;letter-spacing:.03em;color:var(--slate);margin-bottom:12px;flex-wrap:wrap}
.eyebrow .no{color:var(--accent);font-weight:600}.eyebrow .sep{color:var(--line)}
.eyebrow .watch{color:var(--accent);text-decoration:none}
.eyebrow .watch:hover{text-decoration:underline}
.session h2{font-family:var(--serif);font-weight:600;font-size:30px;line-height:1.12;letter-spacing:-.015em;margin:0 0 6px;text-wrap:balance;overflow-wrap:anywhere}
.session .spk{font-size:15px;color:var(--slate);margin:0 0 22px;overflow-wrap:anywhere}
.tldr{font-family:var(--serif);font-size:20px;line-height:1.5;border-left:3px solid var(--accent);padding:1px 0 1px 18px;margin:0 0 20px;overflow-wrap:anywhere}
.takeaway{background:var(--tint);border-radius:12px;padding:16px 18px;margin:0 0 32px}
.takeaway .lab{font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--accent);margin:0 0 5px}
.takeaway p{margin:0;font-size:15.5px;overflow-wrap:anywhere}
figure.slide{margin:0 0 30px}
figure.slide img{width:100%;display:block;aspect-ratio:16/9;object-fit:cover;background:var(--tint);border:1px solid var(--line);border-radius:10px}
figure.slide figcaption{margin-top:12px;font-size:16.5px;line-height:1.55;overflow-wrap:anywhere}
.point{position:relative;background:var(--tint);border-radius:10px;padding:15px 18px 15px 40px;margin:0 0 30px;font-size:16.5px;line-height:1.55;overflow-wrap:anywhere}
.point::before{content:"◆";position:absolute;left:17px;top:16px;color:var(--accent);font-size:12px}
a.ts{font-family:var(--mono);font-size:12.5px;color:var(--accent);text-decoration:none;white-space:nowrap}
a.ts:hover{text-decoration:underline}
.dpn{display:flex;gap:14px;margin-top:16px;border-top:1px solid var(--line);padding-top:20px}
.pn{flex:1;min-width:0}
a.pn{display:flex;flex-direction:column;gap:3px;padding:12px 14px;border:1px solid var(--line);border-radius:10px;text-decoration:none;color:inherit}
a.pn:hover{border-color:var(--accent)}
a.pn.next{text-align:right}
.pn .pnl{font-family:var(--mono);font-size:11px;color:var(--accent)}
.pn .pnt{font-family:var(--serif);font-size:15px;line-height:1.25;overflow-wrap:anywhere}
footer{border-top:1px solid var(--line);padding:26px 0 80px;color:var(--slate);font-family:var(--mono);font-size:11.5px;line-height:1.7}
html{scroll-padding-top:104px}
@media(prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.essaywrap{display:none}
body[data-view=essay] .essaywrap{display:block}
body[data-view=essay] .masthead,body[data-view=essay] .ovwrap,body[data-view=essay] .detailwrap{display:none}
.essaytab{border-color:var(--accent);color:var(--accent);font-weight:600}
.essaytab.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.herocta{display:inline-block;margin-top:6px;font-family:var(--mono);font-size:13px;letter-spacing:.02em;color:#fff;background:var(--accent);padding:11px 18px;border-radius:999px;text-decoration:none}
.herocta:hover{background:#1c31a0}
.masthead .herocta{margin-top:22px}
.essay{max-width:720px;margin:0 auto;padding:30px 0 50px}
.ehead{padding:18px 0 26px;border-bottom:1px solid var(--line);margin-bottom:30px;text-align:center}
.ehead .ekicker{font-family:var(--mono);font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin:0 0 16px}
.ehead h1{font-family:var(--serif);font-weight:600;font-size:clamp(30px,5.4vw,50px);line-height:1.04;letter-spacing:-.018em;margin:0 0 18px;text-wrap:balance}
.ehead .edek{font-family:var(--serif);font-size:21px;line-height:1.5;color:var(--slate);margin:0 auto 16px;max-width:52ch;text-wrap:balance}
.ehead .emeta{font-family:var(--mono);font-size:11.5px;letter-spacing:.03em;color:var(--slate);margin:0}
.esec .ekick{font-family:var(--mono);font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin:38px 0 6px}
.esec h2{font-family:var(--serif);font-weight:600;font-size:27px;line-height:1.15;letter-spacing:-.01em;margin:0 0 16px;text-wrap:balance}
.esec p{font-size:18px;line-height:1.72;margin:0 0 20px;overflow-wrap:anywhere}
body.lang-zh .esec p{line-height:1.9}
.esec.coda{margin-top:18px;padding-top:26px;border-top:1px solid var(--line)}
.esec.coda p{font-family:var(--serif);font-size:20px;line-height:1.6}
.pull{margin:26px 0;padding:4px 0 4px 22px;border-left:3px solid var(--accent);font-family:var(--serif);font-size:23px;line-height:1.4;font-style:italic;text-wrap:balance}
.pull p{margin:0;font-size:inherit;line-height:inherit}
sup.cn{line-height:0;font-family:var(--mono);font-size:11px;white-space:nowrap}
sup.cn a{color:var(--accent);text-decoration:none;padding:0 1px;font-weight:600}
sup.cn a:hover{text-decoration:underline}
.sources{margin-top:44px;padding-top:24px;border-top:1px solid var(--line)}
.sources h2{font-family:var(--mono);font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--slate);font-weight:600;margin:0 0 14px}
.sources ol{list-style:none;margin:0;padding:0}
.sources li{display:flex;gap:10px;align-items:baseline;font-size:14px;line-height:1.5;padding:7px 0;border-bottom:1px solid var(--line)}
.sources .sn{font-family:var(--mono);font-size:12px;color:var(--accent);min-width:22px;font-weight:600}
.sources a{text-decoration:none;color:var(--ink);overflow-wrap:anywhere}
.sources a:hover{text-decoration:underline}
.sources .sd{margin-left:auto;font-family:var(--mono);font-size:11px;color:var(--slate);white-space:nowrap}
"""

LANG_KEY = CFG.get("key", "digest") + "-lang"
JS = """
const grids=[...document.querySelectorAll('.ovgrid')];
const tabs=[...document.querySelectorAll('.daytab')];
const panels=[...document.querySelectorAll('.session')];
const dayKeys=grids.map(g=>g.dataset.day);
const byId=id=>document.getElementById(id);
const hasEssay=!!byId('essay');
function setActive(key){grids.forEach(g=>g.classList.toggle('active',g.dataset.day===key));
 tabs.forEach(t=>t.classList.toggle('active',t.dataset.tab===key));}
function overview(day){if(!dayKeys.includes(day))day=dayKeys[0];
 panels.forEach(p=>p.classList.remove('active'));document.body.dataset.view='overview';setActive(day);window.scrollTo(0,0);}
function openSession(id){const p=byId(id);if(!p||!p.classList.contains('session')){overview();return;}
 panels.forEach(x=>x.classList.toggle('active',x===p));document.body.dataset.view='detail';setActive(p.dataset.day);window.scrollTo(0,0);}
function showEssay(){panels.forEach(p=>p.classList.remove('active'));document.body.dataset.view='essay';setActive('essay');window.scrollTo(0,0);}
function route(){const h=decodeURIComponent(location.hash.slice(1));
 if(h==='essay'&&hasEssay)showEssay();
 else if(byId(h)&&byId(h).classList.contains('session'))openSession(h);
 else if(dayKeys.includes(h))overview(h);else overview();}
addEventListener('hashchange',route);route();
const langBtns=[...document.querySelectorAll('.langsw button')];
function setLang(l){l=(l==='zh')?'zh':'en';document.body.classList.toggle('lang-zh',l==='zh');
 document.body.classList.toggle('lang-en',l==='en');
 langBtns.forEach(b=>b.classList.toggle('active',b.dataset.lang===l));
 document.documentElement.lang=(l==='zh')?'zh-Hant':'en';
 try{localStorage.setItem('LANG_KEY',l)}catch(e){}}
langBtns.forEach(b=>b.addEventListener('click',()=>setLang(b.dataset.lang)));
let L='en';try{L=localStorage.getItem('LANG_KEY')||'en'}catch(e){}
if(langBtns.length)setLang(L);
""".replace("LANG_KEY", LANG_KEY)

title_en, _ = cfg_t("title", "Video Digest")
brand_en, _ = cfg_t("brand", title_en)
kick_en, kick_zh = cfg_t("kicker", "")
head_en, head_zh = cfg_t("headline", "The talks, in slides & takeaways.")
lede_en, lede_zh = cfg_t("lede", "Skim the overview, then open any talk for the slides, the thesis, and what it means for your work.")
foot_en, foot_zh = cfg_t("footer", "Transcripts auto-generated (Whisper) then cleaned; names & quotes ~95% accurate. Slides captured at each highlight; frames showing only the speaker are omitted.")

stats = (f'<span><b>{tot_talks}</b> {T("talks", "場演講")}</span>'
         f'<span><b>{tot_slides}</b> {T("slides", "張投影片")}</span>')
if multi:
    stats += f'<span><b>{esc(", ".join(g["meta"]["label"] for g in groups))}</b></span>'
legend_html = f'<div class="legend">{legend}</div>' if legend else ""
kick_html = f'<p class="kick">{T(esc(kick_en), esc(kick_zh))}</p>' if kick_en else ""

HTML = f'''<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title_en)}</title>
<style>{CSS}</style>
<div class="wrap">
<div class="topbar"><span class="brand">{esc(brand_en)}</span>{langsw}</div>
<header class="masthead">
  {kick_html}
  <h1>{T(esc(head_en), esc(head_zh))}</h1>
  <p class="lede">{T(esc(lede_en), esc(lede_zh))}</p>
  {essay_cta}
  <div class="stats">{stats}</div>
  {legend_html}
</header>
<nav class="tabs">{daytabs}{essay_tab}</nav>
<div class="ovwrap">{"".join(ovwrap)}</div>
<div class="detailwrap">{"".join(panels)}</div>
{essay_html}
<footer>{T(esc(foot_en), esc(foot_zh))}</footer>
</div>
<script>{JS}</script>'''

out = (DIST / "index.html") if DIST else (PROJ / "digest.html")
if DIST: DIST.mkdir(parents=True, exist_ok=True)
out.write_text(HTML)
print(f"wrote {out} — {len(groups)} group(s), {tot_talks} talks, {tot_slides} slides, {out.stat().st_size/1e6:.1f} MB"
      + (f" (+{_ASSET_N} asset files)" if DIST else ""))
