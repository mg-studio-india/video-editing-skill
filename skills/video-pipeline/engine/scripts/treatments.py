"""treatments.py: the seven treatments (plus hero text and registry blocks) as beat builders for any canvas size.

Each builder takes a beat (resolved times) and a context, and returns (html, css, js_lines, placement):
  placement "front"  -> a host on the root, above the camera
            "behind" -> inside the camera, between the footage and the subject matte (layered-head)
            "root"   -> media that must be a direct child of the root (videos, sub-composition hosts)
Timeline lines use the shared paused timeline `tl`. Hosts carry class="clip" with data-start/data-duration and are never
tweened themselves (HyperFrames lint: gsap_animates_clip_element); only their children move.

Context: {"W", "H", "style": style.json dict, "track": int}. Used by stage.py (any canvas) and by compose.py (16:9,
types its own library does not have).

Beat types
  layout   the speaker's video moves: {"type":"layout","id","mode":"stack|pip|hide|full","corner":"tl|tr|bl|br",
           "size":0.32,"focus":[x%,y%],"transition":0.6,"in","out"} (stage.py only; handled by layout_js, not build)
  banner   headline band, full width: {"type":"banner","id","text","em":[i],"in","out","y":0.095,"size":0.068,"bg":"#000"}
  hero     big text on its word:      {"type":"hero","id","text","em":[i],"in","out","y":0.3,"size":0.11,"anim":"rise|slam|fade"}
  cards    items, one per word:       {"type":"cards","id","title":"","items":[[text,t],...],"in","out","y":0.22,"marker":"num|dot|check"}
  whiteout flash to white and back:   {"type":"whiteout","id","in","out","peak":0.25,"hold":0.10,"back":0.35}
  drawer   paper panel from an edge:  {"type":"drawer","id","edge":"left|right|bottom","title","lines":[..],"img":"img/x.png","in","out","w":0.62}
  split    two pictures:              {"type":"split","id","layout":"sbs|stack","a":{"src","focus":[x%,y%],"media_start"},
                                       "b":{"src",...},"in","out","divider":true}   (a = left/top; the base video's audio plays)
  behind   text behind the subject:   {"type":"behind","id","text","em":[i],"in","out","y":0.32,"size":0.18}   (needs "matte")
  clip     full-frame B-roll:         {"type":"clip","id","src","in","out","media_start":0,"focus":[50,50],"drift":true,"label":""}
  block    a registry block:          {"type":"block","id","comp_id","src":"compositions/x.html","in","out","w","h","x":0,"y":0,"vars":{}}
  captions the caption rail:          {"type":"captions","id","groups":[...from captions.group...]} (stage.py fills groups)
"""
from __future__ import annotations

import json
from html import escape

TYPES = {"banner", "hero", "cards", "whiteout", "drawer", "split", "behind", "clip", "block", "captions"}

DEFAULT_STYLE = {
    "colors": {"text": "#ffffff", "accent": "#ffd400", "accent2": "#00e0ff", "money": "#22e07a",
               "dark": "#0b0b0f", "paper": "#f4ecd8", "paper_ink": "#1d1a16"},
    "fonts": {"display": {"family": "Poppins", "files": {}}},
    "motion": {"in": 0.35, "out": 0.25, "ease_in": "power3.out", "ease_out": "power2.in"},
    "cards": {"bg": "rgba(12,12,16,.78)", "text": "#ffffff", "radius": 22, "border": "rgba(255,255,255,.14)"},
    "captions": {"mode": "pop", "case": "upper", "weight": 800},
}


def tok(style: dict, *path, default=None):
    cur = style
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            cur = None
            break
        cur = cur[p]
    if cur is None:
        cur = DEFAULT_STYLE
        for p in path:
            cur = cur.get(p) if isinstance(cur, dict) else None
            if cur is None:
                return default
    return cur


def family_stack(style: dict) -> str:
    """The display family plus an optional fallback family (a second script), written to sit inside one pair of
    quotes in the builders' "font-family:'%s',sans-serif": Inter then Noto Sans Devanagari renders Hindi in Noto."""
    fams = [tok(style, "fonts", "display", "family")]
    fb = ((style.get("fonts") or {}).get("fallback") or {}).get("family")
    if fb:
        fams.append(fb)
    return "','".join(fams)


