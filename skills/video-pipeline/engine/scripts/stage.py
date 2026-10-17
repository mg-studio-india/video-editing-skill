#!/usr/bin/env python3
"""stage.py: storyboard.json -> public/index.html for ANY canvas (9:16 Shorts and Reels, 1:1, 4:5, or 16:9).

compose.py is the 16:9 talking-head composer with the forked format library; stage.py is the canvas-agnostic builder for
the seven treatments, word-exact captions, B-roll, registry blocks and the camera. Same storyboard shape and camera ops,
plus:
  "canvas": [1080, 1920]            output size (default 1080x1920)
  "video": "input-9x16.mp4"         the base footage in public/ (its audio is the programme sound)
  "matte": "subject-matte.webm"     optional alpha matte of the speaker, for "behind" beats (layered-head)
  "origin": "50% 30%"               camera transform origin (keep it on the face; top-anchored for 16:9 talking heads)
  "captions": {"source": "transcript.json", "max_words": 3, "emphasis": ["words"]}   adds the caption rail
  "sfx": [{"id": "pop1", "src": "sfx/pop.mp3", "at": 3.2, "dur": 0.4, "volume": 0.35}]

Usage:
  python3 stage.py --spec W/storyboard.json --out W/public --style W/style.json [--cut-map W/cut-map.json]
  then: npx hyperframes lint W/public && npx hyperframes snapshot W/public --at <beat midpoints>
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import captions as CAP  # noqa: E402
import treatments as T  # noqa: E402

ENGINE = os.path.dirname(HERE)
GSAP_LOCAL = os.path.join(ENGINE, "assets", "vendor", "gsap.min.js")
GSAP_CDN = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"


def camera_js(ops: list) -> list[str]:
    out = []
    for op in ops or []:
        k = op[0]
        if k == "set":
            out.append("tl.set('#cam', { scale: %.3f }, %.3f);" % (op[2], op[1]))
        elif k == "creep":
            out.append("tl.to('#cam', { scale: %.3f, duration: %.3f, ease: 'power1.inOut' }, %.3f);" % (op[3], op[2] - op[1], op[1]))
        elif k == "punch":
            out.append("tl.to('#cam', { scale: %.3f, duration: 0.32, ease: 'power2.out' }, %.3f);" % (op[2], op[1]))
        elif k == "release":
            out.append("tl.to('#cam', { scale: 1, duration: %.3f, ease: 'power2.inOut' }, %.3f);" % (op[2] if len(op) > 2 else 0.5, op[1]))
        elif k == "reveal":
            out.append("tl.fromTo('#cam', { scale: 1.10 }, { scale: 1, duration: 0.5, ease: 'power2.out' }, %.3f);" % op[1])
        else:
            raise SystemExit("unknown camera op %r" % (k,))
    return out


def stage_fonts(style: dict, style_dir: str, out: str) -> dict:
    """Copy the style's font files into public/fonts and rewrite the paths the page uses."""
    st = json.loads(json.dumps(style))
    for role in ("display", "body", "fallback"):
        f = (st.get("fonts") or {}).get(role)
        if not f:
            continue
        for w, path in list((f.get("files") or {}).items()):
            src = T.resolve_font(path, style_dir)
            if not os.path.isfile(src):
                raise SystemExit("font file not found: %s" % src)
            os.makedirs(os.path.join(out, "fonts"), exist_ok=True)
            shutil.copyfile(src, os.path.join(out, "fonts", os.path.basename(src)))
            f["files"][w] = "fonts/" + os.path.basename(src)
    return st


