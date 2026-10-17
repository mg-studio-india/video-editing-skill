#!/usr/bin/env python3
"""captions.py: word-exact captions from the flat-cut transcript, two ways.

1. catalog   inject the words into an installed HyperFrames caption component (npx hyperframes add caption-highlight),
             resized to the canvas, timed to the video, optionally re-fonted with the style's local font (needed for
             Hindi: most catalog fonts have no Devanagari). Writes a sub-composition and prints the host <div>.
             Works with the components that keep their words in WORDS (+ RAW_GROUPS or GROUPS) or TRANSCRIPT:
             caption-highlight, -clip-wipe, -particle-burst, -gradient-fill, -matrix-decode, -neon-glow,
             -kinetic-slam, -texture, -pill-karaoke, -emoji-pop, -glitch-rgb, -neon-accent, -weight-shift.
2. builtin   a caption layer this engine writes itself (pop / karaoke / block), styled from style.json. Used by
             stage.py and compose.py as the "captions" beat; also printed here as JSON groups for inspection.

Grouping (HyperFrames caption rules): 2 to 5 words by energy, break at sentence ends, at pauses of 150 ms or more, at
a max character count, and never across a jump cut; fillers (um, uh) are dropped; one group on screen at a time;
each group ends at its last word + a short hold, or just before the next group.

Usage:
  python3 captions.py groups  --transcript W/transcript.json [--cut-map W/cut-map.json] [--max-words 3] [--max-chars 18]
  python3 captions.py catalog --component W/public/compositions/components/caption-highlight.html \
      --transcript W/transcript.json --out W/public/compositions/captions.html --width 1080 --height 1920 \
      [--cut-map W/cut-map.json] [--style W/style.json] [--y 0.68] [--max-words 3]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

FILLERS = {"um", "uh", "uhm", "umm", "uhh", "er", "erm", "ah", "hmm", "mm", "mhm"}
SENTENCE_END = re.compile(r"[.!?…।]$")          # includes the Devanagari danda
PAUSE_BREAK = 0.30
HOLD = 0.35
NUMERIC = re.compile(r"[\d₹$%]")


def clean(text: str, keep_punct: bool = False) -> str:
    t = text.strip()
    if not keep_punct:
        t = re.sub(r"^[\"'“‘(]+|[\"'”’),.;:!?…]+$", "", t)
    return t


def load_words(transcript: str) -> list[dict]:
    t = json.load(open(transcript))
    words = t["words"] if isinstance(t, dict) else t
    return [{"text": (w.get("text") or w.get("w") or "").strip(), "start": float(w["start"]), "end": float(w["end"])}
            for w in words if (w.get("text") or w.get("w") or "").strip()]


def group(words: list[dict], cuts: list[float] | None = None, max_words: int = 5, max_chars: int = 28,
          pause: float = PAUSE_BREAK, hold: float = HOLD, keep_punct: bool = False,
          emphasis: list[str] | None = None, auto_emphasis: bool = True) -> list[dict]:
    """Pure (tested). Returns natural flowing phrase groups [{start, end, words: [{text, start, end, em}]}]."""
    cuts = sorted(cuts or [])
    emph = {e.lower() for e in (emphasis or [])}
    # a removed filler was still sound: measure pauses against the previous ORIGINAL word, not the previous kept one
    usable, last_end = [], None
    for w in words:
        if re.sub(r"[^\w']", "", w["text"].lower()) in FILLERS:
            last_end = w["end"]
            continue
        usable.append({**w, "_prev_end": last_end})
        last_end = w["end"]
    groups, cur = [], []

    def crosses_cut(a: float, b: float) -> bool:
        return any(a < c <= b for c in cuts)

    for i, w in enumerate(usable):
        if cur:
            prev = cur[-1]
            text_len = sum(len(clean(x["text"], keep_punct)) + 1 for x in cur) + len(clean(w["text"], keep_punct))
            if (len(cur) >= max_words or text_len > max_chars or round(w["start"] - (w["_prev_end"] if w["_prev_end"] is not None else prev["end"]), 3) >= pause
                    or SENTENCE_END.search(prev["text"]) or crosses_cut(prev["end"] - 1e-3, w["start"])):
                groups.append(cur)
                cur = []
        cur.append(w)
    if cur:
        groups.append(cur)

    # Prevent awkward orphan 1-word groups (e.g. isolated "ya", "so", "and") by merging with adjacent groups
    # but never across sentence boundaries, jump cuts, or pause breaks
    if len(groups) > 1:
        merged_groups = []
        for gi, g in enumerate(groups):
            if len(g) == 1 and merged_groups:
                prev_g = merged_groups[-1]
                prev_len = sum(len(clean(x["text"], keep_punct)) + 1 for x in prev_g) + len(clean(g[0]["text"], keep_punct))
                time_gap = g[0]["start"] - prev_g[-1]["end"]
                if (not SENTENCE_END.search(prev_g[-1]["text"])
                        and prev_len <= max_chars
                        and time_gap < pause
                        and not crosses_cut(prev_g[-1]["end"] - 1e-3, g[0]["start"])):
                    prev_g.append(g[0])
                    continue
            merged_groups.append(g)
        if len(merged_groups) > 1 and len(merged_groups[0]) == 1:
            g0 = merged_groups[0]
            g1 = merged_groups[1]
            comb_len = len(clean(g0[0]["text"], keep_punct)) + 1 + sum(len(clean(x["text"], keep_punct)) + 1 for x in g1)
            time_gap = g1[0]["start"] - g0[0]["end"]
            if (not SENTENCE_END.search(g0[0]["text"])
                    and comb_len <= max_chars
                    and time_gap < pause
                    and not crosses_cut(g0[0]["end"] - 1e-3, g1[0]["start"])):
                merged_groups[1] = [g0[0]] + g1
                merged_groups.pop(0)
        groups = merged_groups

    out = []
    for gi, g in enumerate(groups):
        nxt = groups[gi + 1][0]["start"] if gi + 1 < len(groups) else None
        end = g[-1]["end"] + hold
        if nxt is not None:
            end = min(end, nxt - 0.02)
            if nxt - end < 0.6:          # a tiny gap reads as a flicker: hold until the next group
                end = nxt - 0.02
        ws = []
        for w in g:
            txt = clean(w["text"], keep_punct)
            key = re.sub(r"[^\w₹$%']", "", txt.lower())
            em = key in emph or (auto_emphasis and bool(NUMERIC.search(txt)))
            ws.append({"text": txt, "start": round(w["start"], 3), "end": round(w["end"], 3), "em": em})
        out.append({"start": round(g[0]["start"], 3), "end": round(max(end, g[-1]["end"]), 3), "words": ws})
    return out


# ---------------------------------------------------------------- catalog injection
def _replace_array(src: str, name: str, payload: str) -> tuple[str, bool]:
    m = re.search(r"((?:var|const|let)\s+%s\s*=\s*)\[" % re.escape(name), src)
    if not m:
        return src, False
    i, depth = m.end() - 1, 0
    for j in range(i, len(src)):
        if src[j] == "[":
            depth += 1
        elif src[j] == "]":
            depth -= 1
            if depth == 0:
                return src[:m.end() - 1] + payload + src[j + 1:], True
    return src, False


def font_face_css(style: dict, base_dir: str) -> tuple[str, str] | None:
    """The style's family stack and @font-face rules (display + fallback), files staged by the caller."""
    import treatments
    if not (style.get("fonts") or {}).get("display"):
        return None
    return treatments.family_stack(style), treatments.font_faces(style)