def mot(style: dict, key: str, default: float) -> float:
    try:
        return float(((style.get("motion") or {}).get(key)) or default)
    except (TypeError, ValueError):
        return default


def esc(s) -> str:
    return escape(str(s), quote=True)


def host(bid: str, t_in: float, t_out: float, track: int, inner: str, z: int = 30, extra: str = "") -> str:
    return ('<div class="clip tr-host" id="host-%s" data-start="%.3f" data-duration="%.3f" data-track-index="%d" '
            'style="position:absolute;inset:0;z-index:%d;pointer-events:none"%s>%s</div>\n'
            % (bid, t_in, max(0.05, t_out - t_in), track, z, extra, inner))


def outline(style: dict, size_px: int) -> str:
    """Dark outline under display text (style "text_stroke": fraction of the font size, 0 = off). Keeps bright
    accent words readable over bright footage, where a shadow alone failed HyperFrames' 3:1 contrast check."""
    k = float(style.get("text_stroke", 0) or 0)
    if k <= 0:
        return ""
    return "-webkit-text-stroke:%dpx rgba(0,0,0,.92);paint-order:stroke fill;" % max(2, int(round(size_px * k)))


def words_html(text: str, em: list[int], cls: str, bid: str, attrs: str = "") -> str:
    out = []
    for i, w in enumerate(text.split(" ")):
        out.append('<span class="%s%s" id="%s-w%d"%s>%s</span>' % (cls, " em" if i in em else "", bid, i, attrs, esc(w)))
    return " ".join(out)


# ---------------------------------------------------------------- builders
def b_hero(b, ctx):
    W, H, st = ctx["W"], ctx["H"], ctx["style"]
    bid, t0, t1 = b["id"], float(b["in"]), float(b["out"])
    size = int(float(b.get("size", 0.11 if H > W else 0.075)) * W)
    y = float(b.get("y", 0.15 if H > W else 0.42))          # portrait: above the head, below the platform's top bar
    fam = family_stack(st)
    css = (".hero-%s{position:absolute;left:6%%;right:6%%;top:%dpx;text-align:center;font-family:'%s',sans-serif;"
           "font-weight:900;font-size:%dpx;line-height:1.02;color:%s;text-shadow:0 10px 40px rgba(0,0,0,.55);%s}"
           ".hero-%s .hw{display:inline-block}.hero-%s .hw.em{color:%s}"
           % (bid, int(H * y - size / 2), fam, size, tok(st, "colors", "text"), outline(st, size), bid, bid, tok(st, "colors", "accent")))
    inner = '<div class="hero-%s" id="%s">%s</div>' % (bid, bid, words_html(b["text"], b.get("em", []), "hw", bid))
    anim = b.get("anim", "rise")
    js = []
    n = len(b["text"].split(" "))
    for i in range(n):
        sel, t = "#%s-w%d" % (bid, i), t0 + 0.05 + i * 0.06
        if anim == "slam":
            js.append("tl.fromTo('%s', { opacity: 0, scale: 1.6 }, { opacity: 1, scale: 1, duration: 0.22, ease: 'power4.out' }, %.3f);" % (sel, t))
        elif anim == "fade":
            js.append("tl.fromTo('%s', { opacity: 0 }, { opacity: 1, duration: 0.3 }, %.3f);" % (sel, t))
        else:
            js.append("tl.fromTo('%s', { opacity: 0, y: %d }, { opacity: 1, y: 0, duration: %.2f, ease: 'power3.out' }, %.3f);"
                      % (sel, int(size * 0.35), mot(st, "in", 0.4), t))
    js.append("tl.to('#%s', { opacity: 0, duration: 0.25, ease: 'power2.in' }, %.3f);" % (bid, t1 - 0.25))
    return host(bid, t0, t1, ctx["track"], inner, 40), css, js, "front"