def build(spec: dict, style: dict, out: str, cuts: list[float]) -> str:
    canvas = spec.get("canvas")
    if not canvas and spec.get("video"):
        vpath = os.path.join(out, spec["video"]) if not os.path.isabs(spec["video"]) else spec["video"]
        if os.path.exists(vpath):
            pv = CAP.probe_video(vpath)
            if pv.get("width") and pv.get("height"):
                canvas = [pv["width"], pv["height"]]
    W, H = canvas or [1080, 1920]
    D = float(spec["duration"])
    cid = spec.get("id", "root")
    ctx_base = {"W": W, "H": H, "style": style, "camera_sel": "#cam",
                "face_box": spec.get("face_box"), "chin_y": spec.get("chin_y")}
    front, behind, root, css, js = [], [], [], [], []
    track = 10
    beats = list(spec.get("beats", []))
    cap = spec.get("captions")
    if cap:
        words = CAP.load_words(os.path.join(out, cap.get("source", "transcript.json")) if not os.path.isabs(cap.get("source", "")) else cap["source"])
        mw = int(cap["max_words"]) if cap.get("max_words") is not None else None
        mc = int(cap["max_chars"]) if cap.get("max_chars") is not None else None
        groups = CAP.group(words, cuts, max_words=mw, max_chars=mc,
                           emphasis=cap.get("emphasis", []), keep_punct=bool(cap.get("keep_punct", False)))
        groups = [g for g in groups if g["start"] < D - 0.2]
        for g in groups:
            g["end"] = min(g["end"], D - 0.05)
        # step aside: while a panel (drawer, cards) is up, its caption groups dynamically clear the panel
        panels = [(float(b["in"]), float(b["out"])) for b in beats if b["type"] in ("drawer", "cards") and b.get("in") is not None]
        low = float(cap.get("low_y", 0.86 if H > W else 0.92))
        for g in groups:
            if any(g["start"] < p1 and g["end"] > p0 for p0, p1 in panels):
                g["y"] = low
        beats.append({"type": "captions", "id": "captions", "groups": groups, "in": 0, "out": D})
    # one panel at a time: two overlapping panels collide (HyperFrames check: content_overlap)
    PANELS = ("drawer", "cards", "hero", "split", "banner")
    pw = sorted((float(b["in"]), float(b["out"]), b["id"]) for b in beats if b["type"] in PANELS and b.get("in") is not None)
    for (a0, a1, ai), (b0, b1, bi) in zip(pw, pw[1:]):
        if b0 < a1 - 0.05:
            print("WARN: %s and %s are on screen together (%.2f-%.2f); one panel at a time" % (ai, bi, b0, min(a1, b1)))
    lay = [b for b in beats if b["type"] == "layout"]
    for msg in T.layout_overlaps(lay):
        print("WARN: layouts %s; one speaker layout at a time" % msg)
    if lay and spec.get("matte") and any(b["type"] == "behind" for b in beats):
        print("WARN: 'behind' text assumes the full-frame video; keep it out of stack / pip / hide windows")
    beats = [b for b in beats if b["type"] != "layout"]
    for b in beats:
        if b.get("unresolved"):
            raise SystemExit("beat %s is unresolved; fix the plan and resolve again" % b.get("id"))
        if b["type"] not in T.TYPES:
            raise SystemExit("stage.py does not build %r (16:9 library formats are compose.py's)" % b["type"])
        if b["type"] == "behind" and not spec.get("matte"):
            raise SystemExit("beat %s is 'behind' but the storyboard has no \"matte\"" % b["id"])
        h, c, j, where = T.build(b, {**ctx_base, "track": track})
        track += 4
        {"front": front, "behind": behind, "root": root}[where].append(h)
        if c:
            css.append(c)
        js.extend(j)
    audio = []
    for s in spec.get("sfx", []):
        if not s.get("src") or not isinstance(s.get("at"), (int, float)):
            print("WARN: sound %s skipped (%s)" % (s.get("id"), "no file: fetch it with heygen-sound.py" if not s.get("src")
                                                   else "no time: its anchor did not resolve"))
            continue
        if float(s["at"]) >= D - 0.05:
            print("WARN: sound %s at %.2f s is past the end (%.2f s); skipped" % (s.get("id"), float(s["at"]), D))
            continue
        audio.append('<audio id="%s" src="%s" data-start="%.3f" data-duration="%.3f" data-volume="%.2f" data-track-index="%d"></audio>'
                     % (s["id"], s["src"], float(s["at"]), float(s.get("dur", 1.0)), float(s.get("volume", 0.4)), track))
        track += 1
    matte = ""
    if spec.get("matte"):
        matte = ('<video id="matte" class="clip" src="%s" muted playsinline data-start="0" data-duration="%.3f" data-track-index="2" '
                 'style="position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover;z-index:6"></video>' % (spec["matte"], D))
    gsap = "vendor/gsap.min.js" if os.path.isfile(GSAP_LOCAL) else GSAP_CDN
    if os.path.isfile(GSAP_LOCAL):
        os.makedirs(os.path.join(out, "vendor"), exist_ok=True)
        shutil.copyfile(GSAP_LOCAL, os.path.join(out, "vendor", "gsap.min.js"))
    else:
        print("note: no local gsap.min.js in %s; the page loads GSAP from the CDN (renders then need internet)"
              % os.path.dirname(GSAP_LOCAL))
    page = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<style>