def inject(html: str, groups: list[dict], width: int, height: int, duration: float, y: float | None = None,
           font: tuple[str, str] | None = None, upper: bool | None = None,
           sets: dict[str, str] | None = None) -> tuple[str, list[str]]:
    """Pure-ish (tested): returns the new document and a list of what was changed."""
    notes = []
    # the host page already loads GSAP (locally); a second copy from the CDN fails offline and can replace window.gsap
    html, n = re.subn(r'\s*<script[^>]+src="https://cdn\.jsdelivr\.net/npm/gsap[^"]*"[^>]*>\s*</script>', "", html)
    if n:
        notes.append("removed the component's own GSAP <script> (the host provides it)")
    for name, val in (sets or {}).items():          # override a component constant, e.g. COLOR_INACTIVE=#5E5E5E
        lit = val if re.fullmatch(r"-?[\d.]+|true|false", val) else json.dumps(val)
        html, k = re.subn(r"((?:var|const|let)\s+%s\s*=\s*)[^;]+;" % re.escape(name), r"\g<1>%s;" % lit.replace("\\", "\\\\"), html)
        notes.append("%s = %s" % (name, val) if k else "%s: no such constant in this component" % name)
    words = [w for g in groups for w in g["words"]]
    wj = json.dumps([{"text": w["text"], "start": w["start"], "end": w["end"]} for w in words], ensure_ascii=False)
    idx, pairs, objs = 0, [], []
    for g in groups:
        pairs.append([idx, idx + len(g["words"]) - 1])
        objs.append({"wordStart": idx, "wordEnd": idx + len(g["words"]) - 1, "start": g["start"], "end": g["end"]})
        idx += len(g["words"])
    html, ok_w = _replace_array(html, "WORDS", wj)
    html, ok_t = _replace_array(html, "TRANSCRIPT", wj)
    if not (ok_w or ok_t):
        raise SystemExit("this component keeps its words in another shape (not WORDS or TRANSCRIPT); use the builtin "
                         "captions, or wire it by hand following its own comments")
    notes.append("words: %d in %s" % (len(words), "WORDS" if ok_w else "TRANSCRIPT"))
    html, ok = _replace_array(html, "RAW_GROUPS", json.dumps(pairs))
    if ok:
        notes.append("groups: %d (RAW_GROUPS)" % len(pairs))
    html, ok2 = _replace_array(html, "GROUPS", json.dumps(objs))
    if ok2:
        notes.append("groups: %d (GROUPS)" % len(objs))
    # length: the root's data-duration, a DURATION constant, and the 8.0 fallback some components use for the last group
    html = re.sub(r'(data-composition-id="[^"]+"[^>]*?data-duration=")[\d.]+(")', r"\g<1>%.3f\2" % duration, html, count=1)
    html = re.sub(r'(data-duration=")[\d.]+(")', r"\g<1>%.3f\2" % duration, html, count=1)
    html = re.sub(r"(var\s+DURATION\s*=\s*)[\d.]+", r"\g<1>%.3f" % duration, html)
    html = re.sub(r":\s*8\.0\s*;", ": %.3f;" % duration, html)
    # canvas
    html = re.sub(r'data-width="\d+"', 'data-width="%d"' % width, html)
    html = re.sub(r'data-height="\d+"', 'data-height="%d"' % height, html)
    html = html.replace("width=1920, height=1080", "width=%d, height=%d" % (width, height))
    # one pass: replacing 1920 then 1080 in sequence would turn the new 1080 width back into 1920
    html = re.sub(r"\b(1920|1080)px\b", lambda m: "%dpx" % (width if m.group(1) == "1920" else height), html)
    html = re.sub(r"(fitFontSize\([^)]*?,\s*)1620(\s*\))", r"\g<1>%d\2" % int(width * 0.84), html)
    html = re.sub(r"(maxWidth:\s*)1[56]\d\d\b", r"\g<1>%d" % int(width * 0.84), html)
    notes.append("canvas: %dx%d, %.2f s" % (width, height, duration))
    # vertical position: the first bottom offset in the stylesheet is the caption rail in these components
    if y is not None:
        bottom = int(round(height * (1 - y)))
        html, n = re.subn(r"bottom:\s*\d+px", "bottom: %dpx" % bottom, html, count=1)
        notes.append("rail moved to %d px from the bottom" % bottom if n else "no bottom offset found; position unchanged")
    # font
    if font:
        fam, faces = font
        html = re.sub(r'<link[^>]+fonts\.(googleapis|gstatic)\.com[^>]*>\s*', "", html)
        html = re.sub(r'@import url\([^)]*fonts\.googleapis\.com[^)]*\);?', "", html)
        html = re.sub(r'font-family:\s*[^;"\n]*?["\'][^"\']+["\'][^;\n]*;', "font-family: '%s', sans-serif;" % fam, html)
        html = re.sub(r'(\+\s*["\']px )[^"\']+(["\'])', r"\g<1>'%s'\2" % fam, html)          # canvas measure strings
        html = html.replace("<style>", "<style>\n" + faces + "\n", 1)
        notes.append("font: %s (local)" % fam)
    if upper is False:
        html = html.replace("text-transform: uppercase", "text-transform: none").replace(".toUpperCase()", "")
    return html, notes