def b_banner(b, ctx):
    W, H, st = ctx["W"], ctx["H"], ctx["style"]
    bid, t0, t1 = b["id"], float(b["in"]), float(b["out"])
    portrait = H > W
    fs = int(W * float(b.get("size", 0.068 if portrait else 0.036)))
    top = int(H * float(b.get("y", 0.095 if portrait else 0.06)))       # portrait: just under the platform's top bar
    band = b.get("bg", tok(st, "colors", "band") or "#000000")
    css = (".ban-%s{position:absolute;left:0;right:0;top:%dpx;padding:%dpx %dpx;background:%s;text-align:center;"
           "font-family:'%s',sans-serif;font-weight:%s;font-size:%dpx;line-height:1.08;color:%s;text-transform:uppercase;letter-spacing:.01em}"
           ".ban-%s .bw{display:inline-block}.ban-%s .bw.em{color:%s}"
           % (bid, top, int(fs * 0.45), int(W * 0.075), band, family_stack(st), b.get("weight", 800), fs,
              tok(st, "colors", "text"), bid, bid, tok(st, "colors", "accent")))
    inner = '<div class="ban-%s" id="%s"><div id="%s-t">%s</div></div>' % (bid, bid, bid, words_html(b["text"], b.get("em", []), "bw", bid))
    d = mot(st, "in", 0.25)
    js = ["tl.fromTo('#%s', { opacity: 0 }, { opacity: 1, duration: %.2f, ease: 'power2.out' }, %.3f);" % (bid, d, t0),
          "tl.fromTo('#%s-t', { y: %d }, { y: 0, duration: %.2f, ease: 'power3.out' }, %.3f);" % (bid, int(fs * 0.25), d, t0),
          "tl.to('#%s', { opacity: 0, duration: %.2f, ease: 'power2.in' }, %.3f);" % (bid, mot(st, "out", 0.2), t1 - mot(st, "out", 0.2))]
    return host(bid, t0, t1, ctx["track"], inner, 42), css, js, "front"


def b_cards(b, ctx):
    W, H, st = ctx["W"], ctx["H"], ctx["style"]
    bid, t0, t1 = b["id"], float(b["in"]), float(b["out"])
    portrait = H > W
    cw = int(W * (0.84 if portrait else 0.36))
    fs = int(W * (0.052 if portrait else 0.026))
    default_y = 0.58 if portrait else 0.16
    y_val = float(b.get("y", default_y))
    # Safety guard: cards should never float directly over speaker's face in portrait unless explicitly allowed
    if portrait and y_val < 0.40 and not b.get("allow_top", False):
        y_val = 0.58
    top = int(H * y_val)   # portrait: under the face (reframe eye line 38%)
    left = int((W - cw) / 2) if portrait or b.get("pos") == "center" else (int(W * 0.05) if b.get("pos", "tl") == "tl" else W - cw - int(W * 0.05))
    fam, accent = family_stack(st), tok(st, "colors", "accent")
    bg, rad, brd = tok(st, "cards", "bg"), tok(st, "cards", "radius"), tok(st, "cards", "border")
    marker = b.get("marker", "num")
    css = (".cards-%s{position:absolute;left:%dpx;top:%dpx;width:%dpx;display:flex;flex-direction:column;gap:%dpx}"
           ".cards-%s .ttl{font-family:'%s',sans-serif;font-weight:800;font-size:%dpx;color:%s;text-transform:uppercase;"
           "letter-spacing:.04em;margin-bottom:4px;text-shadow:0 4px 18px rgba(0,0,0,.6);%s}"
           ".cards-%s .card{display:flex;align-items:center;gap:%dpx;padding:%dpx %dpx;background:%s;border:2px solid %s;"
           "border-radius:%dpx;box-shadow:0 18px 50px rgba(0,0,0,.35);opacity:0}"
           ".cards-%s .mk{flex:0 0 auto;width:%dpx;height:%dpx;border-radius:50%%;background:%s;color:#111;display:flex;"
           "align-items:center;justify-content:center;font-family:'%s',sans-serif;font-weight:900;font-size:%dpx}"
           ".cards-%s .tx{font-family:'%s',sans-serif;font-weight:700;font-size:%dpx;color:%s;line-height:1.15}"
           % (bid, left, top, cw, int(fs * 0.35), bid, fam, int(fs * 0.7), tok(st, "cards", "title_color") or accent, outline(st, int(fs * 0.7)), bid, int(fs * 0.5), int(fs * 0.45),
              int(fs * 0.6), bg, brd, rad, bid, int(fs * 1.2), int(fs * 1.2), accent, fam, int(fs * 0.62), bid, fam, fs,
              tok(st, "cards", "text")))
    rows = []
    for i, it in enumerate(b["items"]):
        mk = str(i + 1) if marker == "num" else ("&#10003;" if marker == "check" else "")
        rows.append('<div class="card" id="%s-c%d"><div class="mk">%s</div><div class="tx">%s</div></div>' % (bid, i, mk, esc(it[0])))
    title = '<div class="ttl" id="%s-t">%s</div>' % (bid, esc(b["title"])) if b.get("title") else ""
    inner = '<div class="cards-%s" id="%s">%s%s</div>' % (bid, bid, title, "".join(rows))
    js = []
    if title:
        js.append("tl.fromTo('#%s-t', { opacity: 0, y: -16 }, { opacity: 1, y: 0, duration: 0.3, ease: 'power3.out' }, %.3f);" % (bid, t0))
    for i, it in enumerate(b["items"]):
        t = float(it[1]) if len(it) > 1 and isinstance(it[1], (int, float)) else t0 + 0.2 + i * 0.5
        js.append("tl.fromTo('#%s-c%d', { opacity: 0, x: %d }, { opacity: 1, x: 0, duration: %.2f, ease: 'power3.out' }, %.3f);"
                  % (bid, i, -60 if i % 2 == 0 else 60, mot(st, "in", 0.35), t - 0.05))
    js.append("tl.to('#%s', { opacity: 0, y: -10, duration: 0.25, ease: 'power2.in' }, %.3f);" % (bid, t1 - 0.25))
    return host(bid, t0, t1, ctx["track"], inner, 40), css, js, "front"