%s
html, body { margin: 0; background: #000; }
#%s { position: relative; width: 100%%; height: 100%%; overflow: hidden; background: %s; }
#cam-wrap { position: absolute; left: 0; top: 0; width: %dpx; height: %dpx; overflow: hidden; z-index: 1; }
#cam { position: absolute; inset: 0; transform-origin: %s; }
#base { position: absolute; inset: 0; width: 100%%; height: 100%%; object-fit: cover; z-index: 1; }
%s
</style>
</head>
<body>
  <div id="%s" data-composition-id="%s" data-start="0" data-duration="%.3f" data-fps="30" data-width="%d" data-height="%d">
    <div id="cam-wrap">
      <div id="cam" data-layout-allow-overflow>
        <video id="base" class="clip" src="%s" playsinline data-has-audio="true" data-start="0" data-duration="%.3f" data-track-index="1"></video>
%s
        %s
      </div>
    </div>
%s
%s
%s
    <script src="%s"></script>
    <script>
      (function () {
        const tl = gsap.timeline({ paused: true });
        // camera
        %s
        // speaker layouts
        %s
        // beats
        %s
        tl.to({}, { duration: %.3f }, 0);
        window.__timelines["%s"] = tl;
      })();
    </script>
  </div>
</body>
</html>
""" % (T.font_faces(style), cid, T.tok(style, "colors", "dark") or "#000", W, H, spec.get("origin", "50% 30%" if H > W else "52% 0%"), "\n".join(css), cid, cid, D, W, H,
       spec.get("video", "input-video.mp4"), D, "".join(behind), matte, "".join(root), "".join(front), "\n    ".join(audio),
       gsap, "\n        ".join(camera_js(spec.get("camera"))), "\n        ".join(T.layout_js(lay, W, H, style)),
       "\n        ".join(js), D, cid)
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "index.html")
    open(path, "w").write(page)
    hf = os.path.join(out, "hyperframes.json")
    if not os.path.isfile(hf):
        json.dump({"paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}},
                  open(hf, "w"), indent=2)
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--style", required=True)
    ap.add_argument("--cut-map")
    a = ap.parse_args()
    spec = json.load(open(a.spec))
    style = json.load(open(a.style))
    style = stage_fonts(style, os.path.dirname(os.path.abspath(a.style)), a.out)
    cuts = json.load(open(a.cut_map))["cuts"] if a.cut_map and os.path.isfile(a.cut_map) else []
    path = build(spec, style, a.out, cuts)
    n = len(spec.get("beats", []))
    W, H = spec.get("canvas", [1080, 1920])
    print("%s: %dx%d, %.2f s, %d beats%s" % (path, W, H, float(spec["duration"]), n, ", captions" if spec.get("captions") else ""))
    mids = sorted({round((float(b["in"]) + float(b["out"])) / 2, 2) for b in spec.get("beats", []) if b.get("in") is not None})
    print("snapshot: npx hyperframes snapshot %s --at %s" % (a.out, ",".join(str(m) for m in mids[:12]) or "1"))


if __name__ == "__main__":
    main()