def comp_id(html: str) -> str:
    m = re.search(r'data-composition-id="([^"]+)"', html)
    return m.group(1) if m else "captions"


# ---------------------------------------------------------------- builtin layer (used by treatments.py)
def builtin_layer(groups: list[dict], ctx: dict, cfg: dict) -> tuple[str, str, list[str]]:
    """HTML, CSS and timeline lines for a caption rail. cfg comes from style.json "captions"."""
    W, H = ctx["W"], ctx["H"]
    cfg = {**{k: v for k, v in cfg.items() if k not in ("portrait", "landscape")},
           **(cfg.get("portrait" if H > W else "landscape") or {})}      # orientation-specific values win
    mode = cfg.get("mode", "phrase")
    cap_em = cfg.get("max_emphasis")
    if cap_em is not None:
        for g in groups:
            seen = 0
            for w in g["words"]:
                if w["em"]:
                    seen += 1
                    if seen > int(cap_em):
                        w["em"] = False
    size = int(cfg.get("size", 0.075 if H > W else 0.045) * W)
    y = float(cfg.get("y", 0.68 if H > W else 0.86))
    fam = cfg.get("family", ctx.get("font_family", "sans-serif"))
    weight = cfg.get("weight", 800)
    color = cfg.get("color", "#ffffff")
    inactive_color = cfg.get("inactive_color", "rgba(255,255,255,0.70)")
    active = cfg.get("active_color", ctx.get("accent", "#ffd400"))
    em_color = cfg.get("emphasis_color", active)
    pill = cfg.get("pill_color", "")
    upper = cfg.get("case", "upper") == "upper"
    stroke = cfg.get("stroke", 0)
    shadow = cfg.get("shadow", "0 6px 22px rgba(0,0,0,.55)")
    maxw = int(W * float(cfg.get("max_width", 0.86)))
    top = int(H * y - size * 0.6)
    css = (".cap-rail{position:absolute;left:0;right:0;top:%dpx;display:flex;justify-content:center;z-index:60;pointer-events:none}"
           ".cap-g{position:absolute;left:0;right:0;display:flex;flex-wrap:wrap;justify-content:center;align-items:baseline;"
           "gap:0 %dpx;padding:0 %dpx;max-width:%dpx;margin:0 auto;opacity:0;visibility:hidden}"
           ".cap-w{display:inline-block;font-family:'%s',sans-serif;font-weight:%s;font-size:%dpx;line-height:1.15;color:%s;"
           "text-shadow:%s;%s%s padding:%s;border-radius:%dpx;transform-origin:center center}"
           ".cap-w.em{color:%s;%s}"
           % (top, int(size * 0.28), int((W - maxw) / 2), W, fam, weight, size,
              inactive_color if mode in ("phrase", "flow", "karaoke") else color, shadow,
              "-webkit-text-stroke:%dpx rgba(0,0,0,.85);paint-order:stroke fill;" % stroke if stroke else "",
              "text-transform:uppercase;" if upper else "", "0.04em 0.18em" if pill else "0", int(size * 0.22), em_color,
              ("background:%s;padding:0.02em 0.16em;border-radius:%dpx;-webkit-text-stroke:0;text-shadow:none" % (cfg["emphasis_bg"], int(size * 0.14)))
              if cfg.get("emphasis_bg") else ""))
    html = ['<div class="cap-rail" id="cap-rail">']
    js = []
    for gi, g in enumerate(groups):
        spans = "".join('<span class="cap-w%s" id="cw-%d-%d">%s</span>' % (" em" if w["em"] else "", gi, wi,
                        w["text"].replace("&", "&amp;").replace("<", "&lt;")) for wi, w in enumerate(g["words"]))
        gy = ' style="top:%dpx"' % int(H * (float(g["y"]) - y)) if g.get("y") is not None else ""
        html.append('<div class="cap-g" id="cg-%d"%s>%s</div>' % (gi, gy, spans))
        js.append("tl.set('#cg-%d', { visibility: 'visible' }, %.3f);" % (gi, g["start"] - 0.02))
        if mode in ("phrase", "flow", "block"):
            js.append("tl.fromTo('#cg-%d', { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.18, ease: 'power2.out' }, %.3f);"
                      % (gi, g["start"] - 0.02))
        else:
            js.append("tl.set('#cg-%d', { opacity: 1 }, %.3f);" % (gi, g["start"] - 0.02))
        for wi, w in enumerate(g["words"]):
            sel = "#cw-%d-%d" % (gi, wi)
            if mode == "pop":
                js.append("tl.fromTo('%s', { opacity: 0, scale: 0.90, y: 6 }, { opacity: 1, scale: 1, y: 0, duration: 0.14, "
                          "ease: 'power2.out' }, %.3f);" % (sel, w["start"] - 0.02))
            if mode in ("phrase", "flow", "karaoke", "pop") and not w["em"]:
                if pill:
                    js.append("tl.to('%s', { backgroundColor: '%s', color: '%s', duration: 0.08 }, %.3f);" % (sel, pill, color, w["start"]))
                    js.append("tl.to('%s', { backgroundColor: 'rgba(0,0,0,0)', color: '%s', duration: 0.08 }, %.3f);" % (sel, inactive_color, w["end"]))
                else:
                    js.append("tl.to('%s', { color: '%s', duration: 0.08 }, %.3f);" % (sel, active, w["start"]))
                    js.append("tl.to('%s', { color: '%s', duration: 0.10 }, %.3f);" % (sel, color if mode not in ("phrase", "flow") else inactive_color, w["end"]))
            elif w["em"]:
                js.append("tl.fromTo('%s', { scale: 0.94 }, { scale: 1.06, duration: 0.14, ease: 'back.out(1.4)' }, %.3f);" % (sel, w["start"]))
                js.append("tl.to('%s', { scale: 1.0, duration: 0.10, ease: 'power2.out' }, %.3f);" % (sel, w["start"] + 0.15))
        js.append("tl.to('#cg-%d', { opacity: 0, y: -4, duration: 0.12, ease: 'power2.in' }, %.3f);" % (gi, g["end"] - 0.10))
        js.append("tl.set('#cg-%d', { opacity: 0, visibility: 'hidden' }, %.3f);" % (gi, g["end"]))   # hard kill
    html.append("</div>")
    return "\n".join(html), css, js


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mode", choices=["groups", "catalog"])
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--cut-map")
    ap.add_argument("--max-words", type=int, default=3)
    ap.add_argument("--max-chars", type=int, default=18)
    ap.add_argument("--emphasis", nargs="*", default=[], help="extra words to emphasise")
    ap.add_argument("--keep-punct", action="store_true")
    ap.add_argument("--component")
    ap.add_argument("--out")
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--duration", type=float)
    ap.add_argument("--style", help="style.json: its display font replaces the component's (local file, Devanagari-safe)")
    ap.add_argument("--y", type=float, help="caption rail centre as a fraction of height (portrait ~0.66)")
    ap.add_argument("--case", choices=["upper", "keep"])
    ap.add_argument("--set", action="append", default=[], metavar="NAME=VALUE",
                    help="override a component constant (e.g. COLOR_INACTIVE=#5E5E5E when check flags contrast)")
    a = ap.parse_args()
    words = load_words(a.transcript)
    cuts = json.load(open(a.cut_map))["cuts"] if a.cut_map and os.path.isfile(a.cut_map) else []
    gs = group(words, cuts, a.max_words, a.max_chars, keep_punct=a.keep_punct, emphasis=a.emphasis)
    if a.mode == "groups":
        for g in gs:
            print("%7.2f-%7.2f  %s" % (g["start"], g["end"], " ".join(("*%s*" % w["text"]) if w["em"] else w["text"] for w in g["words"])))
        print("%d groups, %d words" % (len(gs), sum(len(g["words"]) for g in gs)))
        return
    if not (a.component and a.out):
        ap.error("catalog needs --component and --out")
    dur = a.duration
    if dur is None:
        cm = a.cut_map and os.path.isfile(a.cut_map) and json.load(open(a.cut_map)).get("flat_duration")
        dur = float(cm) if cm else max(w["end"] for w in words) + 0.5
    font = None
    if a.style:
        import stage
        pub = os.path.dirname(os.path.dirname(os.path.abspath(a.out)))      # <public>/compositions/captions.html
        st = stage.stage_fonts(json.load(open(a.style)), os.path.dirname(os.path.abspath(a.style)), pub)
        font = font_face_css(st, pub)
    html, notes = inject(open(a.component).read(), gs, a.width, a.height, dur, a.y, font,
                         upper=(None if a.case is None else a.case == "upper"),
                         sets=dict(kv.split("=", 1) for kv in a.set))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, "w").write(html)
    cid = comp_id(html)
    print("\n".join("  " + n for n in notes))
    rel = os.path.relpath(a.out, os.path.dirname(os.path.dirname(os.path.abspath(a.out))))
    print('host (paste into the root composition, or use a "block" beat):')
    print('  <div class="clip" data-composition-id="%s" data-composition-src="%s" data-start="0" data-duration="%.3f" '
          'data-width="%d" data-height="%d" data-track-index="50" style="position:absolute;inset:0;z-index:60"></div>'
          % (cid, rel, dur, a.width, a.height))


if __name__ == "__main__":
    main()