def b_whiteout(b, ctx):
    bid, t0, t1 = b["id"], float(b["in"]), float(b["out"])
    peak, hold, back = float(b.get("peak", 0.25)), float(b.get("hold", 0.10)), float(b.get("back", 0.35))
    css = "#%s{position:absolute;inset:0;background:#fff;opacity:0}" % bid
    js = ["tl.fromTo('#%s', { opacity: 0 }, { opacity: 1, duration: %.3f, ease: 'power2.in' }, %.3f);" % (bid, peak, t0),
          "tl.to('#%s', { opacity: 0, duration: %.3f, ease: 'power2.out' }, %.3f);" % (bid, back, t0 + peak + hold)]
    # no brightness "bloom" on the footage: filter is not in HyperFrames' animatable property list, so it is not
    # guaranteed seek-safe. For a richer flash, wire the registry's flash-through-white or editorial-flash-overlay.
    end = max(t1, t0 + peak + hold + back + 0.02)
    return host(bid + "-h", t0, end, ctx["track"], '<div id="%s"></div>' % bid, 90), css, js, "front"


PAPER_NOISE = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'>"
               "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/>"
               "<feColorMatrix values='0 0 0 0 .35  0 0 0 0 .28  0 0 0 0 .18  0 0 0 .22 0'/></filter>"
               "<rect width='100%' height='100%' filter='url(%23n)'/></svg>\")")


def b_drawer(b, ctx):
    W, H, st = ctx["W"], ctx["H"], ctx["style"]
    bid, t0, t1 = b["id"], float(b["in"]), float(b["out"])
    edge = b.get("edge", "left")
    portrait = H > W
    pw = int(W * float(b.get("w", 0.80 if portrait else 0.42)))
    fam = family_stack(st)
    paper, ink, accent = tok(st, "colors", "paper"), tok(st, "colors", "paper_ink"), tok(st, "colors", "accent")
    fs = int(W * (0.050 if portrait else 0.024))
    rot = float(b.get("rotate", -1.6 if edge != "right" else 1.6))
    if edge == "bottom":
        pos = "left:%dpx;bottom:%dpx;width:%dpx" % ((W - pw) // 2, int(H * 0.12), pw)
        frm = "{ y: %d, rotation: %.1f }" % (H, rot)
    elif edge == "right":
        pos = "right:%dpx;top:%dpx;width:%dpx" % (int(W * 0.05), int(H * float(b.get("y", 0.52 if portrait else 0.18))), pw)
        frm = "{ x: %d, rotation: %.1f }" % (pw + int(W * 0.1), rot * 3)
    else:
        pos = "left:%dpx;top:%dpx;width:%dpx" % (int(W * 0.05), int(H * float(b.get("y", 0.52 if portrait else 0.18))), pw)
        frm = "{ x: %d, rotation: %.1f }" % (-(pw + int(W * 0.1)), rot * 3)
    css = (".drw-%s{position:absolute;%s;padding:%dpx %dpx %dpx;background:%s;background-image:%s;color:%s;"
           "border-radius:6px;box-shadow:0 2px 0 rgba(0,0,0,.08),0 24px 60px rgba(0,0,0,.45);font-family:'%s',sans-serif}"
           ".drw-%s:before{content:'';position:absolute;left:50%%;top:-14px;width:120px;height:30px;margin-left:-60px;"
           "background:rgba(255,255,255,.55);box-shadow:0 2px 6px rgba(0,0,0,.15);transform:rotate(-3deg)}"
           ".drw-%s .dt{font-weight:900;font-size:%dpx;line-height:1.05;margin-bottom:%dpx}"
           ".drw-%s .dt .em{color:%s;background:linear-gradient(transparent 58%%,%s 58%%)}"
           ".drw-%s .dl{font-weight:600;font-size:%dpx;line-height:1.3;margin-top:%dpx}"
           ".drw-%s img{display:block;width:100%%;margin-top:%dpx;border-radius:4px}"
           % (bid, pos, int(fs * 0.9), int(fs * 0.8), int(fs * 0.9), paper, PAPER_NOISE, ink, fam, bid, bid, int(fs * 1.25),
              int(fs * 0.3), bid, ink, accent, bid, fs, int(fs * 0.35), bid, int(fs * 0.4)))
    em = b.get("em", [])
    title = '<div class="dt">%s</div>' % " ".join(('<span class="em">%s</span>' % esc(w)) if i in em else esc(w)
                                                  for i, w in enumerate(b.get("title", "").split(" "))) if b.get("title") else ""
    lines = "".join('<div class="dl" id="%s-l%d">%s</div>' % (bid, i, esc(l)) for i, l in enumerate(b.get("lines", [])))
    img = '<img src="%s" alt="">' % esc(b["img"]) if b.get("img") else ""
    inner = '<div class="drw-%s" id="%s">%s%s%s</div>' % (bid, bid, title, lines, img)
    js = ["tl.fromTo('#%s', %s, { x: 0, y: 0, rotation: %.1f, duration: 0.55, ease: 'power3.out' }, %.3f);" % (bid, frm, rot, t0)]
    for i, _ in enumerate(b.get("lines", [])):
        js.append("tl.fromTo('#%s-l%d', { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.3, ease: 'power2.out' }, %.3f);" % (bid, i, t0 + 0.45 + 0.25 * i))
    back = frm.replace("{", "{ duration: 0.45, ease: 'power3.in',", 1)
    js.append("tl.to('#%s', %s, %.3f);" % (bid, back, t1 - 0.45))
    return host(bid, t0, t1, ctx["track"], inner, 45), css, js, "front"


def b_split(b, ctx):
    W, H, st = ctx["W"], ctx["H"], ctx["style"]
    bid, t0, t1 = b["id"], float(b["in"]), float(b["out"])
    stack = b.get("layout", "stack" if H > W else "sbs") == "stack"
    gap = int(b.get("gap", 6))
    if stack:
        boxes = [(0, 0, W, (H - gap) // 2), (0, (H + gap) // 2, W, H - (H + gap) // 2)]
    else:
        boxes = [(0, 0, (W - gap) // 2, H), ((W + gap) // 2, 0, W - (W + gap) // 2, H)]
    html, css = [], ["#%s-bg{position:absolute;inset:0;background:%s}" % (bid, tok(st, "colors", "dark"))]
    html.append(host(bid + "-bg", t0, t1, ctx["track"], '<div id="%s-bg"></div>' % bid, 20))
    js = []
    for k, (side, (x, y, w, h)) in enumerate(zip(("a", "b"), boxes)):
        s = b[side]
        fx, fy = s.get("focus", [50, 50])
        vid = "%s-%s" % (bid, side)
        html.append('<video class="clip" id="%s" src="%s" muted playsinline data-start="%.3f" data-duration="%.3f" '
                    'data-media-start="%.3f" data-track-index="%d" style="position:absolute;left:%dpx;top:%dpx;width:%dpx;'
                    'height:%dpx;object-fit:cover;object-position:%s%% %s%%;z-index:21"></video>\n'
                    % (vid, esc(s["src"]), t0, t1 - t0, float(s.get("media_start", 0)), ctx["track"] + 1 + k, x, y, w, h, fx, fy))
    if b.get("divider", True):
        dv = ("left:0;right:0;top:%dpx;height:%dpx" % ((H - gap) // 2, gap)) if stack else ("top:0;bottom:0;left:%dpx;width:%dpx" % ((W - gap) // 2, gap))
        css.append("#%s-dv{position:absolute;%s;background:%s}" % (bid, dv, tok(st, "colors", "accent")))
        html.append(host(bid + "-dvh", t0, t1, ctx["track"] + 3, '<div id="%s-dv"></div>' % bid, 22))
        js.append("tl.fromTo('#%s-dv', { %s: 0 }, { %s: 1, duration: 0.35, ease: 'power3.out' }, %.3f);"
                  % (bid, "scaleX" if stack else "scaleY", "scaleX" if stack else "scaleY", t0))
    return "".join(html), "".join(css), js, "root"


def b_behind(b, ctx):
    W, H, st = ctx["W"], ctx["H"], ctx["style"]
    bid, t0, t1 = b["id"], float(b["in"]), float(b["out"])
    size = int(float(b.get("size", 0.20 if H > W else 0.16)) * W)
    y = float(b.get("y", 0.30 if H > W else 0.36))
    fam = family_stack(st)
    css = (".bh-%s{position:absolute;left:0;right:0;top:%dpx;text-align:center;font-family:'%s',sans-serif;font-weight:900;"
           "font-size:%dpx;line-height:.92;color:%s;letter-spacing:-.02em;white-space:nowrap}.bh-%s .em{color:%s}"
           % (bid, int(H * y - size / 2), fam, size, b.get("color", tok(st, "colors", "text")), bid, tok(st, "colors", "accent")))
    inner = '<div class="bh-%s" id="%s">%s</div>' % (bid, bid, words_html(b["text"], b.get("em", []), "bw", bid,
                                                                       " data-layout-allow-occlusion"))
    js = ["tl.fromTo('#%s', { opacity: 0, scale: 0.86 }, { opacity: 1, scale: 1, duration: 0.45, ease: 'power3.out' }, %.3f);" % (bid, t0),
          "tl.to('#%s', { opacity: 0, duration: 0.3, ease: 'power2.in' }, %.3f);" % (bid, t1 - 0.3)]
    return host(bid, t0, t1, ctx["track"], inner, 5), css, js, "behind"


def b_clip(b, ctx):
    W, H = ctx["W"], ctx["H"]
    bid, t0, t1 = b["id"], float(b["in"]), float(b["out"])
    fx, fy = b.get("focus", [50, 50])
    html = ('<video class="clip" id="%s" src="%s" muted playsinline data-start="%.3f" data-duration="%.3f" data-media-start="%.3f" '
            'data-track-index="%d" style="position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover;object-position:%s%% %s%%;z-index:25"></video>\n'
            % (bid, esc(b["src"]), t0, t1 - t0, float(b.get("media_start", 0)), ctx["track"], fx, fy))
    css, js = "", []
    if b.get("label"):
        st = ctx["style"]
        fs = int(W * (0.06 if H > W else 0.034))
        css = ("#%s-lb{position:absolute;left:6%%;right:6%%;bottom:%dpx;text-align:center;font-family:'%s',sans-serif;font-weight:800;"
               "font-size:%dpx;color:#fff;text-shadow:0 6px 24px rgba(0,0,0,.7)}" % (bid, int(H * 0.2), family_stack(st), fs))
        html += host(bid + "-lbh", t0, t1, ctx["track"] + 1, '<div id="%s-lb">%s</div>' % (bid, esc(b["label"])), 26)
        js.append("tl.fromTo('#%s-lb', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.35, ease: 'power3.out' }, %.3f);" % (bid, t0 + 0.15))
    return html, css, js, "root"


def b_block(b, ctx):
    bid, t0, t1 = b["id"], float(b["in"]), float(b["out"])
    W, H = int(b.get("w", ctx["W"])), int(b.get("h", ctx["H"]))
    vars_attr = " data-variable-values='%s'" % json.dumps(b["vars"]).replace("'", "&#39;") if b.get("vars") else ""
    html = ('<div class="clip" id="%s" data-composition-id="%s" data-composition-src="%s" data-start="%.3f" data-duration="%.3f" '
            'data-width="%d" data-height="%d" data-track-index="%d"%s style="position:absolute;left:%dpx;top:%dpx;width:%dpx;height:%dpx;z-index:%d"></div>\n'
            % (bid, esc(b["comp_id"]), esc(b["src"]), t0, t1 - t0, W, H, ctx["track"], vars_attr, int(b.get("x", 0)),
               int(b.get("y", 0)), W, H, int(b.get("z", 50))))
    return html, "", [], "root"


def b_captions(b, ctx):
    from captions import builtin_layer
    st = ctx["style"]
    cfg = dict(tok(st, "captions") or {})
    cfg.setdefault("family", family_stack(st))
    cfg.setdefault("active_color", tok(st, "colors", "accent"))
    html, css, js = builtin_layer(b["groups"], {**ctx, "accent": tok(st, "colors", "accent")}, cfg)
    end = max(g["end"] for g in b["groups"]) if b["groups"] else 0.1
    return host(b["id"], 0.0, end + 0.04, ctx["track"], html, 60), css, js, "front"


BUILDERS = {"banner": b_banner, "hero": b_hero, "cards": b_cards, "whiteout": b_whiteout, "drawer": b_drawer, "split": b_split,
            "behind": b_behind, "clip": b_clip, "block": b_block, "captions": b_captions}


def build(b: dict, ctx: dict):
    return BUILDERS[b["type"]](b, ctx)


def resolve_font(path: str, style_dir: str) -> str:
    """Font paths in style.json: absolute, relative to the style file, or "@engine/..." (the engine's own assets)."""
    import os
    if path.startswith("@engine/"):
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), path[len("@engine/"):])
    return path if os.path.isabs(path) else os.path.join(style_dir, path)


# ---------------------------------------------------------------- speaker-video layouts (stage.py)
# Idea adapted from HyperFrames' talking-head-recut (itself adapted from vtake-skills, MIT): the speaker's own video moves
# to make room - stacked above a card, a picture-in-picture corner window, hidden for a pure-graphic moment - instead of
# graphics only ever covering it. Moved with x / y / width / height / opacity, HyperFrames' seek-safe properties.
LAYOUT_MODES = ("full", "stack", "pip", "hide")
LAYOUT_DUR = 0.6


def layout_box(mode: str, W: int, H: int, corner: str | None = None, size: float | None = None) -> tuple[int, int, int, int]:
    """Pure (tested): the video's (x, y, w, h) for a layout. Portrait pip defaults to top-left, below the platform's
    top bar and clear of the action buttons on the right; landscape pip to bottom-right."""
    portrait = H > W
    if mode in ("full", "hide"):
        return 0, 0, W, H
    if mode == "stack":
        return 0, 0, W, int(round(H * (0.44 if portrait else 0.52)))
    if mode == "pip":
        w = int(round(W * (size or (0.32 if portrait else 0.22))))
        h = int(round(w * (4 / 3 if portrait else 3 / 4)))
        m = int(round(W * 0.04))
        top = int(round(H * 0.10)) if portrait else m                  # under the ~180 px top bar on 9:16
        bottom = H - h - (int(round(H * 0.17)) if portrait else m)       # above the ~320 px button zone on 9:16
        corner = corner or ("tl" if portrait else "br")
        x = m if corner[1] == "l" else W - w - m
        y = top if corner[0] == "t" else bottom
        return x, y, w, h
    raise SystemExit("unknown layout mode %r (use %s)" % (mode, ", ".join(LAYOUT_MODES)))


def layout_js(beats: list[dict], W: int, H: int, style: dict) -> list[str]:
    """Timeline lines moving #cam-wrap between layouts. Each layout beat holds from its in to its out, then returns to
    full frame, unless the next layout starts within one transition of it (then it moves straight on)."""
    lb = sorted((b for b in beats if b.get("type") == "layout"), key=lambda b: float(b["in"]))
    js = []
    radius = int(round(W * 0.03))
    ring = "0 0 0 %dpx rgba(255,255,255,.92), 0 18px 50px rgba(0,0,0,.45)" % max(3, int(round(W * 0.004)))
    for i, b in enumerate(lb):
        t0, t1, mode = float(b["in"]), float(b["out"]), b.get("mode", "stack")
        x, y, w, h = layout_box(mode, W, H, b.get("corner"), b.get("size"))
        d = float(b.get("transition", LAYOUT_DUR))
        focus = b.get("focus", [50, 35] if mode in ("stack", "pip") else [50, 50])
        # pip floats above full-frame content (B-roll z 25, split 20-22) but stays under panels (40+) and captions (60)
        chrome = ("%dpx" % radius, ring, 35) if mode == "pip" else ("0px", "none", 1)
        js.append("tl.set('#cam-wrap', { borderRadius: '%s', boxShadow: '%s', zIndex: %d }, %.3f);" % (chrome + (t0,)))
        js.append("tl.set('#base, #matte', { objectPosition: '%s%% %s%%' }, %.3f);" % (focus[0], focus[1], t0))
        if mode == "hide":
            js.append("tl.to('#cam-wrap', { opacity: 0, duration: %.2f, ease: 'power2.inOut' }, %.3f);" % (min(d, 0.4), t0))
        else:
            js.append("tl.to('#cam-wrap', { x: %d, y: %d, width: %d, height: %d, opacity: 1, duration: %.2f, ease: 'power2.inOut' }, %.3f);"
                      % (x, y, w, h, d, t0))
        nxt = lb[i + 1] if i + 1 < len(lb) else None
        # return to full frame only when there is room for the whole move before the next layout; otherwise the next
        # layout's tween moves straight on (a return overlapping it fought its tween and reset its styling mid-move)
        if nxt is None or float(nxt["in"]) - t1 >= d + 0.05:
            js.append("tl.to('#cam-wrap', { x: 0, y: 0, width: %d, height: %d, opacity: 1, duration: %.2f, ease: 'power2.inOut' }, %.3f);"
                      % (W, H, d, t1))
            js.append("tl.set('#cam-wrap', { borderRadius: '0px', boxShadow: 'none', zIndex: 1 }, %.3f);" % (t1 + d))
            js.append("tl.set('#base, #matte', { objectPosition: '50%% 50%%' }, %.3f);" % (t1 + d))
    return js


def layout_overlaps(beats: list[dict]) -> list[str]:
    lb = sorted((b for b in beats if b.get("type") == "layout"), key=lambda b: float(b["in"]))
    return ["%s and %s overlap" % (a["id"], b["id"]) for a, b in zip(lb, lb[1:]) if float(b["in"]) < float(a["out"]) - 0.05]


def font_faces(style: dict) -> str:
    out = []
    for role in ("display", "body", "fallback"):
        f = (style.get("fonts") or {}).get(role)
        if not f:
            continue
        for weight, path in sorted((f.get("files") or {}).items()):
            out.append("@font-face{font-family:'%s';src:url('%s');font-weight:%s;font-style:normal;font-display:block}"
                       % (f["family"], path, weight))
    return "\n".join(out)
